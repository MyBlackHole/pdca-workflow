---
schema: pdca.asset/v2
id: ontology:concept/template-minimal
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 模板的最小性
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-record-identity
---

# 模板的最小性

模板只声明当前协议必要字段，未知值保留null/unknown。初始化草稿不是已执行记录；不填写假的Agent ID、摘要、用户确认或测试结果。参考根templates目录。
