---
schema: pdca.asset/v2
id: ontology:domain/core-inode-acl-opts-shortcircuit
type: domain
layer: Knowledge
status: active
summary: ACL负缓存快路 + opts零值短路 + pack唯一维护
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-vfs-namespace-operations
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: ACL 查询快路、inode 选项热路径短路、标志一致性场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/fs/acl.c 在仓库中存在且含 bch2_get_acl 定义
  evidence_level: unclassified
- name: constraints
  desc: 短路前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认负缓存写入、零值信任、双向校验三条前提在引用代码中有对应实现
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

# ACL 负缓存与 opts 短路

沉淀自 T0498（内核第十轮）。对照 bcachefs `fs/fs/acl.c`、
`fs/fs/inode.c`、`fs/fs/check.c`、`fs/data/write.c`。

## 核心概念

1. **无 ACL 跳过并喂负缓存**：标志未置位直接返空并写 VFS 负
   缓存，不查 btree；查无同样写负缓存（`bch2_get_acl`）。
2. **opts 零值短路**：热路径先读标志，零则取 fs 默认，否则才
   解包；版本升级已跑完故可信任
   （`bch2_extent_update_i_size_sectors`）。
3. **pack 唯一维护**：每遍重算标志，先清后置；创建与改 ACL
   处同步维护（`bch2_inode_pack_inlined`）。
4. **fsck 双向校验**：置位方向验重算一致与 xattr 存在；清位
   方向验 xattr 存在则置位；前者是打破短路的危险方向
   （`check_inode`、`check_xattr`）。

## 复用指南

- 否定性查询必须写负缓存，禁止每次穿透。
- 热路径短路标志必须由 pack 唯一维护 + fsck 双向校验。
