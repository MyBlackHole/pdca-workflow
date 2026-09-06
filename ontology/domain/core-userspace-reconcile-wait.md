---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-reconcile-wait
type: domain
layer: Knowledge
status: active
summary: reconcile判空双计数 + 先唤醒 + 双模等待
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 重整工作判空、等待完成、终端与无人值守场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/commands/reconcile.rs 在仓库中存在且含 reconcile_status_to_text 定义"
- name: constraints
  desc: 等待判空前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认双源判空、先唤醒、模式默认差三条前提在引用代码中有对应实现"
---

# reconcile 等待与判空

沉淀自 T0503（20 轮第 2 轮）。对照 bcachefs
`src/commands/reconcile.rs`。

## 核心概念

1. **判空双计数**：读扫描待办加记账工作量，解类型分数据元数
   据，任一非零即有活（`reconcile_status_to_text`）。
2. **等前先唤醒**：先写触发文件唤醒内核，再进等待
   （`cmd_reconcile_wait`）。
3. **双模等待**：双终端进全屏，否則静默轮询；查与等默认集
   不同（`reconcile_wait_tui/headless`）。
4. **与既有节点边界**：编排节点管内核流水线，本节点管用户态
   等待展示。

## 复用指南

- 等待后台任务必须先唤醒再等，禁止静默等可能睡着的任务。
- 判空必须双源，单源必漏。
