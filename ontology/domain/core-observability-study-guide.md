---
schema: pdca.asset/v1
id: ontology:domain/core-observability-study-guide
type: domain
layer: Knowledge
status: active
summary: 可观测体系专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-observability-status-text-matrix
  - ontology:domain/core-time-stats-cheap-instrumentation
  - ontology:domain/core-sb-persistent-counters
  - ontology:domain/core-chardev-control-plane
  - ontology:principle/observability-first
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 可观测机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 5 个可观测节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# 可观测体系专题学习指南

沉淀自 T0522（可观测体系专题学习报告），来源
`records/T0522-0906-study-observability/`。对照 bcachefs
`fs/debug/`、`fs/util/time_stats.c`。

## 背景

可观测知识分散在 5 个本体节点与 debug 源码中，初学者无入口。
本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **自白展示**：先读 T0522 报告二三节，再读
   `core-observability-status-text-matrix`（矩阵通道），对照
   sysfs.c；原则看 `principle/observability-first`。
2. **性能埋点**：`core-time-stats-cheap-instrumentation`（分级埋点）
   与 `core-sb-persistent-counters`（持久计数），对照
   time_stats.c 与 counters.c。
3. **取证交互**：`core-chardev-control-plane`（控制分发），对照
   chardev.c；围栏取证看 enumerated_ref 与 trans 全景。

## 九条启示速查

见 T0522 学习报告第九节：黑盒是缺陷、自白全员、展示解耦、分级
埋点、双视角、同源事件、命名围栏、取证无锁、计数隔离。

## 复用指南

- 学可观测先定约束（黑盒是缺陷），再看展示，最后看埋点。
- 每个机制问一句：挂死时还能用吗？
