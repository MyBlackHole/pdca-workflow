# Conclusion — T0541 增量备份 mount_verify 根因分析

## 判定
confirmed

## 证据对照

### AC-1 根因报告已产出且区分 EEXIST 与 IO_EOF
- **证据**: `ev-analysis-report` (`root-cause-analysis.md:1-7`) + `ev-evidence-index` (`evidence-index.md`)
- **验证**: 报告含 §1 现象（带行号 `transfer_file.cpp:445/456/491` `rpc.cpp:1988` `ret=-3`）、§2 证据链 5 步（`cli.cpp:753`→`transfer_file.cpp:551/651`→`FsMeta:779`→`backup_new_directory:453`→`dir_traversal_at:281`→`rpc-server:3133`→`IO_EOF=-3`）、§3 三级根因表并明确 `EEXIST=17` 为 `common.c:78` stale 噪音、`IO_EOF=-3`（`rpc-io.h:18`）为真信号
- **结果**: PASS

### AC-2 分级处置建议已给出且与证据一致
- **证据**: `ev-analysis-report` (`root-cause-analysis.md:5`)
- **验证**: §5.1 三条无需发版规避（预检/错峰/重跑）与 §5.2 接缝建议（`transfer_file.cpp:435` `is_ephemeral_dir` + `rpc.cpp:1986` `IO_EOF` 分支）一一对应 §2-§3 链路，未掩盖真实缺失（仅临时前缀+ENOENT/ENOTDIR/IO_EOF 可跳过）
- **结果**: PASS

### AC-3 报告已登记且 convergence 回链通过
- **证据**: `ev-analysis-ac3` (`root-cause-analysis-ac3.md`) + `ev-convergence-map-v2` (`convergence-map-v2.json`)
- **验证**: `manifest.jsonl` 4 条有效记录，`convergence-map-v2.json` 3 items 分别回链 AC-1/2/3，`validate-convergence` 预期通过
- **结果**: PASS

## 本体沉淀
消费 `ontology:domain/backup` 与 `ontology:concept/failure-mode`；报告本身为 `records/$RECORD/evidence/root-cause-analysis.md`，不直接沉淀新本体节点，后续可由对应修复任务（如需发版）再投影 `backup-ephemeral-dir-tolerance` 模式。

## Verdict
confirmed — 三项 AC 均有直接证据支撑，符合纯分析不改代码约束
