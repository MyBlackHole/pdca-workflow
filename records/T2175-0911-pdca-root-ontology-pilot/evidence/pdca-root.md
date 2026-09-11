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
owl_versionIRI: http://pdca.local/ontology/pdca/1.1.0
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
  execution_projections: [tree, dag]
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
    desc: 流程知识以本体图表达，执行计划是图的树或 DAG 投影
    constraint: 不把多关系本体图等同于树；执行投影必须保持依赖可追溯
    testable_signal: "检查 pdca_spec.topology=ontology_graph 且 execution_projections 同时包含 tree 与 dag"
  - name: semantic_serialization_boundary
    desc: 本体语义节点与其 Markdown 序列化资产分离
    constraint: 文件是 pdca.asset/v1 编码载体，不是本体语义本身
    testable_signal: "检查正文含语义节点与序列化载体的明确区分，并运行 ontology-validate"
  - name: ontology_responsibilities
    desc: Do 阶段只使用三个专业本体职责
    constraint: 职责集合固定为 modeling、projection、conformance verification；工具不属于职责集合
    testable_signal: "检查 pdca_spec.ontology_roles 恰含三个值且 execution_contract_fields 恰含四个必需字段"
---
# pdca

PDCA 是基于科学方法的四阶段持续改进模型，也是本仓库 PDCA 子本体的聚合根。常见资料会把 PDCA 称为 Shewhart Cycle 或 Deming Cycle，但历史上 Deming 明确采用并强调的是 PDSA；本仓库沿用 PDCA 作为工作流名称，不把常见别名当作无保留的历史归因。

方法阶段为 `plan → do → check → act`。`archive` 不是 PDCA 方法阶段，而是单任务工作流的终止状态。Act 产生的新认识通过一个新 Task 进入下一轮 Plan；已经 archive 的任务不重新打开，也不在同一任务内部形成转换环。

## 语义模型与存储边界

本体由语义节点、属性、约束和关系构成，是一张允许多关系和多父关联的本体图。`ontology/<type>/<slug>.md` 是节点的 `pdca.asset/v1` 序列化载体，便于审查、版本控制和验证，但文件本身不等同于本体语义。

复杂任务从本体图中选择目标节点和依赖关系，再投影为适合执行的树或 DAG。树是执行视图，不是本体本身。执行叶节点必须单一职责、可独立验证，并具有明确退出判据。

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
