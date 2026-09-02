---
schema: pdca.asset/v1
id: T0523-0903-research-zfs-compress
phase: check
source_ids: [research-compress, ontology-zio-compress, convergence-map-v2]
---

## 上下文

任务 T0523 隶属 Transform 三栈全覆盖研究，聚焦 `ontology:entity/zfs-zio` 的 `transform_stack` 压缩分支。Plan 阶段经 4 轮 Grill 明确范围为 compress 全栈深化（`lz4/zstd/gzip/zle` 与 `ZIO_STAGE_WRITE_COMPRESS/DECOMPRESS` 压栈-弹栈及 `lsize→psize`），PRD 定义 3 项 AC 覆盖研究报告、本体细化与证据链。Do 阶段已产出 `research-compress.md`（37149B）与 `ontology:entity/zfs-zio` 细化（36317B，257 行），经 `register-evidence` 登记并生成 `convergence.json`，`validate-convergence` 验证 `valid:true`，现进入 Check 对照 PRD/证据/收敛条件逐项验收。

## 假设与结果

- 假设：ZIO transform 栈中 compress 可经 `zio_compress_table[ZIO_COMPRESS_FUNCTIONS]` 的 `zio_compress_info_t（ci_compress/ci_decompress/ci_decompress_level/ci_level）` 表驱动建模，`lz4/zstd/gzip1-9/zle/lzjb/empty` 选型与 `ZIO_STAGE_WRITE_COMPRESS` 压 `zio_decompress` / `zio_read_bp_init` 压 `zio_decompress` 及 `lsize→psize` 五分支（`zero/EMPTY/ge_lsize/embedded/roundup→push`）可一图穷尽，且本体 `transform_stack` 可深化至 `compress_func/zio_compress_info_t/compress_empty` 边界并经 `grep -q 'zio_compress'` 回归，证据链可经 `manifest.jsonl + convergence.json` 闭环。
- 结果：假设全部成立。研究报告 3 图全覆盖且每图可溯 `openzfs/zfs file:line`（`grep -c '^```mermaid'`=3 ≥3，`grep -c 'Source:'`=15 ≥3），覆盖 `lz4/zstd/gzip/zle` 四算法与 `ZIO_STAGE_WRITE_COMPRESS (1<<5)` / `zio_decompress` 压栈-弹栈及 `lsize→psize` 变换；本体 `transform_stack` 已细化至表驱动与 ABD 边界及短路分支，`attributes` 3 项、决策树/正反例/门禁齐全，`testable_signal` 含 `grep -q 'zio_compress'` 命中；证据链 `manifest.jsonl` 4 条（含 superseded）、`convergence.json` 3 项逐条回链 `meta.convergence`，`validate-convergence` `valid:true` 无 issues，`ontology-validate` OK 且 `islands:0`。

## 分析

