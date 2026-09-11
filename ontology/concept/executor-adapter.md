---
schema: pdca.asset/v1
id: ontology:concept/executor-adapter
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/executor-adapter/1.0.1
summary: Executor Registry 与平台 Adapter 的职责与信任边界（角色/平台类型/平台实现三层分离）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/process
---

# Executor Adapter 边界（executor-adapter）

## 结论

任意场景工作流应把"角色、平台类型、平台实现"拆成三个稳定层次：

- 子任务 `execution_contract` 引用的 **Executor ID** 表达执行角色；
- 开放 **Executor type** 表达执行协议或平台类别；
- **Registry adapter** 指向可替换的平台插件。

核心 Planner 只负责依据已观察事实判定 ready；Registry preflight 负责解析类型、匹配能力、应用信任策略。Codex/OpenCode/Claude Code/API Agent/MCP 差异都留在 Adapter，核心不得增加平台条件分支。

## 关键发现

- 真实调用前的 invocation request 必须绑定子任务、`ontology_role`、`execution_contract`、registry 与 executor config 摘要；Adapter 调用时重新验证这些摘要与授权，旧 preflight 结果不作长期凭证。
- 仅 `automatic` 且能力满足的请求可直接调用；命令型与 Agent 型默认需审批更安全。
- config 可能含凭据引用/敏感参数；预检与日志只公开摘要。
- Registry 是权限配置面，须版本化、严格解析、限制大小与数量，并对坏配置 fail-closed。
- 平台 Adapter 统一承担输入映射、会话、权限、超时/取消、流式事件、结果归一化。
- Registry preflight 必须为每个独立 PDCA 任务一次性启动全新子 Agent/子智能体，并绑定唯一的当前任务与子 Agent 会话标识；Adapter 必须拒绝既有任务、并行任务或协调 Agent 的会话标识作为执行上下文。跨任务信息只能经明确的持久化 PRD、任务元数据、证据与 context pointer 传递。
- `agent.spawn` 是任务执行的必需能力。若 Adapter 无法创建全新子 Agent 上下文，preflight 必须 fail-closed 并保持当前任务未执行，不得发出 invocation request、不得生成 Do 产物或执行证据，也不得回退协调 Agent 或复用已有子 Agent。
- Adapter 成功返回一次性启动结果后，协调 Agent 必须进入 `suspended_waiting_agent`。恢复时 Adapter 只允许读取当前任务 `task.json`、transition receipts、evidence manifest 与工作产物，并构造 `result=pending` 的内容寻址审查包；任务的 `ontology_role` 保持不变，`ontology_conformance_verification` 作为独立 review action 记录。只有协调器另行绑定 review digest、`confirmed|rejected` 决定和理由后，执行状态才能进入 completed 或 failed；确定性检查不得自我批准语义符合性。不得暴露子 Agent 活动对话上下文或检查其他任务。

## OpenCode tmux 执行器边界

外部 OpenCode 一次完整 PDCA 授权可自动推进 Plan→Do→Check→Act，但执行器必须包住 agent：固定工作目录与变更白名单、启动前记录 git status、`tmux capture-pane` 保存输出、内部工具调用设超时（卡住 interrupt 保留现场有限重试）、要求 agent 输出阶段标识/变更清单/测试命令/结果/局限。阶段推进交 agent，安全边界/可观测性/最终判定由执行器负责。

## 外部项目规约注入

workflow root 与 agent 工作目录分离时，启动器须在创建会话前为目标项目执行平台 setup、仅当目标缺 `AGENTS.md` 才写入（保护用户已有说明）、为旁路状态命令显式传入 workflow root、setup 失败则拒绝启动；这是 executor 前置门禁，不应依赖用户在提示词重复声明流程名。

## 来源

- `（原知识层）executor-adapter-boundary.md`
- `（原知识层）opencode-tmux-executor-adapter.md`
- `（原知识层）external-project-workflow-injection.md`
