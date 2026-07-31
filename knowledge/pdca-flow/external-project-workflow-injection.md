---
schema: pdca.asset/v1
id: knowledge:pdca-flow/external-project-workflow-injection
layer: knowledge
summary: 外部项目启动 OpenCode 前必须注入平台规约并显式绑定 workflow root
tags: [opencode, tmux, setup, workflow-root, executor]
scenarios: [default, technical-design]
phases: [plan, do, check, act]
applies_when: [workflow root 与 agent 工作目录不是同一目录]
excludes_when: [目标项目禁止创建平台规约文件]
source_ids: [experience:T0023--07-26-修复-opencode-tmux-启动时未自动加载-pdca-规约]
confidence: high
status: active
---

# 外部项目规约注入

当 OpenCode 的工作目录与 workflow root 分离时，不能只在 workflow root 保存 `AGENTS.md`，因为 agent 按工作目录加载项目说明。启动器应在创建会话前：

1. 使用 workflow root 的 CLI 为目标项目执行平台 setup。
2. 只在目标缺少 `AGENTS.md` 时写入，保护用户已有说明。
3. 为旁路状态命令显式传入 workflow root，避免从目标目录自动发现错误仓库。
4. 在 setup 失败或规约未生成时拒绝启动 agent。

这是一项 executor 前置门禁，不应依赖用户在自然语言提示词中重复声明流程名称。
