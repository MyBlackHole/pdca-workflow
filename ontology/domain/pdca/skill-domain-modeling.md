---
schema: pdca.asset/v2
id: ontology:domain/skill-domain-modeling
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 建立领域语义模型
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/ontology-asset
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 建立领域语义模型

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

区分类与实例，识别实体、属性、关系和约束；复用已存在节点，记录新增理由。模型应能指导产物和验收，不能只有名词分类。候选发布遵循本体创建门禁。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
