---
schema: pdca.asset/v1
id: ontology:pattern/seq-optimistic-relock
type: pattern
layer: Knowledge
status: active
summary: seq版本号乐观掉锁重拿模式
source_task: T0505
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:domain/core-btree-transaction-memory-io
  - ontology:domain/core-util-sync-primitives
attributes:
  - name: applicability
    desc: 需掉锁做 IO 再重拿、长持锁转短持锁场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-btree-transaction-memory-io 存在
  - name: consequences
    desc: 掉锁期间并发不阻塞、重拿失败需重走、seq 递增有成本
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  - name: violations
    desc: 不用本模式的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# seq 乐观掉锁重拿

来源：T0505 提炼，T0508 扩充；源节点
`core-six-intent-seq-deadlock-free-locking`、
`core-btree-transaction-memory-io`、`core-util-sync-primitives`；
对照 bcachefs `fs/btree/locking.c`、`fs/util/six.h`、
`fs/util/seqmutex.h`。

## 问题

长事务持锁做 IO 阻塞并发；直接放锁重拿无法确认数据未变；
SRCU 等读侧锁长阻塞拖住回收。

## 方案

1. **锁内嵌 seq**：取放写时递增；掉锁前快照，IO 后比对重拿，
   相同视从未掉锁，不同整路重走（`locking.c:66-73`）。
2. **SRCU 预算切分**：等待以 tick 为限切分，超限先放读侧锁再
   长等；慢盘告警阈值按在线设备最大延迟动态放缩
   （`bch2_trans_short_wait_budget`）。
3. **轻量 seqmutex**：mutex 加 seq 混合，lock 递增，relock 双检
   加 trylock 防 ABA（`seqmutex.h:19-43`）。
4. **持锁期绑核免换页**：置免换页内存标志防递归回收，绑核稳
   per-CPU 游标，解锁还原（`trans_set_locked`）。

## 后果

掉锁期间并发不阻塞；重拿失败需整路重走；seq 递增有少量成本；
快照比较必须与重拿原子配对，禁止先比后拿两步分开。

## 违反后果

- 长持锁做 IO：并发全堵，慢盘一次抖动拖死整树。
- 放锁不验证：数据已被改，重拿即静默 corrupt。
- 读侧锁无限等：回收停滞，内存耗尽。
