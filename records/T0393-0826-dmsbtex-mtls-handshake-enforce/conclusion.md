---
schema: pdca.asset/v1
id: T0393-0826-dmsbtex-mtls-handshake-enforce
phase: check
source_ids: [build-log, test-log, diff-log, convergence-map]
---

## 上下文
mTLS 全面审查（T0392）发现 F4：dmsbtex `dm_server_handshake`（`dmsbtex/network.c:204`）不显式检查 `cfg->mtls_enabled`，mTLS 强制依赖 `sbt_server_ctx` 是否构建（间接）与 `main.c:271` 业务帧闸门兜底，与其余三模块（rpc/rdbcomm/libobk）在握手层直接依据 `mtls_enabled` 强制不一致。本任务显式化该强制逻辑。

## 假设与结果
- 假设：在 `dm_server_handshake` 起点显式 `!sbt_server_ctx || !cfg->mtls_enabled` 均拒绝，可使 dmsbtex 与 rpc/rdbcomm/libobk 握手层强制一致，且不破坏既有行为。
- 结果：修复实现并验证，新增区分性回归用例通过，既有 dmsbtex session_test 全过（无回归）。

## 分析
- **AC-1 ✅** `dm_server_handshake` 显式检查 `cfg->mtls_enabled`（mtls=0 或 ctx 缺失均回 `DM_HS_ERR_MTLS_UNAVAILABLE` 拒绝）；runtime 日志印证 `handshake: mTLS unavailable (enabled=0, ctx=yes), reject`。
- **AC-2 ✅** 新增 `dmsbtex/test/session_test.c` 用例 `T0393 F4 server mtls-disabled rejects handshake` 通过；该用例具区分性——无修复时 ctx 存在且未查 `mtls_enabled`，握手会成功致用例失败。
- **AC-3 ✅** 既有用例全过：plain zero-handshake passthrough / forced mTLS upgrade / no-downgrade reject / T3961 算法锁 / T0358 畸形算法；`xmake build` 通过，`xmake run dmsbtex_session_test` 退出码 0（ALL PASS）。

## 适用边界
- 仅改动 dmsbtex 服务端握手入口的强制判定；不改变 mtls 启用时的正确握手流程，也不改动 `main.c:271` 纵深防御。
- 功能上仍 fail-closed：mtls 关闭时明文帧由 `main.c:271` 兜底允许，握手请求由 `dm_server_handshake` 显式拒绝。

## 下一轮建议
- 提交代码仓改动（待用户"提交"指令）；PDCA 仓产物待提交。
- F2/F3/F5 仍为独立后续候选（低危/一致性）。
