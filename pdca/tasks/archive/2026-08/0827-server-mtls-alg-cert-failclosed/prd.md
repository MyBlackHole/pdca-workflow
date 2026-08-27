# 服务端 mTLS 启用且指定算法时算法对应证书异常应启动失败（fail-closed）

## 问题陈述

- **现状**：四服务端（rdbcommd、aio-speedd、dm-ftp、sbt）在 mTLS 开关启用时通过 `tls_cert_init_server` 构建 mTLS 上下文。该函数恒按 `cert_dir` 自动构建 **SM4+AES 双算法链**，且对单算法证书加载失败采取"尽力收集、降级跳过"（T0390），仅当**全部算法**都失败时才整体失败。同时 `tls_cert_server_options_t` 不接收算法参数，四服务端虽各自支持 `tls_algorithm` 配置（值 `TLS_SM4_GCM_SM3`/`TLS_AES_256_GCM_SHA384`），但均未传入启动期证书加载。
- **目标**：当服务端 **mTLS 启用且显式指定算法**时，若该**指定算法对应的证书异常**（文件缺失、证书/密钥损坏或算法不支持），启动期应**以非 0 退出（fail-closed）**，不得被另一算法的证书兜底成功（即不得 fallback 到未指定的算法）。
- **差距**：当前"指定 SM4 但 SM4 证书缺失、AES 证书正常"时，`tls_cert_init_server` 仍以 AES slot 成功整体返回 OK，启动不失败；且服务端算法配置未参与启动期证书加载判据。T3987 仅收口"目录/证书整体缺失"，未覆盖"指定算法但仅该算法证书异常"。

## 解决方案

统一在 `tls_cert_init_server` 引入"指定算法 → 仅加载该算法、失败即整体失败"分支，并让四服务端把算法配置传入启动期 TLS 准备：

1. **`libs/tls_cert.h`**：`tls_cert_server_options_t` 增加 `const char *algorithm;`（注释：NULL/空串=未指定，走双算法链兼容；非空=指定算法，仅加载该算法）。
2. **`libs/tls_cert.c` `tls_cert_init_server`**：
   - 若 `opts->algorithm` 非空：
     - 校验为合法算法名（`RPC_TLS_ALGORITHM_SM4_GCM_SM3` / `RPC_TLS_ALGORITHM_AES_256_GCM_SHA384`），否则返回 `TLS_CERT_ERR_INVALID_PARAM`（fail-closed，非法算法名不静默）。
     - **仅加载**算法名匹配的那个 profile（从 `auto_profiles` 过滤），移除 T0390"降级跳过"——该 profile `tls_cert_slot_create` 失败即 `return ret`（整体失败）。
     - 算法名匹配但 profile 实际不存在（防御）→ `TLS_CERT_ERR_INVALID_PARAM`。
   - 若 `opts->algorithm` 为空/未指定：保持现有双算法链 + 尽力收集语义（向后兼容，不回归）。
3. **四服务端 wiring**（将各自算法配置传入启动期 TLS 准备）：
   - rdbcommd `rdbcommd_tls_boot_prepare`：`opts.algorithm = opts->algorithm_name;`（algorithm_name 可能空=未指定）。
   - aio-speedd `aio_speedd_tls_boot_prepare`：`opts.algorithm = g_rpc_config->tls_algorithm;`。
   - dm-ftp `sbt_session_server_prepare`：`opts.algorithm = cfg->algorithm_name;`。
   - sbt `sbt_session_server_prepare`：`opts.algorithm = cfg->algorithm_name;`。
4. 明确边界：仅当 `mtls_enabled=1` **且指定算法**时对该算法证书异常 fail-closed；未指定算法时保持双算法链兼容；`mtls_enabled=0` 明文模式仍允许明文（与 T3987 一致）。

## Seam 分析

### 测试接缝

- 边界层：四服务端启动期 TLS 准备入口（rdbcommd/aio-speedd boot prepare、dm-ftp/sbt `sbt_session_server_prepare`）与共享 `tls_cert_init_server` 的"指定算法 → 仅加载该算法、失败即整体失败"分支。
- 已有覆盖：`libs/tests/tls_cert_test.c`、`dmsbtex/test/session_test.c`、`libobk/test/session_test.c`、`rdbcomm/tests/server_boot_tls_test.c`、`rpc/tests/server_boot_tls_test.cpp`（均已在 T3987 建立）。
- 新增/扩展覆盖：libs 层直接断言"指定算法 + 该算法证书缺失（另一算法存在）→ 返回非 0"；四服务端 boot/prepare 测试扩展"指定算法 + 该算法证书异常 → 返回非 0 / 启动失败"。
- 隔离策略：测试用临时证书目录构造"仅含 AES 证书、缺 SM4 证书"（或反之）场景，无需真实双算法完整证书与网络；算法名非法则用字面量 `"BOGUS"`。

### 声明的测试接缝

- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c
- seam: rdbcomm/tests/server_boot_tls_test.c -> rdbcomm/rdbcommd-main.c
- seam: rpc/tests/server_boot_tls_test.cpp -> rpc/main.cpp
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c

### 验收可测性

- 每个 AC 可构造输入（指定 algorithm + 仅该算法证书缺失的 cert_dir / 非法算法名 / 未指定算法）并断言函数返回值或进程退出码与日志关键字。
- "指定算法但被兜底"通过"cert_dir 仅含另一算法证书"构造，断言指定算法失败时整体失败（不 fallback）。
- libs 层 `tls_cert_init_server` 返回值断言，作为四服务端共同依赖的底层保证。

