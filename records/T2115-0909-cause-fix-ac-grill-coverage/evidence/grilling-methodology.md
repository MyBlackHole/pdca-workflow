---
schema: pdca.asset/v1
id: ontology:concept/grilling-methodology
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/grilling-methodology/1.0.0
summary: 追问方法论：设计树、前沿、轮次、事实而非观点、完成标准
relations:
  specializes:
  - ontology:principle
---


# Grilling Methodology

追问方法论：设计树、前沿、轮次、事实而非观点、完成标准

## 覆盖必问轮（research 类任务 Grill 必备）

- research 类任务 Grill 必须包含一轮覆盖必问，必问三项：
  1. 本体锚定哪几个节点；
  2. 本次新增还是修订源文档哪几章；
  3. 沉淀计划是什么。
- 该轮须 `captured:true` 落盘到 `clarifications.jsonl`。
- 动因：T2107 三轮 Grill 漏问覆盖导致本体缺三块，来源 `records/T2107-0909-guomi-storage-research/conclusion.md` 偏差记录。
