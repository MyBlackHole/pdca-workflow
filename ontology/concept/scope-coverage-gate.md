---
schema: pdca.asset/v1
id: ontology:concept/scope-coverage-gate
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/scope-coverage-gate/1.0.0
summary: 本体覆盖门禁设计结论（改前具名声明制，推荐声明覆盖检查）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:domain/skill-design-it-twice
  - ontology:domain/skill-codebase-design
  - ontology:concept/pdca-evidence
attributes:
- name: pre_declared_coverage
  desc: 改动模块逻辑须事前具名声明
  constraint: 声明集来自fragment子树或PRD具名；diff超出声明即缺口；事后回链不替代
  testable_signal: 检查设计design.md含scope-declare.json契约与tests/test_scope_coverage.py接缝描述，且grep可命中两者
- name: kind_gap_record
  desc: flow-do所写--kind design代码不接受已记录
  constraint: 实施前二选一：补evidence-design子类型，或修正flow-do写法；本次以document登记
  testable_signal: 运行 register-evidence.py --help 输出与flow-do E路径文字比对，断言一致或差值已立案
---

# 本体覆盖门禁设计结论（scope-coverage-gate）

来源：T2112，记录 `records/T2112-0910-line-ontology-design/conclusion.md`。Grounding：`pdca/tasks/0910-line-ontology-design/design.md`、`scripts/register-evidence.py:73-76`允许集。复用覆盖T2113-0910-line-map-table/T2114-0910-line-alt-compare。

## 背景问题
用户纠偏：本质是修改内容须本体事先具备，非逐行映射。

## 核心机制
1. 具名声明制：改前声明改后判定。（依据：`ontology:domain/skill-design-it-twice`）
2. 推荐声明覆盖检查，语义回链降级补充。（依据：`ontology:domain/skill-codebase-design`）
3. 口径差立案：design kind缺失。（依据：`ontology:concept/pdca-evidence`）

## 适用边界
设计结论；实施另起development。

## 违反后果
无声明实现即孤儿代码；行级误读导致不可执行。

## 关联导航
- 设计：`ontology:domain/skill-design-it-twice`
- 证据：`ontology:concept/pdca-evidence`
