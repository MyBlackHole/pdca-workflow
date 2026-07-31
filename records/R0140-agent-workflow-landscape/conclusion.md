---
schema: pdca.asset/v1
id: R0140-agent-workflow-landscape
phase: check
source_ids: [source-inventory, comparison-matrix, local-measurements, validation-result, research-report]
---

## 上下文

检查五个外部 Agent 工作流项目与本地 PDCA 的准确度、效率、恢复、安全、人类门禁、可审计性和采用成本对比是否有充分证据。

## 假设与结果

- 固定样本且只使用一手资料能形成可追溯机制矩阵：通过，22 个官方来源，五项目各 4–5 个。
- 将官方声明、本地实测和推断分开能避免伪性能排名：通过，报告未计算综合分，也未声称真实 LLM 性能。
- 外部机制能给出当前本地优化方向：成立。无需 runner 可立即验证三项改进：处置 16 个旧格式活跃任务、将 convergence 检查变成可执行验证器、将来源矩阵检查变成 research 门禁；trace、checkpoint、预算和 safe-output 抽象需等待真实 runner 或第二个消费者。

## 分析

本地 PDCA 在任务治理、用户签审、长期证据和知识闭环上强；在运行时节点恢复、工具级审批、usage budget 和事件 tracing 上弱。LangGraph、AutoGen、CrewAI、OpenAI Agents SDK 和 GitHub Agentic Workflows 主要是执行运行时或仓库自动化，与 PDCA 治理层互补。整体引入任一框架目前都缺乏消费者和行为收益证据。

本地复验为：15/15 单元测试、12/12 场景夹具、53 个引用无断链、归档不兼容任务为 0。全库严格验证仍拒绝 16 个旧格式活跃任务；这些任务未获得本轮删除授权，未修改且未增加兼容规则。

## 适用边界

- 官方文档只能证明机制存在，不能证明实际更快或更准。
- 五项目不是完整市场样本，结论不能外推到所有 Agent 框架。
- 未安装外部框架、未使用统一模型和数据集，不能给出真实性能排名。
- `native/configurable/external/not-found` 仍包含架构判断；`not-found` 不等于绝对不支持。

## 下一轮建议

优先对 16 个旧格式活跃任务生成精确 dry-run manifest 并由用户决定处置；随后用正反例评估 convergence validator 与 research evidence validator，只有能改变错误判定才保留。真实 runner 出现后，再分别验证工具级审批、事件 trace、调用预算和节点 checkpoint；不预建空协议。
