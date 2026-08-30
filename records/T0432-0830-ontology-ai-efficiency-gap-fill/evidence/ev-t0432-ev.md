# PDCA 本体 AI 提效缺口补齐

## 新增概念节点（6 个）

| 节点 ID | 中文名 | 父节点 |
|---------|--------|--------|
| ontology:concept/leading-words | 锚定词 | writing-for-agents |
| ontology:concept/pointer-wording | 指针措辞 | writing-for-agents |
| ontology:concept/no-op-judgment | no-op 模型相对判定 | writing-for-agents |
| ontology:concept/failure-mode | 失效模式 | pdca-task |
| ontology:concept/phase-boundary-decision-tree | Phase Boundary 决策树 | pdca-transition |
| ontology:concept/grounding-dependency | Grounding 依赖图 | writing-for-agents |

## 更新的本体节点（2 个）

- ontology:concept/knowledge-provenance：新增 relates_to grounding-dependency
- ontology:concept/writing-for-agents：已被 6 个新节点引用

## 更新的技能文件（4 个）

- skills/writing-great-skills/SKILL.md：relations 新增 leading-words, pointer-wording, no-op-judgment
- skills/to-tickets/SKILL.md：frontmatter 新增 failure_mode
- skills/triage/SKILL.md：frontmatter 新增 failure_mode
- ontology/concept/knowledge-provenance.md：新增 relates_to grounding-dependency

## 验证结果

- ontology-validate: OK
- ontology_graph: 281 nodes, 532 edges, 0 islands
- 所有新节点均有 attributes 含 testable_signal