## 用户故事

1. 作为安全审计，我希望 mTLS 开关开启且显式指定算法时，若该算法证书不可用则服务**拒绝启动**，以便消除"配置指定 SM4 但实际 AES 兜底明文/弱链"的安全假象。
2. 作为运维，我希望 rdbcommd/aio-speedd/dm-ftp/sbt 在"指定算法 + 该算法证书异常"时行为一致（统一 fail-closed），以便排查与值守。

## 实现决策

- **共享层 `libs/tls_cert.c`**：`tls_cert_init_server` 增加 algorithm 分支（见解决方案第 2 点）；语义保持 fail-closed；在 `libs/tests/tls_cert_test.c` 增加用例钉死"指定算法 + 该算法证书缺失（另一算法存在）→ 返回非 0"、"指定非法算法名 → 返回非 0"、"未指定算法 + 双算法目录 → 返回 0"。
- **rdbcommd（`rdbcomm/rdbcommd-main.c` + `rdbcomm/server_boot.c`）**：`rdbcommd_tls_boot_prepare` 增加 algorithm 参数（或读 `opts->algorithm_name`），设 `opts.algorithm`；boot 测试扩展"mtls=1 + 指定算法 + 该算法证书缺失（另一算法存在）→ 返回非 0"。
- **aio-speedd（`rpc/main.cpp` + `rpc/server_boot.cpp`）**：`aio_speedd_tls_boot_prepare` 增加 algorithm 参数，设 `opts.algorithm`；测试同样扩展。
- **dm-ftp（`dmsbtex/network.c`）**：`sbt_session_server_prepare` 设 `opts.algorithm = cfg->algorithm_name`；`dmsbtex/test/session_test.c` 扩展"mtls=1 + 指定算法 + 该算法证书缺失 → 返回非 0"。
- **sbt（`libobk/lib/logic/oracleCmdTbl.c`）**：同 dm-ftp 设 `opts.algorithm`；`libobk/test/session_test.c` 扩展。
- **不改动**：客户端握手流程、`tls_cert_init_server` 未指定算法时的双算法链兼容语义、国密后端、算法白名单解析（T3961）。

## 测试决策

- 以行为测试为主：构造 `cert_dir` 仅含某一算法证书（如仅 `ed25519_*`，缺 `sm2_*`），`mtls_enabled=1` + `algorithm=TLS_SM4_GCM_SM3`，断言 boot/prepare 返回非 0（或进程非 0 退出）。
- 非法算法名（`"BOGUS"`）断言返回非 0（fail-closed）。
- 未指定算法（algorithm 空）且证书存在 → 返回 0（双算法链兼容，不回归）；指定算法且证书正常 → 返回 0。
- 既有 `mixed_mtls_integration`、`handshake_session_test`、`session_test` 需保持通过（验证正常握手路径不回归）。

## 验收标准

- [ ] AC-1: rdbcommd 在 `mtls_enabled=1` 且指定算法 X 时，若**仅 X 的证书异常**（另一算法证书正常）启动期返回非 0 退出，不 fallback 另一算法；日志含算法与证书不可用错误。
- [ ] AC-2: aio-speedd 在 `mtls_enabled=1` 且指定算法 X 时，若仅 X 证书异常启动期返回非 0 退出，不 fallback。
- [ ] AC-3: dm-ftp 在 `mtls_enabled=1` 且指定算法 X 时，仅 X 证书异常则 `sbt_session_server_prepare` 返回非 0，主流程退出（既有语义保持）。
- [ ] AC-4: sbt 在 `mtls_enabled=1` 且指定算法 X 时，仅 X 证书异常则 `sbt_session_server_prepare` 返回非 0，主流程退出。
- [ ] AC-5: 指定算法名非法（`"BOGUS"`）时启动期返回非 0（fail-closed，安全开关解析不变 fail-open）。
- [ ] AC-6: 未指定算法（空）且证书存在时启动成功（双算法链兼容，不回归）；指定算法且证书正常时启动成功。
- [ ] AC-7: 单测覆盖 libs/dm-ftp/sbt/rdbcommd/aio-speedd 的"指定算法 + 该算法证书异常 → 启动失败"分支，全部通过；`xmake build` 成功；既有 mTLS 集成测试无回归。

## 范围外

- oss Go 工具的 mTLS（属 0823 范围外 follow-up）。
- 运行时 reload 证书校验、证书自动轮换（但 `tls_cert_ctx_reload` 的指定算法语义可后续跟进）。
- 客户端证书校验算法/国密 SM2 后端实现（沿用既有）。

## 备注

- 关联任务：T3987（mTLS 启用+证书缺失启动失败，已归档，本任务为其精细化扩展）、T3961（tls_algorithm 无默认值+算法锁 fail-closed）、T0390（双算法链尽力收集，本任务在"指定算法"时绕过其兜底）。
- 注入知识资产：`knowledge/tls/server-boot-tls-failclosed.md`（T3987 沉淀的启动期 boot prepare 模式）、`knowledge/tls/structured-mtls-failure-diagnostics.md`（失败日志应表达角色/阶段/算法/凭据路径）、`knowledge/rdb-config/security-bool-failclosed.md`（安全开关 fail-closed）。Do 阶段改造须保持 `mtls_enabled` 与算法解析的 fail-closed 语义，仅在"指定算法 + 该算法证书异常"时启动报错，不改开关解析层。
