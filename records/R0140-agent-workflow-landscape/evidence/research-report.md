# 外部 Agent 工作流与本地 PDCA 对比调研

访问日期：2026-07-28  
证据范围：官方文档、官方仓库、本地可执行测量。

## 摘要

本地 PDCA 不应被 LangGraph、AutoGen、CrewAI 或 OpenAI Agents SDK 整体替换。它们主要解决“单次或长时 Agent 如何运行”，本地 PDCA 主要解决“任务为何执行、何时允许推进、结论如何确认、证据和知识如何留存”。两类系统是互补层，不是同类排行榜。

本地 PDCA 的突出优势是：

- 阶段语义、用户签审、证据 digest、验收条件映射和 Git 记录组成强治理链。
- 无模型、数据库或云服务依赖，首次执行和长期维护成本低。
- 对开发、调研、设计、文档和审查使用统一生命周期。
- 已有 15 个合约/操作测试、12 个故障与正常场景夹具、53 个入口引用检查。

主要短板是：

- 恢复粒度停留在 phase/task 文件，弱于 LangGraph 的节点 checkpoint 与 replay。
- 人类确认是阶段级，弱于 OpenAI Agents SDK 和 GitHub Agentic Workflows 的具体工具/副作用级审批。
- 没有统一的运行时事件、模型调用、工具调用、handoff、延迟和 usage trace。
- 没有通用 safe-output 执行层或工具沙箱；安全更多依赖流程规则和具体脚本。
- 全库严格校验仍被 16 个旧格式活跃任务污染，降低全局校验信号质量。

结论：当前最科学的方向是保留 PDCA 治理层，只在出现真实执行器和消费者时吸收细粒度运行时机制；现在直接引入完整外部框架会增加依赖和上下文，不足以证明 AI 更准或更快。

## 方法与证据等级

能力矩阵使用 `native/configurable/external/not-found`，不计算综合总分。

- `official-claim`：官方资料证明接口或机制存在，不能单独证明实际更快、更准。
- `local-measurement`：当前仓库命令的可重复结果。
- `inference`：由机制推出的工程判断，必须给出限制或反证条件。

完整来源在 `evidence/source-inventory.jsonl`，机器矩阵在 `evidence/comparison-matrix.json`。

## 逐项目比较

### LangGraph

优势：

