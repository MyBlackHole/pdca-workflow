# 握手逻辑按 rpc 两层结构拆分融入 msg/protocol/network 并项目化命名 — 规格文档

## 问题陈述

- **现状**: T0351 已删除 `libs/rpc-handshake.{c,h}`，但三项目（rdbcomm/dmsbtex/libobk）的 `handshake.{c,h}` 为 libs 全量拷贝，保留 `rpc_hs_*` 共享前缀符号与 `RPC_HS_*` 宏（28 个文件仍含引用），未达成"像 rpc 项目一样项目内部实现"的目标形态：
  - rpc 项目自实现为**两层结构**：协议层（rpc-protocol 帧+算法映射）/ IO 会话层（rpc-io 会话类型+协商），无独立握手文件；
  - 三项目仍是独立全量库文件（477 行，含各项目用不到的导出函数），命名空间仍是共享库风格。
- **目标**: 按 rpc 两层结构将握手逻辑拆分融入三项目既有模块（msg/protocol/network 等），符号彻底项目化（`rdb_hs_*`/`dm_hs_*`/`obk_hs_*`），全仓 `rpc_hs_`/`rpc-handshake` 归零；协议字节与行为零变化。
- **差距**: 3 个项目 × (协议层拆分 + 会话层拆分 + 服务端分流内部化) + 全部调用点改名 + libs/rpc-net.c TIME 帧局部宏核对 + rpc/tests 注释清理。

## 解决方案

以现有行为与协议字节为契约基线，机械搬运转场：

### 两层落点映射

| 层 | 职责 | rdbcomm | dmsbtex | libobk |
|----|------|---------|---------|--------|
| 协议层 | 帧常量/结构/encode/decode/算法映射/decide | `msg.{c,h}` 追加 | `protocol.{c,h}` 追加 | `include/protocol.h` 追加声明 + 新建 `lib/protocol.c` |
| IO 会话层 | 会话类型+生命周期 init_plain/init_tls/cleanup+读写分发+client_negotiate(_config)+request_time | 新建 `io.{c,h}`（对标 rpc-io.h/cpp） | `network.{c,h}` 追加（与既有 sbt_session_* 包装合流） | `lib/sbt/libobk.c` 融入（既有 static 包装合流），会话类型声明入 `include/protocol.h` |
| 服务端分流 | server_accept（TIME/NEGOTIATE 分流+TLS 升级） | `server.c` 内部化 | `network.c`（既有 sbt_session_server_accept 合流） | `lib/logic/oracleCmdTbl.c`（既有 static 包装合流） |

### 命名规则（已确认）

- 函数/类型：`rpc_hs_*` → `rdb_hs_*` / `dm_hs_*` / `obk_hs_*`
- 宏/枚举值：`RPC_HS_*` → `RDB_HS_*` / `DM_HS_*` / `OBK_HS_*`（彻底改）
- include guard 随所在头文件的既有风格（如 rdbcomm `__MSG_H__`/`__IO_H__`）

### 导出面收敛

仅导出各项目实际使用集（rdbcomm 9 个 / dmsbtex、libobk 各 8 个）；encode/decode/decide/server_respond/send_error/send_time_response/send/recv 等仅为内部依赖 → static 化或随模块私有化；`server_negotiate` 全项目无使用 → 删除。

### 清理项

- 删除三项目 `handshake.{c,h}`（rdbcomm/dmsbtex 各一对、libobk include+lib 三份）
- `libs/xmake.lua` 移除 rpc-handshake 目标引用
- `libs/rpc-net.c` 定位确认：rpc time 协议客户端（TIME 帧已内联 HS_NET_* 局部宏，无握手库依赖），供 timed_net_key 使用，保留不动
- rpc/tests 中 `[migrated] rpc_hs_* removed` 注释措辞清理

## Seam 分析

### 声明的测试接缝

- seam: rdbcomm/tests/tool_integration.c -> rdbcomm/msg.h + rdbcomm/io.h（协议层+会话层）
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.h + dmsbtex/protocol.h
- seam: libobk/test/session_test.c -> libobk/include/libobk.h + libobk/include/oracleCmdTbl.h
- seam: libobk/test/protocol_test.c -> libobk/include/protocol.h

## 用户故事

1. 作为各项目维护者，握手代码归属项目自有分层模块（协议层/IO 层），修改协议时在项目内闭环，无共享库前缀的心理耦合。
2. 作为构建维护者，全仓 grep `rpc_hs_|rpc-handshake` 归零，共享库痕迹彻底消除。

## 实现决策

- **模块与顺序**（每项目独立切片，互不阻塞）：
  - 切片 A：rdbcomm —— 协议层入 msg、新建 io 会话层、server.c 内部化 server_accept；改 client/server/msg 调用点与两个 main 的 include；删 handshake.{c,h}；tool_integration 回归
  - 切片 B：dmsbtex —— 协议层入 protocol、会话层入 network（包装合流）；改 main.c/sbt.c；删 handshake.{c,h}；session_test 回归
  - 切片 C：libobk —— protocol.h 追加声明、新建 lib/protocol.c、libobk.c 融入会话层、oracleCmdTbl.c 内部化 server_accept；删三份 handshake 文件；session/protocol_test 回归
  - 切片 D：libs/xmake.lua 与 rpc/tests 清理、全仓 grep 归零验证、全量构建
- **技术澄清**:
  - 移动而非重写：按层搬运后机械改名，协议字节与行为零变化；"学习 rpc"指两层结构与命名空间化，不复制其 C++ 消息继承体系。
  - libobk 对外 ABI：oracleCmdTbl.h/libobk.h 签名中会话类型改名（rpc_hs_session_t→obk_hs_session_t），结构布局不变，宿主重编译即可。
  - 测试中 `rpc_hs_*` 引用同步改为项目内符号。
  - 存量失败甄别：dmsbtex AC-1 rc=-11 与 rdbcomm 17611 为 HEAD 存量失败（T0351 conclusion 已 stash 对照确认），以对照法甄别非本任务引入。

## 测试决策

- 仅测外部行为：三项目现有集成/会话测试套件全绿即为等价证明；不新增测试（行为未变，纯移动重构）。

## 验收标准

- [ ] AC-1: `rdbcomm_tool_integration` 通过（17610 PASS；17611 若失败须经 stash 对照确认为存量）。
- [ ] AC-2: `dmsbtex_session_test` 通过（AC-1 rc=-11 若存在须经 stash 对照确认为存量）。
- [ ] AC-3: `libobk_session_test` 与 `libobk_protocol_test` exit 0 无 assert 失败。
- [ ] AC-4: 全仓 `grep -rn "rpc_hs_\|rpc-handshake" --include="*.c" --include="*.h" --include="*.cpp"` 结果为 0；三项目 handshake.{c,h} 五份文件不存在。
- [ ] AC-5: 全量 `xmake build` 成功，无新增警告。

## 范围外

- 不改变握手协议字节与语义（纯移动重构）。
- 不动 rpc 项目握手实现本身（仅 tests 注释措辞清理）。
- 不做 time 校时链路迁移（libs/rpc-net.c 内联 TIME 帧维持现状）。
- 不修复 dmsbtex rc=-11 / rdbcomm 17611 存量失败（T0351 结论建议另立专项）。

## 备注

- 前置任务：T0351-0823-remove-libs-rpc-handshake（已归档，删除了 libs 共享库并留下项目内拷贝）。
- 本任务是 T0351 的形态重构延续：从"项目内全量副本"进化为"rpc 式两层融入"。
