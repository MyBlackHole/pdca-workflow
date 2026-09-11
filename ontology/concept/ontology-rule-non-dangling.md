---
schema: pdca.asset/v2
id: ontology:concept/ontology-rule-non-dangling
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 引用存在且可定位
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/ontology-rule
  relates_to:
  - ontology:concept/ontology-asset
rule_spec: {}
---

# 引用存在且可定位

递归枚举ontology全部节点ID；relations及domain中的每项必须可定位。未知关系键、字符串冒充列表、重复ID或缺失目标均报错。source_ids中的外部出处不是图边，单独核验可访问性，不伪造来源。
