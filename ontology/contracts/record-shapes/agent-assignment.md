---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 独立任务书：记录格式

本契约定义正式 ontology-backed task 派发给 fresh Agent 的固定输入。
字段中的 null/空列表只表示尚未取得事实，不产生授权。

## 示例

```markdown
---
schema: pdca.agent-assignment/v4
protocol_revision: 4.0.0-rc.3
task_id: null
attempt: null
work_id: null
tree_revision: null
node_id: null
ontology_revision: null
scene: null
project_context_ref: null
ontology_object_refs: []
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

传递用户已确认的目标、当前 ontology/work node、固定 parent seed、必要 relation/constraint、
dependency deliverables、scene 输入和 CONTEXT-01 选择出的 minimum sufficient refs。

不复制父/兄弟完整对话，不附带 unrelated ontology branch，不把共享记忆当隐式输入。
每个 ref 应能说明角色和固定版本/摘要；无法解释用途的材料不应默认加入。

你是本任务的独立可交互 Agent。先向用户提出本任务 Plan 目标请求；
获准后只执行当前阶段。每阶段结束保存产物、报告下一目标并等待。
不要由父 Agent 代答、代写或监控。不自动创建后代；新的 ontology responsibility 只形成 seed 待用户选择。
```
