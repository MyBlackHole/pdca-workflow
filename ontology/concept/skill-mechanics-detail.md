---
schema: pdca.asset/v2
id: ontology:concept/skill-mechanics-detail
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 技能加载边界
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/skill-mechanics
  - ontology:process/select-task-subgraph
---

# 技能加载边界

先定位技能适用条件，再按需读取当前动作的说明；不要把所有技能正文加载到每个任务。辅助模板和来源缺失时明确说明，不臆造宿主命令。
