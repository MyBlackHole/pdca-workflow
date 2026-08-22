# 三项目明文通信跳过协议握手，对齐 rpc 按需握手语义 — 规格文档

## 问题陈述

- **现状**：rpc 项目握手为**按需触发**（`!mtls_enabled → return 0`，明文模式零握手帧；服务端 HANDSHAKE 处理内嵌消息循环非强制首阶段）。而 rdbcomm/dmsbtex/libobk 三项目为**无条件强制握手**：
  - 客户端连接后无论是否启用 mTLS 总是发送 NEGOTIATE 协商帧；
  - 服务端总是阻塞等待首阶段握手帧后才进入业务循环。
- **目标**：三项目对齐 rpc 语义——明文部署下零握手帧、零握手等待；mTLS 部署下握手路径保持不变。
- **差距**：三项目各 2 个入口（client 一体协商 / server 首阶段）的条件化改造 + 对应测试用例更新。

## 解决方案

**条件跳过方案**（保持现有 AIOH 帧格式与 mTLS 路径字节不变）：

| 组件 | mtls_enabled=0 | mtls_enabled=1 |
|------|----------------|----------------|
| 客户端一体协商 | `init_plain` 后直接返回成功，**不发任何帧** | 现行协商+证书升级路径不变 |
| 服务端首阶段 | `init_plain` 后直接返回成功，**不等握手帧**，业务循环照常 | 现行协商分流+TLS 升级路径不变 |

- rdbcomm：`rdb_hs_client_session_init` 入口条件化；`on_connect` 在服务端未启用 mTLS 时跳过 `rdb_hs_server_first_stage` 调用。
- dmsbtex：`sbt_session_client_init`/`sbt_session_server_accept` 同型条件化（network.c 单文件内聚）。
- libobk：`libobk.c` client 侧与 `oracleCmdTbl.c` server 侧同型条件化。

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
  - 仅增加前置短路，不改动任何帧格式、枚举值与 mTLS 路径字节。
  - 行为变化声明（破坏性）：旧版客户端（无条件协商）对新版明文服务端将因帧错位断连——部署需三端同步升级；新版客户端对旧版明文服务端同理。
  - 混合场景（client 要求 mTLS 而 server 未启用）在新语义下表现为帧错位断连而非 ERR_MTLS_UNAVAILABLE 错误码，属可接受退化（PRD 声明）。

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
