---
schema: pdca.asset/v2
id: ontology:domain/core-btree-gc-mark-sweep
type: domain
layer: Knowledge
status: active
summary: btree GC全序位点 + 单调水位 + 提交补标 + 拓扑journal
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-interior-gc-update-gate
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: btree全树一致性扫描、并发提交对账、拓扑修复场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/btree/check.c 在仓库中存在且含 bch2_gc_btrees 定义
  evidence_level: unclassified
- name: constraints
  desc: GC 扫描前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认位点单调、补标条件、修复先记日志三条前提在引用代码中有对应实现
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

# btree GC 全序位点标记清扫

沉淀自 T0493（内核第五轮；btree 无独立 gc.c，GC 即 check.c）。
对照 bcachefs `fs/btree/check.c`、`fs/btree/check.h`、
`fs/btree/commit.c`、`fs/btree/interior.c`。

## 核心概念

1. **全序 GC 位点**：phase>btree>level>pos 字典序，alloc/stripes
   最先；排序定遍历序，保证引用前向搬移不漏标
   （`gc_pos_btree`、`gc_pos_cmp`）。
2. **单调水位发布**：位点禁倒退（BUG_ON）；写序号锁发布，
   读无锁判已访问（`gc_pos_set`、`gc_visited`）。
3. **提交路径补标**：并发事务提交时对已访问更新补跑触发器，
   边走边对账不丢计数（`bch2_trans_commit_run_gc_triggers`）。
4. **自底向上遍历封口**：按靶深度逐键设位 + 进度 + 标记，尾部
   以超位封口；靶深度自适应（有触发器从叶起，fsck 强制从叶）
   （`bch2_gc_btree`）。
5. **逐键 mark 流水线**：换节点才验拓扑，再修版本/位图/key，
   有更新则预留提交重启，最后跑触发器重算
   （`bch2_gc_mark_key`）。
6. **拓扑重写走 journal**：节点 min/max 经指针升级 + 范围更新 +
   日志插入删除；修坏节点先驱逐删除；先提交修复日志再做一次
   性变异防重放（`commit_topology_repair_log`）。
7. **GC 持锁范围**：外层 state 读 + gc 写全程持有；入口排空异步
   父更新；插入侧断言持锁；尾部唤醒被阻塞分配
   （`bch2_check_allocations`）。
8. **分配器记账协同**：头部分段启动（超块/gc/预分配/记账/
   reflink），尾部逐槽比对 + 触发器重算，结束置位释放
   （`bch2_gc_start`、`bch2_gc_alloc_done`）；gens 独立通道可
   异步；GC 后合并节点与预切分片边界。

## 复用指南

- 全树扫描必须定义全序位点 + 单调发布，并发提交用补标对账。
- 拓扑修复必须先记日志再变异，禁止直接改指针。
- GC 与分配器的协同用分段启动/比对收尾，禁止边扫边改无账。
