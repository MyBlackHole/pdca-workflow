---
schema: pdca.asset/v2
id: ontology:domain/core-userspace-study-guide
type: domain
layer: Knowledge
status: active
summary: 用户态运维专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-userspace-mount-flow
  - ontology:domain/core-userspace-device-scan
  - ontology:domain/core-userspace-wait-multipath
  - ontology:domain/core-userspace-fsck-routing
  - ontology:domain/core-userspace-scrub-progress
  - ontology:domain/core-userspace-reconcile-wait
  - ontology:domain/core-userspace-usage-matrix
  - ontology:domain/core-userspace-device-manage
  - ontology:domain/core-userspace-key-rotate
  - ontology:domain/core-userspace-unlock-keyring-policy
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 用户态运维机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 10 个用户态节点 id 全部存在
  evidence_level: unclassified
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: 通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 用户态运维专题学习指南

沉淀自 T0520（用户态运维专题学习报告），来源
`records/T0520-0906-study-userspace/`。对照 bcachefs `src/`。
基于现树旧形态（v1.39.3 重构未合入）。

## 背景

用户态知识分散在 10 个本体节点与 src/ 命令树中，初学者无入口。
本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **挂载扫描**：先读 T0520 报告二三节，再读
   `core-userspace-mount-flow`（流程）、`core-userspace-device-scan`
   （扫描）、`core-userspace-wait-multipath`（等盘），对照
   mount.rs 与 device_scan.rs。
2. **恢复运维**：`core-userspace-fsck-routing`（检查）、
   `core-userspace-scrub-progress`（ scrub）、
   `core-userspace-reconcile-wait`（重整）、
   `core-userspace-usage-matrix`（用量），对照 commands 下四文件。
3. **设备密钥**：`core-userspace-device-manage`（增删改）、
   `core-userspace-key-rotate`（轮换）、
   `core-userspace-unlock-keyring-policy`（解锁），对照 device.rs
   与 key.rs。

## 九条启示速查

见 T0520 学习报告第九节：决策路由、失败自救、快扫回落、事件等盘、
在线优先、双路径、分档强制、哨兵验证、透传保真。

## 复用指南

- 学用户态先分五线，再逐线深入，最后看错误透传。
- 现树旧形态结论需标注版本，重构合入后复核。
