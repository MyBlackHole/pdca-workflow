---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-research-topdown
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-hybrid-research-topdown/1.0.0
summary: 混合方法论Research Topdown：根→叶全面记录（Ontology101 top-down + METHONTOLOGY规格→概念化 + WBS 100% Rule）
relations:
  specializes:
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:pattern/ontology-modular-reference
attributes:
  - name: topdown_completeness
    desc: 根实体经 composed_of 逐层拆至叶子，100%覆盖
    constraint: 父 work = 子works之和（WBS 100% Rule），缺一叶即缺一维度，叶 `attributes` 即开发可测点
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary 检查以 ontology:entity/report-center-system 为根的 composed_of 树叶数≥2 且无孤岛，且 grep -R 'composed_of' ontology/entity/report-center-system.md 可命中"
  - name: middle_significant_first
    desc: 中层显著概念优先（middle-out）
    constraint: 先取显著中层（如 report-center-web/collection）再特化/泛化，术语更稳、返工少
    testable_signal: "检查 ontology/domain/ontology-hybrid-research-topdown.md 含 '中层显著' 且经 ontology-validate 通过"
  - name: spec_provenance
    desc: 调研来源封存与可追溯
    constraint: 每叶记录来源 record 与 `testable_signal` 三模式来源，且被 `disposition ontology:` 回链
    testable_signal: "检查本节点前置 `skill-research##本体沉淀决策` 且 `grep -R 'ONTOLOGY' records/T04*/conclusion.md` 可命中，且经 validate 通过"
  - name: completeness_gate
    desc: 全面性门禁
    constraint: 缺一叶 `validate` 或 `graph` 缺边即 `islands>0` 阻断 `archive`
    testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查0 issues 且 islands:0，否则阻断"
---

# Research Topdown — 根→叶全面记录

> 来源 Ontology101 `top-down` + METHONTOLOGY `spec→concept` + WBS `100% Rule` + NeOn Scenario 1

- **动作**：项目实体为根，`composed_of` 逐层拆至满足叶三准绳的最小叶，调研产出即 `ontology/<type>/<slug>.md` 全面落盘（叶 `attributes.testable_signal` 即开发输入，`grep -c attributes` ≥1 可检）。
- **中层显著优先**（middle-out 稳定）：先取显著中层（`report-center-web`/`collection`）再特化/泛化，术语更稳、返工少。反例：顶层 `report-center` 直接特化至字段级导致叶爆炸。
- **100%检验**：父=子之和，`python3 scripts/ontology_graph.py --format summary` `islands:0` 且 `composed_of` 边可 `grep` 追溯，缺一叶 `validate` 报 `DANGLING`。
- **来源封存**：每叶经 `skill-research##本体沉淀决策` + `knowledge-provenance` 封存 `records/<record>/conclusion##本体沉淀` 与 `meta.disposition ontology:` 回链，可 `grep -R 'ontology:' records/*/conclusion.md` 复核。
- **门禁对接**：`flow-plan##拆分映射` 与 `flow-do#2 ontology-ready` 硬拦缺 `fragment`，`archive` 硬拦 `islands>0`。
