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

## 决策背景（原 ADR-0036：证据锚定）
- 决策：register-evidence 启动时枚举 pdca-evidence 子类型构建允许表；--kind 须命中子类型并写 evidence_type_ref，未知 kind 报错，使证据机器锚定到本体。
