# T0393 对话日志

## Plan 阶段
- 用户确认将 mTLS 审查发现的 F4（dmsbtex dm_server_handshake 不显式检查 mtls_enabled）单开为独立 bugfix 任务 T0393（parent T0392）。
- 走读确认根因：`sbt_session_server_prepare` 在 cert_dir 有效时无论 mtls_enabled 均构建 sbt_server_ctx，故 mtls=0 但 ctx 存在时握手会被实际执行，与"mTLS 已关闭"声明不一致；强制依赖 main.c:271 兜底，与其余三模块握手层强制不一致。
- 修复：dm_server_handshake 起点显式 `!sbt_server_ctx || !cfg->mtls_enabled` 均回 DM_HS_ERR_MTLS_UNAVAILABLE 拒绝（fail-closed），main.c:271 保留为纵深防御。
- 写 prd.md（含 3 条 AC，含区分性回归用例），待 P6 终审确认后进入 Do 实施。

## Do 阶段
- `dmsbtex/network.c` `dm_server_handshake` 起点改为 `if (!sbt_server_ctx || !cfg->mtls_enabled)` 均回 `DM_HS_ERR_MTLS_UNAVAILABLE` 拒绝（fail-closed），并补 ErrorLog 含 enabled/ctx 状态；`main.c:271` 纵深防御不动。
- `dmsbtex/test/session_test.c` 新增区分性用例：mtls=0 + 有效 cert_dir（ctx 已构建）时客户端 mTLS 握手必须被服务端拒绝（exit_code==6）。
- `xmake build dmsbtex_session_test` 通过；运行 `dmsbtex_session_test` 全 PASS，含新用例 `[PASS] T0393 F4 server mtls-disabled rejects handshake`，日志 `enabled=0, ctx=yes, reject` 印证修复。
- 登记证据：build-log / test-log / diff-log / convergence-map；`validate-convergence` 返回 valid:true。

## Check 阶段
- 写 conclusion.md，3 条 AC 全部 ✅（显式 mtls_enabled 强制 / 区分性回归用例 / 既有用例无回归）。
- 待用户 verdict 确认后进入 Act 归档。
