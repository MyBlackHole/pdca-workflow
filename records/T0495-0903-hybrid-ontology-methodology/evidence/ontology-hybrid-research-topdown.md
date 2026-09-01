---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-research-topdown
type: domain
layer: Knowledge
status: active
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
    constraint: 父 work = 子works之和（WBS 100% Rule），缺一叶即缺一维度
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary 检查以 ontology:entity/report-center-system 为根的 composed_of 树叶数≥2 且无孤岛，且 grep -R 'composed_of' ontology/entity/report-center-system.md 可命中"
  - name: middle_significant_first
    desc: 中层显著概念优先
    constraint: 先取显著中层（如 report-center-web）再特化/泛化
    testable_signal: "检查 ontology/domain/ontology-hybrid-research-topdown.md 含 '中层显著' 且经 ontology-validate 通过"
---

# Research Topdown — 根→叶全面记录

> 来源 Ontology101 `top-down` + METHONTOLOGY `spec→concept` + WBS `100% Rule` + NeOn Scenario 1

- **动作**：项目实体为根，`composed_of` 逐层拆至满足叶三准绳的最小叶，调研产出即 `ontology/<type>/<slug>.md` 全面落盘（叶 `attributes.testable_signal` 即开发输入）
- **中层显著优先**（middle-out 稳定）：先取显著中层（`report-center-web`/`collection`）再特化/泛化，减少返工
- **100%检验**：父=子之和，`ontology_graph` `islands:0` 且 `composed_of` 边可追
