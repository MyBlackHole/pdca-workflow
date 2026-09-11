---
schema: pdca.operation/v1
task_id: null
attempt: null
operation_id: null
action: null
target_resources: []
parameters_digest: null
reservation_refs: []
ownership_epoch: null
authorization_ref: null
control_revision: null
idempotency_mode: null
idempotency_key: null
backend_request_ref: null
status: null
result_ref: null
reconciliation_ref: null
settlement_ref: null
limitations: []
protocol_revision: 3.4.10
---

# 业务操作事实草稿

操作ID作用域为(task_id,operation_id)，不使用阶段sequence推断执行次数。实际调用前固定目标/参数/授权/资源/重试策略，调用后保存真实目标返回。

状态可为prepared/submitted/completed/cancelled_before_effect/unknown/isolated。prepared后崩溃不证明调用没发生；unknown只能先对账或可靠隔离。仅在目标已验证支持同幂等键或证明前次无作用时安全重试，不声明exactly-once。

取消不删除operation记录；即使旧Agent进程已退出，远端操作仍须核查。fixture事件与生产I/O严格分开。
