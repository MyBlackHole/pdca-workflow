---
schema: pdca.asset/v1
id: ontology:pattern/graded-selfhealing-schedule
type: pattern
layer: Knowledge
status: active
summary: 错误分级加精准调度加持久限流自愈模式
source_task: T0507
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-fsck-autofix-graded-self-healing
  - ontology:domain/core-fsck-interactive-error-handling
  - ontology:domain/core-damage-ledger-inherit
attributes:
  - name: applicability
    desc: 一致性错误分级修复、昂贵修复限流场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-fsck-autofix-graded-self-healing 存在
  - name: consequences
    desc: 轻错自愈重错上报、修复精准、昂贵限流
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
---

# 分级自愈调度

来源：T0507 提炼；源节点 `core-fsck-autofix-graded-self-healing`、
`core-fsck-interactive-error-handling`、`core-damage-ledger-inherit`；
对照 bcachefs `fs/sb/errors_format.h`、`fs/init/passes.c`。

## 问题

一致性错误要么全人工（运维累死），要么全自动（误修丢数据）。

## 方案

错误声明式分级表；按损坏定位掩码精准调度对应修复；昂贵修复持久化
限流；损伤独立账本随修复提交；交互提问先解锁加超时。

## 后果

轻错自愈重错上报；代价是分级表必须声明式维护，限流状态必须持久化。
