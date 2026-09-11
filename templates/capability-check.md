---
schema: pdca.capability-check/v1
check_id: null
scope_kind: null
work_id: null
task_id: null
attempt: null
checkpoint: null
environment_revision: null
observed_control_revision: null
checks: []
checked_at: null
time_source_ref: null
supersedes_ref: null
checker_ref: null
limitations: []
protocol_revision: 3.4.10
---

# 实际能力核验草稿

每项checks含capability、actual_tool/backend、available/missing/unknown、授权scope、原始evidence_ref/digest、环境/身份和限制。checkpoint按CAP-01，包括派发、Plan探测、Plan→Do、动作前、恢复与环境变更。

## 正负控制与失败

只用授权隔离环境探测。Agent自述不是隔离/排他证据；控制样本能测什么必须说明，不能把测试fixture用作用户批准。缺必需能力阻断相关动作；解除blocked需新证据覆盖原缺项、原授权仍有效，不能伪造恢复时间。

有限维护profile及fixture边界见[生命周期记录契约](../ontology/contracts/lifecycle-records.md)。字段和摘要通过不认证真实宿主能力；不得把示例复制成执行事实。

## 新Agent完整任务与并发（agent-dispatch.1）

按[CAP全流程/并发](../ontology/concept/capability-protocol.md#cap-full-agent-and-parallel)分别记录 spawn_fresh、task.full_pdca、task.interaction、user.confirm、host.dispatch_async、host.capacity、host.events、fs.task_scope。每项使用原checks的capability/actual_tool/status/scope/evidence_ref/digest/limitations；未知保持unknown，任务书不是实际能力证据。

另用 `task.assignment` 项固定[完整任务书](agent-assignment.md)的引用和摘要，status表示绑定可核验而非任务已执行；实际spawn回执应绑定同一内容。调度观测来源及资格在host.schedule项中具名关联，禁止循环摘要：先固定依据/任务书，后实际事件，再外层封存本轮观测。

## 适用环境与本次调用分别证明

按[CAP两层核验](../ontology/concept/capability-protocol.md#cap-environment-and-call)，复用环境依据须说明适用版本/权限/模型/记忆配置未发生相关变化；实际创建/继续的参数、输入、原生身份和当前控制另行关联。旧环境的available不是新调用的成功；unknown保留缺项。前台等待不是上下文隔离，独立会话不是文件排他。
