# 审查全场景本体化：是否基于本体与产出本体操作

## 背景

T0487断定6种scenario中5强核1趋强（review 83%），但未逐场景给出“基于本体”（输入侧）与“产出本体操作”（输出侧）的分离判定。随着wizard/teach等P1/P2补齐，需以当前79 tasks、365 nodes、0 islands快照，对 `development/bugfix/research/documentation/design/review` 6场景做全量复核：每场景的 Plan输入、Do执行、Act产出是否都触及本体，以及是否有可机器校验的产出本体操作。

## 目标

- 逐场景判定“基于本体”（Plan/Do是否以 `ontology_fragment`/`skill`/`pattern` 为输入核）与“产出本体操作”（Act是否产生/深化 `ontology/`节点或强引用边，且被 `disposition`/`check-research-ontology-settlement`/`archive自检` 机器校验）
- 输出6×2矩阵 + 缺口与改进建议

## 范围

- 输入：79 tasks（40 dev/5 bugfix/15 research/10 doc/2 design/7 review）、`ontology/process/flow-*.md` 4流程、`ontology/domain/skill-*.md`、`scripts/ontology_gate.py`、`scripts/check-research-ontology-settlement.py`
- 输出：`records/T0492/report.md` + 证据 + 本结论
- 不做：不改业务代码，不补历史任务的追溯改造

## 功能需求

1. 基于本体：检查每场景 `task.json#meta.ontology_fragment` 有无、`ontology-ready` 是否为Plan→Do硬门禁、Do是否调用该场景skill且skill本体化（`skill-tdd`/`diagnosing-bugs`/`research`/`writing-great-skills`/`codebase-design`/`code-review`）
2. 产出本体操作：检查每场景Act是否必须 `meta.disposition` 含 `ontology:`/`records-only`（`disposition_ontology_issues` 全任务硬门禁）、research是否额外 `##本体沉淀`（`check-research-ontology-settlement.py`）、archive是否 `ontology-validate+islands:0`

## 非功能需求

- 可重跑：每判定给 `grep`/`validate`/`graph` 命令与 file:line

## 验收标准

- [ ] AC-1 6场景“基于本体”已逐项判定且给证据（plan/do输入侧）
- [ ] AC-2 6场景“产出本体操作”已逐项判定且给证据（act输出侧，含机器校验）
- [ ] AC-3 6×2矩阵与覆盖率统计已输出（当前79 tasks分场景统计）
- [ ] AC-4 豁免行为已审计且硬性指标建议已给出（含exempt/records-only是否应收紧为硬指标）
- [ ] AC-5 缺口与改进建议已给出（含review趋强的收紧点）
- [ ] AC-6 报告已登记且 `validate-convergence valid:true`

## 关联本体节点

```
ontology:concept/pdca-ontology-ready
ontology:concept/pdca-task
ontology:process/flow-plan
ontology:process/flow-do
ontology:process/flow-act
ontology:domain/skill-research
```

## 拆分映射

- 基于本体判定 -> ontology:process/flow-do
- 产出本体操作判定 -> ontology:process/flow-act
- 统计与缺口 -> ontology:concept/pdca-task
