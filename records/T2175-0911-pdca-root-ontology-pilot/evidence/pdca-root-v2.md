---
schema: pdca.asset/v1
id: ontology:concept/pdca
type: concept
layer: Knowledge
summary: PDCA 管理模型元本体根概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca/1.1.1
docType: Concept
tags: [pdca, meta-ontology]
relations:
  specializes:
    - ontology:concept/entity
  composed_of:
    - ontology:concept/pdca-task
    - ontology:concept/pdca-phase
    - ontology:concept/pdca-transition
    - ontology:concept/pdca-gate
    - ontology:concept/pdca-acceptance-criterion
    - ontology:concept/pdca-evidence
    - ontology:concept/pdca-verdict
    - ontology:concept/pdca-execution-contract
    - ontology:concept/pdca-recovery
    - ontology:concept/pdca-feedback
    - ontology:concept/pdca-continuous-improvement
  relates_to:
    - ontology:process/pdca-flow-model
    - ontology:concept/executor-adapter
pdca_spec:
  method_phases: [plan, do, check, act]
  workflow_terminal: archive
  next_cycle: new_task
  topology: ontology_graph
  design_core: ontology_tree_driven
  task_projection_pipeline:
    - authoritative_ontology_graph
    - bounded_task_subgraph
    - execution_tree_or_dag
  execution_projections: [tree, dag]
  task_agent_context:
    scope: every_pdca_task_and_subtask
    execution_agent_kind: child_agent
    allocation: fresh_child_agent_per_task
    spawned_by: main_agent
    forbidden_reuse: [parent_task, sibling_task, other_task, main_agent_active_execution_context]
    main_agent_roles: [orchestration, user_confirmation, conclusion_signoff]
    spawn_unavailable: fail_closed_unexecuted
  ontology_roles:
    - ontology_modeling
    - ontology_projection
    - ontology_conformance_verification
  execution_contract_fields:
    - work_product
    - required_actions
    - constraints
    - testable_signal
attributes:
  - name: method_lifecycle
    desc: PDCA 方法循环与单任务生命周期相互分离
    constraint: 方法阶段仅 plan/do/check/act；archive 是工作流终态；下一轮由新任务承载
    testable_signal: "检查 pdca_spec.method_phases、workflow_terminal 与 next_cycle 的取值，并运行 ontology-validate"
  - name: ontology_topology
    desc: 权威本体图经任务有界子图投影为执行树或 DAG
    constraint: 图是语义结构；树驱动是任务投影和执行原则；两者不得互相替代，执行投影必须保持依赖可追溯
    testable_signal: "检查 pdca_spec.topology=ontology_graph、design_core=ontology_tree_driven、task_projection_pipeline 三层有序且 execution_projections 同时包含 tree 与 dag"
  - name: semantic_serialization_boundary
    desc: 本体语义节点与其 Markdown 序列化资产分离
    constraint: 文件是 pdca.asset/v1 编码载体，不是本体语义本身
    testable_signal: "检查正文含语义节点与序列化载体的明确区分，并运行 ontology-validate"
  - name: ontology_responsibilities
    desc: Do 阶段只使用三个专业本体职责
    constraint: 职责集合固定为 modeling、projection、conformance verification；工具不属于职责集合
    testable_signal: "检查 pdca_spec.ontology_roles 恰含三个值且 execution_contract_fields 恰含四个必需字段"
  - name: fresh_task_agent_context
    desc: 每个 PDCA 任务及每个子任务一对一绑定由主 Agent 派生的全新子 Agent 执行上下文
    constraint: 禁止复用父任务、兄弟任务、其他任务或主 Agent 的活动执行上下文；主 Agent 只负责编排、用户确认和结论签审；agent.spawn 不可用时 fail-closed 并保持任务未执行
    testable_signal: "检查 pdca_spec.task_agent_context 的 execution_agent_kind、allocation、spawned_by、forbidden_reuse、main_agent_roles 与 spawn_unavailable，并扫描权威本体不存在主 Agent 执行回退"
---
# pdca

PDCA 是基于科学方法的四阶段持续改进模型，也是本仓库 PDCA 子本体的聚合根。常见资料会把 PDCA 称为 Shewhart Cycle 或 Deming Cycle，但历史上 Deming 明确采用并强调的是 PDSA；本仓库沿用 PDCA 作为工作流名称，不把常见别名当作无保留的历史归因。

方法阶段为 `plan → do → check → act`。`archive` 不是 PDCA 方法阶段，而是单任务工作流的终止状态。Act 产生的新认识通过一个新 Task 进入下一轮 Plan；已经 archive 的任务不重新打开，也不在同一任务内部形成转换环。

## 设计核心：本体树驱动

本体由语义节点、属性、约束和关系构成，是一张允许多关系和多父关联的本体图。`ontology/<type>/<slug>.md` 是节点的 `pdca.asset/v1` 序列化载体，便于审查、版本控制和验证，但文件本身不等同于本体语义。

“本体树驱动”的准确结构是：**权威本体图 -> 任务有界子图 -> 执行树/DAG**。权威本体图表达语义节点、属性、约束及多重关系；任务只选取与其目标和依赖相关的有界子图；执行器再把该子图投影为可调度的树或 DAG。图是权威语义结构，树驱动是任务投影和执行原则，两者不得互相替代，也不得把 Markdown 文件或执行树反向当作本体语义本身。执行叶节点必须单一职责、可独立验证，并具有明确退出判据。

## 子 Agent 上下文隔离不变量

主 Agent（协调器）必须为每个 PDCA 任务以及拆出的每个子任务，在开始任何任务工作前派生一对一的**全新子 Agent/子智能体上下文**。子 Agent 只能通过已落盘的 PRD、任务元数据、证据和 context pointer 接收跨任务输入；不得继承或复用父任务、兄弟任务、其他任务或主 Agent 的活动执行上下文。

主 Agent 只负责任务编排、用户确认和结论签审，不得直接实施任务或子任务。`agent.spawn` 是任务执行的必需能力；不可用时必须 fail-closed，任务保持未执行，不产生 Do 产物或执行证据，也不得回退到主 Agent 或任何既有子 Agent 上下文。

## 核心构成

根节点通过 `relations.composed_of` 机读声明任务、阶段、转换、门禁、验收标准、证据、判定、执行契约、恢复、反馈和持续改进。`pdca-flow-model` 是这些概念的过程化组织，`executor-adapter` 是实现侧关联，不属于方法论组成部分。

## 本体职责

- `ontology_modeling`：建立或修订语义节点、属性、约束和关系，从聚合目标推进到可验证叶节点。
- `ontology_projection`：把已确认的本体约束投射为代码、文档、配置或其他实现资产，并按依赖从叶到根聚合。
- `ontology_conformance_verification`：对本体及其投射产物执行符合性验证，形成可追溯判定。

三者是 Do 阶段的专业职责，不是新的生命周期阶段。具体工具仅作为执行适配器；工作范围由 `work_product`、`required_actions`、`constraints` 和 `testable_signal` 构成的执行契约决定。

## 来源边界

- PDCA 的循环用法与常见别名：ASQ, “PDCA Cycle” (`https://asq.org/quality-resources/pdca-cycle`)。
- Deming 对 PDSA 的采用及其与 PDCA 的区分：The W. Edwards Deming Institute, “PDSA Cycle” (`https://deming.org/explore/pdsa/`)。
