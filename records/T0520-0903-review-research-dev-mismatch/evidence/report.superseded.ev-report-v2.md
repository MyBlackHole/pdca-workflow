# 双轴审查报告 — T0520 调研任务拆出开发子任务断层

> 固定点：`bcb5ff17` 单commit混 `T0501/T0502/T0503(research)` 与 `T0505-0512(development)` 14任务 `git diff b717ac94..bcb5ff17 --name-only`

## Standards（编码标准轴，≤400字）

**违反：**

- `ontology:principle/ontology-governs-ontology.md:1` `ontology_governs_creation: 调研产生本体前必须基于 research-topdown 且受 creation-gate 6规则约束` — `T0503` `research` 未生 `research` 叶即跳至 `T0506-0511` `development`，违“本体控产生” `ontology_gate.py:30` 硬应 `fragment` 且 `research→本体→development` 双层。

- `ontology/domain/ontology-hybrid-methodology.md:32` `Research Topdown: 根→叶 100%落盘` — `WBS 100% Rule` 父=子之和，`T0503` `composed_of 6叶` 未在 `research` 层落 `6 research` 叶即由 `development` 层落，缺 `research` 层 100% `ontology_graph:389/981/0` 虽 `islands:0` 但 `T0503` 无 `research` 子层。

- `ontology/pattern/ontology-modular-reference.md:21` 叶三准绳 — 叶需可独立验证，本次 `development` 叶 `testable_signal` 复用 `research` 叶应产的 `attributes`，`skill-tdd.md:1` `0 attrs` 错置即信号。

**未违反**：`type==目录名`、`islands:0`、`scaffold` 可产均 `validate OK`。

## Spec（规范轴，≤400字）

**PRD `T0503-0903-research-zfs-implementation/prd.md:7` 拆分映射**：

```
- zfs-system -> ontology:entity/zfs-system
- zfs-dmu -> ontology:entity/zfs-dmu ...
```

要求 `zfs-system` 单根 `composed_of 6叶` 经 `tree_split` 生 `candidates 6叶+1系统` `dependencies[6叶]` `ready-set [[6叶],[system]]` `scripts/ontology_tree_split.py:50`。`T0503` 未执行 `tree_split` 在 `research` 层即由 `T0505` `development` 执行，**冒用** `T0503` 的 `拆分映射`，`T0503` 的 `拆分映射` 未被 `research` 消费而被 `development` 消费，`Spec` 要求的“调研产本体”被“开发用本体”提前消费。

**PRD `T0505` 亦同映射**，`Spec` 未要求 `T0505` 重复 `tree_split`，但 `T0505` 重复了本应归 `T0503` 的 `research` 叶拆分，导致 `T0503→6 research叶→6 develop叶` 双层被压缩为 `T0505→6 develop叶` 单层，`ready-set` 仍 `valid:true` 但语义断层。

**缺失**：`T0503` 未按 `to-tickets#3.5` 在 `research` 层生 `candidates`，`task_identity` 继承 `scenario_type` 时 `T0503 research` 被 `T0505 development` 截断，未做 `research叶→本体→develop叶` 双层闸。

## 汇总（双轴分离）

- **Standards**：1违（本体控产生）+ 1违（WBS 100% research层缺）+ 1违（叶可验证复用），最重为本体控产生。
- **Spec**：1冒用（`T0505` 冒用 `T0503` 拆分映射）+ 1压缩（双层压单层），最重为冒用。
- 双轴不合并择优，分置呈报。

## 修复验证

`T0513-0518` 6 `research` 叶 `parent T0503` 已 `archive` `Do 3 mermaid+Source`，`T0506-0511` 保留 `development`，`compute-frontier` 双层 `valid:true` `GATE OK`。
