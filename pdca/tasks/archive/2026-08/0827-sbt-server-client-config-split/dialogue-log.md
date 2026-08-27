# Plan 阶段对话摘要（T3986-0827-sbt-server-client-config-split）

## 任务
拆分 SBT 系（libobk / dmsbtex）服务端/客户端共用的 mTLS rdb 配置，使 libobk_server / libobk_client / dmsbtex_server / dmsbtex_client 四个角色拥有独立配置。

## Triage
- 分类：enhancement / development（含代码与测试）。
- 查重：0818-tool-mtls-config（RPC 系工具级独立配置，已完成）、0819-dmsbtex-libobk-mtls（mTLS 握手接入，已完成）、0819-sbt-mtls-simplify（证书/算法路径简化，Pending 范围更宽）。本任务聚焦 SBT 系 server/client 的 mtls 开关与算法参数拆分，未被覆盖。
- claim 验证：读代码确认 `PARAM_SBT_MTLS_ENABLED`（mtls 开关）与 `PARAM_CERT_DIR`（cert_dir）在 server/client 间共用；算法已部分分裂为 `PARAM_SBT_TLS_ALGORITHM`（srv）/ `PARAM_LIBOBK_CLI_TLS_ALGORITHM`（cli）。

## Grill（4 轮）
- R1：用户纠正"libobk 与 dmsbtex 相互独立，各自都有 server/client"；选择完全迁移删除旧名；dmsbtex 也建 client 入口；算法统一重命名。
- R2：命名选"模块+角色四 section"；澄清 cert_dir 是全局配置（非工具独有）。
- R3：拆分范围确认为仅"工具独有"参数（mtls_enable / tls_algorithm），cert_dir 作为全局配置保留。
- R4（风险核实）：发现 `[security]tls_enable` / `[security]tls_algorithm` 是全局 ini key，被 RPC 系（aio-speedd/rdbcommd 等）复用为兜底层，不能直接删除；用户确认仅删 SBT 专属旧名（env 名 + 参数 ID），保留全局 `[security]` ini key 供 RPC 系。
- 方向确认：用户"理解正确，继续"。

## P3.5 测试接缝
用户"自我审查"确认 4 个 seam：libs/tests/param_registry_test.c、libs/tests/rdb_config_test.c、dmsbtex/test/session_test.c、libobk/test/session_test.c。

## P5 知识注入
4 项（implement.jsonl）：mtls 参数链路审查、安全布尔 fail-closed、dmsbtex/sbt.c 配置覆盖陷阱、rdb.conf 审计契约。

## P6 终审
用户"批准，进入 Do"。final_confirmation 已记录（response=confirmed）。

## 设计要点（锁定）
- 四 section：[libobk_server]、[libobk_client]、[dmsbtex_server]、[dmsbtex_client]，各含 mtls_enable、tls_algorithm。
- 仅拆工具独有参数；cert_dir 全局保留；仅删 SBT 专属 env 名与参数 ID（PARAM_SBT_MTLS_ENABLED / PARAM_SBT_TLS_ALGORITHM / PARAM_LIBOBK_CLI_TLS_ALGORITHM），全局 [security]tls_enable/[security]tls_algorithm 保留。
- 新增 8 个参数 ID；4 个 TLS 配置初始化入口改读各自角色；CLI 覆盖映射到 server 角色；fail-closed/算法白名单范式保持。
- 验收标准 AC-1..AC-8。
