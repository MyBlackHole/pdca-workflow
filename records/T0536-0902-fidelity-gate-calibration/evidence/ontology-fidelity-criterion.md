---
schema: pdca.asset/v1
id: ontology:concept/ontology-fidelity-criterion
type: concept
layer: Knowledge
status: active
summary: 本体保真度与完备性判据 — 七项清单、fidelity score 与致命/严重/一般分级（AI可复现为金标准）
relations:
  specializes:
    - ontology:concept/meta-ontology
  relates_to:
    - ontology:concept/ontology-validate
    - ontology:concept/ontology-rule-fidelity-generic
    - ontology:concept/ontology-rule-fidelity-body
    - ontology:concept/ontology-rule-fidelity-diagram
rule_spec:
  # 七项清单（按Grill Q9确认）
  checklist:
    - concept_definition
    - attributes_complete
    - relations_closed
    - behavior_visualized
    - examples
    - provenance
    - scaffoldable
  # 致命/严重/一般分级阈值
  severity:
    fatal: ["generic_signal", "missing_attributes", "missing_concept"]
    serious: ["missing_diagram", "missing_examples", "dangling_relation"]
    minor: ["missing_source", "body_too_short", "not_scaffoldable"]
  # fidelity score 权重（0-100）
  score_weights:
    attributes: 30
    behavior: 25
    relations: 15
    provenance: 15
    examples: 15
  # 门禁阈值
  gate_thresholds:
    body_min_lines: 60
    mermaid_min: 1
    attributes_min: 1
    fatal_block: true
---

# 本体保真度与完备性判据（Fidelity Criterion）

> **金标准（Q4/Q10确认）**：新AI会话仅读本体即能产出通过 `testable_signal` 的实现；必要条件为 `ontology_test_scaffold.py` 可产且pytest可收集，充分条件为人工盲测抽检实现片段符合原始特性。达不到即不完整。

> **治理范围（Q1确认）**：全量一视同仁 — 全部 `ontology/` 节点（domain/entity/pattern/principle/pitfall/fact/concept/process）纳入本判据，不设类型豁免。`ontology-validate --check fidelity` 为执行者。

## 七项清单（Q2/Q9确认：自我审查是否完整体现知识的本体）

每本体逐项自检，缺一项即不完整需补充：

| # | 项 | 判定 | 门禁码 | 关联规则 |
|---|----|------|--------|----------|
| 1 | **概念定义** | `summary` 非空且正文首段有概念定义 | `[MISSING_CONCEPT]` | fidelity-body |
| 2 | **属性完备** | `attributes≥1` 且每条 `testable_signal` 含可执行动词（`grep -q`/`gate.py`/`scaffold`/`pytest`）且非泛化短语 | `[ATTR_GENERIC]`/`[ATTR_NO_VERB]` | fidelity-generic |
| 3 | **关系闭环** | `relations` 至少1条 `specializes` 且知识类有 `guides`/`relates_to`（复用既有AC-5/AC-6） | `[NO_GUIDES]`/`[DANGLING_REF]` | richness/guides-range |
| 4 | **行为可视化** | `mermaid≥1` 且含 C4/时序/状态机/决策树之一（业务域强制，concept/process可豁免但计分） | `[MISSING_DIAGRAM]` | fidelity-diagram |
| 5 | **正反例** | 正文含 `正例` 与 `反例`（或 Example/Counterexample） | `[MISSING_EXAMPLES]` | fidelity-body |
| 6 | **门禁溯源** | 每图附 `Source:` 且含 `file:line` 行号 | `[MISSING_SOURCE]` | fidelity-diagram |
| 7 | **可scaffold** | `ontology_test_scaffold.py --node <id> --out /tmp/x.py` 可产（有attributes节点强制） | `[NOT_SCAFFOLDABLE]` | fidelity-body |

**泛化signal零容忍（Q3确认，T0536校准）**：`testable_signal` 含 `检查本文件`/`相关章节的完整性` 等泛化短语**且无** `required_verbs`（`grep -q`/`gate.py`/`scaffold`/`pytest`）才判 `[ATTR_GENERIC]` 致命；`检查本文件…且经 python3 scripts/...` 双条件（泛化+可执行）属有效误报，不阻断（T0536抽样19/20=95%误报率校准，符合L3 10%阈值）。增量零容忍仅拒真泛化，存量豁免清单 `ontology/.fidelity-exempt.json` 限期清零。

## 门禁分层（T0535四象限决策树固化，T0536 AC-2）

| 层 | 门禁 | 处置 | 阈值 | 依据 |
|----|------|------|------|------|
| L1 精确硬阻断 | G1-G5（type/非空悬/无环/非空signal/guides） | 保留硬阻断 | 0%误报 | L3编译期0% |
| L2 脆性豁免 | G6 ATTR_GENERIC | 保留但双条件+豁免清单，真泛化才拒 | 有效误报≤10% | T0536抽样校准 |
| L3 统计不阻断 | G7-G10（mermaid/Source/行数/正反例） | audit统计，PR级warning，不升validate硬阻断 | 56%>>10%属过度，当前降级正确 | L1 P4陷阱 |
| L4 无门禁 | 低风险长尾 | 免门禁，靠review | — | L2 gates not loops |

## Fidelity Score（0-100，Q6确认）

```
score = attributes(30) + behavior(25) + relations(15) + provenance(15) + examples(15)
- attributes: 有可执行signal 30分，泛化0分，无attributes 0分
- behavior:  mermaid≥2且含时序/状态机 25，mermaid=1 15，无 0
- relations: specializes+guides闭环 15，仅specializes 8，无 0
- provenance: 每图1 Source行号 15，有Source无行号 8，无 0
- examples:  正反例齐全 15，仅正例 8，无 0
```

分级：`致命 fatal`（含泛化/无attributes/无概念）`严重 serious`（缺图/缺例/空悬）`一般 minor`（缺源/短正文/不可scaffold）。

## 门禁落位（Q7/Q8确认）

- **增量零容忍**：新提交本体触发 `ontology-validate --check fidelity`（或默认validate含fidelity），命中 `fatal` 即非0阻断。
- **存量限期**：审计报告产出豁免清单，按 P0/P1/P2 限期清零（P0两周），CI 每日播报剩余 `fatal` 数。
- **权威锚定**：本节点 `rule_spec` 为阈值唯一事实源；`ontology-validate.py` 与 `production-ontology-gate.py --check fidelity` 运行时读取本节点。

## 与审计脚本关系

`scripts/audit-ontology-fidelity.py` 逐本体按七项打分，产出 `audit-report.md`（统计表 + Top20 + 豁免清单）与 `fidelity.jsonl`（每节点score与缺项），供门禁与路线图消费。

## 正例（可实现本体）

`ontology:entity/zfs-arc`（170行，3 attributes可执行，4 mermaid，Source行号，正反例，scaffold可产）→ score 92 / PASS

## 反例（空洞本体）

`ontology:domain/ai-efficiency-ticket-dag-ready-set`（旧版 59行，1 attribute泛化，0 mermaid，0 Source，无正反例）→ `[ATTR_GENERIC]` fatal / score 18 / FAIL

Source: `ontology/entity/zfs-arc.md` + `ontology/domain/ai-efficiency-ticket-dag-ready-set.md`（审计对比）+ `scripts/audit-ontology-fidelity.py`
