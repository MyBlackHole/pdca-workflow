# T0423 结论：knowledge/ 领域知识迁入 ontology/domain 后删除 knowledge/

## 上下文
T0418~T0422 已确立本体为知识唯一权威来源，但 `knowledge/` 仍含 123 个领域知识文件（649K，约 28 个域），均为本体未承载的领域知识。用户确认"先迁入本体再删"：逐文件迁移为 `ontology/domain/*` 节点，校验通过后删除 `knowledge/`。

## 假设与结果
- Plan 假设：`knowledge/` 122 个 .md 文件可逐文件映射为 `ontology/domain/` 节点（type=domain，specializes pdca 接入，无孤岛）。
- 结果：28 域根 + 122 叶 = 150 个新节点（总节点 239/边 489/孤岛 0）；`knowledge/` 已删除；16 个活动文件引用改写；证据链 + 收敛映射 valid:true；ontology-validate 通过。

## 分析（逐 AC 判定）
- **AC-1 ✅**：`ontology/domain/` 接入设计——28 域根（specializes pdca）+ 122 叶（specializes 域根、`domain` 属性指向域根），叶→根→pdca 连通、无孤岛、type==父目录名。（证据 ev-domain-design）
- **AC-2 ✅**：122 个 knowledge/ 文件逐文件迁移为 ontology/domain/* 节点（保留正文 + 补 pdca.asset/v1 frontmatter），覆盖率 122/122。（证据 ev-migrate）
- **AC-3 ✅**：`knowledge/manifest.jsonl` 与 `README.md` 随目录删除，原索引由域根节点「子主题」列表承载。（证据 ev-index-deleted）
- **AC-4 ✅**：`git rm -r knowledge/` 成功；ontology-validate OK、islands=0（缺失 knowledge/ 有存在性保护，不阻断）。（证据 ev-delete）
- **AC-5 ✅**：16 个活动文件 knowledge/ 引用改写为 ontology/domain/*（含 out-of-scope 占位符 `out-of-scope-<concept>`、manifest 废弃说明）。（证据 ev-refs）
- **AC-6 ✅**：登记 7 证据 + 收敛映射，validate-convergence valid:true。（证据 ev-evidence）
- **AC-7 ✅**：全仓（排除 records/journal/tasks/health-audit）grep knowledge/ 仅剩 ontology-validate.py docstring（守卫逻辑描述），无实时引用。（证据 ev-noref）

## 失败原因
无（全部 AC 达成）。

## 适用边界
- `scripts/out-of-scope-manager.py` 的 `--dir` 默认已改指 `ontology/domain/out-of-scope`，但其内部按 `<concept>.md` 子文件操作的假设已与实际扁平短横命名（`out-of-scope-<concept>.md`）不一致，运行时需相应改造（超出本任务范围，列为后续）。
- `scripts/ontology-validate.py` 的 REDIRECT_DANGLING/KNOWLEDGE_FM_INVALID 仍扫描 knowledge/（已删，守卫跳过），属历史注释，不影响校验。

## 下一轮建议
- 改造 `out-of-scope-manager.py` 以匹配本体扁平命名，或将其能力并入 ontology 编辑流程。
- 后续新建领域知识直接落 `ontology/domain/`，不再使用 `knowledge/`。

## 已知坑
- `records/T0272-0815-self-audit/health-audit.md` 为 T0272 既有未提交改动，提交须始终排除。

## 判定
- verdict.outcome: **confirmed**
- reason: 7 项 AC 全部达成，knowledge/ 已删除，本体承载全部领域知识，校验通过且无孤岛，证据链与收敛映射可复核。
- verdict_id: T0423-confirmed-2026-08-30
- at: 2026-08-30T11:19:10+08:00
