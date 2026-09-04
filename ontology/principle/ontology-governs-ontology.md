---
schema: pdca.asset/v1
id: ontology:principle/ontology-governs-ontology
type: principle
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-governs-ontology/1.0.0
summary: 本体治理本体准则：本体知识控制本体产生与使用，PDCA基于PDCA本体，调研基于调研方法论产出受本体论本体细节约束，科学方法论控AI可验证可审查
relations:
  specializes:
    - ontology:principle
  guides:
    - ontology:concept/domain-entity
    - ontology:process/code-review-process
  relates_to:
    - ontology:concept/ontology-creation-gate
    - ontology:concept/ontology-validate
    - ontology:domain/ontology-hybrid-methodology
    - ontology:concept/pdca-ontology-ready
    - ontology:pattern/testable-signal-to-test-derivation
attributes:
  - name: ontology_governs_creation
    desc: 本体知识控制本体产生
    constraint: 调研产生本体前必须基于 `ontology-hybrid-research-topdown` 方法论，且产出本体受 `ontology-creation-gate` 6规则（type/非空悬/无环/可测/丰富度/range）约束
    testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查新产出本体0 issues 且 grep -R 'Research Topdown' ontology/domain/ontology-hybrid-*.md 可命中"
  - name: ontology_governs_usage
    desc: 本体知识控制本体使用
    constraint: 任务使用本体时必须声明 `meta.ontology_fragment` 且经 `ontology-ready` 硬拦，消费时经 `pdca_context.py --phase` 实时拉取该阶段本体
    testable_signal: "检查 pdca/tasks/0902-*/task.json 中 leaf任务 meta.ontology_fragment==父fragment 且 python3 scripts/ontology_gate.py 校验无 ONTOLOGY_FRAGMENT_MISSING"
  - name: pdca_grounded_in_pdca_ontology
    desc: PDCA流程基于PDCA本体知识
    constraint: PDCA四阶段与门禁由 `pdca-ontology-ready` `pdca-creation-gate` `pdca-validate` 元本体驱动，改流程只改本体节点
    testable_signal: "运行 python3 scripts/pdca_context.py --phase do 检查输出含 pdca-ontology-ready 且经 validate 通过"
  - name: research_grounded_in_research_methodology
    desc: 调研基于调研方法论产生本体
    constraint: 调研必须给予 `ontology-hybrid-research-topdown`（根→叶 100% + middle-out）方法论，产出本体表全面记录 `composed_of` 树
    testable_signal: "检查 ontology/domain/ontology-hybrid-research-topdown.md 含 '100% Rule' 且 grep -R 'composed_of' ontology/entity/report-center-system.md 可命中"
  - name: ontology_expression_governed_by_meta_ontology
    desc: 调研产出本体表达细节受本体论本体要求
    constraint: 本体表达细节（frontmatter `pdca.asset/v1` + `relations` + `attributes`）受 `ontology-creation-gate` + `ontology-validate` 6条规则本体约束，`type==目录名` 且 `guides` 合法
    testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查 TYPE_DIR_MISMATCH/GUIDES_RANGE 0 issues 且经 scaffold 可产"
  - name: science_controls_ai_verifiable_reviewable
    desc: 科学方法论控制AI可验证可审查等
    constraint: AI产生过程受 `ontology-validate`（可验证）+ `code-review` 双轴（可审查）+ `knowledge-provenance`（可追溯）+ `scaffold`（可复现）四硬控制
    testable_signal: "运行 python3 scripts/ci-ontology-gate.py 返回 GATE OK 且 grep -R 'scaffold' ontology/pattern/testable-signal-to-test-derivation.md 可命中"
---

# 本体治理本体准则（Ontology Governs Ontology）

> **准则**：本体知识来控制本体知识的产生与使用。PDCA流程基于PDCA本体知识，调研给予调研方法论产生本体，调研产出本体表的表达细节受本体论的本体要求；使用科学方法论控制AI产生可验证、可审查、可追溯、可复现的过程。

## 1. 本体控产生

调研产出本体前 **必须** 基于 `ontology-hybrid-research-topdown`（根→叶 100%全面记录，`composed_of` 树落盘，`middle-out` 中层显著优先），且产出本体受 `ontology-creation-gate` 6规则（AC-1 type受控/AC-2非空悬/AC-3无环/AC-4可测/AC-5丰富度/AC-6 guides范围）硬校验 `ontology-validate 0 issues`。

## 2. 本体控使用

任务使用本体时 **必须** 声明 `meta.ontology_fragment`，经 `ontology-ready` `plan→do` 硬拦 `ONTOLOGY_FRAGMENT_MISSING`，且 `task_identity` 自动继承 `fragment/node_type` 沿本体边界对齐，`pdca_context.py --phase <phase>` 实时拉取该阶段可消费本体。

## 3. PDCA基于PDCA本体

PDCA四阶段、门禁、证据、结论均由 `pdca-ontology-ready` `pdca-creation-gate` `pdca-validate` `pdca-evidence/verdict` 元本体驱动；改流程只改本体节点，校验行为自动跟随（B方案），文档/脚本漂移从源头消除 `ontology/README.md:109`。

## 4. 调研基于调研方法论

调研必须给予 `research-topdown` 方法论（根→叶全面 + `report-center-system` 正例），产出本体表 **全面记录** `composed_of` 树，缺一叶即缺一维度，`graph islands:0` 可检。

## 5. 本体表达细节受本体论本体要求

调研产出本体表的表达细节（`schema: pdca.asset/v1` + `relations` + `attributes[].testable_signal`）受本体论的本体（`ontology-creation-gate` 6规则）要求：`type==目录名`、`guides` 必为 `DomainEntity/Process`、环检测、信号非泛化。

## 6. 科学方法论控AI

以 `ontology-validate`（可验证）+ `code-review` 双轴 Standards/Spec 并行（可审查）+ `knowledge-provenance`（可追溯）+ `ontology_test_scaffold`（可复现）四硬控制AI产生；`hybrid-methodology` （Ontology101/METHONTOLOGY/NeOn/WBS/DDD）为其科学背书，`ci-ontology-gate.py` 提交级 `GATE OK` 为终检。

## 门禁链

`research Topdown → ontology-validate 6规则 → ontology-ready → tree_split/scaffold → validate-convergence → disposition ontology: → archive islands:0 → ci-gate`

## 已知坑

- 以本体治本体时，元本体自身变更亦受 `ontology-creation-gate` 约束（自举需 `ontology_exempt_reason` 白名单 `T0493:archive`）
- 调研未给方法论即产本体，必漏叶与约束，无法 `scaffold`
