---
schema: pdca.asset/v2
id: ontology:domain/core-six-intent-seq-deadlock-free-locking
type: domain
layer: Knowledge
status: active
summary: SIX三态锁 intent 占位 + seq 乐观重锁 + 等待图环检测的无死锁并发
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-persistent-concurrency-crash-recovery
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 读多写少、多节点原子更新、需掉锁做 IO 的树形结构并发场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/btree/locking.c 与 fs/util/six.h 在仓库中存在且含 SIX_LOCK_intent 定义
  evidence_level: unclassified
- name: constraints
  desc: 三机制的启用前提与代价
  constraint: 见正文
  testable_signal: 通读正文约束节，逐条确认前提（事务幂等可重启、seq 递增语义、等待图仅阻塞时运行）在引用代码中有对应实现
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

# SIX intent + seq 乐观重锁 + 环检测的无死锁并发

沉淀自 T0488（bcachefs 内核巧思分析，confirmed），来源
`records/T0488-0905-bcachefs-strengths/`。对照 bcachefs
`fs/util/six.h`、`fs/btree/locking.c`。

## 核心概念

传统读写锁在"读升写"与"多节点原子更新"下必死锁或并发塌陷。
bcachefs 用三机制组合解决：

1. **intent 第三态占位**：与 Shared 兼容、与 Intent/Exclusive 互斥。
   split 需长期持有父节点排斥权但真改内存仅一瞬——读可在 split
   全程并发，仅最终指针更新才升 Exclusive（`locking.c:31-37`）。
   先拿 intent 占位、逐节点短持 write 真改（`six.h:9-135`）。
2. **seq 乐观重锁**：锁内嵌 seq，取/放 Exclusive 递增；事务可大胆
   丢锁做 IO，事后比对 seq 即可重锁，免整路重走（`locking.c:66-73`、
   `iter.c:120`；`six.h:48` relock 语义）。
3. **等待图环检测 + 幂等重启**：睡眠前走事务等待图，成环则选一
   事务全放锁重启；仅阻塞时运行，不污染快路径
   （`locking.c:77-98`、`bch2_six_check_for_deadlock`）。

配套细节：取子 Intent 前先放父读锁破父子逆序（`locking.c:59-62`）；
死锁检测前比对 hash_val 防复用幻影节点（`locking.c:636-660`）。

## 复用指南

- 树形多节点更新：intent 占位 + 短 write 真改 + downgrade 回读。
- 需掉锁做 IO 的事务：seq 快照 → 掉锁 → relock(seq) 验证。
- 环检测的前提是事务层全幂等可重启，否则重启即 corrupt。
- 与 `core-persistent-concurrency-crash-recovery` 互补：本节点讲
  锁机制免死锁，那个节点讲崩溃注入验证方法论。
