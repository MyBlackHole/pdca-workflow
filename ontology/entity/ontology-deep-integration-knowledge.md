---
schema: pdca.asset/v1
id: ontology:entity/ontology-deep-integration-knowledge
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-deep-integration-knowledge/1.0.0
summary: 全任务知识闭环（任意任务强制本体表达与产出，Act 统一沉淀）
relations:
  specializes:
    - ontology:concept/domain-entity
---

# 全任务知识闭环

叶子实体4：实现“无任务不知识”。

- 任意 `scenario_type` 任务均可通过 `meta.ontology_anchor`（默认 `ontology:concept/pdca-task`）与 `meta.ontology_fragment` 挂到本体图谱
- Act 阶段 `meta.disposition` 强制含 `ontology:` 或显式 `records-only` 理由，否则 `archive` 门禁拒收（`ontology_gate.auto_induce_evidence` 提示反哺）
- 知识优先关联既有节点，缺口创建补强任务（`flow-act` 步骤1），来源封存 `records/<id>/evidence` + `experience.md`
