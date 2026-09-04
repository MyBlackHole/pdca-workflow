---
schema: pdca.asset/v1
id: ontology:pattern/ontology-metrics
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-metrics/1.0.0
summary: 量化度量本体：本体健康×过程硬指标×追溯度×效果verdict（可验证可度量）
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/pdca-task
    - ontology:concept/self-optimization-loop
  relates_to:
    - ontology:concept/ontology-validate
    - ontology:concept/pdca-continuous-improvement
    - ontology:principle/ontology-governs-ontology
attributes:
  - name: health_metrics
    desc: 本体健康三件套
    constraint: validate 0 issues + islands:0 + scaffold可产率100%（4混合方法论节点可scaffold）
    testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查0 issues 且 python3 scripts/ontology_graph.py --format summary 检查islands:0 且 4节点scaffold可产"
  - name: hard_metrics
    desc: 过程硬指标双100%
    constraint: 新任务 fragment 100% + disposition含ontology 100%（T0493硬指标化后）
    testable_signal: "运行 grep -R 'ontology_fragment' pdca/tasks/0903-*/task.json 检查新任务8/8命中 且 grep -R 'ontology:' pdca/tasks/0903-*/task.json中disposition 命中"
  - name: provenance_metrics
    desc: 追溯度
    constraint: ontology file含source_record回链率，records→knowledge单向断链率可量
    testable_signal: "运行 grep -R 'T049' ontology/domain/ontology-hybrid-*.md 检查回链率 且经 validate 通过"
  - name: effectiveness_verdict
    desc: 效果 verdict 三态
    constraint: 跨周期 occurrence→verdict（improved/neutral/regressed）闭环，需 metrics基线
    testable_signal: "检查 ontology/concept/self-optimization-loop.md 含 'improved' 且 ci-ontology-gate 可输出 metrics.json"
  - name: gate_metrics_output
    desc: 门禁度量输出
    constraint: ci-ontology-gate 输出 metrics.json 含 health/hard/provenance/effectiveness 且 GATE OK
    testable_signal: "运行 python3 scripts/ci-ontology-gate.py 检查 GATE OK 且含 metrics 输出"
---

# 量化度量本体（Metrics）

> 来源 `METHONTOLOGY evaluate` + `NeOn empirical evaluation` + `self-optimization-loop`

- **Health**：`validate 0` + `islands:0` + `scaffold 100%`（4混合节点 `scaffold` 可产）— `ontology-validate` `graph` 双检
- **Hard**：新任务 `fragment 100%` + `disposition 100%` — `grep fragment` + `DISPOSITION_ONTOLOGY_MISSING` 硬拦 `pdca_core.py:442`
- **Provenance**：`records→knowledge` 回链率 — `grep T049 ontology/` 可量，T0494断链5/5待补 `source_record`
- **Effectiveness**：`occurrence→candidate→task→verdict(improved/neutral/regressed)` 跨周期闭环 — `self-optimization-loop.md:1` 需 `metrics` 基线，`ci-gate` 输出 `metrics.json` 作下轮 `diff`

**门禁**：`ci-ontology-gate` `GATE OK + metrics.json` 硬拦 `GATE OK` 外加量可复盘
