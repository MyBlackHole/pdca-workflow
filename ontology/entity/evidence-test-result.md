---
schema: pdca.asset/v2
id: ontology:entity/evidence-test-result
type: entity
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 证据类型：逐案例真实测试结果
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/pdca-evidence
  relates_to:
  - ontology:concept/task-unit-test
  - ontology:concept/task-test-case
  - ontology:concept/pdca-evidence
evidence_kind: test-result
---

# 证据类型：逐案例真实测试结果

证据类型为test-result。字段依EVIDENCE-01/TEST-01，必须可回链suite/case/run/实现及环境版本、实际输入输出/断言、退出状态/清理与原始产物；测试计划、示例期望或模型自述不是结果。

正确实现run与错误实现变体run分开；invalid mutation不能作为killed。失败/未知/未执行不得隐藏，返工保留旧记录。
