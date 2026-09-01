---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-leaf-middleout
type: domain
layer: Knowledge
status: active
summary: 混合方法论Leaf Middle-out：叶粒度三准绳（可独立验证/演进/复用）与Yo-Yo校正
relations:
  specializes:
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:pattern/ontology-modular-reference
    - ontology:pattern/testable-signal-to-test-derivation
attributes:
  - name: leaf_three_criteria
    desc: 叶三准绳
    constraint: 满足任一即独立：可独立验证(1 leaf=1 testable_signal)/可独立演进(维度正交)/可独立复用(≥2复用或≥3 attrs)
    testable_signal: "检查 ontology/domain/ontology-hybrid-leaf-middleout.md 含 '三准绳' 且经 ontology-validate 通过，且以 report-center-web 2叶为正例 grep 可命中"
  - name: granularity_repair
    desc: 粒度失衡修复
    constraint: 过粗按正交度split，过细按 relates_to 合并（Yo-Yo跳变）
    testable_signal: "检查本节点含 '过粗' 与 '过细' 且 ontology_graph --format dot 可导出叶边"
---

# Leaf Middle-out — 叶粒度三准绳（Yo-Yo）

> 来源 METHONTOLOGY `middle-out` + WBS `Yo-Yo` + DDD `bounded context`

- **三准绳**：可独立验证 / 可独立演进（正交） / 可独立复用（≥2复用或≥3 attrs或方法论类）——满足任一即独立 Leaf，见 `ontology-modular-reference.md:21`
- **Yo-Yo校正**：调研top-down定框架→开发bottom-up补细节→失衡时跳变：过粗按正交度 `split`，过细按 `relates_to` 合并
- **正例**：`report-center-system` → `web` + `collection` 正交二叶，不再碎
