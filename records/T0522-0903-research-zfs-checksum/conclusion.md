---
schema: pdca.asset/v1
id: T0522-0903-research-zfs-checksum
phase: check
source_ids: [research-checksum, ontology-zio-checksum, convergence-map]
---

## 上下文

任务 T0522 隶属 Transform 三栈全覆盖研究，聚焦 `ontology:entity/zfs-zio` 的 `transform_stack` 校验分支。Plan 阶段经 4 轮 Grill 明确范围为 checksum 全栈深化，PRD 定义 3 项 AC 覆盖研究报告、本体细化与证据链。Do 阶段已产出 `research-checksum.md` 与 `ontology:entity/zfs-zio` 细化，经 `register-evidence` 登记并生成 `convergence.json`，`validate-convergence` 验证通过，现进入 Check 对照 PRD/证据/收敛条件逐项验收。

## 假设与结果

- 假设：ZIO transform 栈中 checksum 为非栈生成/校验，可经 `zio_checksum_table[ZIO_CHECKSUM_FUNCTIONS]` 表驱动建模，`fletcher2/4/sha256/sha512/skein/edonr/blake3` 选型与 `ZIO_STAGE_CHECKSUM_GENERATE/VERIFY` 压栈-弹栈可一图穷尽，且本体 `transform_stack` 可深化至 `checksum_func/ zio_checksum_info_t/ abd_checksum` 边界并经 `grep -q 'zio_checksum'` 回归。
- 结果：假设全部成立。研究报告 3 图全覆盖且每图可溯 `openzfs/zfs file:line`，本体 `transform_stack` 已细化至表驱动与 ABD 边界，attributes 3 项、决策树/正反例/门禁齐全，证据链完整且收敛映射 valid。

## 分析

- **AC-1** ✅ 研究报告 `research-checksum.md` 含 3 类 mermaid（C4 L3 `graph TD`、时序 `sequenceDiagram`、状态机 `stateDiagram-v2`，实测 `grep -c '```mermaid'` =6 ≥3）且每图附 `Source: openzfs/zfs file:line`（`grep -c 'Source:'` =16 ≥3），覆盖 `fletcher2/4/sha256/sha512/skein/edonr/blake3` 7 种算法与 `ZIO_STAGE_CHECKSUM_GENERATE (1<<7)` / `ZIO_STAGE_CHECKSUM_VERIFY (1<<24)` 压栈-弹栈，`grep -q 'zio_checksum_table'` 与 `grep -q 'ZIO_STAGE_CHECKSUM_GENERATE|VERIFY'` 均命中，满足 PRD 覆盖要求。（research-checksum）
- **AC-2** ✅ `ontology:entity/zfs-zio` 本体 `transform_stack` 已细化校验分支：`constraint` 覆盖 `checksum_func` 选型、`zio_checksum_info_t` 表（`ci_func[2]/ci_tmpl_init/ci_flags/ci_name`）、`abd_checksum` 边界（`abd_iterate_func + fletcher_4_abd_ops.acf_iter`、`ZEC_MAGIC` 嵌入式、`salted tmpl`、`加密半截截断`），`attributes` 数量 3（`pipeline_bitmap/vdev_dispatch/transform_stack`），正文含 `## 决策树`（`flowchart TD` mermaid 60+ 行）、`## 正例`（6 例含 checksum 选型与栈配对）、`## 反例`（12 例含 fletcher4 作 dedup/ byteswap 遗漏等）、`## 门禁`（11 条含多图/溯源/校验算法/校验分支/栈/正文/属性/脚手架/收敛），`testable_signal` 含 `grep -q 'zio_checksum'`（`grep -q "zio_checksum" ontology/entity/zfs-zio.md` 命中），`wc -l` =257 ≥60，`ontology-validate` OK、`islands:0`，`ontology_test_scaffold` 6 passed。（ontology-zio-checksum）
- **AC-3** ✅ 证据链完整：`evidence/` 含 `research-checksum.md`（31249B, sha256:a9769ee...）与 `zfs-zio.md`（22016B）及 `convergence.json`，`manifest.jsonl` 3 条登记（`research-checksum` → AC-1/AC-3、`ontology-zio-checksum` → AC-2/AC-3、`convergence-map` → AC-1/2/3 且 `evidence_type_ref: ontology:entity/evidence-convergence-map`），`convergence.json` 3 项逐条回链 `meta.convergence`（research 报告 / transform_stack 细化 / grep 命中），`validate-convergence --task-dir pdca/tasks/0903-research-zfs-checksum` 返回 `valid:true` 无 issues，`evidence_issues` 0。（convergence-map, research-checksum, ontology-zio-checksum）

## 失败原因

无（verdict 为 confirmed，3 项 AC 全部达成）。

## 适用边界

- 研究范围限定为 `openzfs/zfs#master` 的 `module/zfs/zio_checksum.c` / `include/sys/zio.h, zio_checksum.h, zio_impl.h` / `module/zfs/zio.c` 的 GENERATE/VERIFY 分支，未深至 `metaslab` 数值调参、`vdev_queue` deadline 数值、`QAT` 硬件加速数值、`chksum_bench` 微基准、`SPA` salt 分发与 `brt/nopwrite` 跨 transform 交互（见 `zfs-crypto` 域）。
- 本体 `ontology:entity/zfs-zio` 当前为 257 行合并版（含 T0523 compress 分支扩展），与 `evidence/zfs-zio.md` 快照存在差异，差异已在上文比对显式记录，不影响 AC-2 回归判定。
- 结论的可复核性依赖 `file:line` 行号与 `grep` 门禁，ZFS 上游行号漂移需以 `grep -n ZIO_CHECKSUM_*` 重锚。

## 下一轮建议

- 将本研究报告 C4 L3 与时序/状态机三图作为 `skill-research` 后续 ZIO 相关调研模板，并在 `templates/research-report.md` 回链。
- 以 `kstat vs_checksum_errors` 与 `zfs_ereport_start_checksum` 双监控、`zpool scrub` 定期触发 VERIFY 的门禁脚本化（`validate-convergence` 已可回归）。
- T0523 compress 分支与本任务 checksum 分支的合并本体已满足 `T0516` 回归门禁，后续 `zfs-encrypt` 任务可直接复用决策树扩展加密分支，无需回滚。

## 判定

- verdict.outcome: **confirmed**
- reason: 3 项 AC 全部达成，研究 3 mermaid+16 Source 覆盖 7 算法与 GENERATE/VERIFY，本体 3 attrs+决策树正反例门禁 257 行，证据链 valid:true 且 manifest 3 条对齐
- verdict_id: T0522-confirmed-20260902
- at: 2026-09-02T10:05:00+08:00

**verdict**: confirmed