- **AC-1** ✅ 研究报告 `research-compress.md` 含 3 类 mermaid（C4 L3 `graph TD`、时序 `sequenceDiagram`、状态机 `stateDiagram-v2`，实测 `grep -c '^```mermaid'` =3 ≥3，`grep -c '```mermaid'` =6 ≥3）且每图附 `Source: openzfs/zfs file:line`（`grep -c 'Source:'` =15 ≥3，每图 `%% Source:` inline + 紧跟 `*Source:` 外联，双重可溯），覆盖 `lz4`（`lz4_zfs.c:57 BE_32`）、`zstd`（`zfs_zstd.c:555 early-abort+header c_len+level`）、`gzip`（`gzip.c:42 qat→zlib`）、`zle`（`zle.c:29 n=64 literal/run`）四算法与 `ZIO_STAGE_WRITE_COMPRESS=1<<5（zio_impl.h:125）` / `ZIO_WRITE_PIPELINE 含 COMPRESS（zio_impl.h:214）` / `zio_write_compress lsize→psize（zio.c:1907）` / `zio_read_bp_init 压 zio_decompress（zio.c:1803）` / `zio_decompress/d_data（zio.c:545 / zio_compress.c:107）` / `zio_push_transform lsize/psize 链（zio.c:492）` 的压栈-弹栈及 `lsize→psize` 往返（`grep -q 'lz4' && grep -q 'zstd' && grep -q 'gzip' && grep -q 'zle' && grep -q 'ZIO_STAGE_WRITE_COMPRESS' && grep -q 'zio_decompress' && grep -q 'lsize' && grep -q 'psize'` 全部命中），满足 PRD 对 `cabd/psize→lsize/BP_SET_*` 变换的覆盖要求。（research-compress）
- **AC-2** ✅ `ontology:entity/zfs-zio` 本体 `transform_stack` 已细化压缩分支：`constraint` 覆盖 `compress_func` 选型、`zio_compress_info_t` 表（`ci_name/ci_level/ci_compress/ci_decompress/ci_decompress_level`，`gzip 1-9=1..9 / zle 64 / zstd 3 / lz4 0`）、`enum zio_compress` 18 项（`INHERIT/ON/OFF/LZJB/EMPTY/GZIP_1-9/ZLE/LZ4/ZSTD`）、`ZIO_COMPRESS_HASLEVEL/zstd level 1-19/fast`、`compress_empty` 双短路（`abd_cmp_zero→psize 0 hole` / `EMPTY→psize=lsize 不调 ci_compress`）、`zio_compress_data/zio_decompress_data` 的 `d_len 与 c_len>d_len→s_len 回退`、`embedded 短路 BPE_PAYLOAD_SIZE=512` 与 `psize roundup 的 abd_zero_off` 及 `ABD 边界 ZFS_COMPRESS_WRAP_DECL`（`zle n=64 / lz4 BE_32 / gzip qat / zstd early-abort+header`），`attributes` 数量 3（`pipeline_bitmap/vdev_dispatch/transform_stack`），正文 `wc -l` =257 ≥60 且 `ls ontology/entity/zfs-zio.md` 命中，正文含 `## 决策树`（`flowchart TD` mermaid 60+ 行，覆盖 `WRITE_COMPRESS 五分支→ENCRYPT→CHECKSUM→DVA→VDEV→DECRYPT/DECOMPRESS` 全栈）、`## 正例`（6 例：pipeline 位图配对、VDEV taskq、checksum 选型、compress 选型与 lsize→psize、compress_empty、校验自愈）、`## 反例`（12 例：pipeline 错配/漏弹栈/绕 taskq/深度溢出/fletcher4 作 dedup/误 push checksum/byteswap 遗漏/edonr 未 salted/zstd INHERIT/EMPTY 误调 ci_compress/漏 roundup/zstd 漏 ci_decompress_level）、`## 门禁`（12 条：多图/溯源/压缩算法覆盖/校验算法回归/压缩分支/校验分支/栈/校验栈/正文/属性/本体校验/脚手架/收敛/T0516 回归），`testable_signal` 含 `grep -q 'zio_compress'`（`grep -q "zio_compress" ontology/entity/zfs-zio.md` 命中，且 `grep -q 'zio_compress_info_t'` 与 `grep -q 'compress_empty'` 均命中），`ontology-validate --ontology-dir ontology` 返回 `OK` 且 `ontology_graph --format summary` `islands:0`，`ontology_test_scaffold --node ontology:entity/zfs-zio` 可产，满足 AC-2 对 `attributes≥3 且含决策树/正反例/门禁` 的要求。（ontology-zio-compress）
- **AC-3** ✅ 证据链完整：`evidence/` 含 `research-compress.md`（37149B, `sha256:09213a2331d0f52a5cda46c3e8cebc5db54c1a3280533ad416fd91339c1fa486`）与 `zfs-zio.md`（36317B, `sha256:27bff6bdcfafbb098cb72ae7a102d8748aaae9bed99eb218f39585acacaadbd7`）及 `convergence.json`（579B, `sha256:4a817638d2c248f3b25d0282564cb59ca8417835e32cdb6e07cf6cced9886832`）与 `convergence_T0523.superseded.convergence-map-v2.json` 快照，`manifest.jsonl` 4 条登记（`research-compress` → AC-1/AC-3、`ontology-zio-compress` → AC-2/AC-3、`convergence-map` superseded→`convergence-map-v2` → AC-1/2/3 且 `evidence_type_ref: ontology:entity/evidence-convergence-map`），`convergence.json` 3 项逐条回链 `meta.convergence`（1: research 报告含 3 mermaid+Source 覆盖压缩/解压 → AC-1；2: transform_stack 压缩分支细化 → AC-2；3: grep zio_compress 命中 → AC-3），`validate-convergence --task-dir pdca/tasks/0903-research-zfs-compress` 返回 `valid:true` 无 issues，`evidence_issues` 0，`manifest` 中 `size/digest` 与实文件一致且 `convergence.json` 文件物理存在，满足证据链完整性。（convergence-map-v2, research-compress, ontology-zio-compress）

## 失败原因

无（verdict 为 confirmed，3 项 AC 全部达成）。

## 适用边界

