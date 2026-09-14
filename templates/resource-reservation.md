---
schema: pdca.resource-reservation/v4
protocol_revision: 4.0.0-rc.2
reservation_id: null
owner_task_id: null
owner_attempt: null
run_id: null
ledger_writer_ref: null
authorization_ref: null
state: requested
guarantee_profile: null
resource_set: []
canonicalization_evidence_refs: []
backend_acquire_ref: null
ownership_epoch: null
operation_refs: []
revocation_ref: null
settlement_ref: null
retained_scope: null
release_conditions: []
---

# 集中资源预约

保存到PDCA_ROOT/records/resources/<reservation_id>.md；各项目共用冲突范围，task中仅保存引用。resource_set逐项列backend/namespace/canonical_object_id/scope/access，记录真实对象规范化依据。

requested、held、revoking、released、retained只记录事实。held需要实际取得回执，不因填表产生锁；epoch只有后端真实支持才填。停止、过期或归档不直接released。retained记录未决影响、隔离范围与后继可用条件。

单一账本写者是元数据/资源职责，不负责替任务推进阶段；不能由父Agent轮询监工替代。读取其他任务仅限必要冲突元数据，不读取完整上下文。
