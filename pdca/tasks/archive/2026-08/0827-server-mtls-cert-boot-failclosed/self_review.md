# 自我审查结论 — T3987 服务端 mTLS 启用证书缺失启动报错

> 审查依据：code-review-checklist（安全性 / 错误处理 / 正确性维度），聚焦 fail-open 路径。

## 审查对象与结论

### aio-speedd（rpc/main.cpp:443-455）— 严重度 CRITICAL
- 现状：`server_opts.mtls_enabled = 1` 硬编码；`tls_cert_init_server` 失败则 `server_tls_ctx = NULL` 继续明文监听，注释"证书加载失败不阻止启动"。
- 风险：默认 `cert_dir=/opt/aio/cfg/certs` 存在但证书缺失 → 加载失败 → **mTLS 启用却以明文监听**（fail-open）。
- 修复判定：当 `g_rpc_config->mtls_enabled` 为真且 ret != 0 → `exit(EXIT_FAILURE)`。采用最小改动，保留 `server_opts.mtls_enabled=1` 硬编码，仅失败分支按真实开关 fail-closed，避免握手路径回归。mtls 未启用时失败仍忽略（明文允许）。

### rdbcommd（rdbcommd-main.c:397-421）— 严重度 HIGH
- 现状：`if (server_opts.cert_dir[0]) ret = tls_cert_init_server(...)`；cert_dir 显式空时跳过 init，mtls 启用仅 `WarningLog("no cert_dir, serving plain only")` 明文启动。
- 风险：mtls 启用 + cert_dir 显空 → fail-open。
- 修复判定：`tls_cert_init_server` 在 `mtls_enabled=1` 且 cert_dir 空时返回 `TLS_CERT_ERR_INVALID_PARAM`（libs/tls_cert.c:657）。故 mtls 启用时移除"cert_dir 空跳过"即可进入既有 `if (ret != 0 && mtls_enabled) return -ret` 启动失败路径；mtls 未启用保留按需加载语义。

### dm-ftp（dmsbtex/network.c:371-382）— 通过
- `sbt_session_server_prepare`：mtls 启用 + cert_dir 空/加载失败均返回非 0；`dmsbtex/main.c:152` 检查退出。逻辑正确。

### sbt（libobk/oracleCmdTbl.c:194-204）— 通过
- `sbt_session_server_prepare`：mtls 未启用返回 0；启用 + cert_dir 空返回 `TLS_CERT_ERR_INVALID_PARAM`；启用 + 加载失败返回非 0；`libobk/main.c:73` 检查退出。逻辑正确。

## 跨文件一致性
- 四服务端共享 `tls_cert_init_server` 的 fail-closed 语义（mtls_enabled 时 cert_dir 空/加载失败返回非 0），底层保证一致。
- dm-ftp/sbt 已收敛到 `sbt_session_server_prepare` 模式；rdbcommd/aio-speedd 启动期主流程需对齐该模式（抽取可测 boot prepare）。

## 测试与可测性
- 必须：rdbcommd/aio-speedd 抽取 boot prepare 函数以支持单测（覆盖 mtls 启用 + 证书缺失返回非 0）。
- 扩展：libs/tls_cert_test.c、dmsbtex/test/session_test.c、libobk/test/session_test.c 补断言 mtls 启用 + 证书缺失 → 返回非 0。

## 结论
方案与 PRD 一致，修复点明确、风险可控（最小改动原则）。未发现需修订 PRD 的遗漏；aio-speedd 采用最小改动以避免握手行为回归，已记入实现决策。可进入 Do。
