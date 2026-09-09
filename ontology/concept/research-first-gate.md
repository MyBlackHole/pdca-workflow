---
schema: pdca.asset/v1
id: ontology:concept/research-first-gate
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/research-first-gate/1.0.0
summary: 任务必须先调研门禁规则（全场景二选一证据，仅自举豁免）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-gate-do
  - ontology:concept/pdca-ontology-ready
  - ontology:domain/skill-research
attributes:
- name: evidence_disjunction
  desc: 全场景plan→do须本次调研证据二选一
  constraint: 链内research子票已归档，或本次research-report通过mermaid≥3/Source≥3/http≥1/URL≥2；缺失报RESEARCH_FIRST_MISSING
  testable_signal: 运行 pytest tests/test_research_first_gate.py 断言5 passed，且无证据dev任务运行 gate_issues 断言含RESEARCH_FIRST_MISSING
- name: exemption_minimal
  desc: 仅ontology_exempt豁免，无父链继承
  constraint: 豁免任务跳过判定；其余含research自身一律核验
  testable_signal: 运行 pytest tests/test_research_first_gate.py 中豁免用例断言放行，且全量门禁测试不断言豁免外放行
- name: self_reference_limitation
  desc: 新鲜research叶票自指阻断为已知局限，需升级
  constraint: 当前按口径锁定阻断行为；升级前不得擅自加生产者豁免
  testable_signal: 运行 pytest tests/test_research_first_gate.py::ResearchFirstGateTest::test_research_leaf_self_reference_blocked 断言阻断成立
---

# 任务必须先调研门禁规则（research-first-gate）

来源：T2092，记录 `records/T2092-0910-research-first-gate/conclusion.md`。Grounding：`scripts/pdca_core.py` 先调研门禁段、`tests/test_research_first_gate.py:1-160`。复用覆盖T2093-0910-rf-evidence-form/T2094-0910-rf-gate-test/T2095-0910-rf-doc-sync（三报告自证通过新门禁）。

## 背景问题
ontology-ready复用旧fragment即放行，无本次调研动作要求；T2072口径A确认现状后用户要求从严。

## 核心机制
1. 证据二选一：链内research子票已归档（传递闭包），或本次报告通过图/网络门禁。（依据：`ontology:concept/pdca-gate-do`）
2. 最小豁免：仅自举豁免，无父链继承。（依据：`ontology:concept/pdca-ontology-ready`）
3. 自指局限：新鲜research叶票当前阻断并由测试锁定，待升级决策。（依据：`ontology:domain/skill-research`）

## 适用边界
全场景plan→do；旧任务不追溯（门禁仅新生效后转换触发）。

## 违反后果
无本次调研证据的plan→do被拒；擅自加豁免属口径漂移。

## 关联导航
- 准入：`ontology:concept/pdca-gate-do`、`ontology:concept/pdca-ontology-ready`
- 调研：`ontology:domain/skill-research`、`ontology:domain/skill-web-research`
