---
schema: pdca.asset/v1
id: knowledge:pdca-flow.executor-adapter-boundary
layer: knowledge
summary: Executor Registry 与平台 Adapter 的职责和信任边界
tags: [pdca-flow, executor, adapter, multi-agent, security]
scenarios: [software-development]
phases: [do]
applies_when: [接入新的 Agent 执行平台]
excludes_when: [只读规划]
source_ids: []
confidence: high
status: active
---

# Executor Registry 与多 Agent Adapter 边界

## 结论

✅ 任意场景工作流应把“角色、平台类型、平台实现”拆成三个稳定层次：

- Scenario 的 Executor ID 表达业务角色；
- 开放 Executor type 表达执行协议或平台类别；
- Registry adapter 指向可替换的平台插件。

核心 Planner 只负责依据已观察事实判定 ready，Registry preflight 负责解析类型、匹配能力
和应用信任策略。Codex、OpenCode、Claude Code、API Agent 或 MCP 的差异都应留在 Adapter，
不得在核心增加平台条件分支。

## 关键发现

- 真实调用前的 invocation request 必须绑定 scenario、registry 与 executor config 摘要；
  Adapter 调用时必须重新验证这些摘要和授权，旧 preflight 结果不能作为长期凭证。
- 只有 automatic 且能力满足的请求可以直接调用；命令型与 Agent 型默认需要审批更安全。
- config 可能包含凭据引用或敏感参数，预检和日志只应公开摘要。
- Registry 是权限配置面，必须版本化、严格解析、限制大小和数量，并对坏配置 fail-closed。
- 平台 Adapter 统一承担输入映射、会话、权限、超时/取消、流式事件和结果归一化。

## 建议

先以 mock adapter 验证 Adapter SPI 的 prepare/invoke/collect/cancel 生命周期，再接入首个
受限真实平台。接入 OpenCode 时使用独立 `opencode-cli-v1` Adapter，封装可执行文件和
版本探测、非交互模式、权限参数及输出解析；核心只看到统一 Invocation Request 和 Runtime
Events。
