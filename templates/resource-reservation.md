---
schema: pdca.resource-reservation/v1
reservation_id: null
owner_task_id: null
owner_attempt: null
slot_ref: null
state: null
resource_set: []
authorization_ref: null
guarantee_profile: null
capability_check_ref: null
backend_ref: null
acquire_receipt_ref: null
ownership_epoch: null
validity_ref: null
revocation_refs: []
inflight_operation_refs: []
release_receipt_ref: null
retention_reason: null
isolation_refs: []
protocol_revision: 3.4.11
---

# 实际资源预约草稿

resource_set每项填写backend/namespace、canonical_object_id、scope、access、规范化证据、别名/范围冲突判断。跨任务/工作/树版本检查同一对象；字符串不同不能证明无冲突。

## 取得与释放

state来自真实requested/held/revoking/released/retained过程。多个资源完整申请或统一排序try-acquire失败释放；禁止持部分无限等待。epoch仅来自真实执行层，未实现fencing留空并声明限制。

释放需owner仍匹配、停止/撤权证据及在途影响结清。未知资源retained；旧Agent不能释放新owner资源。锁过期并不替代资源侧拒绝或终止证明。
