---
schema: pdca.asset/v2
id: ontology:domain/skill-improve-codebase-architecture
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 受控的架构改进
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:domain/skill-codebase-design
  - ontology:concept/pdca-execution-contract
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 受控的架构改进

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

先定位真实复杂度/耦合问题与影响，比较改进收益和迁移成本，固定验收与回归范围。可分批兼容迁移，避免未经授权清理。指标必须来自实际分析，优化效果需后续观测。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
