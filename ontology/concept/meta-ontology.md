---
schema: pdca.asset/v1
id: ontology:concept/meta-ontology
type: concept
layer: Knowledge
summary: 本体的本体（ontology of ontology）——建模本体资产、创建门禁与校验规则的元元本体
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/meta-ontology/1.0.0
---
# meta-ontology

本体的本体（ontology of ontology）：把"本体系统本身"作为建模对象的一套元本体。

- **目的**：使本工作流本体（ontology/）的**创建门禁与校验规则**成为本体自身的节点与关系，从而让门禁的权威依据来自本体（自描述），而非仅来自 `ontology/README.md` 散文或 `scripts/ontology-validate.py` 的硬编码逻辑。
- **构成**：本体资产（`ontology-asset`）、创建门禁（`ontology-creation-gate`）、校验器（`ontology-validate`）、规则类（`ontology-rule`）及其 6 条规则实例（`ontology-rule-*`）。
- **权威链**：`ontology-creation-gate` 由 `ontology-validate` 配置执行（`configured_by`），并依据（`relates_to`）AC-1~AC-6 规则节点；`ontology-asset` 受该门禁约束。详见各子节点。
- **范围**：本 meta-ontology 是"权威依据"层（范围 A）；不替代 `ontology-validate.py` 的执行逻辑（其读取规则节点为范围 B，留待后续）。
