---
schema: pdca.asset/v1
id: ontology:concept/capability-protocol
type: concept
layer: Knowledge
summary: PDCA 能力协议（flow/skill 声明能力而非平台工具，doctor 解析）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/capability-protocol/1.0.1
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
- `agent.spawn` 对每个独立 PDCA 任务都是 `required: true`：协调 Agent 派发时必须一次性启动与当前任务一对一绑定的全新子 Agent/子智能体上下文，并拒绝既有任务、并行任务或协调 Agent 活动执行上下文的复用。
- 派发成功后协调 Agent 必须进入 `suspended_waiting_agent` 并停止运行；子 Agent 在当前任务上下文内自主执行。
- `agent.spawn` 探测失败时状态必须为 `missing` 并 fail-closed：当前任务保持未执行，不产生 Do 产物或执行证据；不得把它标记为 `fallback`，不得由协调 Agent 或任何既有子 Agent 顺序执行。
- 协调 Agent 恢复后只读当前任务持久化产物并执行 `ontology_conformance_verification`，禁止跨任务检查。转交当前任务持久化的 `awaiting_confirmation` 请求属于确认通道；真实用户确认不得由子 Agent 代签。
- `context.retrieve` 降级为使用 `rg` 搜索 knowledge、records 和任务元数据，并记录选取理由。
- 内容量审查使用 UTF-8 bytes，不依赖模型 tokenizer；模型真实 token、延迟和成本只允许由未来 Agent runner 实测。

## 决策背景（原 docs/capability-protocol.md）

- 背景：能力声明曾与具体 Agent 平台工具名耦合，导致跨平台不可移植、降级路径缺失。
- 决策：能力协议与平台解耦，能力解析交由适配层 doctor；必需能力缺失即 fail-closed，可选能力缺失走声明降级。该事实原记录于 `docs/capability-protocol.md`，现迁入本节点作为唯一权威来源。
