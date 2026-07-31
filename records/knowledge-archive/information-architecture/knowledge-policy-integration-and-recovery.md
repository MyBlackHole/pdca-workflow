---
schema: pdca.asset/v1
id: knowledge:information-architecture.knowledge-policy-integration-and-recovery
layer: knowledge
summary: 用真实 Scenario Contract 验证 Knowledge policy，并在归档重放时 fail-closed 处理 stale marker
tags: [knowledge, policy, recovery, integration]
scenarios: [technical-design, default]
phases: [act]
applies_when: [需要验证知识处置矩阵或归档恢复]
excludes_when: [需要进程级 crash failpoint 的测试]
source_ids: [experience:T0017--07-26-补充知识策略集成与归档恢复测试]
confidence: high
status: active
---

# Knowledge Policy 集成与归档恢复规则

四种 knowledge policy 必须在真实 Scenario Contract 的生命周期中验证，而不只依赖单元矩阵：

- `always` 只接受 `projected`；
- `when_reusable` 接受 `projected`、`not_reusable`、`task_only`；
- `task_only` 只接受 `task_only`；
- `none` 只接受 `policy_none`。

Runtime Act 归档重放时，先验证 archived task 的 Disposition、receipt、scenario digest 和
decision digest，再处理 active marker。marker 指向当前归档任务时清除并返回
`already_advanced`；指向其他任务时 fail-closed，避免误删或跨任务恢复。