- 内置 checkpoint、状态历史、pending writes、replay 和 fork，失败后可以从成功节点恢复，明显强于本地 phase 级备份。[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- `interrupt` 可保存状态、等待人工批准/编辑后恢复；官方明确要求副作用幂等，恢复语义清楚。[Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- 已完成 task 结果可在恢复时复用，避免重复模型/API 调用。[Functional API](https://docs.langchain.com/oss/python/langgraph/functional-api)

相对本地 PDCA 的劣势：

- 必须把任务拆成节点、可序列化状态和幂等副作用，工程接入成本远高于 Markdown/JSON 文件协议。
- 核心运行时不替应用定义 PRD、结论确认、知识处置或不可变 evidence。
- 完整 tracing/evaluation 通常依赖 LangSmith；核心资料未显示类似 GitHub safe outputs 的默认副作用边界。

适合：有真实长时 Agent、昂贵中间步骤、崩溃恢复需求的执行层。  
不适合：仅为了改进当前人工驱动 PDCA 而整体引入。

### Microsoft AutoGen

优势：

- 提供 RoundRobin、Selector、Swarm 等团队模式，以及消息数、token、timeout、handoff 等可组合终止条件。[Teams](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html) [Termination](https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/termination.html)
- 支持 team state 的 save/load；有 pause/resume 和 OpenTelemetry tracing。[Team API](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html) [Tracing](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tracing.html)
- 官方明确建议简单任务先用单 Agent，只有单 Agent 不足时才升级团队，这与本地 `agent.spawn` 缺失时走主会话的策略一致。

相对本地 PDCA 的劣势：

- 多 Agent 共享上下文和轮次容易增加 token、协调及终止设计成本；“更多 Agent”本身不证明准确度更高。
- pause/resume 是实验能力，自定义 Agent 需自行正确实现，运行中保存状态还可能不一致。
- 终止条件解决“何时停止对话”，不等价于本地 PRD/证据/结论门禁。
- 所审核心资料未发现默认最小权限或 safe-output 写边界。

适合：确有角色专长和交互必要性的动态协作。  
不适合：把所有 PDCA 子任务默认转换为多 Agent 对话。

### CrewAI

优势：

- Crew 负责开放式协作，Flow 提供事件、路由、结构化状态和持久化，抽象层次比 LangGraph 更高。[Flows](https://docs.crewai.com/en/concepts/flows)
- Task 可使用 Pydantic 输出、确定性函数 guardrail、LLM guardrail、重试及人工 review。[Tasks](https://docs.crewai.com/en/concepts/tasks)
- Agent 提供 `max_iter`、`max_rpm`、timeout、cache、context-window 和 retry 控制；Flow 能汇总 token usage。[Agents](https://docs.crewai.com/en/concepts/agents)

相对本地 PDCA 的劣势：

- Crew 与 Flow 双范式、Agent/Task/Process 配置增加选择和调试面。
- 许多正确性、人工确认、持久化和预算能力是可选配置，而本地关键阶段门禁默认强制。
- LLM guardrail 仍有同模型偏差和额外调用；确定性约束应优先用代码。
- 官方已移除内置代码解释工具并建议外部 sandbox，说明安全执行仍需额外系统。

适合：需要快速开发角色团队与结构化业务 Flow 的 Python 应用。  
不适合：为了已有文件工作流增加运行时和配置依赖。

### OpenAI Agents SDK

优势：

- 核心抽象较少，直接提供 agent loop、handoff、session、结构化输出和 `max_turns`。
- 输入、输出和函数工具 guardrail 能在运行时阻断错误；工具级审批可在展示 tool/arguments 后暂停、批准或拒绝，并序列化 RunState 长期恢复。[Guardrails](https://openai.github.io/openai-agents-python/guardrails/) [Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- tracing 默认覆盖模型生成、工具、handoff、guardrail 和自定义事件，比本地任务末端 evidence 更细。[Tracing](https://openai.github.io/openai-agents-python/tracing/)
- session 与 compaction 能自动维护或压缩多轮上下文，但官方也披露自动压缩可能增加流式尾延迟。[Sessions](https://openai.github.io/openai-agents-python/sessions/)

相对本地 PDCA 的劣势：

- 不同工具类别的 guardrail 覆盖并不完全一致，不能假设所有副作用都经过同一管线。
- session 解决对话记忆，不替代 PRD、Check verdict、知识准入或任务归档。
- 通用 durable execution 仍需应用或额外集成；高级审批和状态持久化需要代码。

适合：本地未来存在真实 Agent runner 时，作为工具审批和事件追踪的参考。  
不适合：在没有 runner 的当前仓库预建 SDK 适配层。

### GitHub Agentic Workflows

优势：

- Markdown 源编译为锁定的 GitHub Actions YAML，兼具自然语言配置和确定性执行工件。[Workflow structure](https://github.github.com/gh-aw/reference/workflow-structure/)
- 默认只读；写操作必须通过 safe outputs，支持 staged preview、数量/patch 限制、失败分类和重放。[Official repository](https://github.com/github/gh-aw) [Safe outputs](https://github.github.com/gh-aw/reference/safe-outputs/)
- 对 `AGENTS.md`、依赖清单、`.github/` 等关键文件提供保护策略，能 blocked、request review 或 fallback-to-issue。[Protected files](https://github.github.com/gh-aw/reference/safe-outputs-pull-requests/)
- Actions 日志、artifact、Markdown 源和 lock 文件天然可版本审计。

相对本地 PDCA 的劣势：

- 强绑定 GitHub、Actions、仓库事件和容器启动；不能覆盖通用研究、设计或本地非 GitHub 任务。
- safe outputs 约束副作用安全，不证明 Agent 生成内容本身准确。
- 源文件与编译 lock 文件形成双工件，需要维护同步和版本升级。

适合：自动 issue、PR、维护和审查等仓库副作用。  
不适合：取代本地跨场景 PDCA 管理中心。

## 七维横向结论

| 维度 | 本地 PDCA 判断 | 外部可借鉴点 |
|------|----------------|--------------|
| 准确度 | 结构与阶段正确性强；运行时输出/工具检查弱 | CrewAI/OpenAI 的结构化输出与工具 guardrail |
| 效率 | 零运行时依赖、渐进披露好；人工步骤多，无调用预算 | AutoGen 单 Agent 优先；CrewAI/OpenAI 的轮次、时间、usage 控制 |
| 恢复 | phase 级 receipt/backup，粒度粗 | LangGraph checkpoint、pending writes、replay、幂等规范 |
| 人类门禁 | Plan/Check 决策强制，但粒度较粗 | OpenAI 工具参数级审批；GitHub staged safe output |
| 安全 | 特定清理脚本保护强，通用工具边界不足 | GitHub 默认只读、关键文件保护、safe outputs |
| 可审计性 | 长期任务证据链强，单次运行细节弱 | OpenAI 默认 trace、AutoGen OTel、GitHub Actions artifacts |
| 采用成本 | 当前最低且跨场景 | 外部框架能力更强，但均需运行时、代码、存储或平台 |

## 本地 PDCA 的明确优势

1. **治理正确性高**：用户签审不能由 Agent 代替，外部框架通常只提供可配置 HITL。
2. **结论可追溯**：PRD→evidence criteria→conclusion→verdict→knowledge 的链条比单次 trace 更适合长期组织记忆。
3. **平台中立**：缺少 Agent 或 context 能力有明确 fallback，不绑定模型或云平台。
4. **低成本**：不用启动 runtime、数据库、观测后端或模型即可管理和验证任务。
5. **失败关闭**：未知 schema、非法状态、坏 digest、越界证据和缺确认会被拒绝。

## 本地 PDCA 的明确弱点

1. **运行时不可见**：不知道每次模型调用、工具调用、handoff、延迟和 usage。
2. **恢复粒度粗**：只能恢复 task phase 文件，无法跳过已成功的昂贵执行步骤。
3. **副作用门禁不统一**：`audit-history` 有 dry-run/manifest，但其他未来写操作没有统一 safe-output 层。
4. **确认粒度粗**：无法像工具级 HITL 一样只审批某个命令及其参数。
5. **并发与预算缺失**：没有统一 max turns、timeout、token/费用预算或并发资源控制。
6. **历史信号污染**：16 个旧格式活跃任务使全库严格验证失败；当前严格任务本身有效，但全局结果不可直接作健康信号。
7. **人工维护成本**：多份 task/record/journal/knowledge 文件增加流程摩擦，适合高价值任务而非每个微操作。

## 优化建议及淘汰门槛

### 立即处理

#### 1. 处置 16 个旧格式活跃任务

- 预期收益：恢复 `validate-workflow --all` 的健康信号，避免 AI 把真实新错误淹没在固定旧错误中。
- 成本：需要逐项 dry-run manifest 和用户删除/保留授权。
- 验证：全库严格校验 `invalid_count=0`。
- 淘汰条件：若这些任务仍在真实执行，则不得直接删除；应先完成或单独迁移，但不增加兼容分支。

这是当前唯一无需新 Agent runner 就能直接改善准确度的新增动作。

### 条件采用

#### 2. 高风险写操作的 safe-output 契约

- 借鉴：GitHub Agentic Workflows staged/safe outputs 与 OpenAI 工具审批。
- 触发条件：出现第二种需要自动执行的高风险副作用，不为单一脚本预建抽象。
- 设计目标：声明允许路径、最大变更量、保护对象、dry-run 预览和逐调用审批。
- 验证：故障夹具必须拒绝越界路径、超量写入、关键文件修改和缺审批。
- 删除条件：没有两个实际消费者，或只形成文档而无法执行。

#### 3. 统一 run-event trace

- 借鉴：OpenAI 默认 tracing、AutoGen OpenTelemetry。
- 触发条件：仓库出现真实模型/工具 runner。
- 最小事件：run、model、tool、handoff、guardrail、approval、usage、error。
- 验证：失败能回链到具体事件，且 trace 对排障或回归测试有真实消费者。
- 删除条件：只有写入没有查询、评测或故障定位消费者。

#### 4. 节点级 checkpoint/replay

- 借鉴：LangGraph。
- 触发条件：任务包含昂贵、长时、可重放的自动步骤，phase 备份不足。
- 验证：故障恢复不重复已成功的模型/API 调用，副作用满足幂等。
- 删除条件：所有任务仍是短时主会话执行，checkpoint 成本高于重跑。

#### 5. 模型调用预算

- 借鉴：AutoGen termination、CrewAI `max_iter/max_rpm/timeout`、OpenAI `max_turns/usage`。
- 触发条件：真实 runner 能可靠报告调用与 usage。
- 验证：超预算得到稳定错误码，并能在不破坏状态的情况下停止。
- 删除条件：没有可测 usage 或预算不会影响执行决策。

### 不采用

- **整体引入任一框架**：当前没有运行时消费者，新增依赖不能证明提升。
- **默认多 Agent**：官方 AutoGen 也建议简单任务先单 Agent；额外角色会增加上下文和协调成本。
- **用 LLM guardrail 替代 JSON Schema/代码门禁**：确定性条件交给模型会降低可重复性并增加调用。
- **为了排名增加综合分**：不同项目目标不同，权重会掩盖机制差异。
- **现在加入模型 token/延迟排行榜**：没有统一模型、硬件、数据集和预算，结论不可归因。
- **预建 trace/checkpoint/adapter 空协议**：没有消费者的协议违反“必须提升 AI”的价值门槛。

## 最终判断

本地 PDCA 在“任务治理准确性、人工签审、长期证据与知识闭环”上优于五个运行时项目的默认形态；在“运行时细粒度恢复、工具级审批、调用预算和逐步可观测性”上明显落后。

最优路线不是替换，而是分层：

```text
PDCA：目标、PRD、阶段门禁、证据、结论、知识
  ↓ 仅在真实自动执行需要时
Runner：tool approval、safe outputs、trace、budget、checkpoint
  ↓
模型与工具
```

在当前仓库状态下，先解决 16 个旧格式活跃任务的全局校验噪声；其他外部机制全部等待真实 runner 或第二个消费者出现后再实施。
