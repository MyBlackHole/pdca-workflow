# 补齐 PDCA 本体 P0 差距：ask-matt 节点、writing-great-skills relations、pdca-task 字段

## 目标

修复 T0434 审查发现的 3 项 P0 差距，确保 PDCA 本体完整覆盖 Matt Pocock/skills v1.2.3 的核心原则。

## 背景

T0434 审查发现 3 项 P0 差距：
1. **G1**：`ask-matt` 路由概念节点缺失——ask-matt 是用户入口路由技能，概念层无对应节点
2. **G2**：`writing-great-skills`（ontology/domain 版）relations 未更新——T0432 结论声称更新了 relations，但实际文件仍缺少 leading-words, pointer-wording, no-op-judgment 的 relates_to
3. **G3**：`pdca-task` 缺少 steps 和 completion criteria 字段——技能步骤和完成标准无法在本体层面建模

## 参考

- T0434 结论：`records/T0434-0830-pdca-ai-efficiency-review-2/conclusion.md`
- T0432 结论：`records/T0432-0830-ontology-ai-efficiency-gap-fill/conclusion.md`
- ask-matt skill：`ontology/domain/skill-ask-matt.md`
- writing-great-skills：`ontology/domain/skill-writing-great-skills.md`
- pdca-task：`ontology/concept/pdca-task.md`

## 验收标准

- [ ] AC-1：添加 `ontology:concept/ask-matt` 概念节点，ontology-validate 通过
- [ ] AC-2：更新 `skills/writing-great-skills/SKILL.md` 的 relations，新增 leading-words, pointer-wording, no-op-judgment
- [ ] AC-3：为 `pdca-task` 补充 `steps` 和 `completion_criteria` 字段，schema 校验通过
- [ ] AC-4：登记证据，收敛映射 valid:true

## 实施计划

### G1：ask-matt 概念节点
- 新建 `ontology/concept/ask-matt.md`
- 类型：concept
- specializes: `ontology:concept/skill-mechanics`
- attributes: applicability, testable_signal
- relates_to: `ontology:concept/router-skill`, `ontology:concept/skill-invocation`

### G2：writing-great-skills relations 更新
- 更新 `ontology/domain/skill-writing-great-skills.md` 的 relations 块
- 新增 relates_to: `ontology:concept/leading-words`, `ontology:concept/pointer-wording`, `ontology:concept/no-op-judgment`

### G3：pdca-task 字段补充
- 在 `schemas/task.schema.json` 的 `meta` .properties 中新增 `steps` 和 `completion_criteria` 字段
- 在 `ontology/concept/pdca-task.md` 中添加对应属性描述
- `steps`: 数组类型，每个元素含 name/description/completion_criterion
- `completion_criteria`: 字符串类型，清晰且有需求强度的完成条件

## 领域本体引用
- `ontology:concept/skill-mechanics`
- `ontology:concept/router-skill`
- `ontology:concept/skill-invocation`
- `ontology:concept/writing-for-agents`
- `ontology:concept/leading-words`
- `ontology:concept/pointer-wording`
- `ontology:concept/no-op-judgment`
- `ontology:concept/pdca-task`