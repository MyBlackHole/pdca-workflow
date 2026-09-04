---
schema: pdca.asset/v1
id: ontology:concept/pdca-evidence
type: concept
layer: Knowledge
summary: PDCA 证据元概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-evidence/1.0.0
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

## 决策背景（原 ADR-0003：Convergence 证据映射与 Do→Check 硬门禁）
- 背景：旧 evidence gate 能验证证据文件/摘要/单项 criteria，但无法证明全部 PRD 验收条件已覆盖，也无法证明 Plan 每条 `meta.convergence` 有验收条件与证据支持；verify-convergence 依赖 AI 手工比对。
- 决策：在 record evidence 中登记独立 `convergence.json`，作为 Do→Check 硬门禁；meta.convergence 为 Plan 基线，不被执行结果反向修改；脚本 `validate-convergence.py` 机器校验覆盖与文本一致。
