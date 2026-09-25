---
schema: pdca.asset/v2
id: ontology:concept/pdca-execution-contract
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: CONTRACT-01：复用任务／计划／验收；Do 内使用有界 Work Unit
---

# CONTRACT-01：复用任务／计划／验收；Do 内使用有界 Work Unit

Plan 前把用户问题、目标、范围、非目标和预期产物写在任务说明与 `phase_start` 请求。
获准 Plan 后产出计划、固定输入、验收标准及测试设计；Plan 完成后仍等待新的 Do
`phase_start`。不另建 GoalContract／PhaseContract 体系。

任务计划至少明确：`work_product`、`required_actions`、`constraints`、
`testable_signal`。具体 AC 说明可检验的预期和失败边界；Claim—Evidence—Verdict
解释如何满足 AC，不能取代 AC 或事后修改 expected。

固定输入清单列真实 ref、sha256、角色（需求/本体/实现/工具/参考）和保存方式。
摘要固定内容，不证明真实执行或来源。冻结 oracle 改变需要新的用户决策与适当的新 run/attempt，
不得因测试失败放宽。

## Do-only Work Unit

Work Unit 是**当前已批准 Do 内的执行接口**，不是新的 PDCA task、不是第五阶段，也不是新的授权层。
它可以由原 Agent 内联执行，也可以委派给隔离上下文执行者或获准外部工具。

每个 Work Unit 使用：

`C=(I,O,S,R,T,Φ,Ψ)`

| 字段 | 必须固定的内容 |
|---|---|
| I — Inputs | 输入 ref/digest、前置产物、共享不变量 |
| O — Outputs | 预期输出、格式与落点 |
| S — Scope | 最小读域、写域和明确非目标 |
| R — Resources | 需要的资源、权限、预约与冲突条件 |
| T — Termination | completed/blocked/failed/cancelled/unknown 的终止条件和止损条件 |
| Φ — Completion | 可机械或证据化判断的完成判据 |
| Ψ — Evidence | 必须返回的证据以及允许声明的 claims |

Contract 只描述局部执行边界，不复制父 Plan，也不产生平行的 Goal/Phase 对象。
一个 Work Unit 超出 S/R、改变 O/Φ、需要新增不可逆副作用，或暴露新的独立业务目标时，
必须停止；不能在 Work Unit 内自行扩大父 Do 授权。

### minimum sufficient context

委派时只传完成 Contract 所需的局部输入、共享不变量和必要公共规则。
禁止默认复制父/兄弟完整对话、活动历史或未选择的知识资产。
需要额外上下文时，执行者返回 blocked/unknown 和缺口，由当前 Do 决定是否仍在原授权内补充。

### 结果

Work Unit 返回的结构至少包含：

```text
contract_id
termination
completion
outputs
evidence
claims
limitations
```

`termination` 表示执行如何结束；`completion` 对照 Φ；
`evidence` 支撑可复核事实；`claims` 只能声明 Ψ 允许且被证据支持的结论。
结果由当前 Do 写入既有 run/evidence，不要求新增持久化 schema。

### 调度与恢复

Work Unit 可有数据依赖和阻塞边；ready 只意味着在**当前已批准 Do**中可执行。
父 Do 可以依据固定依赖自主选择 ready Work Unit，但不自动创建正式任务。

父 Do 不轮询、不监工、不维护委派执行者生命周期。派发后只消费宿主原生完成事件、
固定结果或用户主动返回的结果。结果 unknown 时只对账原请求，不重复派发制造第二份副作用。

## 正式工作节点不是 Work Unit

正式节点首先必须来自固定 ontology/work instance 中的具名 object/node 与语义关系，
再按 [NODE-01](work-node-contract.md) / [DECOMP-01](task-decomposition.md)
验证独立职责、固定 I/O、可独立拒收成果和验证边界。
用户批准创建后，它绑定 node_id/ontology revision，由 fresh Agent 使用
[CONTEXT-01](../process/select-task-subgraph.md) 选择出的 minimum sufficient subgraph
执行完整 Plan→Do→Check→Act。

Work Unit 只是这个正式 task 的 Do 内局部执行切片，不能因为上下文很大、想并行或需要另一个执行者，
就反向创造新的 ontology responsibility 或正式节点。

各场景必需产物仍由 SCENE 与已批准目标共同确定。知识地图只有满足稳定对象身份、关系、约束、
来源和可检验性才可作为本体，不因叫 pdca-model 而自动合格。

记录格式在[记录契约索引](../contracts/record-shapes/index.md)，仅采用其中列出的 v4 schema 与示例。
