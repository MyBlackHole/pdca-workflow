---
schema: pdca.asset/v1
id: ontology:domain/core-btree-transaction-memory-io
type: domain
layer: Knowledge
status: active
summary: btree事务 bump 分配 + 队列化写 + SRCU 短等待预算
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 事务内存管理、持锁 IO 调度、长等待防卡回收场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/btree/iter.h 在仓库中存在且含 bch2_trans_kmalloc_ip 定义"
- name: constraints
  desc: 机制启用前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认重启作废语义、队列冲刷点、预算阈值三条前提在引用代码中有对应实现"
---

# btree事务 bump 分配 + 队列化写 + SRCU 预算

沉淀自 T0491（内核遗漏扫描）。对照 bcachefs `fs/btree/iter.h`、
`fs/btree/iter.c`、`fs/btree/write.c`、`fs/btree/locking.c`、
`fs/btree/update.h`。

## 核心概念

1. **bump 分配 + 重启作废**：`mem/mem_top` 重启即 `mem_top=0`
   作废；`roundup8` 快道 + 按 2 幂扩容；超 64K 转 mempool 并以
   `restart_mem_realloced` 重启。修复循环用 lazy commit 到 1/4
   即中途提交防 ENOMEM（`bch2_trans_kmalloc_ip`、
   `bch2_trans_commit_lazy_if_full`）。
2. **持锁零块层 IO**：`__bch2_btree_node_write` 只组 bio 挂链表，
   解锁或等 IO 前集中下发；读前先冲刷本事务队列防读旧数据
   （`bch2_trans_submit_write_bios`）。
3. **SRCU 短等待预算**：trans 持 SRCU 读锁保节点内存，等待以
   HZ 为限切分，超限先放 SRCU 再长等；慢盘告警阈值按在线设备
   最大读延迟动态放缩（`bch2_trans_short_wait_budget`）。
4. **持锁期 NOIO + 绑核**：`trans_set_locked` 置 NOIO 防递归回收、
   migrate_disable 稳 per-CPU 游标，解锁还原；食人锁单任务串行
   拆借，unlock 即释放。

## 复用指南

- 事务内存用 bump 分配 + 重启作废，禁止事务内 free 链表。
- 持锁期间禁止直接下发块层 IO，一律队列化到解锁点。
- 长等待必须先放读侧锁（SRCU/RCU），预算切分而非无限等。
