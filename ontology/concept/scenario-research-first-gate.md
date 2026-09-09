---
schema: pdca.asset/v1
id: ontology:concept/scenario-research-first-gate
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/scenario-research-first-gate/1.0.0
summary: 六场景先本体后操作判定规则（Do准入复用即算，Act强制回写，仅自举豁免）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-gate-do
  - ontology:concept/pdca-ontology-ready
  - ontology:concept/pdca-scenario-boundary-rule
  guides:
  - ontology:domain/skill-triage-work
attributes:
- name: do_admission_reuse
  desc: 六场景Do准入均强制ontology-ready，复用合法fragment即算先调研
  constraint: development/bugfix/research/documentation/design/review在phase=do时须含ontology_fragment合法或ontology_exempt合规，否则ONTOLOGY_FRAGMENT_MISSING阻断
  testable_signal: 运行 python3 scripts/ontology_reason.py admission --phase do 断言返回含ontology-ready，且运行 python3 scripts/transition-phase.py在缺fragment任务上返回rejected含ONTOLOGY_FRAGMENT_MISSING
- name: act_mandatory_produce
  desc: 六场景Act均强制新产生本体，不再接受records-only
  constraint: T0513起disposition须含ontology:xxx且节点存在，否则DISPOSITION_ONTOLOGY_MISSING或NOT_FOUND阻断archive
  testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 断言返回OK，且运行 python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/0909-six-scenario-research-first 断言不报SETTLEMENT_MISSING
- name: boundary_misclass_guard
  desc: 含代码产出标research属错配，须走development
  constraint: 含脚本/测试/可回归验证产物判定为development，纯结论判定为research，unknown退出码1
  testable_signal: 运行 python3 scripts/scenario-boundary-check.py --judge --desc含代码信号断言返回development，且纯调研描述断言返回research
---

# 六场景先本体后操作判定规则（scenario-research-first-gate）

来源：T2072，记录 `records/T2072-0909-six-scenario-research-first/conclusion.md`。Grounding：`scripts/ontology_gate.py:23-43`、`scripts/ontology_reason.py:128-146`、`scripts/pdca_core.py:447-451`。

## 背景问题
六场景Do路径文档分散，误读为每次开发前必须新建research票，或误将含代码任务标research绕过测试。

## 核心机制
1. Do准入复用式先调研：`pdca-gate-do`对六场景全覆盖，`ontology_reason.admission_conditions(do)=[ontology-ready]`，有合法fragment即放行。（依据：`ontology:concept/pdca-gate-do`）
2. 执行消费本体：development/bugfix靠Seam+测试，documentation靠Diataxis+Source门禁，design靠双方案+grilling，review靠双轴+grilling，research本身生产本体。（依据：`ontology:process/flow-do`）
3. Act强制回写：disposition须含`ontology:`且节点可解析，archive前validate+islands:0。（依据：`ontology:process/flow-act`）
4. Do前向指针（T2073审查补记，复用覆盖T2074-0909-design-review-standards/T2075-0909-design-review-spec）：design/review在Do内只产`design.md/review.md+evidence`，回写在Act统一执行；Do缺沉淀字样按严格标准记文档Warning，建议E/F各加一句指向Act回写，避免误读为无回写。（依据：`records/T2073-0909-design-review-writeback-audit/conclusion.md`）

## 适用边界
适用于含`ontology:concept/pdca`元本体的仓库版本；仅`meta.ontology_exempt=true`自举任务豁免，需reason≥20字符含ontology。

## 违反后果
缺fragment无豁免则plan→do被拒；Act无本体回写则archive被拒；含代码标research则边界检查判development，research路径缺测试环节。

## 关联导航
- 准入：`ontology:concept/pdca-gate-do`、`ontology:concept/pdca-ontology-ready`
- 边界：`ontology:concept/pdca-scenario-boundary-rule`
- 执行：`ontology:process/flow-do`、`ontology:domain/skill-research`
- 沉淀：`ontology:process/flow-act`
