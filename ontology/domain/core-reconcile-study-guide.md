---
schema: pdca.asset/v1
id: ontology:domain/core-reconcile-study-guide
type: domain
layer: Knowledge
status: active
summary: reconcile编排专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-reconcile-phased-orchestration
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:domain/core-copygc-fragment-selection
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-userspace-reconcile-wait
  - ontology:pattern/unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: reconcile 编排机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 6 个编排节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# reconcile 编排专题学习指南

沉淀自 T0528（reconcile 编排专题学习报告），来源
`records/T0528-0906-study-reconcile/`。对照 bcachefs
`fs/data/reconcile/`。

## 背景

编排知识分散在 6 个本体节点与 work.c 中，初学者无入口。本节点做
导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **编排流水线**：先读 T0528 报告一至四节，再读
   `core-reconcile-phased-orchestration`（九阶段），对照 work.c。
2. **搬迁协同**：`core-move-unified-relocation-engine`（引擎）与
   `core-copygc-fragment-selection`（选桶）及
   `pattern/unified-relocation-engine`，理解驱搬关系。
3. **修复等待**：`core-ec-repair-evacuate-retry`（修复）与
   `core-userspace-reconcile-wait`（等待），对照 trigger 与命令。

## 八条启示速查

见 T0528 学习报告第七节：固定流水线、双沿打标、分型扫描、待定
闭环、有序扇出、硬约束路由、无丢失唤醒、边界串行。

## 复用指南

- 学编排先定阶段，再看扫描，最后看协同。
- 用户态等待与内核编排对照读，判空双源是关键。
