---
schema: pdca.asset/v2
id: ontology:concept/knowledge-provenance
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 知识来源与可复核范围
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/ontology-asset
  - ontology:concept/pdca-evidence
---

# 知识来源与可复核范围

本体知识保留来源任务、原始资料locator、版本、采用理由与局限。来源字段不是relations图边；缺失历史材料标为不可复核，不能补造任务记录。本次迁移未复验继承的领域源码事实，使用前应核对授权的实际源码版本。
