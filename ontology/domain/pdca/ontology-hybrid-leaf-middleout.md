---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-leaf-middleout
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-hybrid-leaf-middleout/1.0.0
summary: 混合方法论Leaf Middle-out：叶粒度三准绳（可独立验证/演进/复用）与Yo-Yo校正
relations:
  specializes:
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:pattern/ontology-modular-reference
    - ontology:pattern/testable-signal-to-test-derivation
attributes:
  - name: leaf_three_criteria
    desc: 叶三准绳（可独立验证/演进/复用）
    constraint: 满足任一即独立：可独立验证(1 leaf=1 testable_signal可scaffold)/可独立演进(维度正交如 web vs collection)/可独立复用(≥2复用或≥3 attrs或方法论/Checklist类)
    testable_signal: "检查本节点含 '三准绳' 且经 ontology-validate 通过，且以 report-center-web 2叶为正例 grep -R 'report-center' ontology/entity/report-center-*.md 可命中"
  - name: granularity_repair
    desc: 粒度失衡修复（Yo-Yo跳变）
    constraint: 过粗（1叶多约束无法单信号派生）按正交度split，过细（叶无约束可测）按 relates_to 合并
    testable_signal: "检查本节点含 '过粗' 与 '过细' 且 python3 scripts/ontology_graph.py --format dot 可导出叶边且经 validate 通过"
  - name: bounded_context_alignment
    desc: 有界上下文对齐
    constraint: 叶边界与 DDD bounded context 一致，跨叶仅经 `relates_to` 弱联
    testable_signal: "检查本节点含 'bounded context' 且以 report-center-web/collection 正交为例可 grep 命中"
  - name: leaf_min_size
    desc: 叶最小可交付
    constraint: 叶至少含1条可测信号且可分配至1人1验，`pytest --collect-only` 可命中
    testable_signal: "运行 python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-hybrid-leaf-middleout --out /tmp/leaf_demo.py 可产且可收集"
---

# Leaf Middle-out — 叶粒度三准绳（Yo-Yo）

> 来源 METHONTOLOGY `middle-out` + WBS `Yo-Yo` + DDD `bounded context` + `ontology-modular-reference:21`

- **三准绳**：可独立验证（1 leaf =1 `testable_signal` 可 `scaffold`）、可独立演进（维度正交如 `web` 鉴权 vs `collection` 调度）、可独立复用（≥2复用或≥3 attrs或方法论/Checklist类）——满足任一即独立 Leaf。
- **Yo-Yo校正**：调研top-down定框架→开发bottom-up补细节→失衡时跳变：**过粗**（1叶多约束无法单信号派生，如 `report-center-system` 单叶含双约束）按正交度 `split` 为 `web` + `collection`；**过细**（叶无约束可测）按 `relates_to` 合并。
- **有界上下文**：叶边界与 `bounded context` 一致，跨叶仅经 `relates_to` 弱联，`composed_of` 仅父→叶强组合。
- **正例/反例**：正例 `report-center-system` → `web` + `collection` 正交二叶（各 `testable_signal` 可 `scaffold`）；反例 单叶 `report-center` 过粗、`report-center-web-auth` 再碎为过细（无独立约束）。
- **门禁**：`check-ontology-leaf.py` 可 `grep -R '三准绳'` + `ontology_graph --format dot` 导出叶边 + `scaffold` 可产三检。
