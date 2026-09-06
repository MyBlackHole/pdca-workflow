---
schema: pdca.asset/v1
id: ontology:pattern/unified-relocation-engine
type: pattern
layer: Knowledge
status: active
summary: 单引擎加谓词注入统一搬迁模式
source_task: T0507
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:domain/core-reconcile-phased-orchestration
  - ontology:domain/core-copygc-fragment-selection
attributes:
  - name: applicability
    desc: 多搬迁策略共存（清运/疏散/均衡/修复）场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-move-unified-relocation-engine 存在
  - name: consequences
    desc: 策略扩展只加谓词、IO管线单一、调度契约纯函数
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
---

# 单引擎谓词注入统一搬迁

来源：T0507 提炼；源节点 `core-move-unified-relocation-engine`、
`core-reconcile-phased-orchestration`、`core-copygc-fragment-selection`；
对照 bcachefs `fs/data/move.c`。

## 问题

清运疏散均衡修复各一套 IO 管线，重复代码且语义漂移。

## 方案

一个搬迁引擎加多谓词：谓词只决策搬跳与目标，异步管线全共享；
调度契约收敛为单一纯函数；整单元搬迁优先；碎片排序选桶。

## 后果

新策略只加谓词；代价是引擎必须足够通用，谓词禁碰 IO 细节。
