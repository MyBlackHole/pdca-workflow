# AI 本体 P0-b：426 全量外扩（复用 P0-a 10 CQ 模板与 disjoint 基线）

## 背景

`T2034 P0-a` 的 `50 核心` 垂直切片已验证 `AI 10 CQ + disjoint 154 + 人定 4 问` 闭环（`5435 bytes` `islands:0`），现外扩至 `426 全量`（`T2036` 的 `8 桶 FAIR` 已全量）。

输入锚点：
- `file: pdca/tasks/archive/2026-09/0904-ai-ontology-p0a-pdca50/cq-delta-draft.md:1` — 10 CQ 模板
- `file: pdca/tasks/archive/2026-09/0904-ai-ontology-p0a-pdca50/disjoint.ttl:1` — disjoint 基线
- `file: ontology/domain/{pdca,core,zfs,report-center}/` — 426 全量 5 域

## 目标

复用 `P0-a` 的 `10 CQ` 模板至 `426`，更新双基线成本锚至全量，`disjointness` 扩至全域，`人定` 从 `4/10` 扩至 `85/426`（`20%` 复杂关系），全量证据可回溯。

## 范围

- 输入：`426` 全量（`islands:0`）
- 输出：`426 CQ` 草拟 + 全量 `disjoint` + `85` 人审 `Grill` 记录
- 不做：不改 `T2036` 的 `8 桶` 结构，仅外扩 `P0-a` 模板

## 功能需求

1. **AI 草拟外扩**：`10 CQ` 模板采样 `426`（每 `20 节点` 1 `CQ`，共 ~20 `CQ`），`o1 vs Mistral` `F1/A100h` 更新至 `426` 规模（`A100h` 线性外推）
2. **机审外扩**：`disjointness` 从 `4` 阶段扩至 `426` 的 `核心互斥`（`pdca/zfs/bcachefs` 域间），`OOPS! 0 critical` 保持
3. **人定外扩**：`85/426` 复杂关系（`Reification/Restriction`）采样人审，`HITL` 时长从 `7 问` 线性外推可度量

## 验收标准

- [ ] AC-1 426 草拟已产：`20 CQ` 覆盖 5 域且 `F1` 衰减表更新至全量
- [ ] AC-2 全量机审已产：`426` 的 `disjoint` 扩增后 `OOPS!/OWL 0 critical` 保持且 `islands:0`
- [ ] AC-3 全量人定已产：`85/426` 复杂关系人审记录（`captured:true`）+ `HITL` 外推可度量

## 关联本体节点

```
ontology:concept/pdca-task
ontology:process/flow-do
```

## 拆分映射

- AI 草拟外扩 -> T2038 本体
- 机审/人定外扩 -> T2038 本体
