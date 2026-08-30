---
schema: pdca.asset/v1
id: ontology:concept/capability-protocol
type: concept
layer: Knowledge
summary: PDCA 能力协议（flow/skill 声明能力而非平台工具，doctor 解析）
status: active
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/ontology-asset
---

# PDCA 能力协议（capability-protocol）

## 原则

- flow 与 skill 只声明"需要什么能力"，不声明"调用哪个 Agent 平台工具"；执行前由 `doctor` 在当前环境解析能力。
- 能力探测**不是授权**；每次新会话或执行环境变化后都必须重新运行 `doctor`。

## 结果状态

每项能力只能处于三态之一：

- `available`：探测成功，可以执行。
- `fallback`：可选能力缺失，必须执行声明的降级路径。
- `missing`：必需能力缺失，fail-closed。

## 核心约束

- `required: true` 且探测失败：停止任务。
- `required: false` 且探测失败：只能走 `fallback`，不得尝试未定义工具。
- flow/skill 不得写入 Codex、Claude Code、OpenCode 或其他平台专用条件分支。
- `agent.spawn` 降级为主会话顺序执行；确认和风险接受仍由主会话完成。
- `context.retrieve` 降级为使用 `rg` 搜索 knowledge、records 和任务元数据，并记录选取理由。
- 内容量审查使用 UTF-8 bytes，不依赖模型 tokenizer；模型真实 token、延迟和成本只允许由未来 Agent runner 实测。

## 决策背景（原 docs/capability-protocol.md）

- 背景：能力声明曾与具体 Agent 平台工具名耦合，导致跨平台不可移植、降级路径缺失。
- 决策：能力协议与平台解耦，能力解析交由适配层 doctor；必需能力缺失即 fail-closed，可选能力缺失走声明降级。该事实原记录于 `docs/capability-protocol.md`，现迁入本节点作为唯一权威来源。
