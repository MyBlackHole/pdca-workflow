---
schema: pdca.asset/v2
id: ontology:concept/self-optimization-loop
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 自我优化：观测到独立验证
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-continuous-improvement
  - ontology:concept/pdca-feedback
---

# 自我优化：观测到独立验证

记录问题→分析原因→形成候选→受控发布→在后续真实任务验证效果。审计发现不等于变更授权；同一模型复述同一条规则不等于效果证据。

分析维度可包括定位成本、测试缺口、指令冲突、无效动作、工具调用和信息访问。只为独立目标创建新任务，不按每条发现机械派发。

发布和处置遵循LEARN-01。优化基线、指标、样本与观察方法需提前固定；仅在实际数据足够时得出改善/无效/退化结论，缺数据为unknown。
