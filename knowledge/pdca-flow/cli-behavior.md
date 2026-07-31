---
schema: pdca.asset/v1
id: knowledge:pdca-flow.project-conventions
layer: knowledge
summary: PDCA 项目操作约定：SKILL.md 编辑规则、提交策略、测试注意事项
tags: [conventions, skill, commit, testing]
scenarios: [software-development]
phases: [plan, do, check, act]
applies_when: [编辑技能、提交代码、编写测试]
excludes_when: []
source_ids: []
confidence: high
status: active
---

# 项目操作约定

## SKILL.md 编辑规则

SKILL.md 的 frontmatter 和 body 分开管理：修改 `meta.phase`、`meta.scenario_type` 等字段时只动 frontmatter，不修改 body 中的步骤描述。如需更新模板内容需手动编辑 body。

## 提交安全策略

根文档（README.md、AGENTS.md、SKILLS-INDEX.md）需手动 `git add + git commit`。`scripts/` 下的自动化工具有各自的文件白名单。

## 测试注意事项

- 新建 skill 时 ID 不能与已有 skill 重名，应先扫 `skills/` 目录确认
- 任务 ID 必须单调递增：扫描 `pdca/tasks/` 和 `pdca/tasks/archive/` 中所有 `task.json` 的 `id` 字段，取最大值 +1 分配
- flow skill 中要求的步骤必须对应实际执行的 skill 调用；新增 flow 步骤时，应同步验证进入该 flow 的前置门禁条件

## 阶段流转

详见 `skills/advance-phase/SKILL.md`：通过更新 `task.json` 的 `meta.phase` 手动推进阶段，advance-phase 负责校验门禁条件。