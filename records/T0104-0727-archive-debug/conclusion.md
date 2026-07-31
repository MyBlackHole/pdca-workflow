---
schema: pdca.asset/v1
id: T0104-0727-archive-debug
layer: experience
summary: 审查归档失败根因并修复 3 处断裂
tags: [archive, advance-phase, disposition, data-corruption]
---

# 结论: T0104 — 归档失败根因审查

## 发现的根因

| # | 问题 | 影响 |
|---|------|------|
| 1 | flow-act 从不调用 advance-phase，archive mv 无门禁 | 100% 归档任务 phase 卡在 act/do |
| 2 | 阶段跳跃：6 个任务以 phase=do 直接被归档 | 缺 disposition/record/journal |
| 3 | task.json 数据损坏（重复 meta 块） | 1 个任务不可解析 |

## 修复

1. flow-act 步骤 8：归档前加载 advance-phase 校验 disposition + 更新 metadata
2. 修复 0727-skill-extraction 损坏的 task.json
3. 批量补齐 18 个归档任务的 active=false
