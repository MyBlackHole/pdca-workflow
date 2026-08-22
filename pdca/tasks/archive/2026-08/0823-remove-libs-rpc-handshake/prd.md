# 删除 libs/rpc-handshake：rdbcomm/dmsbtex/libobk 项目内实现握手逻辑 — 规格文档

## 问题陈述

- **现状**: `libs/rpc-handshake.{c,h}` 是共享握手库，rpc/rdbcomm/dmsbtex/libobk 四项目均依赖。rpc 项目已自实现握手（`rpc-protocol.h` 帧 + `rpc-server.cpp` 分流 + `rpc-io.cpp` 客户端），libs 版成为冗余；且各项目业务语义不同（rdbcomm/dmsbtex/libobk 的握手帧与 rpc 不同源），共享层造成跨项目耦合。
- **目标**: 删除 `libs/rpc-handshake.{c,h}` 与 `libs/rpc-net.c` 中的握手部分，rdbcomm/dmsbtex/libobk 三项目各自在项目内部实现等价握手逻辑（会话初始化、算法映射、协商分流），rpc 项目不受影响。
- **差距**: 三项目共约 60 处 `rpc_hs_*` 引用需迁移为项目内实现。

## 解决方案

以 libs 现有**行为与协议字节**为契约基线，学习 rpc 项目自实现模式：**按"协议层 / IO 会话层"两层结构拆分，融入各项目既有模块**（不保留独立 handshake 文件）：

rpc 参照分层：
- 协议层（rpc-protocol）：帧类型/常量、hton/ntoh 编解码、算法映射 `hs_algorithm_*`；
- IO 会话层（rpc-io）：会话类型内嵌读写函数指针分发 plain/TLS、生命周期 init/cleanup、客户端协商；
- 服务端分流在 server 模块内处理（rpc-server.cpp）。

三项目落点映射：

| 层 | 职责 | rdbcomm | dmsbtex | libobk |
|----|------|---------|---------|--------|
| 协议层 | 帧常量/结构/encode/decode/算法映射/decide | `msg.{c,h}` 追加 | `protocol.{c,h}` 追加 | `include/protocol.h` 追加声明 + 新建 `lib/protocol.c` 实现 |
| IO 会话层 | 会话类型+生命周期+send/recv 分发+client_negotiate(_config)+request_time | 新建 `io.{c,h}`（对标 rpc-io） | `network.{c,h}` 追加（与既有 sbt_session_* 包装合流） | `lib/sbt/libobk.c` 融入（与既有 static 包装合流），会话类型声明入 `include/protocol.h` |
| 服务端分流 | server_accept（TIME/NEGOTIATE 分流+TLS 升级） | `server.c` 内部化 | `network.c`（既有 sbt_session_server_accept 合流） | `lib/logic/oracleCmdTbl.c`（既有 static 包装合流） |

1. **符号彻底项目化**：`rpc_hs_*`→`rdb_hs_*`/`dm_hs_*`/`obk_hs_*`；宏/枚举值 `RPC_HS_*`→`RDB_HS_*`/`DM_HS_*`/`OBK_HS_*`；include guard 随新头归属（如 `__IO_H__`/`__MSG_H__` 已有风格）。
2. **导出面按需收敛**（协议字节零变化）：仅导出各项目实际使用集（rdbcomm 9 个 / dmsbtex、libobk 各 8 个）；encode/decode/decide/server_respond/send_error/send_time_response 等仅为内部依赖，static 化或随模块私有化；server_negotiate 全项目无使用，删除。
3. **删除** `libs/rpc-handshake.{c,h}`（已删）、三项目 handshake.{c,h} 共四份文件；`libs/xmake.lua` 移除目标引用。
4. **libs/rpc-net.c 定位**：rpc time 协议客户端（TIME 帧已内联 HS_NET_* 局部实现，无握手库依赖），供 timed_net_key 使用，保留。
5. **rpc 项目不动**；rpc/tests 中 `[migrated] rpc_hs_* removed` 注释措辞清理（避免 AC-4 grep 命中）。

## Seam 分析

### 声明的测试接缝
- seam: rdbcomm/tests/tool_integration.c -> rdbcomm/msg.h + rdbcomm/io.h（项目内握手协议/会话层）
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.h + dmsbtex/protocol.h
- seam: libobk/test/session_test.c -> libobk/include/libobk.h + libobk/include/oracleCmdTbl.h
- seam: libobk/test/protocol_test.c -> libobk/include/protocol.h

### 验收可测性

- 每项目现有测试套件作为回归基线：rdbcomm_tool_integration / dmsbtex_session_test / libobk_session_test 全绿即等价。

## 用户故事

1. 作为各项目维护者，我希望握手逻辑归属本项目内部，修改协议时无需协调共享库多项目发布。
2. 作为构建维护者，我希望删除无主共享库文件，消除 libs 中仅剩单点使用的伪共享代码。

## 实现决策

- **模块与顺序**（每项目独立切片，互不阻塞）：
  - 切片 A：rdbcomm —— `rdbcomm/handshake.{c,h}` 项目化改造（改名+static 收敛），改 `client.c/client.h/server.c/server.h/msg.c/msg.h/rdbcomm-main.c/rdbcommd-main.c` 引用，tool_integration 回归
  - 切片 B：dmsbtex —— 同模式，改 `network.c/network.h/sbt.c/main.c`，session_test 回归
  - 切片 C：libobk —— `libobk/include/handshake.h` + `libobk/lib/handshake.c` 项目化，删 `lib/handshake.h` 冗余份，改 `libobk.h/oracleCmdTbl.h/libobk.c/oracleCmdTbl.c`，session/protocol_test 回归
  - 切片 D：清理 `libs/xmake.lua` 目标引用、rpc/tests 注释措辞、全仓 grep 归零、全量构建
- **技术澄清**:
  - 移动而非重写：从 libs 拷贝后机械改名（sed 级），协议字节与行为零变化；"学习 rpc"指实现形态（项目自有+按需+命名空间化），不复制其 C++ 消息体系。
  - rpc 项目已自实现，不在本任务范围。
  - 测试中 `rpc_hs_*` 引用同步改为项目内符号。

## 测试决策

- 仅测外部行为：三项目现有集成/会话测试套件全绿即为等价证明；不新增测试（行为未变）。

## 验收标准

- [ ] AC-1: `rdbcomm_tool_integration` 全用例 PASS。
- [ ] AC-2: `dmsbtex_session_test` 全用例 PASS。
- [ ] AC-3: `libobk_session_test` 全用例 PASS。
- [ ] AC-4: 全仓 `grep -rn "rpc_hs_\|rpc-handshake"` 结果为 0（libs 源文件已删除）。
- [ ] AC-5: 全量 `xmake build` 成功，无新增警告。

## 范围外

- 不改变握手协议字节与语义（纯移动重构）。
- 不动 rpc 项目（已自实现）。
- 不做 T0348 遗留 F5 文档化。

## 备注

- 已知存量问题：`dmsbtex_session_test` AC-1 rc=-11 在改动前即失败（HEAD 存量），修复属独立问题不计入本任务 AC；以 stash 对照甄别非本任务引入的失败。
