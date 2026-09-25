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
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: TASK-01：任务是固定本体工作节点在一个场景中的独立执行实例
---

# TASK-01：任务绑定本体节点、场景与独立执行者

每个正式 task 必须对应一个已经定义的 `work_id/node_id/scene/attempt`。
Task 不是任意 prompt 容器，而是**固定 ontology/work node 在某个场景中的执行实例**。

根、内部组合节点、叶都可以有 task；同一 `node_id` 的 model / implement / verify 是不同 scene task，
但必须引用同一个语义节点和兼容的 ontology revision，不能在后续场景静默改职责。

## Task 必须固定的身份

Task 至少绑定：

- `task_id` / `attempt`；
- `work_id` / `tree_revision` / `node_id`；
- `ontology_revision`；
- `scene`；
- 对应 ontology object/work instance refs；
- 当前节点 responsibility、I/O、AC/oracle；
- parent seed / composition relation；
- dependency refs 及其固定可用交付；
- CONTEXT-01 选择出的 minimum sufficient context refs；
- allowed record/product scope；
- 用户创建授权来源。

这些信息可以复用现有 task / assignment / baseline 的 refs 表达，不要求新增一套 subgraph schema。

## 一个任务一个独立可交互 Agent

不同正式任务使用真实独立 Agent／会话；同一任务的 Plan、Do、Check、Act 保持原绑定。
Agent 类型名、角色名和四份文本不证明独立运行。

创建必须由用户明确选定具名任务。父只传固定 task seed 和 CONTEXT-01 选择出的必要 refs，
不传父/兄弟完整活动历史，不替 child 规划或批准阶段，不监控其过程。

新 Agent 在 Plan 前向用户说明本任务目标、范围、预期产物和约束；Plan 未启动前不执行正式业务动作。
子 Agent 可以基于自己的 ontology node 发现新的 child seed，但不能自动派发后代。

## 上下文独立

Task 的独立性不仅是“不同 Agent”，还包括输入隔离：

```text
task context
  = current node
  + required relation endpoints
  + fixed parent seed
  + required dependency deliverables
  + applicable shared invariants
  + original requirement/AC
  + current scene inputs
```

显式排除：

- 父/兄弟完整 conversation；
- 兄弟任务中间思考和临时假设；
- 未采用 reference；
- 与当前 node 无关的 ontology 分支；
- 仅因为“可能有用”而附带的项目历史。

需要额外信息时由当前 Agent根据真实缺口追加具名输入；不能默认扩大为整个仓库/ontology/history。

## 恢复与阶段

逻辑身份允许进程重启／上下文压缩，但必须恢复同一 task、同一 attempt、同一绑定和固定输入。
原会话丢失不允许新建冒充恢复；需要新执行者时先安全结束旧 attempt，再由用户明确启动新 attempt。

每阶段结束保存事实并等待。一次获准阶段内可自主执行；禁止自动进入下一阶段／scene／attempt。
统一 UI 可以无损路由用户消息，不能让父 Agent 代答。

对应记录契约：[task](../contracts/record-shapes/task.md)、
[assignment](../contracts/record-shapes/agent-assignment.md)、
[dispatch](../contracts/record-shapes/dispatch.md)。
