---
schema: pdca.asset/v1
id: ontology:pattern/intent-staged-update
type: pattern
layer: Knowledge
status: active
summary: intent占位分阶段多节点原子更新模式
source_task: T0505
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:domain/core-interior-gc-update-gate
  - ontology:domain/core-btree-commit-batch-filter
attributes:
  - name: applicability
    desc: 树形多节点原子更新、读升写频繁场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-six-intent-seq-deadlock-free-locking 存在
  - name: consequences
    desc: 读并发保留、Exclusive持有缩至一瞬、需降级路径
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  - name: violations
    desc: 不用本模式的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# intent 分阶段多节点原子更新

来源：T0505 提炼，T0508 扩充；源节点
`core-six-intent-seq-deadlock-free-locking`、
`core-interior-gc-update-gate`、`core-btree-commit-batch-filter`；
对照 bcachefs `fs/util/six.h`、`fs/btree/interior.c`、
`fs/btree/locking.c`。

## 问题

树形多节点原子更新中，传统读写锁要么整路持写锁（并发塌陷），
要么读升写（必死锁）。split 操作需长期持有父节点排斥权，但真正
改内存只有指针切换一瞬——排斥权与修改时长严重不匹配。

## 方案

1. **引入 intent 第三态**：与 Shared 兼容、与 Intent/Exclusive
   互斥。先拿 intent 占位锁定更新范围，读全程并发；逐节点短持
   写锁真改；最后指针切换处升级并立即降级
   （`six.h:SIX_LOCK_intent`、`locking.c:31-37`）。
2. **改降级精细流转**：downgrade 为加读加解 intent，tryupgrade
   原子检查后转换，同型直接成功（`six.c:six_lock_downgrade`、
   `six_lock_tryupgrade`）。
3. **异步落盘解耦**：split/merge 只记链表挂未写队列，由 worker
   刷盘；commit 段持专用锁串行（`interior.c:1016-1042`）。
4. **父子逆序破除**：取子 Intent 前先放父读锁加事后校验，打破
   持有等待（`locking.c:59-62`）。
5. **提交段合并**：写锁段内同叶更新去重加锁并预检容量，防他线程
   改空间（`commit.c:bch2_trans_commit_write_locked`）。

## 后果

读并发保留，Exclusive 持有缩至一瞬；代价是需 intent→write→read
精细流转与降级路径；异步落盘需 commit 锁串行保证顺序。

## 违反后果

- 整路持写锁：读全堵，split 期间整树不可读，并发塌陷。
- 读升写：与持读等写的线程必死锁，无自愈只能重启。
- 无降级路径：指针切换后长期持写锁，效果等同整路持写。
