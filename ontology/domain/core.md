---
schema: pdca.asset/v1
id: ontology:domain/core
type: domain
layer: Knowledge
status: active
summary: core 领域知识根节点（由 ontology/domain/core/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
---

# core（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `btree-node-rewrite-key-extent-contract` → `ontology:domain/core-btree-node-rewrite-key-extent-contract`
- `btree-random-op-consistency-proptest-pattern` → `ontology:domain/core-btree-random-op-consistency-proptest-pattern`
- `btree-split-proptest-enomem-restart-pattern` → `ontology:domain/core-btree-split-proptest-enomem-restart-pattern`
- `combined-op-domain-model` → `ontology:domain/core-combined-op-domain-model`
- `concurrent-combined-commit-log` → `ontology:domain/core-concurrent-combined-commit-log`
- `derived-state-validator-recovery-gate` → `ontology:domain/core-derived-state-validator-recovery-gate`
- `deterministic-interleave` → `ontology:domain/core-deterministic-interleave`
- `device-bucket-geometry-pointer-contract` → `ontology:domain/core-device-bucket-geometry-pointer-contract`
- `discard-boundary-guards` → `ontology:domain/core-discard-boundary-guards`
- `discard-worker-fifo-fairness` → `ontology:domain/core-discard-worker-fifo-fairness`
- `file-metadata-management-via-lmdb` → `ontology:domain/core-file-metadata-management-via-lmdb`
- `foreground-merge-mount-semantics` → `ontology:domain/core-foreground-merge-mount-semantics`
- `fsck-repair-fault-injection` → `ontology:domain/core-fsck-repair-fault-injection`
- `fsck-repair-mode` → `ontology:domain/core-fsck-repair-mode`
- `fsck-style-cli-healthcheck` → `ontology:domain/core-fsck-style-cli-healthcheck`
- `journal-key-layout-validation` → `ontology:domain/core-journal-key-layout-validation`
- `journal-reclaim-proptest-pattern` → `ontology:domain/core-journal-reclaim-proptest-pattern`
- `model-guard-decision-injection` → `ontology:domain/core-model-guard-decision-injection`
- `open-bucket-lifecycle-and-device-rw` → `ontology:domain/core-open-bucket-lifecycle-and-device-rw`
- `persistent-concurrency-crash-recovery` → `ontology:domain/core-persistent-concurrency-crash-recovery`
- `physical-pointer-derived-state-recovery-boundary` → `ontology:domain/core-physical-pointer-derived-state-recovery-boundary`
- `pointer-trigger-derived-chain` → `ontology:domain/core-pointer-trigger-derived-chain`
- `project-goal` → `ontology:domain/core-project-goal`
- `public-guard-assertions` → `ontology:domain/core-public-guard-assertions`
- `recovery-derived-state-publication-gate` → `ontology:domain/core-recovery-derived-state-publication-gate`
- `recovery-fault-matrix-public-validation` → `ontology:domain/core-recovery-fault-matrix-public-validation`
- `snapshot-table-lifecycle-filter-semantics` → `ontology:domain/core-snapshot-table-lifecycle-filter-semantics`
- `transactional-pointer-runner-publication` → `ontology:domain/core-transactional-pointer-runner-publication`
- `trigger-audit-derived-state-boundary` → `ontology:domain/core-trigger-audit-derived-state-boundary`
- `verify-all-aggregate-pattern` → `ontology:domain/core-verify-all-aggregate-pattern`
- `worker-verify-checkpoint-pattern` → `ontology:domain/core-worker-verify-checkpoint-pattern`
