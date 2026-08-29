## T0393 纠错记录（verdict overturn）

**时间**：2026-08-26T23:36:54+08:00

**事由**：T0393 原 verdict=confirmed、处置=projected，修复为 `dm_server_handshake` 起点 `if (!sbt_server_ctx || !cfg->mtls_enabled)` 拒绝。经用户确认 `mtls_enabled=0` 语义为「不强制（mTLS 可选/明文允许）」而非「禁止 mTLS」。

**重新判定**：
- 握手函数仅在客户端主动发 `CMD_HANDSHAKE` 时被调用；mtls=0 表示服务器不强制，但仍有能力(ctx)时应允许完成 mTLS 握手（可选语义）。
- 原实现 `if (!sbt_server_ctx)`（仅按能力判定）正确，且与 rpc/rdbcomm/libobk 一致（握手层查能力、业务帧层查是否强制）。
- 原 F4「dm_server_handshake 不检查 mtls_enabled 属不一致」为**误判**。

**处置**：
- 代码仓 `git revert b79b3b0`（新提交 `204f048`），恢复 `if (!sbt_server_ctx)`，删除区分性测试；`dmsbtex_session_test` 全 PASS，原 `no-downgrade reject` 行为完好。
- F4 重新定性为**审查误报（false positive）**，无需修复。
- 知识库 `audit-findings.md` F4 节已改写为误报结论。

**纠正后状态**：T0393 任务以「误报/无需修复」收尾（原 archived 不动，仅追加本纠错记录）。
