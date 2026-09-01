# 本体闭环完整性审计与mattpocock差距收敛

## 背景

T0450（0831闭环审查）与 T0482（0903深化收敛）已完成本体深度融合（拆分×测试×树形执行×全任务知识闭环）与全量信号去泛化、模板硬化、复用检索、Act门禁收紧。但用户最新要求重新以“完成闭环”视角全量复审：本体是否真正贯穿PDCA各阶段并成为可验证交付物；对照 mattpocock/skills 最新版本（243k stars, 457 commits）是否仍有未吸收机制；并重点回答——调研是否必须产生本体知识、开发是否必须依赖本体进行任务拆分与单元测试、本体如何持续补充/优化/修复、每种scenario_type是否皆以本体为核心、本体自循环（产生→使用→优化→修改）是否闭合、本体如何支撑测试用例。

本审查为 research 场景，产出为带可复核证据的结论报告与改进候选清单，不产生生产代码变更。

## 目标

- 给出本体在PDCA全周期的“使用完成闭环”成熟度判定（plan/do/check/act/archive五阶段逐项）与证据索引
- 复审 mattpocock/skills 自 T0450 后新增/遗漏的可借鉴内容，输出优先级矩阵与本体映射
- 明确“调研→本体知识→拆分→测试”的链路形态，判定当前每种工作模式是否本体为核、链路是否自循环、测试如何被本体驱动

## 范围

- 输入：`ontology/` 363节点/871边（`scripts/ontology_graph.py --format summary`）、`scripts/ontology-validate.py`、6条Do路由（development/bugfix/research/documentation/design/review）、12个活跃+62个归档task.json、`ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms`、mattpocock/skills main（36 skills: user-invoked 21/model-invoked 15）
- 输出：`records/T0487-0901-ontology-closure-audit/report.md` + `evidence/manifest.jsonl` + 本结论
- 不做：不改 `task.schema.json`、不引入图数据库、不强制历史任务补 `fragment`、不改生产业务代码

## 功能需求

1. 闭环审查：逐阶段验证本体消费点是否为硬门禁或顾问式，提供 `ontology/README.md §10/§12`、`flow-*.md`、`ontology_gate.py`、`ci-ontology-gate.py` 的逐条证据
2. mattpocock差距复审：以 T0450 P0/P1/P2 为基线，增量比对 wayfinder/triage/implement/codebase-design/tdd/diagnosing-bugs/prototype/wizard/teach/grilling 等36技能的最新描述，标记已吸收/部分吸收/未吸收
3. 链路形态：绘制“调研→本体知识（research本体沉淀决策）→拆分（clash-check+tree-split+task_identity+compute-frontier）→测试（testable_signal三模式+scaffold）→验证（validate-convergence+ontology-validate）”的依赖链，判定各scenario_type的本体核化程度
4. 自循环：梳理本体4支自循环（产生：grilling+domain-modeling+induction；使用：ontology_fragment+relations；优化：retrospective七类+self-optimization-loop；修改：ontology-check+validate+archive自检），评估断点
5. 测试支撑：以 `ontology:pattern/testable-signal-to-test-derivation` 与 `ontology:pattern/ontology-modular-reference` 为源，说明属性断言/契约测试/收敛验证三模式如何落地为 `scripts/ontology_test_scaffold.py` 与 `tests/test_*_scaffold.py`

## 非功能需求

- 可复核：每结论带 file:line 或可重跑命令（`ontology-validate`/`ontology_graph`/`validate-convergence`/`compute-frontier`）
- 零幻觉：引 mattpocock 时标注 commit/版本与本地对照节点
- 可门禁：结论写入 `records/<record>/conclusion.md ## 本体沉淀` 与 `meta.disposition` 含 `ontology:` 关键词，否则 `archive` 拒收

## 验收标准

- [ ] AC-1 本体“使用完成闭环”已逐阶段审查：plan/do/check/act/archive 各给出“硬门禁/顾问式/缺口”判定与证据索引，且 `ontology-validate 0 issues, islands 0` 可重跑
- [ ] AC-2 mattpocock差距已增量复审：列出自T0450后新增/仍未吸收的机制（≥5项对比），每项给优先级、本体映射与落地建议
- [ ] AC-3 链路与工作模式已澄清：明确调研是否必须产生本体、开发拆分/单元测试是否必须依赖本体，每种 scenario_type（6种）给出“本体为核/豁免/顾问式”判定
- [ ] AC-4 自循环已建模：给出本体“产生→优化→修改→使用”四支闭环图与断点/改进点，且与 `self-optimization-loop` / `knowledge-provenance` / `ontology-creation-gate` 对齐
- [ ] AC-5 测试支撑已说明：以 `testable_signal` 三模式解释测试用例如何从本体派生，并验证至少2个实例的 `scaffold-map.json` 与 `pytest --collect-only` 可收集
- [ ] AC-6 持续演进已说明：本体补充/完善/修复的触发器（research沉淀、retrospective、auto_induce、validate失败）与门禁链已梳理
- [ ] AC-7 报告已登记为证据：`report.md` 经 `register-evidence` 登记且 `convergence.json` 回链AC与证据，`validate-convergence valid:true`

## 关联本体节点

```
ontology:concept/pdca
ontology:concept/pdca-task
ontology:concept/pdca-ontology-ready
ontology:concept/self-optimization-loop
ontology:concept/knowledge-provenance
ontology:concept/ontology-creation-gate
ontology:concept/ontology-validate
ontology:concept/ontology-rule-attr-testable
ontology:pattern/testable-signal-to-test-derivation
ontology:pattern/ontology-modular-reference
ontology:entity/ontology-deep-integration
ontology:domain/ontology-deep-integration-overview
ontology:domain/skill-research
ontology:domain/skill-to-tickets
ontology:domain/skill-testing-strategy
ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms
ontology:domain/ai-efficiency
```

## 拆分映射

- 闭环逐阶段审查 -> ontology:concept/pdca-ontology-ready
- mattpocock增量差距复审 -> ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms
- 链路与工作模式本体核化判定 -> ontology:entity/ontology-deep-integration
- 自循环与持续演进建模 -> ontology:concept/self-optimization-loop
- 测试支撑与scaffold验证 -> ontology:pattern/testable-signal-to-test-derivation
- 报告登记与收敛验证 -> ontology:concept/pdca-evidence

## 风险与对策

- 风险：历史任务disposition含非本体关键词导致“全任务知识闭环”统计失真。对策：本审查以新门禁后任务为主分母，历史任务单独标注
- 风险：mattpocock最新提交滞后于本地快照。对策：以访问时main分支计，注明版本号与日期
- 风险：research本体化判定过度严苛导致“一词一节点”。对策：复用 `ontology-modular-reference` 独立四准强制约

## 开放问题

- 是否将 wizard（HTIL人工向导）与 teach（连续教学）引入为正式skill？当前本地未覆盖，需在差距矩阵中P2决策
