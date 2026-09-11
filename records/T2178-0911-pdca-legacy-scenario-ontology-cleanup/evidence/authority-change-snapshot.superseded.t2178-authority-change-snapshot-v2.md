# T2178 本体与路由变更快照

快照日期：2026-09-11。

## 唯一控制模型

- 专业职责只允许：`ontology_modeling`、`ontology_projection`、`ontology_conformance_verification`。
- `execution_contract` 只使用四个必需字段：`work_product`、`required_actions`、`constraints`、`testable_signal`。
- `research`、`web-research`、`code-review`、`design-it-twice`、TDD、诊断、原型和文档写作仅为 `required_actions` 可选择的工具或动作；产物类型可由 `work_product` 声明。
- `bug`/`enhancement` 只描述请求性质，不映射专业职责、阶段路径或门禁。

## 入口与阶段

- `AGENTS.md`：Do 路由改为 `meta.ontology_role` + `meta.execution_contract`。
- `ontology/process/flow-plan.md`：移除旧边界关系和来源，triage/Grill/拆票统一消费职责与契约。
- `ontology/process/flow-do.md`：确认当前权威正文只按三个职责和四字段契约执行；工具是适配层。
- `ontology/process/flow-act.md`：知识处置不再枚举六类任务，三个职责使用同一规则。
- `ontology/concept/pdca-phase.md`、`ontology/entity/phase-do.md`：移除“6 路由”和 A 路径准入。
- `ontology/concept/runtime-transition-coordinator.md`：transition receipt 绑定职责、契约和 Evidence 快照 digest。

## 分诊、用户路由与上下文

- `skill-triage-work.md`、`skill-triage.md`：分诊输出一个专业职责和四字段契约；删除六值表、边界脚本调用、`--scenario-type` 与 A 路径建议。
- `skill-ask-matt.md`、`concept/ask-matt.md`：所有自然语言请求先进入 triage；请求词只形成职责/契约候选。
- `skill-context-orchestration.md`、`skill-context-retrieval.md`：上下文按职责、契约、阶段和来源链选择，不按请求类别字段筛选。
- `skill-wayfinder.md`、`skill-wayfinding-chart.md`、`skill-wayfinding-work.md`：ticket 声明职责与四字段契约；工具动作写入 `required_actions`，并行只由依赖边与 ready-set 决定。

## 契约化知识资产

以下 active PDCA domain 资产已删除结构化 `scenarios:`，改用 `ontology_roles` 与完整四字段 `execution_contract`：

- `workflow-code-review-dual-axis.md`
- `skill-context-retrieval.md`
- `skill-context-orchestration.md`
- `skill-project-goal.md`
- `workflow-skill-invocation-convention.md`
- `ai-efficiency-writing-for-agents-levers.md`
- `ai-efficiency-uplift-assessment-before-adoption.md`
- `ai-efficiency-unified-entrypoint-discipline.md`
- `ai-efficiency-skills-candidate-review.md`
- `ai-efficiency-mattpocock-skills-enhancement-mechanisms.md`
- `ai-efficiency-lever-audit-limits.md`
- `ai-efficiency-contract-scope-limiting.md`
- `ai-efficiency-ai-execution-and-invocation-contracts.md`
- `ai-efficiency-knowledge-assets-and-ai-workflow.md`
- `ai-efficiency-ai-friendliness-review-methodology.md`
- `ai-efficiency-frontier-batch-grilling.md`
- `ai-efficiency-contract-test-pattern.md`

## 门禁与验收语义

- `research-first-gate.md`、`research-first-compliance.md`、`research-web-mandatory-gate.md`：只在契约要求基于来源调研，或报告本身为 `work_product` 时适用。
- `pdca-acceptance-criterion.md`：逐章映射由来源报告产物触发，不由任务类别触发。
- `skill-write-conclusion.md`、`skill-web-research.md`：附加动作由契约选择工具触发。
- `research-plan-ontology-prompt-gap.md`：保留“Plan 提前声明本体锚点”的知识，改为契约缺口 pitfall。

## 删除节点

- `ontology:concept/pdca-scenario-boundary-rule`
- `ontology:concept/scenario-research-first-gate`
- `ontology:concept/tickets-leaf-exemption`
- `ontology:decision/t2148-bugfix-specialization`

以上节点分别依赖旧六类裁决、六类门禁、parent/children 生命周期豁免或 bugfix/A 路径特化；迁移后无独立当前权威意义，因此直接删除，不建立 alias 或 redirect。`ontology:decision/t2153-opt-backlog` 已移除对删除决策的关系，并明确旧分类闸由职责契约取代。

## 版本与索引

- 所有本任务改写正文的本体节点均将 `dcterms_modified` 更新为 `2026-09-11`，并在当前工作树版本基础上增加 `owl_versionIRI` 修订号。
- `SKILLS-INDEX.md` 由 `python3 scripts/generate-skills-index.py --root .` 重生成；当前包含 50 个技能资产。

