---
schema: pdca.asset/v2
id: ontology:domain/skill-codebase-design
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 把本体约束映射为模块设计
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-execution-contract
  - ontology:process/select-task-subgraph
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 把本体约束映射为模块设计

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

读取必要代码与约束，明确模块职责、接口、状态、所有权、错误及验证边界，比较合理替代方案。产出可回链AC的设计，不仅是目录清单。未经契约授权不顺便实施大规模改造。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
