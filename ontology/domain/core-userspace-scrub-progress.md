---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-scrub-progress
type: domain
layer: Knowledge
status: active
summary: scrub按盘起任务 + 事件解析 + 原地重绘 + 位图退出码
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-observability-status-text-matrix
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 多盘 scrub 检查、进度展示、中断处理场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/commands/scrub.rs 在仓库中存在且含 read_data_event 定义"
- name: constraints
  desc: 进度展示前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认按盘起任务、定长解析、位图退出三条前提在引用代码中有对应实现"
---

# scrub 按盘进度展示

沉淀自 T0503（20 轮第 2 轮）。对照 bcachefs
`src/commands/scrub.rs`。

## 核心概念

1. **按盘起任务加元数据过滤**：元数据只扫 btree 盘，否则全盘；
   单盘直起，多盘遍历起（`start_scrub`）。
2. **定长事件手工解析**：屏蔽绑定结构体，读满定长取类型错码
   与进度，短读报错（`read_data_event`）。
3. **进度速率原地重绘**：跳过空事件，算速率更新四计数，终端
   原地覆写，秒轮询（`ScrubDev::format_line`）。
4. **退出码位图加离线态**：纠正未纠正中断各占位，离线显离线
   否则速率（`scrub`）。
5. **中断并行停核线程**：信号置位，主循环收尾并行关 fd 触发停
   机，防串行阻塞（`sigint_handler`）。

## 复用指南

- 多盘长任务必须按盘起任务加独立进度，禁止单总进度。
- 退出码必须位图语义，纠正未纠正中断各占一位。
