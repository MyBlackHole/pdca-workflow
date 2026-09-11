---
schema: pdca.termination/v1
termination_id: null
task_id: null
attempt: null
terminal_reason: null
stop_event_ref: null
last_valid_phase: null
last_transition_ref: null
last_transition_digest: null
execution_revocation_refs: []
record_handoff_ref: null
inflight_operations: []
settlement_refs: []
isolation_refs: []
retained_resource_refs: []
released_resource_refs: []
sealing_owner_ref: null
backend_receipt_ref: null
protocol_revision: 3.4.10
---

# 非正常尝试终止回执草稿

必须有真实停止来源、执行资格撤销与记录写权交回。inflight每项必须settled或isolated并有证据；孤立的超时/心跳丢失不能填终止完成。

last_valid_phase只取plan/do/check/act；phase不变、execution_state=interrupted，未经过的PDCA边不生成。保留未决影响、隔离资源和原失败。retained资源不因attempt终止就给后继使用；它们解除需要另有真实证据。

## 接续限制

终止不授权新任务。新task、新attempt、新Agent按SCHED准入；旧请求迟到确认只审计。此回执生成前保持stopping，不能在取消尚在途时写“已结束”。

有限维护profile及fixture边界见[生命周期记录契约](../ontology/contracts/lifecycle-records.md)。字段和摘要通过不认证真实宿主能力；不得把示例复制成执行事实。
