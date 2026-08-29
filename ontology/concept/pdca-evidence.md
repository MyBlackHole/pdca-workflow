---
schema: pdca.asset/v1
id: ontology:concept/pdca-evidence
type: concept
layer: Knowledge
summary: PDCA 证据元概念
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-evidence

证据元概念。Do 阶段登记、Check 阶段对照的可复核事实。

- **含义**：支持验收标准的事实，通过 `evidence/manifest.jsonl` 登记，每条含 digest 可复核。
- **受识别类型**：`test-result` / `convergence-map` / `review`（由 `evidence-*` 节点 specializes `pdca-evidence` 声明）；`ontology_reason.recognized_evidence` 据此识别。
- **convergence-map 特殊性**：描述 `meta.convergence → AC → evidence ID` 映射，本身不能作为验收通过证据。

