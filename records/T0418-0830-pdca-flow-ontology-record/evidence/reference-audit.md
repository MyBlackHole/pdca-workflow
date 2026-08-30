# T0418 引用审计（AC-6）

删除 knowledge/pdca-flow 与 knowledge/pdca-workflow 前的全仓引用检索结果：

## 已清理（本体节点来源路径已改为「原知识层」标注）
- ontology/process/flow-*.md、ontology/concept/*.md 内 knowledge/ 路径前缀已移除

## 已更新（其余任务规划文档）
- pdca/tasks/0815-followup-identity-observation/prd.md（T0263）：2 处方法引用已指向 ontology:concept/task-record-identity 与 self-optimization-loop

## 保留为历史（不可变 journal 叙事，非功能引用）
- pdca/journal/2026-08-15.md
- pdca/journal/2026-07-31.md
- pdca/journal/2026-08-14.md
- pdca/journal/2026-07-30.md

## 结论
scripts/SKILL/flows/docs 中无任何对两目录的引用；本体节点已自洽；仅历史 journal 保留溯源引用（按不可变记录原则保留）。
