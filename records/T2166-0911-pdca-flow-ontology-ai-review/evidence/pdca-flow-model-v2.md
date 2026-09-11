---
schema: pdca.asset/v1
id: ontology:process/pdca-flow-model
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-flow-model/1.0.0
summary: PDCA AI 工作流流程本体模型：阶段、转换、门禁、证据、判定与核心场景关系
relations:
  specializes:
    - ontology:concept/process
  part_of:
    - ontology:concept/pdca
  relates_to:
    - ontology:concept/pdca-task
    - ontology:concept/pdca-phase
    - ontology:concept/pdca-transition
    - ontology:concept/pdca-gate
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-verdict
  composed_of:
    - ontology:concept/pdca-phase
    - ontology:concept/pdca-transition
    - ontology:concept/pdca-gate
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-verdict
attributes:
  - name: pdca_lifecycle
    desc: PDCA 任务生命周期及阶段顺序
    constraint: plan→do→check→act，archive 是任务生命周期终态，不是方法论阶段
    testable_signal: "grep -q 'plan.*do.*check.*act' ontology/process/pdca-flow-model.md && grep -q 'archive' ontology/process/pdca-flow-model.md"
  - name: evidence_verdict_chain
    desc: Do 产出证据、Check 形成判定、Act 处置知识的闭环
    constraint: 每个 acceptance criterion 必须映射 evidence 或显式失败，Check 后必须有 verdict
    testable_signal: "grep -q 'acceptance criterion' ontology/process/pdca-flow-model.md && grep -q 'verdict' ontology/process/pdca-flow-model.md"
  - name: ai_workflow_core_scene
    desc: AI 执行使用 A/B/C 核心场景和独立 skill/tool route
    constraint: B 本体建模、A 本体实现、C 本体验证；skill/tool 不成为核心场景
    testable_signal: "grep -q '本体建模' ontology/process/pdca-flow-model.md && grep -q '本体实现' ontology/process/pdca-flow-model.md && grep -q '本体验证' ontology/process/pdca-flow-model.md"
---

# PDCA 流程本体模型

## 核心关系

`pdca-task` 载体经过 `pdca-phase` 阶段，由 `pdca-transition` 驱动转换；转换受 `pdca-gate` 约束。Do 产出 `pdca-evidence`，Check 将证据对照 acceptance criterion 形成 `pdca-verdict`，Act 依据 verdict 进行知识处置并进入 archive 或下一轮 plan。

## AI 工作流投射

- B：本体建模，根到叶创建本体树。
- A：本体实现，叶到根实现本体树。
- C：本体验证，检查实现与本体的一致性。
- skill/tool route：由核心场景选择具体执行技能，不改变流程本体的核心职责。

## 不变量

1. 阶段不得跳过合法转换和前置门禁。
2. Do 产生的每个产物必须登记为 evidence。
3. Check 必须逐项覆盖 PRD acceptance criteria。
4. 用户确认属于阶段转换条件，不由执行器自行推断。
5. Act 必须记录知识处置；可复用结论关联 ontology，任务性结论关联 record。
