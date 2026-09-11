---
schema: pdca.asset/v1
id: ontology:process/pdca-flow-model
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-flow-model/1.0.1
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
    - ontology:concept/executor-adapter
    - ontology:concept/pdca-continuous-improvement
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
  - name: skill_route_contract
    desc: skill route 是执行层属性而非核心场景
    constraint: core_scene 只允许 A/B/C，skill_route 必须映射到对应 skill、产物类型和 evidence kind
    testable_signal: "grep -q 'skill_route.*执行层' ontology/process/pdca-flow-model.md && grep -q '产物类型' ontology/process/pdca-flow-model.md"
  - name: recovery_feedback_loop
    desc: 失败恢复与执行效果反馈属于 PDCA 闭环关系
    constraint: rejected/partial 必须关联恢复或跟进任务，confirmed 结果必须记录效果反馈或 unknown
    testable_signal: "grep -q '失败恢复' ontology/process/pdca-flow-model.md && grep -q '效果反馈' ontology/process/pdca-flow-model.md"
---

# PDCA 流程本体模型

## 核心关系

`pdca-task` 载体经过 `pdca-phase` 阶段，由 `pdca-transition` 驱动转换；转换受 `pdca-gate` 约束。Do 产出 `pdca-evidence`，Check 将证据对照 acceptance criterion 形成 `pdca-verdict`，Act 依据 verdict 进行知识处置并进入 archive 或下一轮 plan。

## AI 工作流投射

- B：本体建模，根到叶创建本体树。
- A：本体实现，叶到根实现本体树。
- C：本体验证，检查实现与本体的一致性。
- skill/tool route：由核心场景选择具体执行技能，不改变流程本体的核心职责。
- skill route 是执行层属性，必须同时约束具体 skill、产物类型和 evidence kind。

## 恢复与反馈

- rejected/partial verdict 关联失败恢复、人工升级或后续 Improvement Task。
- confirmed verdict 记录执行效果；缺少遥测时显式记录 `unknown`，不得把一次执行冒充效果闭环。
- 所有恢复和反馈结果回流到下一轮 plan，形成可追踪的持续改进关系。

## 不变量

1. 阶段不得跳过合法转换和前置门禁。
2. Do 产生的每个产物必须登记为 evidence。
3. Check 必须逐项覆盖 PRD acceptance criteria。
4. 用户确认属于阶段转换条件，不由执行器自行推断。
5. Act 必须记录知识处置；可复用结论关联 ontology，任务性结论关联 record。
