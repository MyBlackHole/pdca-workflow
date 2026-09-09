---
schema: pdca.asset/v1
id: ontology:pitfall/research-plan-ontology-prompt-gap
type: pitfall
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/research-plan-ontology-prompt-gap/1.0.0
summary: 调研任务Plan期无本体计划提醒pitfall：沉淀校验只在Act触发，Plan/Do全程无提示，须Grill必问本体兜底
relations:
  specializes:
    - ontology:pitfall
  relates_to:
    - ontology:concept/pdca-scenario-boundary-rule
    - ontology:concept/scenario-research-first-gate
    - ontology:pattern/sm4-storage-encryption
attributes:
  - name: plan_no_ontology_prompt
    desc: Plan期门禁与模板均不强制本体计划可测
    constraint: plan→do门禁对research仅查立项确认与研究报告门禁，不查本体锚定；PRD模板本体节点标注可选
    testable_signal: "运行 python3 scripts/transition-phase.py pdca/tasks/0909-guomi-storage-research --to do 在缺本体锚定时返回rejected仅含FINAL_CONFIRMATION_MISSING不含ontology字样，且运行 python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/0909-guomi-storage-research 在phase=plan时输出SKIP"
  - name: grill_mandatory_ontology
    desc: Grill必须包含本体产出一问可测
    constraint: research任务Grill至少一轮明确本体锚定节点与沉淀计划（R3或新节点），captured:true落盘
    testable_signal: "运行 grep -q 'ontology:pattern' pdca/tasks/0909-guomi-storage-research/prd.md 命中且 grep -q '\"source\":\"grilling\"' pdca/tasks/0909-guomi-storage-research/clarifications.jsonl 命中且 grep -q '本体' pdca/tasks/0909-guomi-storage-research/clarifications.jsonl 命中"
---

# Plan 期本体计划无提醒 Pitfall

> 来源：`records/T2107-0909-guomi-storage-research/conclusion.md` 偏差记录（T2099 triage 纠正链）。

## 反模式

research 任务 Plan 期：门禁不查本体、模板标可选、执行者 Grill 漏问本体，
本体缺失一路绿灯到 Act 才被 `check-research-ontology-settlement.py` 拦截，
返工成本最大（报告写完才补锚定与沉淀计划）。

## 正模式（兜底）

1. triage 定 research 的同时即锚定领域本体节点（有现成 pattern 优先复用）。
2. Grill 必留一轮本体问：锚定哪些节点、本次新增还是修订、Act 校验点是什么。
3. PRD 验收标准单列本体沉淀 AC（结论 `## 本体沉淀` 节 + `disposition.reason` 含 `ontology:` + 反向引用）。
