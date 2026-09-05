---
schema: pdca.asset/v1
id: ontology:domain/core-damage-ledger-inherit
type: domain
layer: Knowledge
status: active
summary: Damage btree快照继承损伤账本与饱和合并
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-fsck-interactive-error-handling
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: inode粒度损伤记录、快照继承、跨链累积场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/init/damage.c 在仓库中存在且含 bch2_damage_accumulate 定义"
- name: constraints
  desc: 账本继承前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认同事务提交、有序归并、饱和合并三条前提在引用代码中有对应实现"
---

# Damage 快照继承账本

沉淀自 T0497（内核第九轮，二轮复核）。对照 bcachefs
`fs/init/damage.c`。

## 核心概念

1. **独立 btree 账本**：inode 粒度独立 btree，随修复同事务提交，
   按错误 id 排序，跨父链累积，饱和合并
   （`bch2_damage_record`、`bch2_damage_keys_merge`、
   `bch2_damage_accumulate`）。
2. **与既有节点边界**：超块错误计数是整盘计数，交互错误节点管
   删查操作，本节点管账本结构与继承语义。

## 复用指南

- 损伤记录必须独立账本随修复同事务，禁止散落日志。
- 快照继承必须沿父链累积，禁止只看当前快照。
