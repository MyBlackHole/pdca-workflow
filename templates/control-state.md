---
schema: pdca.control-state/v1
task_id: null
attempt: null
revision: 0
last_event_ref: null
execution_allowed: null
stop_pending: null
record_owner_ref: null
record_grant_ref: null
observed_last_transition_ref: null
termination_ref: null
retained_resource_refs: []
blocked_actions: []
blocked_reasons: []
integrity_status: null
protocol_revision: 3.4.11
---

# 宿主控制视图草稿

本视图由可信控制事件重建，不是Agent业务状态的平行权威。stop_pending时即使task仍running也不得继续；没有真实准入依据的execution_allowed不能填true。

record_owner是实际写权主体，绑定Agent身份保留在dispatch；交回前后不可两人共写task。terminal材料损坏在独立完整性记录隔离，不重开archive。blocked解除依新的CAP/RESOURCE证据和原授权，不能直接改一位布尔值。
