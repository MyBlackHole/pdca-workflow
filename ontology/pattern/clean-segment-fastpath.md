---
schema: pdca.asset/v1
id: ontology:pattern/clean-segment-fastpath
type: pattern
layer: Knowledge
status: active
summary: clean段加速加校验回退模式
source_task: T0506
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:domain/core-superblock-readback-validation
attributes:
  - name: applicability
    desc: 干净关闭加速挂载、加速结构可信校验场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-superblock-readback-validation 存在
  - name: consequences
    desc: 干净挂载秒开、校验失败全量回退、写入成本略增
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
---

# clean 段加速加校验回退

来源：T0506 提炼；源节点 `core-journal-seq-blacklist-pin-reclaim`、
`core-superblock-readback-validation`；对照 bcachefs
`fs/sb/clean.c`。

## 问题

每次挂载全量回放日志太慢；但加速结构不可信则 corrupt。

## 方案

干净关闭把树根用量时钟打包进 clean 段；下次比对序号与树根，
一致跳过回放，不一致丢弃强制走日志。

## 后果

干净挂载秒开；校验失败全量回退保证正确；代价是关机多写一段；
clean 段是纯加速，绝不能是唯一真相源。
