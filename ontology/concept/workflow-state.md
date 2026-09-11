---
schema: pdca.asset/v2
id: ontology:concept/workflow-state
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 任务工作流位置的共同类，区分方法阶段与终态
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-phase-status
---

# 工作流状态值的共同类

本类表示任务记录phase字段的合法工作流位置，不代表全部都是PDCA方法阶段。`pdca-phase`是它的子类，实例只有plan/do/check/act；archive直接属于本类，state_kind=terminal。

查询pdca-phase实例得到四个方法阶段。查询workflow-state时包含其子类实例，得到五个工作流值。execution_state（例如stopping/interrupted）是另一维度，不是这些phase值的实例。

字段与合法组合只由STATE-01定义；类型修复不改变四条正常边或持久化`phase=archive`兼容编码，不添加父Agent审批。
