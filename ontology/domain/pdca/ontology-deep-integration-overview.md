---
schema: pdca.asset/v1
id: ontology:domain/ontology-deep-integration-overview
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-deep-integration-overview/1.0.0
summary: 本体深度融合总览（拆分×测试×树形执行×知识闭环的方法论扇出）
domain:
  - ontology:domain/ai-efficiency
relations:
  specializes:
    - ontology:concept/pdca
  relates_to:
    - ontology:entity/ontology-deep-integration
    - ontology:pattern/testable-signal-to-test-derivation
    - ontology:pattern/ontology-modular-reference
    - ontology:domain/ai-efficiency-ticket-dag-ready-set
    - ontology:concept/pdca-task
attributes:
  - name: applicability
    desc: 任意 PDCA 任务通过本体表达与产出
    constraint: 任务须声明 meta.ontology_fragment 与 ontology_anchor，Act 须沉淀本体或显式 records-only
    testable_signal: "检查任务 task.json 的 meta.ontology_fragment 存在且指向合法 pdca.asset/v1 目录，且 meta.disposition 含 ontology: 或 records-only 关键词，否则 archive 门禁拒收"
  - name: link_depth
    desc: 实例到本体的链路深度自然可控
    constraint: 按本体关系自然拆分，单任务仅涉及1-3本体扇出而非串联，不设硬性跳数上限
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary 检查实例强引用本体均存在且 0 islands，单任务引用本体数通常≤3"
  - name: checklist_propagation
    desc: 清单透传而非独立节点
    constraint: B1-B4 等清单在领域节点 attributes 中承载，实例通过属性继承而非额外跳数
    testable_signal: "检查清单类本体不存在独立 pattern 节点，而是在领域节点内可 grep 命中 检查清单"
---

# 本体深度融合总览

以 `ontology:entity/ontology-deep-integration` 的 `composed_of` 树为 WBS，以 `testable_signal` 为测试源，以 `ontology_ready` 与 `disposition` 为闭环门禁，实现“本体即任务树、叶→根、万物皆本体、事事产知识”。

## 扇出维度

- **拆分**：`ontology:entity/ontology-deep-integration-split` + `ai-efficiency-ticket-dag-ready-set`（显式依赖边+ready-set）
- **测试**：`ontology:entity/ontology-deep-integration-test` + `testable-signal-to-test-derivation`（三派生）
- **执行**：`ontology:entity/ontology-deep-integration-tree` + `ontology-modular-reference`（扇出而非串联）
- **知识**：`ontology:entity/ontology-deep-integration-knowledge` + `knowledge-provenance`（来源封存）
