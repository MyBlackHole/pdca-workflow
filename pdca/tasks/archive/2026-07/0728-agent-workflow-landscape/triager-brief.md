# T0140 Triage

- 分类：enhancement
- 场景：research
- 查重：现有 T0135 建立本地 AI 友好度基线，但没有外部项目的同维度系统对照，本任务不重复。
- 初步事实核验：
  - LangGraph 官方文档声明 durable execution、persistence 和 human-in-the-loop。
  - AutoGen 官方文档提供 team、termination、pause/resume，并建议简单任务优先单 Agent。
  - CrewAI 官方资料区分 Crews 与 Flows，并提供结构化状态、持久化、guardrail。
  - OpenAI Agents SDK 官方文档提供 guardrail、handoff、session 和内置 tracing。
  - GitHub Agentic Workflows 使用 Markdown 编译到 Actions，默认只读并通过 safe outputs 限制写操作。
- 信息缺口：用户需要确认样本边界，以及是否接受“不做付费模型跑分”的科学限制。
- 推荐下一步：固定五项目样本，先做官方证据矩阵与本地可执行对照；只有发现会改变决策的缺口才增加项目。
