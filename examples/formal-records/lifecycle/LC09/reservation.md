---
schema: pdca.resource-reservation/v1
reservation_id: LC09-RES
owner_task_id: LC09-OLD
owner_attempt: 1
slot_ref: fixture:slot
state: retained
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
release_receipt_ref: null
retention_reason: unknown remote effect; retain full target
isolation_refs:
- ref: effect-proof.md
  digest: 72d5c9624e0f7d911109ad0dc66e945a7f252ddeeacb2949ef453febd6c4a719
protocol_revision: 3.4.4
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
