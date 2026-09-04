---
schema: pdca.asset/v1
id: ontology:concept/template-minimal
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/template-minimal/1.0.0
summary: 最小模板约束（三件套必填+扩展区自由），模板即本体节点
relations:
  specializes:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-phase
attributes:
- name: required_trio
  desc: 本体节点与任务表达的最小机读约束，仅 id/relations/testable_signal 三件套必填
  constraint: 三件套缺一即 SCHEMA_MISSING_FIELD/ATTR_NO_TEST_SIGNAL 阻断，其余字段不得阻断
  testable_signal: python3 scripts/ontology-validate.py 2>&1 | grep -q "^OK" && grep -q "extensions" schemas/task.schema.json && grep -q "template-exempt" scripts/ontology-validate.py
- name: extension_zone
  desc: 自由扩展区不参与门禁解析，供 AI 发散假设与新概念先行
  constraint: task.json:meta.extensions 自由对象门禁跳过内容；prd ## 自由扩展节不计 AC；本体 <!-- template-exempt --> 块内跳过正文扫描
  testable_signal: python3 -c "import json; d=json.load(open('schemas/task.schema.json')); assert d['properties']['meta']['properties']['extensions']['additionalProperties'] is True" && grep -q "自由扩展" scripts/pdca_core.py
---

# template-minimal

最小模板约束：尺子只量三件套（`id/relations/testable_signal`），其余放自由区。

## 决策背景

`T2045 §5` 确认模板束缚主因是 `a填空化+b门禁过严`；根治不是删除模板，而是模板收敛为本体节点的最小机读约束（`T2049`）。模板演进即本体演进：改约束先改本节点再改三处投射（`schemas/task.schema.json`、`scripts/pdca_core.py:acceptance_criteria`、`scripts/ontology-validate.py`）。
