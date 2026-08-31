# P0 差距补齐实施验证

## 实施内容

### G1：ask-matt 概念节点
- ✅ 新建 `ontology/concept/ask-matt.md`
- ✅ specializes: `ontology:concept/router-skill`
- ✅ relates_to: `ontology:concept/skill-invocation`, `ontology:concept/user-invoked`
- ✅ attributes: applicability + testable_signal

### G2：writing-great-skills relations 更新
- ✅ `ontology/domain/skill-writing-great-skills.md` 新增 relates_to:
  - `ontology:concept/leading-words`
  - `ontology:concept/pointer-wording`
  - `ontology:concept/no-op-judgment`

### G3：pdca-task 字段补充
- ✅ `schemas/task.schema.json` 新增 `steps`（对象数组）和 `completion_criteria`（字符串数组）
- ✅ `ontology/concept/pdca-task.md` 添加步骤与完成标准章节

## 验证结果

- ✅ `ontology-validate`：OK
- ✅ `ontology_graph`：333 nodes, 687 edges, 0 islands
- ✅ schema 校验通过（含新字段）
- ✅ 所有新节点均有 attributes 含 testable_signal