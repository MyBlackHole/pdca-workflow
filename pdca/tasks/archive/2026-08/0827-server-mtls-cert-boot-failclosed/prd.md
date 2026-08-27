# 服务端 mTLS 启用且证书缺失时启动报错（fail-closed）

## 问题陈述

- **现状**: 四个 C 服务端（rdbcommd、aio-speedd、dm-ftp、sbt）在 mTLS 开关（`mtls_enabled`）启用时，依赖启动期 `tls_cert_init_server` 构建 mTLS 上下文。但存在 fail-open 缺陷：
  - rdbcommd：当 `mtls_enabled` 为真且证书目录为空时，启动期**跳过** `tls_cert_init_server`，仅 `WarningLog("no cert_dir, serving plain only")` 即以明文监听，未启动失败。
  - aio-speedd：证书加载失败时把 TLS 上下文置空（`server_tls_ctx = NULL`）并继续以明文监听，注释明确"证书加载失败不阻止启动"。
  - dm-ftp、sbt：启动期 `sbt_session_server_prepare` 在 mTLS 启用且证书缺失时已返回非 0，主流程检查后退出，行为正确。
- **目标**: 任一服务端在 mTLS 启用、但缺少可用证书（证书目录缺失，或服务端证书/客户端 CA 加载失败）时，**启动期以非 0 退出（fail-closed）**，不得降级为明文监听。
- **差距**: rdbcommd、aio-speedd 两处主流程未对"mTLS 启用 + 证书不可用"执行启动期 fail-closed；缺少统一、可测的启动期 TLS 准备与失败判据。

## 解决方案

统一四服务端启动期 TLS 准备语义为"mTLS 启用即 fail-closed"：

1. 共享能力 `tls_cert_init_server` 已是 fail-closed（mtls_enabled 时 cert_dir 空或加载失败返回非 0），保持其语义不变并补单测钉死。
2. rdbcommd、aio-speedd：将启动期 TLS 准备逻辑收敛为可测的 boot prepare（与 dm-ftp/sbt 的 `sbt_session_server_prepare` 模式一致），当 `mtls_enabled` 为真且 `tls_cert_init_server` 返回非 0 时，主流程非 0 退出。
3. dm-ftp、sbt：既有 prepare 已正确，补充单测断言"mtls_enabled + 证书缺失 → 返回非 0"，固化不回归。

明确边界：仅当 `mtls_enabled` 为真时强制 fail-closed；mTLS 未启用（明文模式）时证书缺失仍允许明文启动，保持既有按需/明文语义不回归。

## Seam 分析

### 测试接缝

- 边界层：各服务端启动期 TLS 准备入口（rdbcommd、aio-speedd 主流程；dm-ftp、sbt 的 server prepare 函数）与共享 `tls_cert_init_server` 的 fail-closed 返回。
- 已有覆盖：`libs/tests/tls_cert_test.c`（`tls_cert_init_server` 部分降级测试）、`dmsbtex/test/session_test.c`、`libobk/test/session_test.c`（均含 `sbt_session_server_prepare` 测试）、`rdbcomm/tests/handshake_session_test.c`、`rpc/tests/mixed_mtls_integration.cpp`。
- 新增覆盖：rdbcommd、aio-speedd 抽取 boot prepare 后新增单测，专门覆盖"mtls_enabled + 证书缺失/目录缺失 → 返回非 0"。
- 隔离策略：单测用临时空目录/缺失路径构造 `cert_dir`，无需真实证书与网络。

### 声明的测试接缝

- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c
- seam: rdbcomm/tests/server_boot_tls_test.c -> rdbcomm/rdbcommd-main.c
- seam: rpc/tests/server_boot_tls_test.cpp -> rpc/main.cpp

### 验收可测性

- 每个 AC 可构造输入（缺失/空的 cert_dir、mtls_enabled=1）并断言进程退出码/函数返回值与日志关键字。
- 启动期 fail-closed 通过抽取 boot prepare 返回非 0 断言，避免依赖真实进程退出测试。
- libs 层 `tls_cert_init_server` 返回值断言，作为四服务端共同依赖的底层保证。

## 用户故事

1. 作为安全审计，我希望 mTLS 开关开启时若证书不可用则服务**拒绝启动**，以便消除"配置启用但链路实际明文"的安全假象。
2. 作为运维，我希望 rdbcommd/aio-speedd 与 dm-ftp/sbt 在证书缺失时行为一致（统一 fail-closed），以便排查与值守。
3. 作为维护者，我希望启动期 TLS 准备逻辑可单测，以便回归不退化。

## 实现决策

