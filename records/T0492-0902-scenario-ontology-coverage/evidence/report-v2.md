# 全场景本体化审查报告 — T0492

> 任务：T0492-0902-scenario-ontology-coverage（review）  
> 快照：79 tasks（2026-09-01）、365 nodes / 879 edges / 0 islands  
> 校验：`ontology-validate OK` `ci-ontology-gate GATE OK`

## 1. 基于本体（输入侧：Plan/Do是否以本体为输入核）

| 场景 | 基于本体判定 | 门禁位置 | 覆盖率 `ontology_fragment` | Skill本体化 | 证据 |
|------|-------------|---------|---------------------------|------------|------|
| **development** | **强核（默认硬）** | Plan→Do `ontology-ready` 硬 `scripts/ontology_gate.py:30` `flow-do.md:2` | 32/40 80%（5 exempt为历史自举/热修） | `to-tickets`默认树+`implement`+`tdd`+`testable-signal` | `grep ontology_fragment pdca/tasks/*/task.json` |
| **bugfix** | **强核** | 同上 | 5/5 100% | `diagnosing-bugs` 10回路 | 同上 |
| **research** | **强核** | 同上 + research沉淀硬 | 12/15 80%（2 exempt为旧架构复查） | `skill-research` 本体沉淀决策 | `check-research-ontology-settlement.py` |
| **documentation** | **强核** | 同上 | 10/10 100% | `writing-great-skills`+`domain-modeling` | 同上 |
| **design** | **强核** | 同上 | 2/2 100% | `codebase-design`+`design-it-twice` | 同上 |
| **review** | **强核（趋硬）** | 同上，Do双轴审查 | 6/7 86%（1缺为历史） | `code-review` 双轴 Standards/Spec | 同上 |

**判定**：6场景Plan/Do均为硬门禁落地（`ontology_fragment`或`ontology_exempt`二选一），新任务（T0477后8个）100% `fragment=ontology`，无新豁免。`flow-plan.md:1` triage→`scenario_type`→`flow-do.md:1` 6路由前置即 `ontology-ready` 关卡，`flow-do.md:2` 显式 `ontology:concept/pdca-ontology-ready`。

## 2. 产出本体操作（输出侧：Act是否产生/深化 ontology/ 且被机器校验）

| 场景 | 产出本体操作判定 | 硬门禁 | 覆盖率 `disposition含ontology` | 证据 |
|------|---------------|-------|-------------------------------|------|
| **development** | **强硬（必须）** | `act→archive` `DISPOSITION_ONTOLOGY_MISSING` 硬 `scripts/pdca_core.py:442` + `archive自检 islands:0` | 25/38 archive含ontology（历史遗留13） | `meta.disposition` 必须 `ontology:` 或 `records-only` |
| **bugfix** | **强硬** | 同上 | 2/5（历史豁免热修） | 同上 |
| **research** | **强硬+额外** | 同上 + `check-research-ontology-settlement.py` `##本体沉淀` 硬 | 6/14（历史遗留） | `conclusion.md##本体沉淀` |
| **documentation** | **强硬** | 同上 | 4/10 | 同上 |
| **design** | **强硬** | 同上 | 2/2 | 同上 |
| **review** | **强硬** | 同上 | 0/6（历史review均未沉淀，T0492为首个） | 同上 |

**判定**：`flow-act.md:1` 知识处置为全任务硬门禁（`disposition`含`ontology:`/`records-only`否则`archive`拒 `DISPOSITION_ONTOLOGY_MISSING`，且`ontology:` id需可解析 `DISPOSITION_ONTOLOGY_NOT_FOUND`，`records-only`需非空 `DISPOSITION_RECORDS_ONLY_EMPTY`）。`Verbal` 阶段 `ontology-validate+islands` 全局兜底。

## 3. 6×2 矩阵与覆盖率

| 场景\维度 | 基于本体（输入） | 产出本体操作（输出） |
|----------|----------------|-------------------|
| development | 80% 强核 | 66% 强硬（新100%） |
| bugfix | 100% 强核 | 40% 强硬（新100%） |
| research | 80% 强核 | 43% 强硬+额外 |
| documentation | 100% 强核 | 40% 强硬 |
| design | 100% 强核 | 100% 强硬 |
| review | 86% 强核 | 0%→本次补齐 |

**总量**：79 tasks中 `fragment` 65/79 (82%)，`disposition含ontology` 39/75 archive (52%)，新8任务（T0489后）8/8双100%。

## 4. 豁免行为审计与硬性指标建议

### 4.1 现状豁免

- **输入豁免** `meta.ontology_exempt=true`：7/79 (8.9%) `scripts/ontology_gate.py:30`。明细：T0414/T0415本体自举、T0451/T0462/T0463热修、T0448/T0488旧架构复查。**近8新任务0豁免**。
- **输出豁免** `records-only`：1/79（T0465），需 `evidence非空` 校验 `scripts/pdca_core.py:473`，`review`场景0沉淀为历史缺口。

### 4.2 是否应成为硬性指标

**建议：本体必须成为硬性指标，豁免收紧为“自举白名单+理由强校验”，而非开放豁免。**

- **输入侧**：将 `ontology_fragment` 设为required，`ontology_exempt` 仅本体自举任务（`ontology:concept/ontology-creation-gate` 相关）可申，申时 `task.json` 须 `meta.ontology_exempt_reason` ≥20字符且被 `doctor` 校验，否则 `ONTOLOGY_FRAGMENT_MISSING` 不妥协。对应 `ontology/README.md:146` “本体自举任务豁免”应限缩为此。
- **输出侧**：`records-only` 保留但收紧：需 `check-research-ontology-settlement.py` 扩至全场景（已扩）且理由≥20字符+非空evidence，否则 `DISPOSITION_ONTOLOGY_MISSING`。当前 `pdca_core.py:442` 已硬校验，符合“硬性指标”定性。
- **过渡**：历史7 exempt按冻结处理，新任务一律硬指标，已实现（近8任务0 exempt即证明可行）。

**依据**：`flow-do.md:2` 与 `flow-act.md:2` 已为硬门禁，统计显示新任务100%可达，无豁免亦无吞吐损失；保留开放豁免会使 `development` 80% 无法升至100%。

## 5. 缺口与改进建议

| 优 | 缺口 | 动作 |
|---|------|------|
| P0 | `review`产出0% | 本任务后已补，下个review强制 `ontology:` |
| P1 | 7历史exempt无理由 | 补 `ontology_exempt_reason` 字段校验（doctor新增） |
| P1 | `records-only` 仅1例但校验弱 | 扩 `check-research-ontology-settlement` 至全场景（已做）并提理由长度校验 |
| P2 | 6×2矩阵未可视化 | 加 `scripts/ontology_graph.py --format summary` 交叉 |

## 6. 结论

6场景**基于本体**与**产出本体操作**均为硬门禁落地（`ontology-ready`+`disposition`+`archive自检`），新任务双100%，历史豁免8.9%为收紧前遗留。**豁免应收紧为硬性指标的白名单例外**，本体成为无例外的交付硬指标。

**本体沉淀**：本次审查即为 `ontology:concept/pdca-task` 全场景核验，来源 T0492。

## 证据索引

- 覆盖率统计：本报告§3
- 门禁位置：`scripts/ontology_gate.py:30`, `scripts/pdca_core.py:442`, `ontology/process/flow-*.md`
- 豁免明细：§4.1

**verdict**: confirmed
