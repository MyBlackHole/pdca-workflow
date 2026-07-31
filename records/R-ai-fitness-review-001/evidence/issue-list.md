# 问题清单

## Critical（必须修复）

| # | 问题 | 文件 | 影响 |
|---|------|------|------|
| C1 | SKILLS-INDEX.md 行数信息严重过期 | SKILLS-INDEX.md | 误导 AI 对内容量的判断，4 个技能偏差 >30 行 |

## Major（应该修复）

| # | 问题 | 文件 | 影响 |
|---|------|------|------|
| M1 | context-retrieval 依赖 pdca context CLI 命令 | skills/context-retrieval/SKILL.md:30 | 若 CLI 不存在，整个 skill 不可执行 |
| M2 | to-tickets Dispatch 缺子代理错误处理 | skills/to-tickets/SKILL.md:52-66 | 子代理失败无法自动恢复，与 flow-do 容错脱节 |
| M3 | flow-plan P4 的 task() 派发未引用容错机制 | flows/flow-plan/SKILL.md:98-108 | 子代理出错无恢复路径 |

## Minor（建议修复）

| # | 问题 | 文件 | 影响 |
|---|------|------|------|
| m1 | advance-phase 行数膨胀（index 25→实际 58） | skills/advance-phase/SKILL.md | 内容量偏大，但功能合理 |
| m2 | writing-great-skills 字节量仍偏高 | skills/writing-great-skills/SKILL.md | 2,409 字节，可进一步精简 |
| m3 | code-review description 为空 | skills/code-review/SKILL.md | 影响入口引导和自动触发判断 |
| m4 | triage 为 user-invoked 但含 AI 执行指令 | skills/triage/SKILL.md | 人机分工边界模糊 |

## Info（建议关注）

| # | 问题 | 文件 | 影响 |
|---|------|------|------|
| i1 | flow-do 仍有 13 次 skill 引用 | flows/flow-do/SKILL.md | 每次引用需额外上下文加载 |
| i2 | 11 个 skill 超过 2,000 字节 | skills/*/SKILL.md | 总体量 52KB，可考虑局部精简 |
| i3 | 无上下文窗口溢出恢复机制 | 项目范围 | 长任务可能意外中断 |
