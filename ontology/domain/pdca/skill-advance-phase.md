---
schema: pdca.asset/v2
id: ontology:domain/skill-advance-phase
type: domain
semantic_kind: individual
layer: Knowledge
status: archived
authority: reference
revision: 3.1.1
summary: 阶段推进动作
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-26'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-gate
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

> 归档说明（2026-09-26）：本页重复当前阶段事件方法，且历史正文的“单阶段回执”未区分开始、完成等事件。
> 当前方法见 [TRANSITION-01](../../concept/pdca-transition.md) 与 [GATE-01](../../concept/pdca-gate.md)。
> 下方保留原正文供比较，不作为新任务操作入口；替代链接不自动迁移既有采用，验证状态仍为 unverified。

# 阶段推进动作

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

只执行TRANSITION-01：重读当前事实、核验对应GATE-01、写单阶段回执、重读后更新task快照。重复请求返回匹配回执；未满足条件保持原phase并报告缺项。不要调用旧CLI或把目标状态存在当作提交成功。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
