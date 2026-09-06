---
schema: pdca.asset/v1
id: ontology:domain/core-journal-study-guide
type: domain
layer: Knowledge
status: active
summary: journal崩溃恢复专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:domain/core-journal-space-topk-ram
  - ontology:domain/core-journal-write-assembly
  - ontology:domain/core-journal-pin-lifetime-flush
  - ontology:domain/core-journal-watermark-thread
  - ontology:domain/core-journal-lifecycle-flush
  - ontology:domain/core-journal-entry-selfheal-validate
  - ontology:pattern/seq-blacklist-ordering
  - ontology:pattern/watermark-staged-reclaim
  - ontology:pattern/clean-segment-fastpath
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: journal 机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 10 个 journal 相关节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# journal 崩溃恢复专题学习指南

沉淀自 T0515（journal 专题学习报告），来源
`records/T0515-0906-study-journal/`。对照 bcachefs `fs/journal/`。

## 背景

journal 知识分散在 10 个本体节点（7 domain + 3 pattern）与 9200 行
源码中，初学者无入口。本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **写入语义**：先读 `core-journal-write-assembly`（组装）与
   `core-journal-entry-selfheal-validate`（自愈），再读 write.c
   组装校验段。
2. **空间回收**：`core-journal-space-topk-ram`（记账）、
   `core-journal-watermark-thread`（水位机）、
   `core-journal-pin-lifetime-flush`（钉住），对照 reclaim.c；
   pattern 侧读 `watermark-staged-reclaim`。
3. **崩溃恢复**：`core-journal-seq-blacklist-pin-reclaim`（保序）、
   `core-journal-lifecycle-flush`（生命周期），对照 read.c 三区；
   pattern 侧读 `seq-blacklist-ordering`、`clean-segment-fastpath`。

## 七条启示速查

见 T0515 学习报告第八节：三矛盾建模、分段语义、非对称钳制、
就地回收、显式 pin、三区定界、状态机单调。

## 复用指南

- 学 journal 先分清写入/空间/恢复三矛盾，再逐个深入。
- 读源码先看 types.h 中枢结构，再跟三条主线。
