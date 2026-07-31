---
schema: pdca.asset/v1
id: knowledge:information-architecture.decision-disposition-gates
layer: knowledge
summary: 用 Verdict 与 Knowledge Disposition 将 Check 和 Act 转换为可验证、可重放的机器门禁
tags: [pdca, decision, knowledge, runtime, idempotency]
scenarios: [default, research, technical-design]
phases: [check, act]
applies_when: [工作流需要自动推进判断与知识沉淀阶段]
excludes_when: [只读取历史 schema 1 或 schema 2 任务]
source_ids: [experience:T0016--07-26-实现结构化检查判定与知识处置闭环]
confidence: high
status: active
---

# Decision / Disposition 双门禁

## 原则

Check 回答“实验事实意味着什么”，Act 回答“这个结论如何进入未来任务”。两者不是同一事实，
必须分别形成不可变、内容寻址的 Verdict 与 Knowledge Disposition。

## Verdict 契约

Verdict 至少绑定 task、record、scenario digest、Experience digest、完整 Evidence 集合、
outcome、reason 与 next action。`confirmed/rejected/partial` 都进入 Act；负结果的 next action
由 failure policy 给出，而不是通过跳过 Act 实现。

## Disposition 契约

Disposition 绑定 Verdict、knowledge policy、outcome 与投影回执。`projected` 必须引用
Knowledge Manifest 中与当前 Experience source/digest 匹配的完整回执；非投影结果必须明确为
`not_reusable`、`task_only` 或 `policy_none`。处置封存后禁止继续新增投影。

## 自动转换

自动 Check/Act 转换必须在单一 coordinator lock 内执行 CAS，并在 task 中先写入绑定 decision
ID、decision digest、scenario digest 与 next action 的 transition receipt。重试逐项复验 receipt；
归档后从 archive 查找任务并恢复 stale active marker，成功重试返回 `already_advanced`。

## Validator 语义

`confirmed` 要求 required Validator 为 pass；`rejected/partial` 要求 Validator 已被观察，
允许 fail 成为否证数据。否则负结果会被错误阻塞在 Check，无法完成知识处置。

## 兼容边界

新任务使用 schema 3 强制双门禁；历史 schema 1/2 保持可读和原生命周期兼容。手工与自动路径
共享 decision 和 seal 漂移验证，Runtime Journal phase exit 只约束自动推进。
