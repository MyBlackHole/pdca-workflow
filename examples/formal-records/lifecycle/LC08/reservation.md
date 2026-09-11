---
schema: pdca.resource-reservation/v1
reservation_id: LC08-RES
owner_task_id: LC08-OLD
owner_attempt: 1
slot_ref: fixture:slot
state: released
resource_set:
- backend: fixture
  namespace: lc
  canonical_object_id: OBJ-A
  scope: whole_object
  access: write
authorization_ref: null
guarantee_profile: null
capability_check_ref: null
backend_ref: null
acquire_receipt_ref: null
ownership_epoch: 1
validity_ref: null
revocation_refs: []
inflight_operation_refs: []
release_receipt_ref:
  ref: release.md
  digest: c4029b6a8bdbd0cd714c0a2fd08fab3802e59f4d7e83244e144fe90870cc562b
retention_reason: null
isolation_refs: []
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
