---
schema: pdca.asset/v1
id: ontology:domain/core-recovery-study-guide
type: domain
layer: Knowledge
status: active
summary: recovery全流程专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-fsck-autofix-graded-self-healing
  - ontology:domain/core-fsck-interactive-error-handling
  - ontology:domain/core-damage-ledger-inherit
  - ontology:domain/core-sb-error-persistence-display
  - ontology:domain/core-recovery-fault-matrix-public-validation
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: recovery 机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 5 个恢复节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# recovery 全流程专题学习指南

沉淀自 T0526（recovery 全流程专题学习报告），来源
`records/T0526-0906-study-recovery/`。对照 bcachefs `fs/init/`。

## 背景

恢复知识分散在 5 个本体节点与 init 源码中，初学者无入口。本节点做
导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **编排调度**：先读 T0526 报告一至四节，再读
   `core-fsck-autofix-graded-self-healing`（分级调度），对照
   passes.c 编排。
2. **错误损伤**：`core-sb-error-persistence-display`（持久计数）与
   `core-damage-ledger-inherit`（账本），对照 errors.c 与 damage.c。
3. **交互验证**：`core-fsck-interactive-error-handling`（提问降级）与
   `core-recovery-fault-matrix-public-validation`（矩阵），对照
   error.c。

## 八条启示速查

见 T0526 学习报告第八节：编排收敛、编号隔离、延迟闭包、去重自证、
持久限流、分级调度、账本同事务、提问解锁。

## 复用指南

- 学恢复先定编排，再看分级，最后看交互。
- 限流与账本是易漏点，单拎出来先学。
