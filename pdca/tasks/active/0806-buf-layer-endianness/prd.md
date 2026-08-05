# T0218 buf 层(rpc_conn_* 高层)字节序统一切小端

## 问题陈述

T0217 已完成协议层（rpc-protocol/rpc-msg/帧头/STREAM INIT body）小端化，
但 rpc_conn_* 高层封装的 buf 层（conn->msgw/msgr）仍保持大端
（buf_put_u32/buf_get_u32），共 84 处调用（rpc-server.cpp 为主）。
当前状态：buf 层收发对称自洽，本机测试通过，但 wire 格式混杂大端（buf 层）
与小端（协议层），存在跨机异构风险与维护负担。

## 已知信息

- buf 层 API：buf_put_u32/buf_get_u32/buf_put_u16/buf_get_u16 等位于 libs/ 或 rpc 公共头
- 84 处调用点集中在 rpc-server.cpp 的 rpc_conn_* 高层封装（lstat/chmod/chown/access/upload/download 等）
- 需要协调 rdbcomm 共用方（同一 buf 工具被 rdbcomm 模块使用，需确认改动是否波及其 wire 格式）
- STREAM INIT body 已用 buf_put_u32_le/buf_get_u32_le 切换（T0217 完成），可作参照
- 用户决策（T0217 Ac1）：纳入后续任务处理

## 信息缺口

- buf_put_u32/get_u32 的调用方完整清单（84 处逐一核对收发对称）
- rdbcomm 是否使用 buf_put_u32 及其 wire 格式是否与 rpc 共享
- 是否有既有测试覆盖 buf 层大端路径（download_fileats/upload_fileats 等）
- RPC_FRAME_VERSION 是否需再提升（buf 层 wire 变更属不兼容变更）

## 验收标准（草案，待 P1 澄清）

- [ ] AC-1: buf_put_u32/get_u32 全套切换为 LE（含 u16/u64 变体）
- [ ] AC-2: 84 处调用点逐一核对收发对称，无半边改半边
- [ ] AC-3: rdbcomm 共用方兼容性确认（不受影响或已协调）
- [ ] AC-4: 协议版本提升（如需）混跑返回 PROTO_VERSION
- [ ] AC-5: 全量回归通过（含 download/upload 流路径）
- [ ] AC-6: buf 层大端零残留静态扫描
