# 三项目明文通信跳过协议握手，对齐 rpc 按需握手语义 — 规格文档

## 问题陈述

- **现状**：rpc 项目握手为**按需触发**（`!mtls_enabled → return 0`，明文模式零握手帧；服务端 HANDSHAKE 处理内嵌消息循环非强制首阶段）。而 rdbcomm/dmsbtex/libobk 三项目为**无条件强制握手**：
  - 客户端连接后无论是否启用 mTLS 总是发送 NEGOTIATE 协商帧；
  - 服务端总是阻塞等待首阶段握手帧后才进入业务循环。
- **目标**：三项目对齐 rpc 语义——明文部署下零握手帧、零握手等待；mTLS 部署下握手路径保持不变。
- **差距**：三项目各 2 个入口（client 一体协商 / server 首阶段）的条件化改造 + 对应测试用例更新。

## 解决方案

**方案 Z'：握手内嵌消息循环 + 无降级**（完全对齐 rpc 决策树并收紧）：

利用三项目已有帧类型字段承载协商（新增 HANDSHAKE 类型常量）：
- rdbcomm：消息首字节 type 表追加 HANDSHAKE 类型；
- dmsbtex：`network_header_t.cmd` 追加 `CMD_HANDSHAKE`；
- libobk：`activeioHeader.cmdId` 枚举追加 HANDSHAKE 值。

### 行为矩阵（终版）

| server \\ client | 明文直连（不协商） | 协商（want_mtls=1） |
|---|---|---|
| server mtls=0 + 证书可用 | 明文业务 | **OK_MTLS 升级（按需）** |
| server mtls=0 + 证书不可用 | 明文业务 | **拒绝（ERR_MTLS_UNAVAILABLE），不允许降级** |
| server mtls=1 | 拒绝明文业务帧 | OK_MTLS 升级 |

### 各端改造
- 客户端：`mtls_enabled=0` 零握手直连；`=1` 时发送项目帧封装的协商载荷，
  收到非 OK_MTLS 一律失败断开（无降级容忍）。
- 服务端：握手处理内嵌消息循环——HANDSHAKE 类型帧走决策树
  （强制/按需升级/无证书拒绝），其余帧按原业务分发；
  强制模式下未握手的明文业务帧拒绝。
- rdbcomm：type 分发表扩展；dmsbtex：cmd 分支扩展；libobk：cmdId 枚举扩展。

## Seam 分析

### 声明的测试接缝

- seam: rdbcomm/tests/handshake_session_test.c -> io.h
- seam: dmsbtex/test/session_test.c -> network.h
- seam: libobk/test/session_test.c -> oracleCmdTbl.h

### 验收可测性

- 明文零握手以链接级测试证明：明文用例中服务端不期待握手帧、业务帧直达往返。
- mTLS 路径回归：既有 mTLS 正向/负路径用例全绿即等价。
- 组合矩阵以 grep 断言辅助确认条件分支存在。

## 用户故事

1. 作为明文部署用户，连接建立后立即进入业务，无额外一次往返的握手开销。
2. 作为三项目维护者，与 rpc 项目共享一致的"按需握手"心智模型。

## 实现决策

- **切片 A**：rdbcomm 条件化（client.c 入口判断已具备 conn->mtls_enabled 字段；server.c on_connect 增加 options.mtls_enabled 判断）。
- **切片 B**：dmsbtex network.c 两函数入口条件化。
- **切片 C**：libobk 两处入口条件化（client 侧读 ctx->tls_mtls_enabled；server 侧读 cfg->mtls_enabled）。
- **技术澄清**:
  - 协商帧 wire 格式变更：由裸 AIOH 帧改为项目帧头封装（mTLS 场景字节变化，PRD 声明的破坏性变更）。
  - **无降级约束**（用户明确）：服务端对协商请求只回 OK_MTLS 或错误码，永不回 OK_PLAIN；客户端收到任何非 OK_MTLS 即失败断开。
  - 明文部署（双方都不启用）零握手零开销；混布新旧版本在 mTLS 场景不兼容，需三端同步升级。
  - AIOH 裸帧格式随本任务废弃，rdb_hs/dm_hs/obk_hs 的 encode/decode 与帧常量随之清理。

## 测试决策

- 既有链接级套件更新语义：明文用例验证"零握手直通"，mTLS 用例保持原断言。
- 不新增测试框架；沿用 socketpair+fork/thread 模式。

## 验收标准

- [ ] AC-1: rdbcomm handshake_session_test 更新后全绿（含新增明文零握手直通用例）。
- [ ] AC-2: dmsbtex_session_test 全绿（AC-3 plain 用例语义更新为零握手直通）。
- [ ] AC-3: libobk_session_test 全绿。
- [ ] AC-4: xmake build -r 全量成功无新增警告；xmake test 全绿。
- [ ] AC-5: 三项目代码中明文路径不再调用协商/首阶段函数（grep 断言条件分支存在）。

## 范围外

- 不改帧格式/枚举值/mTLS 路径字节（协议兼容性仅限握手触发时机）。
- 不动 rpc 项目。
- 不做混合版本（新旧混布）的错误码增强。
- 不处理 libs/rpc-net.c（T0353 已完成）。

## 备注

- rpc 基线参照：rpc-io.cpp `rpc_ensure_handshake`（!mtls_enabled → hs_done=true return 0）、rpc-server.cpp HANDSHAKE 内嵌循环。
