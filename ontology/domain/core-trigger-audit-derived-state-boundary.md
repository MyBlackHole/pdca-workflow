---
schema: pdca.asset/v1
id: ontology:domain/core-trigger-audit-derived-state-boundary
type: domain
layer: Knowledge
status: active
summary: Trigger 审计的派生状态边界
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 trigger-audit-derived-state-boundary 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# Trigger 审计的派生状态边界

审计 bcachefs 风格的 transaction trigger 时，不能只按公开 API 产生的 key type
判断是否适用。必须从写入源扩展到同一 transaction 内派生的状态：

`extent / btree pointer -> alloc -> backpointer / stripe-backpointer -> accounting /
reconcile -> journal / recovery / GC`。

内部 btree pointer 也属于触发审计范围：本地 bcachefs 把 `BKEY_TYPE_btree` 列为
transactional trigger node type，且 btree pointer key-op 使用 extent trigger。
backpointer 通常是 extent/btree-pointer trigger 写入的派生目标，而不是可独立忽略的
叶子 key。

若独立 Rust 引擎尚未具备 GC visited 模型，GC trigger 必须在依赖图中明确标为前置
条件，不可孤立移植。仅当每一条边的上游语义、当前生产路径和恢复边界均得到证明后，
才能拆分最小实现任务。

来源：T0179 partial，`records/T0179-0802-trigger-chain-applicability-audit/conclusion.md`。
