# dmsbtex：init_sbt_config 从 sbt-config.conf 读取 mTLS 状态与算法 — 规格文档

## 问题陈述

- **现状**: dmsbtex 客户端（`sbt.c`）的 `init_sbt_config(const char *cfg, dmsbtex_t *sbt)` 解析 `sbt-config.conf`（`--log-path/--host/--port/--checksum-enabled/--compress-enabled/--backup-dirs`），其 mTLS 状态与算法目前由末尾调用的 `sbt_tls_config_init()` 从 **env/ini**（`sec_resolve_bool`/`sec_resolve_str`）读取，配置文件内容对 mTLS 无影响。
- **目标**: dmsbtex 应支持通过 `init_sbt_config` 传入的 `sbt-config.conf` 直接获取 mTLS 启用状态与算法，使配置集中化、可随配置文件下发。
- **差距**: `init_sbt_config` 不解析 mTLS 相关键；`sbt->tls_cfg.mtls_enabled`/`algorithm` 的来源与配置文件解耦。

## 解决方案

在 `init_sbt_config` 内新增对 `sbt-config.conf` 中 `--mtls-enabled` 与 `--tls-algorithm` 两个键的解析；先以 `sbt_tls_config_init` 从 env/ini 完成 `tls_cfg` 基线初始化，随后**仅覆盖配置文件中存在的键**，键缺失则跳过（保留 env/ini 基线）。

## Seam 分析

### 测试接缝
- 边界层：`init_sbt_config`（dmsbtex/sbt.c）作为配置解析入口，纯函数式可测（给定临时配置文件路径与 `dmsbtex_t`）。
- 已有覆盖：`dmsbtex/test/session_test.c` 已测 `sbt_tls_config_init` 与握手；需新增针对 `init_sbt_config` 文件解析的用例。
- 隔离策略：用例在临时目录生成含不同 mTLS 键组合的 `sbt-config.conf`，调用 `init_sbt_config` 后断言 `sbt->tls_cfg` 字段；不依赖真实网络/证书。

### 声明的测试接缝
- seam: dmsbtex/test/session_test.c -> dmsbtex/sbt.c

### 验收可测性
- 每个 AC 均有明确 pass/fail（字段值或返回码）。
- 非法值、键缺失等边界可独立构造临时配置文件。
- 分层：单元级验证配置解析，构建级验证无回归。

## 用户故事

1. 作为运维，我想要在 `sbt-config.conf` 中直接配置 mTLS 开关与算法，以便配置随文件统一下发、无需依赖环境变量。
2. 作为开发者，我想要配置文件对 mTLS 状态/算法具有唯一权威，以便消除 env/ini 与文件双源不一致的歧义。

## 实现决策

- **修改模块**: 仅 `dmsbtex/sbt.c` 的 `init_sbt_config`（客户端路径）；`libobk`/`rdbcomm` 等其他模块不动。
- **接口**: 复用现有 `dmsbtex_tls_config_t`（`mtls_enabled:int` / `algorithm_name[128]` / `algorithm:uint16_t`）；`init_sbt_config` 签名不变。
- **解析规则**:
  - `--mtls-enabled`：值为 `0`/`1`；键**缺失则跳过**，保留 `sbt_tls_config_init` 从 env/ini 得到的基线值。
  - `--tls-algorithm`：值为 `TLS_SM4_GCM_SM3` 或 `TLS_AES_256_GCM_SHA384`（对应 `RPC_TLS_ALGORITHM_SM4_GCM_SM3` / `RPC_TLS_ALGORITHM_AES_256_GCM_SHA384`）；键**缺失则跳过**，保留基线（env/ini 默认 `RPC_TLS_ALGORITHM_DEFAULT`，即 `TLS_SM4_GCM_SM3`）。
- **填充顺序**: 先以 `sbt_tls_config_init(&sbt->tls_cfg)` 初始化全集（含 `cert_dir`，来自 env/ini，本次不变）作为基线；随后**仅当配置文件中存在对应键**（`file_mtls_present`/`file_alg_present` 标志）时，用解析并校验后的值覆盖 `mtls_enabled`/`algorithm_name`/`algorithm`。键缺失不写入，沿用基线。
- **技术澄清（fail-closed）**: 值非法时（mtls-enabled 非 0/1；tls-algorithm 非已知规范名）`init_sbt_config` 返回 `-1`，与 T0361 `sec_resolve_bool` 的 fail-closed 范式一致，不静默降级。
- **算法字段**: `algorithm_name` 直接用解析到的规范名；`algorithm` 经 `dm_hs_algorithm_from_name(algorithm_name)` 映射（与 `sbt_tls_config_init` 一致），保证握手协商使用统一枚举。
- **迁移说明**: 配置文件在**键存在时**覆盖 env/ini；原仅经 env/ini 启用 mTLS 且未加文件键的部署行为保持不变（回退 env/ini）。新增文件键即按文件生效，无需删除环境变量。

## 测试决策

- 仅测外部行为（解析后 `tls_cfg` 字段值与返回码），不测解析实现细节。
- 被测模块：`dmsbtex/sbt.c` 的 `init_sbt_config`。
- 先例：`dmsbtex/test/session_test.c` 中 `sbt_tls_config_init` 的 fail-closed 与算法名校验用例。

## 验收标准

- [ ] AC-1: 给定含 `--mtls-enabled=1` 与 `--tls-algorithm=TLS_AES_256_GCM_SHA384` 的配置文件，`init_sbt_config` 返回 0 且 `sbt->tls_cfg.mtls_enabled==1`、`algorithm_name=="TLS_AES_256_GCM_SHA384"`、`algorithm==dm_hs_algorithm_from_name("TLS_AES_256_GCM_SHA384")`。
- [ ] AC-2: 给定含 `--mtls-enabled=0` 与 `--tls-algorithm=TLS_SM4_GCM_SM3` 的配置文件，`init_sbt_config` 返回 0 且 `mtls_enabled==0`、`algorithm_name=="TLS_SM4_GCM_SM3"`；两键均缺失时回退 env/ini 基线（测试环境 env 未设 → `mtls_enabled==0` 且 `algorithm_name=="TLS_SM4_GCM_SM3"`）。
- [ ] AC-3: 给定 `--mtls-enabled=2`（或任意非 0/1）的配置文件，`init_sbt_config` 返回 -1；给定 `--tls-algorithm=BOGUS` 的配置文件，`init_sbt_config` 返回 -1（fail-closed，tls_cfg 不生效）。
- [ ] AC-4: `xmake -P . dmsbtex_session_test` 全量用例通过（含既有 `sbt_tls_config_init`/握手回归），且 `dmsbtex`/`dm-ftp` 目标构建成功。

## 范围外

- 不改造 `libobk`/`rdbcomm`/`rpc` 等模块的配置来源（仍走各自既有 env/ini）。
- 不改变 `cert_dir` 的解析来源（维持 env/ini）。
- 不实现配置热加载/监听；仅在 `init_sbt_config` 启动时读取一次。
- OCSP/CRL 等吊销检查不在本次范围。

## 备注

- 关联任务：T0328（0819-dmsbtex-libobk-mtls，mTLS 握手接入，已完成）与本任务边界为“配置来源”而非“握手能力”。
- 关联任务：T0366（TLS 证书 P2 增强）提供 `tls_cert` 层 reload/CRL 等能力，本任务仅消费其既有 `dmsbtex_tls_config_t` 接口。
