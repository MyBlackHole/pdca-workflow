---
schema: pdca.asset/v2
id: ontology:domain/core-crypto-study-guide
type: domain
layer: Knowledge
status: active
summary: 压缩加密专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-compress-algorithm-heuristics
  - ontology:domain/core-compress-retry-verify
  - ontology:domain/core-checksum-negotiation-narrow
  - ontology:domain/core-userspace-key-rotate
  - ontology:domain/core-userspace-unlock-keyring-policy
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 压缩加密校验机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 5 个压缩加密节点 id 全部存在
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

# 压缩加密专题学习指南

沉淀自 T0521（压缩加密专题学习报告），来源
`records/T0521-0906-study-crypto/`。对照 bcachefs
`fs/data/compress.c`、`checksum.c`。

## 背景

压缩加密知识分散在 5 个本体节点与两文件源码中，初学者无入口。
本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **压缩两面**：先读 T0521 报告二三节，再读
   `core-compress-algorithm-heuristics`（选型建池）与
   `core-compress-retry-verify`（重试验证），对照 compress.c。
2. **校验协商**：`core-checksum-negotiation-narrow`（强度合并），
   对照 checksum.c；先验后解看读路径。
3. **密钥管理**：`core-userspace-key-rotate`（轮换）与
   `core-userspace-unlock-keyring-policy`（解锁），对照 key.rs；
   nonce 步进看 checksum.c。

## 八条启示速查

见 T0521 学习报告第八节：顺序固定、启发选型、重试收敛、强度分级、
优先级不掩盖、步进生命线、少中转、类型清零。

## 复用指南

- 学压缩加密先定分层顺序，再逐层深入，最后看密钥。
- 安全不变量（顺序/步进/清零）背下来，性能可调安全不可调。

详见 T0536 代码级精讲扩充版报告（逐函数签名参数返回调用链）。
