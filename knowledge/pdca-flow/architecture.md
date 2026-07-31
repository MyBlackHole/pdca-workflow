---
schema: pdca.asset/v1
id: knowledge:pdca-flow.architecture
layer: knowledge
summary: PDCA workflow 的核心资产边界与架构决策
tags: [architecture, asset-model]
scenarios: [software-development]
phases: [plan, do]
applies_when: [修改工作流核心资产或索引]
excludes_when: []
source_ids: []
confidence: high
status: active
---
# 架构决策

## flow skill 与 agent skill 的分工

**原则：** flow skill 永远是标准流程，不可修改或自定义；业务专有逻辑写在 agent skill 中。

反例：曾尝试创建自定义 `flow-web-research`，后更正为标准 flow skills + `web-research` agent skill。

**创建方式：**
- agent skill：在 `$PDCA_HOME/skills/<name>/SKILL.md` 中创建，需包含 `schema: pdca.asset/v1` frontmatter
- flow skill：在 `$PDCA_HOME/flows/flow-<phase>/SKILL.md` 中定义阶段标准步骤
- 关联方式：在 `task.json` 的 `meta.scenario_type` 中选择场景，flow-do 根据场景路由到对应 skill

## Asset 操作约束

- 可检索资产按 Evidence、Experience、Knowledge、Skill 分层；Evidence 只索引摘要，
  Experience 按需追溯，Knowledge/Skill 是默认上下文候选
- 新增资产时同步更新 `manifest.jsonl`（见 flow-act 步骤 2）

## 阶段校验顺序

task.json 的阶段流转校验链：`phase 字段 → advance-phase 门禁 → 对应 flow-<phase> 入口条件 → 步骤执行 → 手动 phase 推进`
