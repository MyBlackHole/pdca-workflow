---
schema: pdca.asset/v1
id: ontology:domain/core-snapshot-study-guide
type: domain
layer: Knowledge
status: active
summary: 快照专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-snapshot-delete-execution
  - ontology:domain/core-snapshot-table-lifecycle-filter-semantics
  - ontology:domain/core-reflink-trigger-refcount-self-delete
  - ontology:domain/core-damage-ledger-inherit
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 快照机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 4 个快照相关节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# 快照专题学习指南

沉淀自 T0519（快照专题学习报告），来源
`records/T0519-0906-study-snapshot/`。对照 bcachefs
`fs/snapshots/`。

## 背景

快照知识分散在删除执行、表生命周期、reflink 共享、损伤账本
节点与 5800 行源码中，初学者无入口。本节点做导航聚合。

## 学习路径（三阶段）

1. **语义与判定**：先读 T0519 报告一二节，再读
   `core-snapshot-table-lifecycle-filter-semantics`（表语义），
   对照 snapshot.c 祖先判定。
2. **删除执行**：`core-snapshot-delete-execution`（索引下迁落盘），
   对照 delete.c 全流程；共享看 `core-reflink-trigger-refcount-
   self-delete`，损伤看 `core-damage-ledger-inherit`。执行细节见
   T0533 报告（主循环出入口状态机、v2 索引单跳迁移、下迁合并原子、
   四段落盘序、子卷收尾三步）。
3. **子卷与校验**：对照 subvolume.c 两阶段与 check_snapshots.c
   逆序校验。

## 九条启示速查

见 T0519 学习报告第九节：分支树语义、热路加速、判定分离、删读
耦合、索引快路、分阶段落盘、数据为准、两阶段删除，外加复活裁决。

## 复用指南

- 学快照先定语义（分支树），再看判定，最后看删除。
- 删除与校验对照读，删是剪枝，验是验树。
