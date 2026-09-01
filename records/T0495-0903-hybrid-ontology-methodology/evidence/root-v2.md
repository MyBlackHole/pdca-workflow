---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-methodology
type: domain
layer: Knowledge
status: active
summary: 混合方法论本体根：调研顶向下（top-down 100%）与开发底向上（bottom-up Work Package）双向，叶粒度middle-out Yo-Yo（对齐 Ontology101/METHONTOLOGY/NeOn/WBS/DDD）
relations:
  specializes:
    - ontology:concept/pdca
  composed_of:
    - ontology:entity/report-center-system
  relates_to:
    - ontology:domain/ontology-hybrid-research-topdown
    - ontology:domain/ontology-hybrid-develop-bottomup
    - ontology:domain/ontology-hybrid-leaf-middleout
    - ontology:pattern/ontology-modular-reference
    - ontology:pattern/testable-signal-to-test-derivation
attributes:
  - name: hybrid_bidirectional
    desc: 调研根→叶全面记录，开发叶→根实现，同树反向闭环
    constraint: 项目实体为根 composed_of 树全面落盘；叶 dependencies:[] 根聚叶
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary 检查本根 composed_of 3叶可追且 islands:0，且 grep -R 'hybrid' ontology/domain/ontology-hybrid-*.md 可命中"
  - name: applicability
    desc: 调研产本体、开发用本体的双向场景
    constraint: 适用于项目实体经多本体组合/继承实现的调研→开发双向
    testable_signal: "检查本文件含 Research Topdown 与 Develop Bottomup 且经 ontology-validate 通过"
---

# 混合方法论本体根（Hybrid Research→Dev）

> 综合 `Ontology101 top-down/bottom-up/combination` + `METHONTOLOGY evolving prototype` + `NeOn 9场景` + `WBS 100%/Yo-Yo` + `DDD bounded context`，解决“调研一层层往下拆到叶子，开发一层层往根实现”的本体叶粒度与双向一致性。

## 双向同树

- **调研（根→叶）**：项目实体为根，`composed_of` 逐层拆至叶，调研产出即 `ontology/<type>/<slug>.md` 全面落盘（`100% Rule` 父=子之和，`middle-out` 中层显著优先）
- **开发（叶→根）**：叶→根实现，`ontology_tree_split --ontology-dir` 叶→根生 `candidates`，`compute-frontier` `ready-set [[叶],[根]]`，叶并行根串行，Work Package可分配

## 叶粒度（middle-out Yo-Yo）

满足三准绳任一即叶：可独立验证 / 可独立演进 / 可独立复用；过粗split、过细merge

## 应用

以 `report-center-system(composed_of: web, collection)` 为示范，2叶正交满足三准绳，`tree_split` 可调度，叶即任务1:1 硬映射

## 来源

- Stanford Ontology101 (Noy & McGuinness 2001)
- METHONTOLOGY (Gómez-Pérez et al. 1997)
- NeOn Methodology (Suárez-Figueroa et al. 2012)
- PMI WBS Practice Standard (Yo-Yo, 100% Rule)
- DDD bounded context (Evans)
