---
schema: pdca.asset/v2
id: ontology:domain/core-allocator-wfq-watermark-reservation
type: domain
layer: Knowledge
status: active
summary: WFQ 条纹选盘 + 七档水位 + 双层预留的分配器防饿死与防死锁
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-open-bucket-lifecycle-and-device-rw
  - ontology:domain/core-discard-boundary-guards
  - ontology:domain/core-device-bucket-geometry-pointer-contract
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 多设备条带化分配、后台清运与前台分配共存、高并发预留场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/alloc/foreground.c 与 fs/alloc/types.h 在仓库中存在且含 BCH_WATERMARKS 定义
  evidence_level: unclassified
- name: constraints
  desc: 三机制的启用前提与代价
  constraint: 见正文
  testable_signal: 通读正文约束节，确认虚拟时间同步、水位 bail 条件、预留作废三条前提在引用代码中有对应实现
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

# WFQ 选盘 + 七档水位 + 双层预留

沉淀自 T0488（confirmed），来源
`records/T0488-0905-bcachefs-strengths/`。对照 bcachefs
`fs/alloc/foreground.c`、`fs/alloc/types.h`、`fs/alloc/buckets.c`。

## 核心概念

1. **WFQ 条纹选盘防饿死**：`dev_stripe_state.next_alloc` 虚拟时间，
   最小者胜出、步长 `1/free_space` 实现按空闲比例加权；新盘加入
   时抬到旧盘最小值而非 0，避免新盘独占；rescale 防 u64 溢出
   （`foreground.c:dev_stripe_state_sync`）。排序先比故障域再比
   虚拟时间，EC 时同域盘变硬约束剔除（`__dev_alloc_list`）。
2. **七档水位防清运死锁**：stripe/normal/copygc/btree 等七档；
   无桶时唤醒 copygc 并挂 freelist_wait；水位为 copygc 时非 btree
   直接欠复制提交，避免"清运者等自己"（`req_alloc_should_bail`）；
   耗尽开桶反压 journal（`bch2_journal_set_watermark`）。
3. **预留双层记账防超卖**：per-cpu 无锁快扣，不足批量补充；
   缩容时 capacity_gen 作废旧预留（`buckets.c:
   __bch2_disk_reservation_add`）。

配套：`struct bucket` 借首字节跑 bit_spin_lock 省内存
（`buckets_types.h:26-45`）；空/非空双 seq + noflush 快丢
（`background.c:bch2_trigger_alloc`）。

## 复用指南

- 多盘分配：虚拟时间加权 + 新成员抬升缺一不可，否则新盘饿死
  旧盘或反之。
- 后台清运与前台分配的水位必须是同一标尺，否则互相等待。
- 预留必须有代际作废机制，拓扑变更后旧预留即毒药。
- 与 `core-open-bucket-lifecycle-and-device-rw`（开桶生命期）、
  `core-discard-boundary-guards`（discard 边界）互补。
