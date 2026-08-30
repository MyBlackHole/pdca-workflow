---
schema: pdca.asset/v1
id: ontology:concept/executor-adapter
type: concept
layer: Knowledge
status: active
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

- Scenario 的 **Executor ID** 表达业务角色；
- 开放 **Executor type** 表达执行协议或平台类别；
- **Registry adapter** 指向可替换的平台插件。

核心 Planner 只负责依据已观察事实判定 ready；Registry preflight 负责解析类型、匹配能力、应用信任策略。Codex/OpenCode/Claude Code/API Agent/MCP 差异都留在 Adapter，核心不得增加平台条件分支。

## 关键发现

- 真实调用前的 invocation request 必须绑定 scenario、registry 与 executor config 摘要；Adapter 调用时重新验证这些摘要与授权，旧 preflight 结果不作长期凭证。
- 仅 `automatic` 且能力满足的请求可直接调用；命令型与 Agent 型默认需审批更安全。
- config 可能含凭据引用/敏感参数；预检与日志只公开摘要。
- Registry 是权限配置面，须版本化、严格解析、限制大小与数量，并对坏配置 fail-closed。
- 平台 Adapter 统一承担输入映射、会话、权限、超时/取消、流式事件、结果归一化。

## OpenCode tmux 执行器边界

外部 OpenCode 一次完整 PDCA 授权可自动推进 Plan→Do→Check→Act，但执行器必须包住 agent：固定工作目录与变更白名单、启动前记录 git status、`tmux capture-pane` 保存输出、内部工具调用设超时（卡住 interrupt 保留现场有限重试）、要求 agent 输出阶段标识/变更清单/测试命令/结果/局限。阶段推进交 agent，安全边界/可观测性/最终判定由执行器负责。

## 外部项目规约注入

workflow root 与 agent 工作目录分离时，启动器须在创建会话前为目标项目执行平台 setup、仅当目标缺 `AGENTS.md` 才写入（保护用户已有说明）、为旁路状态命令显式传入 workflow root、setup 失败则拒绝启动；这是 executor 前置门禁，不应依赖用户在提示词重复声明流程名。

## 来源

- `（原知识层）executor-adapter-boundary.md`
- `（原知识层）opencode-tmux-executor-adapter.md`
- `（原知识层）external-project-workflow-injection.md`
