---
schema: pdca.wait-policy/v1
policy_id: null
revision: null
scope: null
mode: null
authority_source_ref: null
authorization_scope: null
deadline_rule: null
clock_requirements: null
host_owner_ref: null
protocol_revision: 3.4.10
---

# 派发前等待策略草稿

mode仅explicit_wait/deadline_interrupt。scope明确工作、任务或请求类别；真实authority_source_ref与版本必填，不能用尚未取得的Plan确认自举其自身超时。

explicit_wait没有自动截止，允许用户随时取消。deadline_interrupt明确期限如何从宿主事件生成、clock epoch/continuity和停止授权；相应deadline放到每次request，不接受Agent自填wall clock作为竞争裁决。

## 故障与变更

策略改变只作用于明确授权的新请求/新任务，不追溯缩短旧等待；若用户明确取消旧请求，用独立事件处理。时间域断裂停止消费并人工核对，不能猜“已经超时”。工作级树确认到期只阻止提案冻结，不把节点取消。
