# T0409 元本体正文补全清单（AC-1）

仅补充 `# 标题` 之下正文，frontmatter 的 `id/type/relations` 未改动，故 `ontology-validate` 与 `ontology_reason` 推理无回归。

## 阶段节点（entity/）
- `ontology/entity/phase-plan.md`：定义/目的/进入条件/关键活动(triage→Grill→PRD→final_confirmation)/退出/对应 flow-plan
- `ontology/entity/phase-do.md`：定义/目的/进入条件(含 ontology-ready)/关键活动(路由 A–F→TDD→ontology_graph 孤岛自检→审查→evidence→convergence-map)/退出/对应 flow-do
- `ontology/entity/phase-check.md`：定义/进入条件(evidence+convergence-map 齐备)/关键活动(回顾→Grill→验证收敛→conclusion→verdict)/退出/对应 flow-check
- `ontology/entity/phase-act.md`：定义/进入条件/关键活动(沉淀→disposition→架构改进→handoff→journal→提交→归档)/退出/对应 flow-act
- `ontology/entity/phase-archive.md`：定义/进入条件/关键活动(advance-phase→提交→git mv)

## 概念节点（concept/）
- `pdca-gate.md`：门禁元概念 + 理由 + 由 `ontology_reason.admission_conditions` 驱动
- `pdca-gate-do.md`：do 准入门禁 + 准入条件来源(`admission do` 实测 `["ontology-ready"]`) + 理由
- `pdca-ontology-ready.md`：含义(ontology_fragment 合法或 exempt) + 理由
- `pdca-verdict.md`：confirmed/rejected/partial 含义 + 不从 Check 退回理由
- `pdca-evidence.md`：含义/受识别类型(test-result,convergence-map,review)/convergence-map 特殊性
- `pdca-acceptance-criterion.md`：AC 含义(须有 evidence 支撑)/理由
- `pdca-task.md`：任务载体含义/关键不变量(final_confirmation 不可代签)
