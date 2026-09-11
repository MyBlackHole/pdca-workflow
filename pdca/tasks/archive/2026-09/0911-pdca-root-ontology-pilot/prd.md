# 试点重构 PDCA 根本体

## 问题陈述

当前根概念把本体图描述成树、把 Markdown 文件等同于本体语义节点，机读关系不足，并直接绑定旧 Python 实现；PDCA/PDSA 历史关系也表述不准确。首轮改写又弱化了“设计核心：本体树驱动”，且既有能力协议允许任务回退到主会话执行，无法保证任务上下文隔离。本试点修正这些根层约束，以验证后续流程本体建模的方法和粒度。

## 范围

- `ontology:concept/pdca` 的定义、关系、构成、不变量和投影边界。
- 为根节点关系完整及消除 Agent 隔离语义冲突所必需的 PDCA 本体、流程和领域技能节点。
- 不创建或重构 Python runtime；实现差距作为后续投射工作记录。

## 验收标准

- [ ] AC-1（回链父 AC-2）: 准确区分 PDCA 与 Deming 的 PDSA，不再把常见别名写成无保留历史事实。
- [ ] AC-2（回链父 AC-1）: 明确流程本体是图，任务拆解与执行可从图投影为树或 DAG。
- [ ] AC-3（回链父 AC-1）: 明确本体语义节点与 Markdown 序列化资产不是同一概念。
- [ ] AC-4（回链父 AC-1）: 根节点 frontmatter 以机读关系连接任务、阶段、转换、门禁、验收、证据、判定、执行契约、恢复、反馈和持续改进。
- [ ] AC-5（回链父 AC-3）: 三个专业职责作为后续待建模概念被引用，不使用 A/B/C 或六场景控制字段。
- [ ] AC-6（回链父 AC-9）: 根本体不绑定具体 Python 文件；实现仅作为后续投射层消费者。
- [ ] AC-7（回链父 AC-8）: `python3 scripts/ontology-validate.py --ontology-dir ontology` 通过且根节点无悬空关系或关系环。
- [ ] AC-8（纠偏）: 保留“设计核心：本体树驱动”，并明确其结构为“权威本体图 -> 任务有界子图 -> 执行树/DAG”，不得用“本体是图”替代产品设计原则。
- [ ] AC-9（纠偏）: 每个 PDCA 任务都是独立完整循环，必须由一对一的全新子 Agent 执行；派发后协调上下文进入 `suspended_waiting_agent` 并停止运行，恢复时只读取当前任务自身的 `task.json`、transition receipts、evidence manifest 和产物，不检查或聚合其他子任务，并进入 `ontology_conformance_verification` 审查本体、实现/产物与证据的一致性。
- [ ] AC-10（纠偏）: `agent.spawn` 不可用时任务必须 fail-closed 并保持未执行状态，本体权威来源不得再声明回退到主会话执行。

## 关联本体节点

`ontology:concept/pdca`、`ontology:concept/pdca-task`、`ontology:concept/capability-protocol`、`ontology:concept/executor-adapter`、`ontology:process/flow-do`、`ontology:domain/skill-to-tickets`

## 拆分映射

- PDCA 根本体 -> ontology:concept/pdca
- 任务上下文隔离不变量 -> ontology:concept/pdca-task
- Agent 创建能力与阻断语义 -> ontology:concept/capability-protocol、ontology:concept/executor-adapter
- 执行与子任务调度约束 -> ontology:process/flow-do、ontology:domain/skill-to-tickets
