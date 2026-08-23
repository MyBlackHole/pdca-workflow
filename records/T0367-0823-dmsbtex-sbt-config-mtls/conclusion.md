# T0367 结论文档 — dmsbtex：init_sbt_config 从 sbt-config.conf 读取 mTLS 状态与算法

## 结论摘要

`init_sbt_config`（dmsbtex/sbt.c:662）新增对 `--mtls-enabled` 与 `--tls-algorithm` 两个配置键的解析，使 mTLS 启用状态与算法可随 `sbt-config.conf` 配置文件下发，无需依赖环境变量。

**优先级语义（经用户修正）**：先以 `sbt_tls_config_init(&sbt->tls_cfg)` 完成 `tls_cfg` 全集（含 `cert_dir`，来自 env/ini）的基线初始化；随后**仅当配置文件中存在对应键**时，用解析并校验后的值覆盖 `mtls_enabled`/`algorithm_name`/`algorithm`。键缺失则跳过，沿用 env/ini 基线（不强制置 0 / 默认）。值非法时 fail-closed 返回 `-1`。

## 验收对照

| AC | 期望 | 验证结果 |
|----|------|----------|
| AC-1 | `--mtls-enabled=1` + `--tls-algorithm=TLS_AES_256_GCM_SHA384` → 返回 0、`mtls_enabled==1`、`algorithm_name=="TLS_AES_256_GCM_SHA384"`、`algorithm==dm_hs_algorithm_from_name(...)` | PASS（用例 `AC-1 init_sbt_config mtls enabled+AES`） |
| AC-2 | `--mtls-enabled=0` + `--tls-algorithm=TLS_SM4_GCM_SM3` 生效；两键缺失回退 env/ini 基线 | PASS（用例 `AC-2a`、`AC-2b`） |
| AC-3 | 非法 `--mtls-enabled`（`--mtls-enabled=2`）或未知 `--tls-algorithm`（`BOGUS`）→ 返回 `-1` | PASS（用例 `AC-3a`、`AC-3b`） |
| AC-4 | `dmsbtex_session_test` 全量通过（含既有 `sbt_tls_config_init`/握手回归），`dmsbtex`/`dm-ftp` 构建成功 | PASS（`xmake -P . dmsbtex_session_test` 输出 `ALL PASS`；`xmake -P . dmsbtex` 构建 ok） |

## 关键实现点

- 解析块置于 `--backup-dirs` 处理之前：原 `--backup-dirs` 缺失分支 `goto next__` 会跳过后置解析逻辑（首次实现缺陷，已修正）。
- `file_mtls_present` / `file_alg_present` 标志驱动的“仅覆盖存在的键”，避免对缺失键的误写。
- 算法字段 `algorithm` 经 `dm_hs_algorithm_from_name(algorithm_name)` 统一映射，与 `sbt_tls_config_init` 一致。
- 测试接缝：在 `dmsbtex/test/session_test.c` 中 `#include "../sbt.c"`，直接调用 `init_sbt_config` 并断言 `dmsbtex_t::tls_cfg`（不改动公共头文件）。

## 证据

- `ev-t0367-sbt-config-code`（code_change）：dmsbtex/sbt.c 实现。
- `ev-t0367-sbt-config-tests`（test_pass）：dmsbtex/test/session_test.c 新增用例（AC-1~AC-3 及全量 ALL PASS）。
- `ev-t0367-sbt-config-conv-final`（convergence-map）：收敛图，校验 `valid: true`。

## 判定

- **verdict**: 待用户确认（confirmed / rejected / partial）
