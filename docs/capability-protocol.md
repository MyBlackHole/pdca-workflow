# PDCA 能力协议

flow 和 skill 声明“需要什么能力”，不声明“调用哪个 Agent 平台工具”。当前环境在执行前通过 doctor 解析能力。

## 结果

每项能力只能处于：

- `available`：探测成功，可以执行。
- `fallback`：可选能力缺失，必须执行声明的降级路径。
- `missing`：必需能力缺失，fail-closed。

能力探测不是授权。每次新会话或执行环境变化后都要重新运行 doctor。

## 核心约束

- `required: true` 且探测失败：停止任务。
- `required: false` 且探测失败：只能走 `fallback`，不得尝试未定义工具。
- flow/skill 不得写入 Codex、Claude Code、OpenCode 或其他平台专用条件分支。
- `agent.spawn` 降级为主会话顺序执行；确认和风险接受仍由主会话完成。
- `context.retrieve` 降级为使用 `rg` 搜索 knowledge、records 和任务元数据，并记录选取理由。

内容量审查使用 UTF-8 bytes，不依赖模型 tokenizer；模型真实 token、延迟和成本只允许由未来 Agent runner 实测。
