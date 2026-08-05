# T0218 Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- 来源：T0217 Ac1 用户决策"buf 层字节序统一纳入后续任务"（followup_of: T0217-0805-rpc-serialization-hardening）

## 查重结果

- 搜索 pdca/tasks/、knowledge/ 无已存在的 buf 层字节序任务
- knowledge/data-formats/backup-tools-serialization-practice.md 为备份工具序列化实践（不同主题，无冲突）
- T0217 已归档（archive/2026-08/0805-rpc-serialization-hardening），其 conclusion.md "下一轮建议"明确列出此跟进项

## Claim 验证

- 代码事实（已由 T0217 Check 阶段核实）：全仓库 84 处 buf_put_u32/buf_get_u32 调用（rpc-server.cpp 的 rpc_conn_* 高层为主），协议层已零大端残留
- STREAM INIT body 已用 buf_put_u32_le 切换（T0217 完成），可作切换参照
- 影响面：rpc_conn_* 高层 API（文件下载/上传/元数据），需协调 rdbcomm 共用方

## 信息缺口

- buf_put_u32/get_u32 是否被 rdbcomm 共享（需查 libs/ 头文件与 rdbcomm 引用）
- buf 层 wire 变更是否需 RPC_FRAME_VERSION 再提升
- 既有覆盖测试清单（download_fileats/upload_fileats 等）

## 推荐下一步

1. P1 澄清：确认 buf 层切换范围（rpc 专用 vs 全局 buf 工具）
2. P2 Grill：rdbcomm 兼容策略（同步改 vs 隔离）
3. P3 PRD：明确 AC 与版本策略
