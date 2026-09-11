---
schema: pdca.asset/v2
id: ontology:concept/skill-invocation-contract
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 技能调用的范围
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-execution-contract
  - ontology:concept/capability-protocol
---

# 技能调用的范围

技能是契约内的局部动作说明，输入、输出、适用条件和失败处理必须明确。它不新建生命周期，不自定义确认权限，不直接宣称切换phase。宿主原生调用方式由实际工具说明决定。
