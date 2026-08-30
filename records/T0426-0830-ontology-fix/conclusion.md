# T0426 结论：清理本体 knowledge/ 残留引用并重建 manifest 索引

## 上下文
T0425 审查发现本体融入存在缺口：43 个本体文件含 `knowledge/` 残留引用，`ontology/manifest.jsonl` 缺失。

## 假设与结果
- Plan 假设：清理 `knowledge/` 残留引用并重建 manifest 可完成本体融入闭环。
- 结果：34 个文件已清理，manifest 已重建（240 条记录），`ontology-validate.py` 新增 `KNOWLEDGE_REF_CLEANUP` 规则，全部通过。

## 分析（逐 AC 判定）
- **AC-1 ✅**：34 个本体文件已清理 `knowledge/` 残留引用，改为 `ontology/domain/` 路径。（证据 ev-review-report）
- **AC-2 ✅**：`ontology/manifest.jsonl` 已重建，包含 240 条记录及 `ontology_type`/`specializes`/`domain`/`entity_refs`/`attributes` 索引。（证据 ev-manifest, ev-review-report）
- **AC-3 ✅**：`ontology-validate.py` 通过（含新增 `KNOWLEDGE_REF_CLEANUP` 规则）。（证据 ev-validate, ev-review-report）
- **AC-4 ✅**：ontology_graph 无新增孤岛（nodes:239/edges:489/islands:0）。（证据 ev-review-report）
- **AC-5 ✅**：`test_ontology_full_lifecycle.py` 8 passed，`test_out_of_scope.py` 8 passed，`test_pdca_ontology_correct.py` 10 passed。（证据 ev-review-report）
- **AC-6 ✅**：证据已登记，收敛映射 valid:true。（证据 convergence-map）

## 失败原因
无（全部 AC 达成）。

## 适用边界
- 9 个含 `knowledge-`（连字符）的文件为合法概念名称（如 `knowledge-artifact`），无需清理。
- `ontology/README.md` 为 SSOT v3 文档，非节点文件。

## 下一轮建议
- 推进 T0399（知识表达按本体论重构）至完成
- 推进 T0403（全量迁移其余域与 manifest 索引重写）至完成

## 已知坑
- `test_ontology_validate.py` 有 3 例因临时本体缺规则节点失败（T0413 遗留），不在本任务 AC-5 清单。

## 判定
- verdict.outcome: **confirmed**
- reason: 6 项 AC 全部达成，knowledge/ 残留引用已清理，manifest 已重建，ontology-validate 通过（含新规则），测试通过。
- verdict_id: T0426-confirmed-2026-08-30
- at: 2026-08-30T14:29:00+08:00
