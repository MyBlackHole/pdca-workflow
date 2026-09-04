# AI 本体 P0-a：pdca 50 核心 AI→机审→人定闭环（OOPS 冷启动+双基线成本锚）

## 背景

自审暴露“AI 草拟+机审+人定”方案的 3 硬伤：成本失真（`o1` 商用 vs 本地可检）、`OOPS!` 冷启动死锁、人定过载。P0 拆为 `P0-a` 仅 `pdca 50 核心`（`18 pdca` 相关节点 + `32 flow/skill/gate`）先闭环，再外扩 426。

输入锚点：
- `file: ontology/manifest.jsonl:1` — 18 pdca 相关节点
- `file: scripts/ontology-validate.py:1` + `OOPS!` 基线（`DRAGON-AI`）
- `file: arxiv 2503.05388/OLLM` — `o1 vs Llama/Mistral` 双基线

## 目标

在 `pdca 50 核心` 上跑通 **AI 草拟（`CQ→delta`）→ 机审（`OOPS!+OWL+Judge`，`0 critical`）→ 人定（`grilling` 20% 复杂 CQ 采样）** 闭环，产 **双基线成本锚表**（`o1` vs `Mistral 7B` 的 `F1` 衰减与 `A100h`）。

## 范围

- 输入：`ontology/concept/pdca-*` `ontology/process/flow-*` 等 50 核心
- 输出：`delta` 示例 + `OOPS!` 基线报告 + 成本锚表 + `records/<id>/` 证据
- 不做：不扩 426 全量，不改 `aio-tools` 域

## 功能需求

1. **AI 草拟**：对 `pdca` 50 核心提 `10 CQ`（如 `rdbcomm 32 槽是否可答`），用 `o1-preview+Ontogenia` 与 `Mistral 7B` 双基线各产 `delta`，比 `F1` 与 `A100h`
2. **机审冷启动**：为 `pdca` 补 `disjointness` 约束，使 `OOPS!+OWL` 可跑且 `0 critical`（`grep -q disjoint ontology/process/flow-*.md` 命中）
3. **人定量化**：`95 CQ` 采样 20% 复杂关系（`inverse/restriction/reification`）人审，余 80% 仅机审，`HITL` 时长可度量

## 验收标准

- [ ] AC-1 双基线表已产：`o1` vs `Mistral` 的 `CQ 覆盖率` 与 `A100h` 成本对比，`F1` 衰减可检
- [ ] AC-2 `OOPS!` 基线已产：`pdca` 50 核心经 `OOPS!+OWL` 后 `0 critical`，`validate+islands:0`
- [ ] AC-3 人定量化已验证：20% 复杂 CQ 采样人审记录（`captured:true`）+ 80% 机审，`HITL` 时长可度量

## 关联本体节点

```
ontology:concept/pdca-task
ontology:process/flow-plan
ontology:process/flow-do
```

## 拆分映射

- AI 草拟+机审 -> T2034 本体
- 人定量化 -> T2034 本体
