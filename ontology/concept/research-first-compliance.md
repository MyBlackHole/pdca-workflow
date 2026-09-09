---
schema: pdca.asset/v1
id: ontology:concept/research-first-compliance
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/research-first-compliance/1.0.0
summary: 全场景先调研产本体满足度结论（五满足一partial零不满足）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/research-first-gate
  - ontology:concept/pdca-ontology-ready
  - ontology:process/flow-act
attributes:
- name: dual_criterion_verdict
  desc: 双条件下五场景满足research部分满足
  constraint: development/bugfix/documentation/design/review双条件齐备判满足；research自指判partial；任一条件缺失判不满足
  testable_signal: 运行 pytest tests/test_research_first_gate.py 断言5 passed，且抽查各场景门禁命中与回写门禁配置后断言结论一致
- name: transition_gap
  desc: 存量plan任务过渡缺口非机制缺失
  constraint: 机制上线后存量plan下次推进受检属预期行为，需同步不豁免
  testable_signal: 运行 gate_issues 对抽样存量plan任务断言RESEARCH_FIRST_MISSING出现，且确认其可通过补调研消除
---

# 全场景先调研产本体满足度结论（research-first-compliance）

来源：T2096，记录 `records/T2096-0910-research-first-compliance-audit/conclusion.md`。Grounding：`scripts/pdca_core.py` 先调研门禁段、`records/T2096-0910-research-first-compliance-audit/evidence/review.md`。复用覆盖T2097-0910-compliance-standards/T2098-0910-compliance-spec。

## 背景问题
新门禁上线后需复审六场景是否满足先调研产本体要求。

## 核心机制
1. 双条件判定：Do门禁与Act回写齐备即满足。（依据：`ontology:concept/research-first-gate`）
2. research partial：生产者自指待升级，不掩盖为满足。（依据：`ontology:domain/skill-research`）
3. 过渡缺口：存量plan受检属预期，需同步。（依据：`ontology:process/flow-act`）

## 适用边界
机制层结论；执行层各任务自行补调研。

## 违反后果
把partial说成满足属结论粉饰；把过渡缺口说成机制断裂属误判。

## 关联导航
- 门禁：`ontology:concept/research-first-gate`
- 回写：`ontology:process/flow-act`