- **共享层 `libs/tls_cert.c`**：`tls_cert_init_server` 在 `mtls_enabled` 为真时，cert_dir 空（`TLS_CERT_ERR_INVALID_PARAM`）或证书/CA 加载失败（`TLS_CERT_ERR_LOAD_CA` 等）均返回非 0，语义保持不变；在 `libs/tests/tls_cert_test.c` 增加用例钉死"mtls_enabled=1 + 空/不存在 cert_dir → 返回非 0"。
- **rdbcommd（`rdbcomm/rdbcommd-main.c`）**：将启动期 TLS 准备收敛为 `rdbcommd_tls_boot_prepare(server_opts) -> int`：
  - `mtls_enabled` 为真时**无条件**调用 `tls_cert_init_server`；cert_dir 空或加载失败返回非 0，主流程据此 `return -ret`（启动失败并日志"mTLS enabled but no usable cert"）。
  - `mtls_enabled` 为假时保留既有按需语义（cert_dir 非空则尝试加载，失败仅明文，不强制）。
  - 新增 `rdbcomm/tests/server_boot_tls_test.c` 覆盖上述两分支。
- **aio-speedd（`rpc/main.cpp`）**：将启动期 TLS 准备收敛为 `aio_speedd_tls_boot_prepare(g_rpc_config) -> tls_cert_ctx_t*`（失败返回 NULL 且设错误）：
  - `g_rpc_config->mtls_enabled` 为真且 `tls_cert_init_server` 失败 → `exit(EXIT_FAILURE)`（或返回错误由主流程退出），日志"mTLS enabled but cert load failed"。
  - `mtls_enabled` 为假时失败可忽略（明文），保持既有注释语义。
  - 新增 `rpc/tests/server_boot_tls_test.cpp` 覆盖两分支（用桩 g_rpc_config）。
- **dm-ftp（`dmsbtex/network.c`）**：`sbt_session_server_prepare` 已正确（mtls_enabled 且 cert_dir 空/加载失败返回非 0）；在 `dmsbtex/test/session_test.c` 增加断言"mtls_enabled=1 + 证书缺失 → 返回非 0"。
- **sbt（`libobk/lib/logic/oracleCmdTbl.c`）**：`sbt_session_server_prepare` 已正确；在 `libobk/test/session_test.c` 增加断言"mtls_enabled=1 + 证书缺失 → 返回非 0"。
- **不改动**：客户端握手流程、`tls_cert_init_server` 的白名单/算法语义、国密后端；仅启动期 fail-closed 判据。

## 测试决策

- 以行为测试为主：构造 `cert_dir` 为不存在路径/空目录，`mtls_enabled=1`，断言 boot prepare 返回非 0（或进程非 0 退出）。
- 既有的 `mixed_mtls_integration`、`handshake_session_test` 需保持通过（验证 mTLS 正常握手路径不回归）。
- rdbcommd/aio-speedd 通过抽取 boot prepare 函数实现单测，避免直接测 main。

## 验收标准

- [ ] AC-1: rdbcommd 在 `mtls_enabled=1` 且 cert_dir 缺失/证书加载失败时，启动期返回非 0 退出，日志含证书不可用错误，不以明文监听。
- [ ] AC-2: aio-speedd 在 `mtls_enabled=1` 且证书加载失败时，启动期返回非 0 退出，日志含证书不可用错误，不以明文监听。
- [ ] AC-3: dm-ftp 在 `mtls_enabled=1` 且证书缺失时，启动期 `sbt_session_server_prepare` 返回非 0，主流程退出（既有语义保持）。
- [ ] AC-4: sbt 在 `mtls_enabled=1` 且证书缺失时，启动期 `sbt_session_server_prepare` 返回非 0，主流程退出（既有语义保持）。
- [ ] AC-5: 四服务端在 `mtls_enabled=0`（明文模式）且证书缺失时，仍允许明文启动，不回归既有按需/明文行为。
- [ ] AC-6: 单测覆盖 libs/dm-ftp/sbt/rdbcommd/aio-speedd 启动期 fail-closed 分支，全部通过。
- [ ] AC-7: `xmake build` 成功；既有 mTLS 集成测试（mixed_mtls_integration、handshake_session_test、session_test）通过，无回归。

## 范围外

- oss Go 工具的 mTLS（属 0823 范围外 follow-up，不在本次四服务端内）。
- 运行时 reload 证书校验、证书自动轮换。
- 客户端证书校验算法/国密 SM2 后端实现（沿用既有）。

## 备注

- 关联任务：0823-oss-https-cert（mTLS 为其范围外）、0818-tool-mtls-config、0827-f139-parse-config-unify（其备注要求安全开关 fail-closed 语义不变；本任务即收口"mTLS 启用 + 证书缺失"的启动期 fail-closed）。
- 注入知识资产：`knowledge/tls/structured-mtls-failure-diagnostics.md`（失败日志应表达角色/阶段/算法/凭据路径）、`security-bool-failclosed.md`（安全开关 fail-closed，不得 fail-open）。Do 阶段改造须保持 `mtls_enabled` 解析的 fail-closed 语义，仅在"证书缺失"时启动报错，不在开关解析层引入 fail-open。
