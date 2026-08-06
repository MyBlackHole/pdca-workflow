# T0218 buf 层(rpc_conn_* 高层)字节序统一切小端

## 问题陈述

T0217 已完成协议层（rpc-protocol/rpc-msg/帧头/STREAM INIT body）小端化，
但 buf 工具（libs/buf.h 的 buf_put_u32/buf_get_u32）仍保持大端，被 rpc_conn_*
高层封装（84 处调用）与 rdbcomm 协议（server.c/client.c）共享。当前 wire
格式混杂大端（buf 层）与小端（协议层），存在跨机异构风险与维护负担。

## 决策（用户确认）

**全局切小端同步改 rdbcomm**：buf_put_u32/get_u32 全套切换为小端，
同步修改 rdbcomm/server.c + client.c 的 RDBCOMM 协议编解码（两端同步升级），
wire 格式完全统一。

## 已知信息

- buf API：libs/buf.h（buf_put_u32/buf_get_u32/buf_put_u16/buf_get_u16/buf_put_u8 等）
- buf_put_u32 调用方：rpc/（rpc-server.cpp rpc_conn_* 高层、rpc-command.cpp、rpc.cpp、rpc-msg.c）、rdbcomm/（server.c、client.c）、fs-backup/fsdeamon/unix_server.cpp、libs/unix_ipc.c
- rdbcomm 用 buf_put_u32 构建 RDBCOMM_MSG_STATUS/HANDLE 消息（server.c L371-373/L403-405），get_u32 解析（L470/L574-576）
- STREAM INIT body 已用 buf_put_u32_le 切换（T0217 完成，rpc-msg.h L107）
- 协议层零大端残留已验证（T0217 AC-4）
- T0217 提交 c4549f4a，buf_put_u32_le/buf_get_u32_le 变体已存在

## 信息缺口（P1 待核实）

- fs-backup/fsdeamon/unix_server.cpp、libs/unix_ipc.c 的 buf_put_u32 用途（是否 rdbcomm 相关或独立协议）
- rdbcomm 是否有独立测试覆盖（wire 格式断言）
- 全局 buf 切 LE 是否影响 RPC_FRAME_VERSION 判断（buf 层 wire 变更属不兼容变更，两端同步升级即可）

## 验收标准（P1 更新版）

- [ ] AC-1: buf_put_u32/get_u32/buf_put_u16/get_u16 全套切换为 LE
- [ ] AC-2: rpc_conn_* 高层 84 处调用点逐核对，收发对称无半边改半边
- [ ] AC-3: rdbcomm server.c/client.c RDBCOMM 协议编解码同步切 LE，两端同步升级
- [ ] AC-4: fs-backup/unix_ipc 等其余调用方核对（是否受影响或同步）
- [ ] AC-5: 全量回归通过（rpc 全部测试 + rdbcomm 相关 + download/upload 流路径）
- [ ] AC-6: 全仓库 buf 大端调用零残留静态扫描
