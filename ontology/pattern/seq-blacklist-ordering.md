---
schema: pdca.asset/v1
id: ontology:pattern/seq-blacklist-ordering
type: pattern
layer: Knowledge
status: active
summary: seq黑名单保序重放模式
source_task: T0506
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:domain/core-journal-pin-lifetime-flush
attributes:
  - name: applicability
    desc: 日志结构存储崩溃恢复保序场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-journal-seq-blacklist-pin-reclaim 存在
  - name: consequences
    desc: 乱序永不发生、黑名单持久化成本、seq永不复用
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
---

# seq 黑名单保序重放

来源：T0506 提炼；源节点 `core-journal-seq-blacklist-pin-reclaim`、
`core-journal-pin-lifetime-flush`；对照 bcachefs
`fs/journal/seq_blacklist.c`。

## 问题

crash 后部分数据先于其日志落盘，直接重放会乱序；且同一 seq absolute
不能二次使用，否则新旧难分。

## 方案

每条落盘数据记 seq；启动时新于最新日志则丢弃，且该 seq 永不复用并
持久化；脏引用用 pin 钉住阻止推进；区间合并加二分查询。

## 后果

乱序永不发生；代价是黑名单持久化与 seq 空间消耗；seq 单调是硬前提。
