# T0369 审查 rdb.cfg 配置的使用问题

## 问题陈述
`rdb.cfg`（代码实际文件名 `rdb.conf`，默认 `/opt/aio/cfg/rdb.conf`）是仓库内 C/Go 工具统一读取的配置文件，经 `libs/rdb-config.c` 的 `sec_resolve_*` 4 层解析（env / 工具段 / 全局段 / 默认）与各模块自写解析消费。近期 T0367（dmsbtex 读 sbt-config.conf）、T0368（oss 读 rdb.conf）均涉及该配置体系，暴露出跨工具不一致、常量重复、解析语义隐患等问题。本任务对 rdb.cfg 配置的使用做系统性审查，产出问题清单与（按决定）修复建议/修复。

## 初步事实（Triage 已查证）
- `sec_resolve_str` 实际优先级：**env(第1) > 工具段(第2) > 全局段(第3) > 默认(第4)**；但 T0368 oss 实现为 工具段 > 全局段 > env > 默认（**env 与工具段顺序相反**），且 oss 自写 INI 解析（`oss/cmd/tls.go`）与 inih 解析语义可能不一致（注释/引号/大小写/重复键）。
- `RDB_CONFIG` / `DEFAULT_RDB_CONFIG_PATH` 在 6 个 `config.h` 各抄一份（libs/rdb-config.h、s3tools/s3file、s3tools/s3mount、rpc/rpc-config.h、fs-backup/fsdeamon、fs-backup/fsclient），无单一来源。
- `config_get_string` 在 section 缺失时回退到文件顶部「无 section」键（隐式第 0 层），超出文档 4 层模型。
- `CONFIG_KV_MAX` 达上限时 `do_parse_config` 返回 0 → inih 停止解析 → 后续配置**静默截断**。
- `config_get_int` 用 `atoi`（脏值→0 无校验）；`config_get_int_env` 对 env 仅判 `!= NULL` 未判空串。
- 全局双缓冲 `_kv_stores[2]` + `config_index` 切换无锁，`init_config` 并发 reload/读取有竞态风险。
- 命名混淆：代码用 `rdb.conf`，运维/用户称 `rdb.cfg`。
- 配置源分散：dmsbtex 读 `sbt-config.conf`、oss 读 `rdb.conf`、其余读 `rdb.conf`，无统一配置源。
- `sec_resolve_str` 第1层直接返回 `getenv` 指针（运行时 env 变化即变行为；`RPC_TLS_CERT_DIR` 等未做路径校验 → 证书路径注入风险，依赖 env 可信）。

## 方案方向（待 Grill 确认）
- 审计方法：静态核对 `grep sec_resolve` 全部 56 处调用点的优先级参数与默认值；通读 `rdb-config.c` 解析路径；比对各 `config.h` 常量；比对 oss(Go)/dmsbtex 解析语义。
- 产出：审查报告（每条 finding 含 位置/复现/影响/严重度/修复建议）。

## 验收标准
- [ ] AC-1: 输出审查报告 `review.md`，覆盖全部已查证问题，每条含 位置、复现/证据、影响、严重度（高/中/低）、修复建议。
- [ ] AC-2: 一致性核对——列出所有 `sec_resolve_*` 调用点的优先级顺序，标注与文档 4 层模型不符处（含 oss/Go 与 C 的顺序差异）。
- [ ] AC-3: 列出常量重复（`RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH`）与配置源分散（sbt-config.conf vs rdb.conf）清单。
- [ ] AC-4: 解析语义隐患（静默截断、无 section 回退、atoi、双缓冲无锁、env 直接返回）逐条评估严重度与修复建议。
- [ ] AC-5: 按 Grill 决定（报告+修复全部中/高），对全部中/高优先级问题执行修复：① C 与 Go(oss) 配置优先级顺序对齐为 `env > 工具段 > 全局段 > 默认`；② 修复 `CONFIG_KV_MAX` 达上限静默截断（改为报错或扩容并提示）；③ 抽取/统一 `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 常量（消除 6 处重复）；④ 收敛「无 section 回退」隐式层；⑤ `atoi`/`config_get_int_env` 空串与脏值校验；⑥ 双缓冲无锁切换加锁或文档化；⑦ 收敛配置源（sbt-config.conf vs rdb.conf）与 Go 重写解析语义对齐 inih；⑧ 命名 rdb.conf vs rdb.cfg 文档统一。低优先级仅给建议。每处修复含复现/影响说明与回归验证。

## 范围外
- 不重写配置系统整体架构（除非决定要求）。
- 不改动业务默认值语义（仅修正不一致/隐患）。

## 备注
- review 场景无测试产物，跳过测试接缝声明。
- 关联任务：T0367（dmsbtex sbt-config）、T0368（oss rdb.conf HTTPS）。
