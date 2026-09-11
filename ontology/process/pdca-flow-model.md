---
schema: pdca.asset/v1
id: ontology:process/pdca-flow-model
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-flow-model/1.0.3
summary: PDCA AI 工作流流程本体模型：阶段、转换、门禁、证据、判定与本体职责关系
relations:
  specializes:
    - ontology:concept/process
  relates_to:
    - ontology:concept/pdca-task
    - ontology:concept/pdca-phase
    - ontology:concept/pdca-transition
    - ontology:concept/pdca-gate
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-verdict
    - ontology:concept/pdca-execution-contract
    - ontology:concept/pdca-recovery
    - ontology:concept/pdca-feedback
    - ontology:concept/executor-adapter
    - ontology:concept/pdca-continuous-improvement
  composed_of:
    - ontology:concept/pdca-phase
    - ontology:concept/pdca-transition
    - ontology:concept/pdca-gate
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-verdict
    - ontology:concept/pdca-execution-contract
    - ontology:concept/pdca-recovery
    - ontology:concept/pdca-feedback
attributes:
  - name: pdca_lifecycle
    desc: PDCA 任务生命周期及阶段顺序
    constraint: plan→do→check→act，archive 是任务生命周期终态，不是方法论阶段
    testable_signal: "grep -q 'plan.*do.*check.*act' ontology/process/pdca-flow-model.md && grep -q 'archive' ontology/process/pdca-flow-model.md"
  - name: evidence_verdict_chain
    desc: Do 产出证据、Check 形成判定、Act 处置知识的闭环
    constraint: 每个 acceptance criterion 必须映射 evidence 或显式失败，Check 后必须有 verdict
    testable_signal: "grep -q 'acceptance criterion' ontology/process/pdca-flow-model.md && grep -q 'verdict' ontology/process/pdca-flow-model.md"
  - name: ai_workflow_ontology_role
    desc: AI 执行使用本体职责和独立 skill/tool route
    constraint: modeling、projection、conformance verification；skill/tool 不成为本体职责
    testable_signal: "grep -q 'ontology_modeling' ontology/process/pdca-flow-model.md && grep -q 'ontology_projection' ontology/process/pdca-flow-model.md && grep -q 'ontology_conformance_verification' ontology/process/pdca-flow-model.md"
  - name: execution_contract
    desc: 本体产出契约决定执行内容，工具仅为适配器
    constraint: execution_contract 必须声明 work_product、required_actions、constraints 和 testable_signal
    testable_signal: "grep -q 'execution_contract' ontology/process/pdca-flow-model.md && grep -q 'required_actions' ontology/process/pdca-flow-model.md"
  - name: fresh_agent_context
    desc: 每个独立 PDCA 任务由一对一全新子 Agent 自主执行，协调 Agent 派发后挂起
    constraint: coordinator_execution_state=suspended_waiting_agent；恢复后只读当前任务持久化产物并执行 ontology_conformance_verification；禁止跨任务检查；agent.spawn 不可用时 fail-closed
    testable_signal: "grep -q 'suspended_waiting_agent' ontology/process/pdca-flow-model.md && grep -q 'ontology_conformance_verification' ontology/process/pdca-flow-model.md && grep -q 'fail-closed' ontology/process/pdca-flow-model.md"
  - name: recovery_feedback_loop
    desc: 失败恢复与执行效果反馈属于 PDCA 闭环关系
    constraint: rejected/partial 必须关联恢复或跟进任务，confirmed 结果必须记录效果反馈或 unknown
    testable_signal: "grep -q '失败恢复' ontology/process/pdca-flow-model.md && grep -q '效果反馈' ontology/process/pdca-flow-model.md"
---

# PDCA 流程本体模型

## 核心关系

`pdca-task` 载体经过 `pdca-phase` 阶段，由 `pdca-transition` 驱动转换；转换受 `pdca-gate` 约束。Do 产出 `pdca-evidence`，Check 将证据对照 acceptance criterion 形成 `pdca-verdict`，Act 依据 verdict 进行知识处置并进入 archive 或下一轮 plan。

## AI 工作流投射

权威语义与执行的投影顺序是“权威本体图 -> 任务有界子图 -> 执行树/DAG”。图是语义结构，树驱动是任务投影和执行原则，两者不得互相替代。

- `ontology_modeling`：本体建模，根到叶创建本体树。
- `ontology_projection`：本体投射，叶到根产出实现资产。
- `ontology_conformance_verification`：本体符合性验证，检查产出与本体的一致性。
- execution_contract：由本体建模产出，声明 work_product、required_actions、constraints 和 testable_signal。
- skill/tool：执行适配器，只实现契约要求，不参与核心职责分类。

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
6. 每个 PDCA 任务都是独立完整循环；协调 Agent 必须为当前任务一次性启动一对一的全新子 Agent/子智能体上下文，随后立即进入 `suspended_waiting_agent` 并停止运行。子 Agent 在当前任务上下文内自主执行，禁止复用其他活动上下文。
7. 协调 Agent 恢复后只读当前任务 `task.json`、transition receipts、evidence manifest 与工作产物，并执行 `ontology_conformance_verification`：对照 ontology fragment、execution contract 和 acceptance criteria 审查“本体定义 -> 实现或产物 -> evidence”的一致性，再决定是否满足进入 Check 的条件。跨任务检查被禁止。
8. 当前任务需要用户确认时持久化 `awaiting_confirmation`；主会话转交真实用户确认并写回。子 Agent 不得代签；该确认通道不是其他任务的生命周期控制。
9. `parent` 与 `dependencies` 只表达任务拆分和调度关系，不表达生命周期控制或验收代理。`suspended_waiting_agent` 与 `awaiting_confirmation` 是执行状态而非新增 phase；`agent.spawn` 不可用时 fail-closed，当前任务保持未执行且不得产生 Do 产物或执行证据。
