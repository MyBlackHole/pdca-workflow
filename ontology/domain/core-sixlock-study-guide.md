---
schema: pdca.asset/v1
id: ontology:domain/core-sixlock-study-guide
type: domain
layer: Knowledge
status: active
summary: SIX锁专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:domain/core-six-slowpath-wakeup
  - ontology:domain/core-util-sync-primitives
  - ontology:pattern/intent-staged-update
  - ontology:pattern/seq-optimistic-relock
  - ontology:pattern/deadlock-detect-restart
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: SIX 锁机制系统学习、锁相关节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 6 个锁相关节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# SIX 锁专题学习指南

沉淀自 T0512（SIX 锁专题学习报告），来源
`records/T0512-0906-study-sixlock/`。对照 bcachefs
`fs/util/six.h` DOC。

## 背景

SIX 锁知识分散在 7 个本体节点（4 domain + 3 pattern）与源码 DOC
中，初学者无入口。本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **语义入门**：先读 `core-six-intent-seq-deadlock-free-locking`
   （三态语义）与 `pattern/intent-staged-update`（问题方案后果），
   再读 six.h 头 124 行 DOC。
2. **机制深挖**：`core-six-slowpath-wakeup`（慢路径唤醒）与
   `pattern/seq-optimistic-relock`、`pattern/deadlock-detect-restart`，
   对照 six.c 与 locking.c 实现。
3. **轻量对比**：`core-util-sync-primitives`（seqmutex/io 时钟），
   理解何时用重锁、何时用轻原语。

## 七条启示速查

见 T0512 学习报告第九节：错配量化、零分配快路、seq 版本化、
定向唤醒、原语策略分离、升级可失败、DOC 即文档。

## 复用指南

- 学新锁先问三态语义，再问升降级，最后问死锁策略。
- 读源码先读头文件 DOC，再跟实现，顺序不可反。
