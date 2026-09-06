---
schema: pdca.asset/v1
id: ontology:pattern/weighted-fair-allocation
type: pattern
layer: Knowledge
status: active
summary: 虚拟时间加权公平分配模式
source_task: T0507
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:domain/core-lru-bitmap-selfheal
attributes:
  - name: applicability
    desc: 多资源按容量加权分配、新成员加入场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-allocator-wfq-watermark-reservation 存在
  - name: consequences
    desc: 按需分配无饿死、新成员不独占、需虚拟时间同步
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
---

# 虚拟时间加权公平分配

来源：T0507 提炼；源节点 `core-allocator-wfq-watermark-reservation`、
`core-lru-bitmap-selfheal`；对照 bcachefs `fs/alloc/foreground.c`。

## 问题

多盘按空闲分配时，简单轮询饿死小盘，贪心最空盘饿死大盘；新盘加入
瞬间独占分配。

## 方案

每资源虚拟时间，最小者胜出、步长按空闲加权；新成员抬到旧成员最小
值而非零；计数溢出重缩放；水位分级保后台任务。

## 后果

按需分配无饿死；代价是虚拟时间需同步维护，新成员抬升策略必须显式。
