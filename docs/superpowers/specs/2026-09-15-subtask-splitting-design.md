# Do 工作单元与正式工作节点拆分设计

> 本文是设计说明。运行权威以
> [DECOMP-01](../../../ontology/concept/task-decomposition.md)、
> [CONTRACT-01](../../../ontology/concept/pdca-execution-contract.md)、
> [SCHED-01](../../../ontology/concept/work-tree-scheduling.md)、
> [CONFIRM-01](../../../ontology/concept/pdca-ai-friendly-confirmation.md)
> 和当前 Skill 为准。

## 1. 为什么重构

旧设计把“执行切片”和“正式 PDCA 子任务”混在一起，并引入 LOC/工时/置信度阈值、
父任务协调、Agent 资源池、自动冲突裁决和生命周期监控。这会产生四个问题：

1. 一个 Do 被拆成多个新的 Plan→Do→Check→Act，授权成本和上下文成本急剧放大。
2. 父 Agent 变成调度器/监工，与“不轮询、不接管子 Agent”冲突。
3. 500 LOC、40h、0.7 等阈值与业务可验收边界没有稳定关系。
4. 执行器被绑定到特定 subagent/并发模型，降低跨宿主可移植性。

当前设计只保留两个层次：**正式工作节点**与 **Do-only Work Unit**。

## 2. 正式工作节点

正式节点表达独立业务/工程义务，而不是执行步骤。

只有同时满足以下性质时才建议成为候选节点：

- 有独立职责；
- 输入/输出可固定；
- 成果可以被独立接受或拒收；
- 有独立验证边界；
- 与父节点之间可以写清组合责任和依赖。

Plan 只产生 seed 和理由。节点 ready 不等于授权创建；用户明确批准工作级创建操作后，
宿主才创建独立 Agent。每个正式节点运行完整 Plan→Do→Check→Act，
并遵循自己的阶段授权。

父 Agent 不轮询该 Agent，不推进其阶段，不代写结果。宿主事件或用户主动打开会话
是正式任务状态变化的入口。

## 3. Do-only Work Unit

Work Unit 是一个已批准 Do 内的最小充分执行单元。

它具有以下性质：

- 不创建 task/attempt；
- 不拥有独立 Plan/Check/Act；
- 不要求用户对每个 Work Unit 再做 phase_start；
- 不改变父 Plan 的目标、AC/oracle、写域和资源边界；
- 可以 inline、delegated 或 external；
- 委派时使用隔离上下文，但不复制父任务完整历史。

### 3.1 Contract

每个 Work Unit 使用：

`C=(I,O,S,R,T,Φ,Ψ)`

| 字段 | 内容 |
|---|---|
| I | 固定输入、ref/digest、共享不变量 |
| O | 期望输出、格式和落点 |
| S | 最小读/写作用域与非目标 |
| R | 所需权限、资源和预约 |
| T | 完成、阻断、失败、取消、unknown 的终止条件 |
| Φ | 可验证完成判据 |
| Ψ | 必须返回的证据与允许声明的 claims |

示例：

```yaml
contract_id: wu-do-003
I:
  - plan_ref: records/tasks/T42/plan.md
  - source_digest: sha256:...
O:
  - path: src/index.rs
S:
  write:
    - src/index.rs
  deny:
    - Cargo.toml
R:
  - repo_write_reservation
T:
  stop_if:
    - requires_schema_change
    - resource_result_unknown
Phi:
  - unit_test_index_insert_passes
Psi:
  evidence:
    - command
    - exit_code
    - output_digest
  claims:
    - index_insert_behavior
```

### 3.2 Result

执行结果至少返回：

```yaml
contract_id: wu-do-003
termination: completed | blocked | failed | cancelled | unknown
completion:
  satisfied: true
outputs: []
evidence: []
claims: []
limitations: []
```

父 Do 只消费固定结果，不从“做完了”“应该可以”等文字推断完成。

## 4. minimum sufficient context

委派 Work Unit 时只给：

- Contract；
- I 中固定输入；
- 当前节点必要模型/接口；
- 共享不变量；
- 完成该单元需要的公共规则。

不传父/兄弟完整活动对话，不注入未采用知识库，不把父 Agent 的推理摘要当事实来源。
执行者缺信息时返回 blocked/unknown 和明确缺口。

## 5. 调度而非监控

Work Unit 可以声明数据依赖：

```text
WU-A ──> WU-C
WU-B ──> WU-C
```

A/B 的固定结果都满足后，C 在当前已批准 Do 范围内变为 ready。
父 Do 可以选择 ready 单元继续，但不建立轮询循环、不维护 Agent pool、
不做后台进度监控。

委派后只有以下结果入口：

- 宿主原生 completion/event；
- 固定外部工具结果；
- 用户主动返回/打开的结果。

unknown 只对账原请求，不重复派发。

## 6. 什么时候必须回到用户

Work Unit 出现以下任一情况就停止：

- 新增目标或交付；
- 修改 AC/oracle；
- 扩大读/写域；
- 需要新的资源权限；
- 引入新的不可逆副作用；
- 发现可独立拒收的新正式工作节点；
- 原输入/版本已失效。

这些都不是“执行细节”，不能由 Work Unit 自行批准。

## 7. 不再使用的机制

当前设计删除以下运行语义：

- `estimatedLOC > 500`；
- `estimatedTime > 40h`；
- `agent.confidence < 0.7`；
- 固定 max split depth；
- 父任务持续跟踪子任务；
- Agent 资源池与自动扩缩；
- 自动协调失败后由父任务裁决；
- 通过 ready/frontier 自动创建正式任务。

它们可以作为历史研究材料，但不能作为当前授权或调度依据。

## 8. 迁移

不原地改写既有活动任务记录。恢复旧任务时继续核对其原规则 Git 来源、原授权和原事件；
若旧记录与当前 Work Unit 语义冲突，报告差异并停止，不伪造迁移。

新的 Plan/Do run 使用本设计。旧的历史设计文档不具有高于当前 normative ontology 的权限。
