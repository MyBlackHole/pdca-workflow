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
---

# seq 乐观掉锁重拿

来源：T0505 提炼；源节点 `core-six-intent-seq-deadlock-free-locking`、
`core-btree-transaction-memory-io`、`core-util-sync-primitives`；
对照 bcachefs `fs/btree/locking.c`、`fs/util/six.h`、
`fs/util/seqmutex.h`。

## 问题

长事务持锁做 IO 阻塞并发；直接放锁重拿无法确认数据未变。

## 方案

锁内嵌 seq，取/放写时递增。掉锁前快照 seq，做 IO 后比对重拿：
相同视从未掉锁，不同则重走。SRCU 等读侧锁用预算切分长等，
超限先放再等。轻量场景用 seqmutex 混合原语。

## 后果

掉锁期间并发不阻塞；重拿失败需整路重走；seq 递增有少量成本；
快照比较必须与重拿原子配对，禁止先比后拿两步分开。
