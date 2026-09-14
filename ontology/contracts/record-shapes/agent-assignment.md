---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 独立任务书：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.agent-assignment/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
work_id: null
node_id: null
scene: null
project_context_ref: null
input_refs: []
allowed_record_scope: null
allowed_product_scope: []
creation_authorization_ref: null
---

# 独立任务书

传递用户已确认的目标与固定seed、范围、预期产物、依赖和原始来源；不复制父／兄弟对话。

你是本任务的独立可交互Agent。先向用户提出Plan目标请求，获准后只执行该阶段。每阶段结束保存产物、报告下一目标并等待；同一会话完成四阶段。不要由父Agent代答、代写或监控。不自动创建后代；分解仅提出seed待用户选择。
```
