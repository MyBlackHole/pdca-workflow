---
schema: pdca.asset/v1
id: ontology:concept/auto-induce-flow-trigger
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/auto-induce-flow-trigger/1.0.0
summary: FlowIssue→本体补强自动触发：occurrence 阈值达标后提示创建本体补强 candidate
relations:
  specializes:
  - ontology:concept/pdca-continuous-improvement
  relates_to:
  - ontology:concept/self-optimization-loop
  - ontology:concept/pdca-evidence
---

# FlowIssue→本体补强自动触发（auto-induce-flow-trigger）

聚合 `pdca/improvements/flow-issue-backlog.json`，对 `occurrence_count >= threshold`（默认 3）且尚未创建 `improvement_candidate` 的 FlowIssue 提示可自动创建候选，闭合 `flow-audit → issue backlog → improvement candidate → PDCA task` 环路。

- **触发**：`ontology_gate.auto_induce_flow_issues(root, threshold)` 扫描 backlog，顾问式不阻断。
- **阈值**：可配置 `threshold`（默认 3），避免单次 fail 误触发（self-optimization-loop 单次 fail 不足证明原则）。
- **输出**：`AUTO_FLOW_INDUCE_CANDIDATE` Issue，携带 `python3 scripts/create-improvement-candidate.py --issue <id>` 指引。
- **HITL**：候选仍需走正常 Plan/Grill/`final_confirmation`，审计发现不是自动变更授权。
- **防刷屏**：单次最多提示 3 条，按 occurrence_count 降序。

## 决策背景
- 背景：flow-audit 记录后无自动到 candidate 的触发，依赖人工聚合与判断。
- 决策：新增阈值触发器，顾问式提示，保证改进候选仍受控实施。

## 来源
- `T0456-0831-ontology-auto-induce`
