---
schema: pdca.asset/v1
id: knowledge:pdca-flow/opencode-tmux-executor-adapter
layer: knowledge
summary: 用 tmux 驱动 OpenCode 自动执行完整 PDCA 时必须提供可观测、超时和重试边界
tags: [opencode, tmux, executor, pdca, recovery]
scenarios: [default, technical-design]
phases: [plan, do, check, act]
applies_when: [外部 agent 通过交互终端自动完成多阶段任务]
excludes_when: [agent 没有可捕获的终端输出或目标目录无法隔离]
source_ids: [experience:T0021--07-26-使用-opencode-通过-tmux-验证-six-锁逻辑-pdca-流程]
confidence: high
status: active
---

# OpenCode tmux 执行器边界

给外部 OpenCode 一次完整 PDCA 授权可以让它自动推进 Plan→Do→Check→Act，但执行器必须包住 agent：

- 固定工作目录和变更白名单，启动前记录 git status。
- 使用 `tmux capture-pane` 保存阶段输出和最终完成标记。
- 为内部工具调用设置超时；卡住时 interrupt 并保留现场，再按有限次数重试。
- 要求 agent 输出阶段标识、变更清单、测试命令、结果和局限，而不是只返回自然语言结论。
- 完成后由控制端重新运行关键测试并比较原有未提交修改，不能把 agent 的自报结果视为唯一证据。

这使“自动 PDCA”与“无人监管”区分开：阶段推进交给 agent，安全边界、可观测性和最终判定仍由执行器负责。
