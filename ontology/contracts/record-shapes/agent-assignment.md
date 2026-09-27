---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 独立任务书：记录格式

本契约只定义 **fresh Agent 实际接收的固定 assignment 字段**。
Task 身份语义以 TASK-01 为准，输入选择以 CONTEXT-01 为准；字段为空只表示事实未取得，不产生授权。

## 示例

```markdown
---
schema: pdca.agent-assignment/v4
protocol_revision: 4.0.0-rc.5
task_id: null
attempt: null
work_id: null
tree_revision: null
node_id: null
ontology_revision: null
scene: null
project_context_ref: null
ontology_object_refs: []
root_seed_ref: null
parent_seed_ref: null
dependency_refs: []
input_refs: []
definition_refs: []
context_refs: []
allowed_record_scope: null
allowed_product_scope: []
creation_authorization_ref: null
---

# 独立任务书

普通 task 的身份字段引用 TASK-01 已固定对象；`input_refs/definition_refs/context_refs`
只保存 CONTEXT-01 选出的 minimum sufficient context，不复制父/兄弟完整活动历史。

root modeling bootstrap 的 node/revision 为空时按 TASK-01 保持 null，并由 `root_seed_ref`
与 CONTEXT-01 的 bootstrap 输入固定真实起点，不造占位模型。

allowed scope 是 assignment 边界，不证明宿主实际拥有对应能力；能力事实由 CAP-01 / capability-check 记录。
`creation_authorization_ref` 只证明用户批准创建该具名 task，不授权 Plan 或任何后续 phase。
```
