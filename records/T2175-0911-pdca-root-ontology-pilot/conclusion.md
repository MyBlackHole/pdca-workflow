---
schema: pdca.asset/v1
id: T2175-0911-pdca-root-ontology-pilot
phase: check
source_ids: [pdca-root-model, root-validation, convergence-map]
---

## 上下文

本轮是 PDCA 流程本体建模的受控试点，只重构 `ontology:concept/pdca` 根节点及维持正确关系方向所必需的核心概念父关系，不判定完整流程本体已经完成。

## 假设与结果

假设：先修正根节点，可以验证“本体图作为权威、执行树/DAG 作为投影”的建模方法，并为后续逐节点建模提供稳定聚合边界。

结果：根节点现在具有机读组成关系和 `pdca_spec`；历史归因、生命周期、拓扑、序列化边界、职责和执行契约边界已明确。本体结构校验及任务收敛校验均通过。

## 分析

- **AC-1** ✅ 已区分 PDCA 常见别名与 Deming 实际采用的 PDSA，并登记来源边界。（pdca-root-model, root-validation）
- **AC-2** ✅ 已明确本体为图，任务执行为树或 DAG 投影。（pdca-root-model, root-validation）
- **AC-3** ✅ 已明确语义节点与 Markdown `pdca.asset/v1` 序列化载体分离。（pdca-root-model, root-validation）
- **AC-4** ✅ 根节点以 `composed_of` 连接 11 个核心概念，并以 `relates_to` 连接流程模型和执行器适配器。（pdca-root-model, root-validation）
- **AC-5** ✅ `pdca_spec` 恰声明三个专业职责，未引入 A/B/C 或六场景控制字段。（pdca-root-model, root-validation）
- **AC-6** ✅ 根本体不再绑定具体 Python 文件，实现被限定为后续投射层消费者。（pdca-root-model, root-validation）
- **AC-7** ✅ `ontology-validate` 与 `validate-convergence` 均通过，无悬空关系或关系环。（root-validation, convergence-map）

## 适用边界

本结论只确认根本体建模方法和根节点产物。三个职责尚无独立 role 节点，执行契约、恢复、反馈及流程完整性规范仍需后续逐节点建模；不得据此宣称完整 PDCA 流程本体已完成。

## 下一轮建议

确认本试点后，返回 T2170 重新拆分 WBS：按一个本体节点一个任务补建三个 role 节点，分开 recovery 与 feedback，并把 `pdca-flow-model` 留作最后聚合任务。

---

## 复审结论 v2（取代上述初始判定）

### 上下文

初始 Check 后，用户连续纠偏了“本体树驱动”、专业职责命名、子 Agent 执行边界及任务独立性。任务回滚至 Do 完成修订后，本次只审查当前独立 PDCA 的本体定义、实现产物和证据，不检查、控制或聚合其他任务。

### 假设与结果

假设成立：PDCA 根本体可以同时保持“权威本体是图”和“本体树驱动是执行设计原则”，并以独立任务、一对一全新子 Agent、协调挂起及恢复后的本体实现符合性验证形成明确执行不变量。

结果成立：根本体及必要关联节点已完成修订，当前有效证据覆盖 AC-1 至 AC-10；本体校验、收敛校验、技能索引校验及旧控制语义定向扫描均通过。

### 分析

- **AC-1** ✅ 已准确区分 PDCA 的常见称谓与 Deming 实际采用的 PDSA，未再作无保留历史等同。（pdca-root-model-v4, root-validation-v5）
- **AC-2** ✅ 已明确权威流程本体是图，任务执行是从有界子图投影出的树或 DAG。（pdca-root-model-v4, root-validation-v5）
- **AC-3** ✅ 已明确本体语义节点与 Markdown `pdca.asset/v1` 序列化资产不是同一概念。（pdca-root-model-v4, root-validation-v5）
- **AC-4** ✅ 根节点已用 `composed_of` 和 `relates_to` 机读连接任务、阶段、转换、门禁、验收、证据、判定、执行契约、恢复、反馈、持续改进、流程模型与执行器边界。（pdca-root-model-v4, root-validation-v5）
- **AC-5** ✅ 核心职责仅保留 `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification`，A/B/C 与六场景不再承担控制语义。（pdca-root-model-v4, root-validation-v5）
- **AC-6** ✅ 根本体未绑定具体 Python 文件，runtime 被限定为后续 `ontology_projection` 的消费者。（pdca-root-model-v4, root-validation-v5）
- **AC-7** ✅ `ontology-validate`、`validate-convergence` 与技能索引校验通过，根节点未发现悬空关系或关系环。（root-validation-v5, convergence-map-v7）
- **AC-8** ✅ 已保留“设计核心：本体树驱动”，并固定“权威本体图 -> 任务有界子图 -> 执行树/DAG”三层结构。（pdca-root-model-v4, root-validation-v5）
- **AC-9** ✅ 已声明每个 PDCA 是独立完整循环，由一对一全新子 Agent 自主执行；协调上下文派发后进入 `suspended_waiting_agent`，恢复时只读取当前任务持久化产物并执行 `ontology_conformance_verification`，禁止跨任务检查。（pdca-root-model-v4, root-validation-v5）
- **AC-10** ✅ 已将 `agent.spawn` 定义为必需能力，不可用时 `fail_closed_unexecuted`，且不得回退到主会话执行。（pdca-root-model-v4, root-validation-v5）

### 失败纠正

初始版本遗漏“本体树驱动”核心原则，并把协调恢复错误地描述成对子任务的检查。两项偏差均经回滚、用户纠偏和重新执行修正；本次判定不沿用初始证据或初始 AC-1 至 AC-7 结论。

### 适用边界

本次确认的是 PDCA 根本体及必要关联节点的**本体建模结果**。`config/capabilities.yaml`、`scripts/pdca-doctor.py` 和相关测试仍保留旧的主会话回退行为，属于下一轮 `ontology_projection` 的已知实现差距；在该投射完成前，不得宣称运行时已经强制执行 `agent.spawn` fail-closed。

### 下一轮建议

建立独立的 `ontology_projection` PDCA，把已确认的子 Agent 隔离、协调挂起、当前任务产物恢复和 fail-closed 约束投射到配置、runtime 与回归测试。

### 判定

- outcome: confirmed
- reason: AC-1 至 AC-10 均由当前有效证据覆盖，本体实现符合性审查与结构校验通过；已知 runtime 差距在本任务明确排除的投射范围内。
- verdict_id: V-T2175-20260911-R2
- at: 2026-09-11T15:03:29+08:00

## 本体沉淀

- disposition: ontology
- 已沉淀：`ontology:concept/pdca`、`ontology:concept/pdca-task`、`ontology:concept/capability-protocol`、`ontology:concept/executor-adapter`、`ontology:process/flow-do`、`ontology:process/pdca-flow-model`。
- 来源：`records/T2175-0911-pdca-root-ontology-pilot`；本轮把“本体树驱动”、三个专业职责和独立 PDCA 的子 Agent 执行不变量固化为可复用权威知识。
- 处置边界：Act 回顾发现 `AGENTS.md`、`ontology:process/flow-act`、`ontology:concept/pdca-phase` 仍有旧 `scenario_type`、六场景或“6 路由”措辞。这属于仓库级旧场景语义清理缺口，应先由新的独立 `ontology_modeling` PDCA 处理，再进行 runtime `ontology_projection`；本任务不越过已确认范围修改。
