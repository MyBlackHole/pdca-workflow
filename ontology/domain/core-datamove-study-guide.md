---
schema: pdca.asset/v1
id: ontology:domain/core-datamove-study-guide
type: domain
layer: Knowledge
status: active
summary: 数据搬迁专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:domain/core-copygc-fragment-selection
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-reconcile-phased-orchestration
  - ontology:domain/core-device-membership-lifecycle
  - ontology:pattern/unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 数据搬迁机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 6 个搬迁节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# 数据搬迁专题学习指南

沉淀自 T0530（数据搬迁专题学习报告），来源
`records/T0530-0906-study-datamove/`。对照 bcachefs
`fs/data/move.c`、`copygc.c`。

## 背景

搬迁知识分散在 6 个本体节点与 move 源码中，初学者无入口。本节点做
导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **引擎选桶**：先读 T0530 报告二三节，再读
   `core-move-unified-relocation-engine`（引擎）与
   `core-copygc-fragment-selection`（选桶），对照 move.c。
2. **疏散修复**：`core-device-membership-lifecycle`（移除流水线）与
   `core-ec-repair-evacuate-retry`（疏散重试），理解驱搬关系。
3. **编排协同**：`core-reconcile-phased-orchestration`（编排）与
   `pattern/unified-relocation-engine`，看边界串行化。

## 七条启示速查

见 T0530 学习报告第七节：再平衡定位、策略解耦、排序选桶、自留预留、
两跳疏散、整体搬迁、判据纯函数。

## 复用指南

- 学搬迁先定服务方（清运疏散均衡修复），再看引擎，最后看协同。
- 判据纯函数是防互等的关键，单拎出来先学。

详见 T0537 代码级精讲扩充版报告（逐函数签名参数返回调用链）。
