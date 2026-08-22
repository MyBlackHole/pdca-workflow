# Triage Brief — rpc-mixed-mtls

- **category**: enhancement
- **scenario_type**: development
- **summary**: rpc 需支持混合模式：服务端未配置 `mtls` 时，客户端对同一服务端可同时以明文或密文建连（按服务端首阶段协商结果自适应，不强制）；服务端配置 `mtls` 后，客户端必须密文，否则建连失败，不回退明文。
- **current behavior**: `rpc/main.cpp:412` 与 `rdbcomm/rdbcommd-main.c:348` 按 `mtls_enabled` 决定是否创建 `tls_cert` 上下文；`rpc/rpc-io.cpp:133` 的 `rpc_handshake_client_negotiate` 已按 `HS_OK_MTLS/HS_OK_PLAIN/HS_ERR_MTLS_REQUIRED` 分支，但服务端未配置时是否明确回 `PLAIN` 且客户端无 `cert_dir` 时的回退路径未在单测中显式覆盖，`mtls` 与 `plain` 的矩阵缺失导致混合模式是否可同时共存未被回归。
- **desired behavior**: 首阶段协商后：`server mtls=0` → 客户端无论自身 `mtls` 开关，`HS_OK_PLAIN` 走明文，`HS_OK_MTLS` 仅当客户端 `cert_dir+algorithm+ca_cn` 完备时走密文，否则回退明文（不报错）；`server mtls=1` → 客户端 `HS_OK_MTLS` 必须完成 `tls_cert` 握手，缺证书或协商失败即建连失败，不回退。
- **key interfaces**: `rpc_hs_server_accept` / `rpc_hs_client_negotiate` / `rpc_handshake_client_negotiate` / `tls_cert_init_*` / `g_rpc_config.mtls_enabled` / `cert_dir`
- **acceptance criteria**: 混合矩阵可测：`server 0 x client 0` 明文通，`server 0 x client 1` 明文通（或按需密文通），`server 1 x client 0` 建连失败，`server 1 x client 1` 密文通；无配置漂移。
- **out of scope**: 不改证书文件名与双格式回退（T0342 已交付），不改 `sec_*` 签名，不引入自动重连策略。
- **information gaps**: 服务端 `mtls=0` 时是否仍需下发 `ca_cn` 供客户端按需密文（当前为 `PLAIN` 不带 `ca_cn`，客户端无法走 `cert_dir/ca_cn`）；需在 PRD 明确 `PLAIN` 时 `ca_cn` 为空且客户端不尝试 `tls_cert`。
- **dedup results**: 与 T0342 `tls_cert` 初始化、`0820-tls-session-integration-test` 的 `ca_cn` 透传无重叠，本任务聚焦 `rpc` 首阶段协商的混合/强制分支与矩阵单测。
- **recommended next steps**: 补 PRD 矩阵与 seam，明确 `PLAIN` 时 `ca_cn` 空值语义，增量 `rpc_handshake_test` 覆盖 4 象限，静态校验 `HS_OK_MTLS` 仅在 `mtls=1` 时产生。
