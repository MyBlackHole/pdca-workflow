---
schema: pdca.asset/v2
id: ontology:concept/context-pointer
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 2.0.0
summary: 具名、版本固定的上下文指针
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/pdca-evidence
---

# 具名、版本固定的上下文指针

指针包含node_id或source_ref、固定版本/内容摘要、明确读取理由和触发条件。启动只加载必要规则，领域正文按需读取。路径可读不等于已获授权；历史绝对路径不是当前环境可用性的证据。
