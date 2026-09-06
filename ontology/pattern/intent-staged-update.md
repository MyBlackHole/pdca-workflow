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
---

# intent 分阶段多节点原子更新

来源：T0505 提炼；源节点 `core-six-intent-seq-deadlock-free-locking`、
`core-interior-gc-update-gate`、`core-btree-commit-batch-filter`；
对照 bcachefs `fs/util/six.h`、`fs/btree/interior.c`。

## 问题

树形多节点原子更新中，传统读写锁要么整路持写锁（并发塌陷），
要么读升写（必死锁）。

## 方案

引入 intent 第三态：与读兼容、与 intent/写互斥。先拿 intent 占位
锁定更新范围，读全程并发；逐节点短持写锁真改；最后指针切换处
升级并立即降级。split/merge 只记链表异步落盘，commit 段串行。

## 后果

读并发保留，Exclusive 持有缩至一瞬；代价是需 intent→write→read
精细流转与降级路径；父子逆序需先放父读锁配合。
