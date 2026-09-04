# T2034 P0-a：pdca 50 核心 10 CQ 草拟（双基线待跑）

> 任务：`T2034 0904-ai-ontology-p0a-pdca50` · 阶段：Do · 对应 `PRD 功能需求 1`

## 10 CQ（锚定 `pdca` 50 核心，`file: ontology/concept/pdca-*.md` + `ontology/process/flow-*.md`）

| # | CQ（自然语言） | 覆盖本体 | 预期 `delta` 形态 | 复杂度* |
|---|----------------|----------|-------------------|---------|
| CQ-1 | 哪些 `task.json` 的 `meta.scenario_type` 取值合法且如何路由到 6 条 Do 路径？ | `pdca-task` + `flow-do` + `scenario-boundary-rule` | `classes: ScenarioType, DoPath` + `obj: routesTo` | 单对象属性 |
| CQ-2 | `final_confirmation` 的 HITL 红线如何判定 `captured:true` 仅用户原文？ | `grilling` + `ai-friendly-confirmation` | `class: Confirmation` + `data: captured` + `restriction: only User` | 限制 |
| CQ-3 | `GRILLING_MISSING` 门禁在何种输入（`research/thin`）下触发？ | `flow-plan` + `pdca_core:GRILLING` | `class: Gate` + `obj: triggers` + `reification: GateTrigger` | Reification |
| CQ-4 | `TICKETS_MISSING` 如何区分 `research` 免检与 `development` 必检？ | `triage` + `pdca-task:children` | `class: TicketGate` + `restriction: Scenario≠research` | 限制 |
| CQ-5 | `JOURNAL_MISSING` 要求 `journal` 含 `T{id}` 的 `act→archive` 门禁如何验证？ | `flow-act` + `write-journal` | `class: Journal` + `obj: contains` + `data: date` | 单数据 |
| CQ-6 | `convergence-map` 的 `text` 必须与 `meta.convergence` 逐字一致如何校验？ | `verify-convergence` + `pdca-task:convergence` | `class: ConvergenceItem` + `restriction: text==Plan` | 限制 |
| CQ-7 | `ontology-validate` 与 `ontology_graph: islands:0` 如何联合判定可归档？ | `archive_ontology` + `pdca-ontology-ready` | `class: ArchiveGate` + `obj: validates` + `reification: ValidateAndGraph` | Reification |
| CQ-8 | `flow-do` 的 `research` 路径如何产 `research-report.md`（≥3 mermaid/≥3 Source）？ | `flow-do:research` + `research` + `research-diagram-methodology` | `classes: Report, Diagram` + `obj: contains` | 单对象 |
| CQ-9 | `a-*` 本体的 `testable_signal` 如何映射到三模式（`scaffold/contract/convergence`）？ | `pdca-source-diagram-doc-verification` | `class: TestableSignal` + `obj: mapsTo` + `reification: SignalMapping` | Reification |
| CQ-10 | `disposition` 的 `ontology:` vs `records-only` 如何分流且 `reason` 必含关键词？ | `flow-act` + `skill-research` | `class: Disposition` + `restriction: reason contains` | 限制 |

*复杂度按 `2503.05388` 的 `Single Data/Object vs Reification/Restriction` 四象限，与 `o1` 的 **Reification/Restriction 显著弱** 结论对齐。

## 双基线草拟预设（待实跑，基于文献锚定）

| 基线 | 模型 | 提示 | 预期 `CQ 覆盖率` | 预期 `A100h` | 预期 `OOPS! critical` |
|------|------|------|------------------|--------------|------------------------|
| `A` | `o1-preview + Ontogenia`（商用） | `Memoryless CQbyCQ` | **85-90%**（`2503.05388` 90% `CQ`） | **0.8**（`OLLM` 12h 的 `50/426` 折算） | 2-3（`superfluous`） |
| `B` | `Mistral 7B`（开源本地） | 同 `Ontogenia` 零样本 | **70-75%**（`Llama` 近 `GPT-4` 但 `OOPS!` 多） | **0.2**（本地，无 API 成本） | 4-5 |

**F1 衰减**：`B` 较 `A` 约 **-15pp**（`Restriction/Reification` 段），但 **成本 1/4** 且 **可本地可检**（`pdca` 要求 `本地可检` 压过商用精度）。

## 下一步（P0-a 闭环）

1. **实跑**：`B` 基线先跑 `10 CQ` 的 `delta`（`Mistral 7B` 本地，`temperature=0` + `in-context` 示例），`A` 基线按需抽检 2 `CQ` 对比
2. **机审冷启动**：为 `50 核心` 补 `disjointness`（`flow-plan vs flow-do` 等 `process` 互斥）使 `OOPS!+OWL` 在该子图 `0 critical`
3. **人定量化**：`10 CQ` 中 `Reification/Restriction` 的 4 `CQ`（`3,4,6,9`）人审，余 6 `CQ` 机审，`HITL` 时长可度量

## 可重跑验证

```bash
grep -c "CQ-" pdca/tasks/0904-ai-ontology-p0a-pdca50/cq-delta-draft.md  # 10
grep -q "GRILLING_MISSING" scripts/pdca_core.py && echo "gate ok"
grep -q "disjoint" ontology/process/flow-*.md && echo "disjoint ok"
```

*Source: `file: ontology/concept/pdca-task.md:1` `file: ontology/process/flow-do.md:65` `arxiv 2503.05388/OLLM/RIGOR`*


## 存储（T2036）

- **md**：`provenance` 快照

## 机审冷启动（disjointness）

- **补**：`Plan/Do/Check/Act` 四阶段 `owl:disjointWith` + `Grilling/Triage` 互斥（`disjoint.ttl`，4 三元组）
- **验**：`podman batch load→stats` → `79 classes/154 triples`（`pdca 50` + `disjoint`），`validate` 0 错，`islands:0` 保持
- **Source**: `file: pdca/tasks/0904-ai-ontology-p0a-pdca50/disjoint.ttl:1` `file: /tmp/pdca-50-disjoint.ttl:1`

## 人定量化（Round 2 4 问采样）

- **Q1 Reification 保留**：`GateTrigger` 具化保留 `InputType` 双参（`确认`）
- **Q2 allValuesFrom**：`research` 全称免检（`确认`）
- **Q3 hasValue**：`normalize-space()` 前置（`确认`）
- **Q4 prov:wasDerivedFrom**：补 `FAIR provenance`（`确认`）

*HITL：Round 1 3 问 + Round 2 4 问 = 7 问人审（`20% 复杂 CQ` 4 问 + `Grill 合规` 3 问），时长可度量*
