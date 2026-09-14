---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 实际副作用操作：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.operation/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
run_id: null
operation_id: null
reservation_ref: null
resource_ref: null
arguments_digest: null
idempotency_key: null
idempotency_evidence_ref: null
status: planned
backend_request_ref: null
result_ref: null
reconciliation_ref: null
---

# 实际副作用操作

保存到本任务集中记录区。登记和调用间中断不能证明尚未调用；无返回记录unknown并查询原operation。planned/submitted/unknown/succeeded/failed/settled是观察状态，不是执行器。

只在原任务、原run及同一后端已验证幂等语义内重试；用户批准阶段不授权扩大参数或资源范围。后端失败、对象失败、结果未知分别记录，原结果不覆盖。
```
