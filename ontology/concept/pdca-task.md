---
schema: pdca.asset/v2
id: ontology:concept/pdca-task
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: TASK-01：一任务一可交互逻辑执行者
---

# TASK-01：一任务一可交互逻辑执行者

每个 work/tree/node/scene/attempt 唯一 task_id；根、内部组合节点、叶均有自己的完整 PDCA。不同任务使用真实独立 Agent／会话；同一任务的 Plan、Do、Check、Act 保持原绑定。Agent 类型名、角色名和四份文本不证明独立运行。

创建必须由用户明确选定任务；新 Agent 在 Plan 前与你沟通目标、范围、预期产物及约束。父只传固定 seed 和任务边界，不替子 Agent 规划或批准阶段，不监控其过程。子 Agent 可以提出分解候选，不能自动派发后代；用户选择后由宿主创建各自独立任务。

逻辑身份允许进程重启／上下文压缩，但必须恢复同一会话和必要任务状态。原会话丢失不允许新建冒充恢复；需要新执行者时先安全结束旧 attempt，再由用户明确启动新 attempt。

每阶段结束保存事实并等待。一次获准的阶段内自主执行，不需要父 Agent 逐步指挥；禁止自动进入下一阶段／场景／attempt。统一 UI 可无损路由用户消息，不能让父 Agent 代答。

输入只含公共规则、固定需求和具名允许材料；不继承其他任务完整活动历史，不通过共享记忆绕过。任务 record writer 为绑定 Agent；消息副本由可信来源导出，执行者可以抄录但不能认证自己编造的批准。

对应模板：[task](../../templates/task.md)、[assignment](../../templates/agent-assignment.md)、[dispatch](../../templates/dispatch.md)。