- 研究范围限定为 `openzfs/zfs#master @ /tmp/zfs` 的 `include/sys/zio_compress.h:31-49,52-58,116-135` / `module/zfs/zio_compress.c:33-142` / `module/zfs/zio.c:492-560,1777-2140` / `include/sys/zio_impl.h:125,214` / `module/zfs/lz4_zfs.c:57` / `module/zfs/gzip.c:42` / `module/zfs/zle.c:29` / `module/zstd/zfs_zstd.c:449-711` 的选型-压栈-变换分支，未深至 `metaslab` 的 `DVA_ALLOCATE` 数值调参、`vdev_queue` deadline 数值、`QAT` 硬件阈值调参、`zstd early-abort` 阈值数值、`SPA sync_pass` 多 pass 收敛（见 `T0503`）与加密-校验跨栈交互（见 `T0522/T0524`）。
- 本体 `ontology/entity/zfs-zio.md` 当前为 257 行合并版（含 `T0522` checksum 分支与 `T0523` compress 分支），与 `evidence/zfs-zio.md` 快照（36317B）为同一内容落盘，无实质差异；行号以 `grep -n zio_compress` 重锚可抵御上游漂移。
- 结论可复核性依赖 `file:line` 行号与 `grep` 门禁，ZFS 上游行号漂移需以 `grep -n ZIO_COMPRESS_/zio_compress_table/zio_compress_data` 重锚，`grep -c '^```mermaid'` 与 `grep -c 'Source:'` 双门禁已在报告附录自检脚本中显式给出。

## 本体沉淀

- 决策：`ontology:entity/zfs-zio` 已沉淀（`ontology:entity/zfs-zio` 的 `transform_stack` 压缩分支细化至 `compress_func/zio_compress_info_t/compress_empty/lsize→psize/ABD 边界`，含决策树/正反例/门禁，且 `attributes` 3 项均含 `testable_signal grep -q` 可回归；`records/T0523-0903-research-zfs-compress/research-compress.md` 与 `ontology/entity/zfs-zio.md` 双轨可复核）。
- 依据：`research-compress.md` 3 类 mermaid 每图附 `Source: openzfs/zfs file:line` 覆盖 `lz4/zstd/gzip/zle` 与 `ZIO_STAGE_WRITE_COMPRESS/DECOMPRESS` 压栈-弹栈及 `lsize→psize`，本体 `wc -l 257`、`ontology-validate OK`、`islands:0`、`validate-convergence valid:true`，`manifest.jsonl` 4 条登记对齐。
- 处置：本体已在本任务 Do 阶段落盘并经 evidence 登记，无需另建 `ontology:pattern/research-diagram-methodology` 或 `ontology:concept/pdca-task` 新节点；`records-only` 不适用。
- 可复核：`grep -q 'zio_compress' ontology/entity/zfs-zio.md && grep -q 'zio_compress_info_t' ontology/entity/zfs-zio.md && grep -q 'compress_empty' ontology/entity/zfs-zio.md` 命中；`grep -c '^```mermaid' records/T0523-0903-research-zfs-compress/research-compress.md` =3 且 `grep -c 'Source:'` =15。

## 下一轮建议

- 将本研究报告 C4 L3（选型）与时序（压栈-弹栈 `lsize→psize`）与状态机（五分支一栈）三图作为 `skill-research` 后续 ZIO 相关调研模板，并在 `templates/research-report.md` 回链；后续 `zfs-encrypt`（`T0524`）可直接复用决策树扩展加密分支，无需回滚。
- 以 `zpool get compressratio` 与 `zdb -bb` 的 `L/PSIZE` 双监控、`grep -q 'zio_compress'` 与 `validate-convergence` 门禁脚本化纳入 CI；生产先定 `compression=lz4/zstd` 再调 `recordsize`，`dn_compress==EMPTY` 时禁 `dedup`。
- `T0516` 回归门禁（`grep -q 'ZIO_WRITE_PIPELINE' records/T0516-0903-research-zfs-zio/research-zio.md`）与 `T0522` 校验分支门禁（`grep -q 'zio_checksum' ontology/entity/zfs-zio.md`）均已在本体 `## 门禁` 中显式保留，后续归档无需额外回归。

## 判定

- verdict.outcome: **confirmed**
- reason: 3 项 AC 全部达成，研究 3 mermaid+15 Source 覆盖 lz4/zstd/gzip/zle 与 WRITE_COMPRESS/DECOMPRESS 及 lsize→psize，本体 transform_stack 细化至 compress_func/zio_compress_info_t/compress_empty 且 3 attrs+决策树正反例门禁 257 行，证据链 manifest 4 条+convergence 3 项 valid:true 且 ontology-validate OK islands:0
- verdict_id: T0523-confirmed-20260902
- at: 2026-09-02T11:00:00+08:00

**verdict**: confirmed
