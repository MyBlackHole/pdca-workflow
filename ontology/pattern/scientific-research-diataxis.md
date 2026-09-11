---
schema: pdca.asset/v2
id: ontology:pattern/scientific-research-diataxis
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/scientific-research-diataxis/3.1.0
summary: 科学调研Diátaxis支：四象限 tutorial/how-to/reference/explanation（对齐diataxis.fr Procida）
relations:
  guides:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:pattern/research-diagram-methodology
  instance_of:
  - ontology:pattern
attributes:
- name: four_quadrants
  desc: 四象限
  constraint: tutorial(习得实践)/how-to(应用实践)/reference(应用认知)/explanation(习得认知)四且仅四
  testable_signal: 运行 grep -q 'diataxis' ontology/pattern/scientific-research-diataxis.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
- name: compass
  desc: Diátaxis罗盘
  constraint: 混淆四类为文档差的首因，罗盘可纠偏
  testable_signal: 检查本文件含 'Diátaxis' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/scientific-research-diataxis.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
- name: lightweight_iterative
  desc: 轻量迭代
  constraint: 不预设四空结构，小迭代中自然成形
  testable_signal: 检查本文件含 '迭代' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/scientific-research-diataxis.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 科学调研Diátaxis支

> 来源 `diataxis.fr` Procida（Django/NumPy/Cloudflare官方），Fellowship 2021

- **四象限**：`tutorial`（习得实践习）、`how-to`（应用实践）、`reference`（应用认知查）、`explanation`（习得认知理）— 实践×认知×习得×应用二维推导，四且仅四
- **罗盘**：决策树纠 `tutorial` 混 `reference` 误
- **轻量迭代**：不建四空盒，小迭代中自然成形，`skill-research` 多图模板即 `reference` 象限
