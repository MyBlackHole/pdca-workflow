# AC-3 证据：计划 ↔ 本体（PRD 模板 + Plan 阶段提示）

## 改动
- `scripts/task_identity.py` 默认 PRD 模板新增 `## 关联本体节点` 小节，说明一行一个 `ontology:...` 节点 id。仅影响新建任务的默认模板，既有任务不受影响。
- `flows/flow-plan/SKILL.md`：在「声明领域本体片段」段落补充——若 `meta.ontology_fragment` 非空（或拆分自带片段的父任务），须在 PRD 的 `## 关联本体节点` 登记本任务消费/产出/对齐的本体节点 id，供 Do 阶段本体消费回链。该小节为可选登记，不影响门禁。

## 验证
- `tests/test_task_identity.py::test_default_prd_has_ontology_section` 断言默认 PRD 含 `## 关联本体节点`，通过。
