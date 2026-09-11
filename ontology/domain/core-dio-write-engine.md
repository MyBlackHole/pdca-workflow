---
schema: pdca.asset/v2
id: ontology:domain/core-dio-write-engine
type: domain
layer: Knowledge
status: active
summary: DIO写iov暂存 + 预留快检 + FDM防死锁 + 双阶段结算
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-vfs-folio-reservation-writeback
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 直接 IO 绕页缓存写入、对齐裁剪、预留快检场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/vfs/direct.c 在仓库中存在且含 bch2_dio_write_copy_iov 定义
  evidence_level: unclassified
- name: constraints
  desc: 直通写入前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认对齐门槛、快检条件、死锁防护三条前提在引用代码中有对应实现
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

# DIO 写直通引擎

沉淀自 T0499（内核第十一轮）。对照 bcachefs
`fs/vfs/direct.c`、`fs/vfs/direct.h`、`fs/data/write.c`。

## 核心概念

1. **iov 暂存与同步降级**：免拷贝；非 iovec 强制转同步；小段
   内联免分配，否则分配拷贝；仅首轮尝试，失败转同步
   （`bch2_dio_write_copy_iov`）。
2. **块尾对齐裁剪**：入口要求整块对齐；每轮砍尾并回退迭代器，
   砍空报错（`bch2_dio_write_loop`）。
3. **预留失败快检复用**：预留失败才查 btree，覆盖写命中则忽略
   空间不足继续（`bch2_dio_write_check_allocated`）。
4. **扩展写强制同步**：超尾全程持锁且同步；非扩展首段即解锁，
   并发靠起止栅栏（`bch2_direct_write`）。
5. **dsync 末键提交**：每轮置刷盘标志，仅末键传闭包做事务刷盘；
   nocow 置 FUA，否则记待刷（`__bch2_write_index`）。
6. **FDM 防 fault 死锁**：每轮设清映射标记；fault 见标记回忙，
   更大则放锁重取；失效后空转继续
   （`fdm_set/clear`、`bch2_page_fault`）。
7. **异步 mm 保持与 bio 复用**：入口存 mm，续跑绑核重入；同步
   异步 bio 标志区分；完成按模式切换（`bch2_dio_write_continue`）。
8. **双阶段结算**：每轮记位置扩容配额放页；终局放块引用释内存
   关写引用，异步返排队码（`bch2_dio_write_end/done`）。
9. **入口 RO 拦截与零分配**：写引用失败返只读；内嵌 bio 零分配；
   DIO 靠提交原子性免快照锁（`bch2_direct_write`）。

## 复用指南

- 直通 IO 必须对齐门槛 + 预留快检 + 死锁防护三件套。
- 异步续跑必须保持 mm 并复用 bio，禁止重分配。
