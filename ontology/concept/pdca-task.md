---
schema: pdca.asset/v1
id: ontology:concept/pdca-task
type: concept
layer: Knowledge
summary: PDCA 任务元概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-task/1.0.2
relations:
  specializes:
  - ontology:concept/entity
  testable_signal: "引用存活：test $(grep -rl 'ontology:concept/pdca-task' ontology/ tests/ scripts/ | wc -l) -ge 92"
task_execution_spec:
  cycle_scope: independent_pdca_task
  execution_agent_kind: child_agent
  allocation: fresh_child_agent_per_pdca_task
  child_execution_mode: autonomous
  coordinator_after_dispatch: suspended
  coordinator_execution_state: suspended_waiting_agent
  resume_source: current_task_persisted_artifacts
  resume_artifacts: [task_json, transition_receipts, evidence_manifest, work_products]
  resume_action: ontology_conformance_verification
  cross_task_inspection: forbidden
  task_dependencies_role: scheduling_only
  context_reuse_forbidden_from: [previous_task_active_context, concurrent_task_active_context, coordinator_active_context]
  confirmation_request_state: awaiting_confirmation
  confirmation_authority: user
  confirmation_resume_receipt: user_confirmation_recorded
  conformance_bundle_result: pending
  conformance_decision_authority: coordinator
  spawn_requirement: required
  spawn_unavailable_result: fail_closed_unexecuted
---
# pdca-task

PDCA 任务元概念：一个完整 PDCA 周期的载体。

- **含义**：由 `task.json` 跟踪 `meta.phase` / `status` / 各类标记；阶段只能经 `transition-phase.py` 按 `pdca-transition` 合法边推进。
- **关键不变量**：`final_confirmation` / `check_confirmation` 不可由 AI 代签；阶段推进须经门禁校验。
- **独立循环**：每个 PDCA 任务独立经历完整生命周期；`parent` 与 `dependencies` 仅用于拆分和调度，不赋予其他任务生命周期控制、检查或验收代理权。
- **执行上下文隔离**：协调 Agent 为当前 PDCA 任务一次性启动一对一的全新子 Agent/子智能体。子 Agent 在当前任务上下文内自主执行；跨任务输入只经明确的持久化 PRD、任务元数据、证据与 context pointer 传递，禁止共享活动上下文。
- **协调 Agent 挂起与恢复**：派发后协调 Agent 立即进入 `suspended_waiting_agent` 并停止运行。恢复后只读取当前任务自身的 `task.json`、transition receipts、evidence manifest 与工作产物，构造 `result=pending` 的内容寻址审查包；任务职责保持原 `ontology_role`，`ontology_conformance_verification` 作为 review action。协调器审查“本体定义 -> 实现或产物 -> evidence”后，必须另行登记绑定 review digest、决定与理由的 receipt，确定性门禁不得自我批准。
- **确认通道**：当前任务需要用户确认时持久化 `awaiting_confirmation`；该状态拒绝 Agent 直接完成。主会话转交真实用户确认并写入合法确认记录后，协调器以 `user_confirmation_recorded` receipt 绑定请求之后新增的 clarification 条目及摘要，才把同一 Agent 恢复到 `suspended_waiting_agent`。子 Agent 不得伪造用户确认；该通道不构成其他任务的控制。
- **状态与能力**：`suspended_waiting_agent`、`awaiting_confirmation` 是执行状态，不是 PDCA phase。`agent.spawn` 是必需能力；不可用时 fail-closed，当前任务保持未执行，不得产生 Do 产物或证据，不得由协调 Agent 或既有子 Agent 代为执行。

## 决策背景（原 ADR-0002：严格任务合约与能力适配边界）
- 背景：流程曾同时依赖自然语言门禁、松散 task.json 字段与具体 Agent 平台工具名；历史任务 phase/status/active/states 互相矛盾仍通过校验。
- 决策：冻结严格新 schema（task.schema.json），fail-closed，不为旧格式增加兼容分支；清理不合规历史任务；技能只声明所需抽象能力（能力协议），具体平台工具由适配层解析。"

## 决策背景（原 ADR-0017：to-tickets 显式依赖边与 ready-set）
- 背景：to-tickets 只顺序拆解，无显式依赖边，无法校验 DAG 无环、无法计算可并行任务集。
- 决策：子任务显式声明 `dependencies`（直接前置边）；ready-set = 所有 blocker 已完成的可执行集合；`schemas/task.schema.json` 的 `additionalProperties:false` 要求新增字段同步改 schema，否则 doctor 校验失败。

## 步骤与完成标准
- **steps**：技能/流程的可执行步骤序列，每个步骤含 `name`（名称）、`description`（描述）、`completion_criterion`（完成标准）。步骤是 agent 按序执行的动作，每条有可检查完成标准。
- **completion_criteria**：任务完成的判定条件列表，需清晰且有需求强度。最强判据同时具备 checkable（可检验）和 exhaustive（穷尽）。
- 映射 mattpocock/skills writing-for-agents 原则：信息层级中步骤为首要层级，完成标准需 clarity（防过早完成）和 demand（驱动 legwork）两者兼备。
