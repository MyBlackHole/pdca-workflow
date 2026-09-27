---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# 原生派发契约 v4

agent-dispatch 只负责**一次正式 task 的原生创建事务**。
Task 身份由 TASK-01 定义，上下文由 CONTEXT-01 选择，宿主资格由 CAP-01 判断，
用户创建授权由 CONFIRM-01 提供；本契约不复制这些规则。

Do-only Work Unit 不进入本契约，按 CONTRACT-01 执行。

## 创建前提

创建前必须已经存在并固定：

1. TASK-01 合法的 task/attempt 身份；root bootstrap 的例外也由 TASK-01 判定；
2. CONTEXT-01 选出的 assignment refs，以及 task seed / creation authorization 已固定的初始 record/product scope；
3. 适用于当前宿主/配置的 CAP-01 能力证据；
4. 用户针对该具名 task 的未撤销 creation authorization；
5. 唯一 `dispatch_request_id`，以及本任务 record/control scope 的实际写权。

精确字段分别写入 [task](record-shapes/task.md)、
[assignment](record-shapes/agent-assignment.md) 和
[dispatch](record-shapes/dispatch.md)；不要在本页维护第二份字段清单。

## 原生创建一次

1. 从固定 task + CONTEXT-01 结果物化 assignment；不得临时追加父/兄弟活动历史。
2. 使用现场已核验的宿主原生 new/create 能力提交唯一 dispatch request。
3. 保存真实调用参数、原生 receipt、Agent/conversation 身份及可观察的隔离证据。
4. 核对返回对象仍绑定同一 task/attempt/assignment；无法确认时保持 unknown。
5. accepted 后，新 Agent 只展示自己的 Plan 目标并等待用户 `phase_start`；创建授权不能直接启动 Plan。

父 Agent 不轮询、不推进该 task 的 phase、不代答用户，也不在创建成功后继续“帮它执行”。

## 结果

| 创建结果 | 处理 |
|---|---|
| accepted | 固定 dispatch/assignment/原生身份后停止；后续交互回该 Agent |
| unknown | 保留原 request 与可能占用，只对账同一 request；不得再次创建或换 attempt 绕过 |
| blocked / error | 保留事实与 limitation；能力/权限/输入未满足时不声称 task 已执行 |

恢复既有 task、继续原 Agent、迟到返回和输入失效不属于“新建派发”：
分别按 entry-recovery / RECOVERY-01 / DEPENDENCY-01 处理，不能通过再次 dispatch 解决。

没有原生可交互、可继续、可核查初始上下文的宿主能力时，可以给出非正式分析，
但不得把它记录为正式 task 已派发或已运行。
