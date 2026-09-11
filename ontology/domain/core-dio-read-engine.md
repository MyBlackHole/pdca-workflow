---
schema: pdca.asset/v2
id: ontology:domain/core-dio-read-engine
type: domain
layer: Knowledge
status: active
summary: DIO读对齐截断 + 分片闭包 + 脏旗防回挂
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-dio-write-engine
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 直接 IO 绕页缓存读取、对齐整形、分片下发场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/vfs/direct.c 在仓库中存在且含 __bch2_direct_IO_read 定义
  evidence_level: unclassified
- name: constraints
  desc: 直通读取前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认对齐门槛、尾部归还、防回挂三条前提在引用代码中有对应实现
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

# DIO 读直通引擎

沉淀自 T0500（内核第十二轮）。对照 bcachefs `fs/vfs/direct.c`、
`fs/vfs/direct.h`。

## 核心概念

1. **对齐截断与回补**：入口要求整块对齐；尾部非整块暂扣，末尾
   归还（`__bch2_direct_IO_read`）。
2. **分片闭包**：首 bio 内嵌，超限循环拆分，计数器同步；同步
   等待，异步经完成回调（`bch2_direct_IO_read_endio`）。
3. **脏旗防回挂**：用户回写迭代器置脏防 loop 回挂死锁
   （`should_dirty`）。
4. **与既有节点边界**：写引擎节点管写入，本节点管读取；直接
   读裁剪是其子集特写。

## 复用指南

- 直通读必须对齐整形 + 尾部归还，禁止静默截断。
- 分片必须计数器同步，异步经完成回调。
