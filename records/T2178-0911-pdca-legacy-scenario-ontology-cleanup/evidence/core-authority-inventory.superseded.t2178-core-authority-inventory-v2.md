# T2178 核心权威入口全集与旧词分类

扫描时间：2026-09-11（Do 阶段，变更前快照）。

## 文件集合

本清单不是“预计修改文件”清单，而是以下确定集合的全集扫描：

1. 全局入口：`AGENTS.md`。
2. 活跃流程节点：`ontology/process/*.md` 中首个 `pdca.asset/v1` frontmatter 声明 `status: active` 的全部文件。
3. 活跃概念节点：`ontology/concept/*.md` 中首个 `pdca.asset/v1` frontmatter 声明 `status: active` 的全部文件。
4. 活跃 PDCA domain/skill 节点：`ontology/domain/pdca/*.md` 中首个 `pdca.asset/v1` frontmatter 声明 `status: active` 的全部文件。
5. 阶段实体：`ontology/entity/phase-plan.md`、`ontology/entity/phase-do.md`、`ontology/entity/phase-check.md`、`ontology/entity/phase-act.md`。

集合由以下只读扫描枚举并以 Git 工作树当前内容为准：

```bash
rg -l '^status: active$' ontology/process ontology/concept ontology/domain/pdca
```

旧词扫描覆盖 `scenario_type`/`scenario type`、六值 `development|bugfix|research|documentation|design|review`、结构化 `scenarios:`、`A/B/C`、`6 路由`/`六场景`，以及与“路由、路径、分类、职责、门禁、分流”共现的中英文场景表述。

## 控制语义（必须删除或改写）

| 文件 | 命中 | 控制作用 | 处置 |
|---|---|---|---|
| `AGENTS.md` | `meta.scenario_type` | Do 执行路由 | 改为 `meta.ontology_role` + `meta.execution_contract` |
| `ontology/concept/pdca-phase.md` | `do(6 路由...)` | 阶段行为摘要 | 改为三个专业职责与四字段契约 |
| `ontology/entity/phase-do.md` | `A 核心场景`、`development/bugfix` | Do 准入条件 | 改为职责与契约准入 |
| `ontology/process/flow-plan.md` | `pdca-scenario-boundary-rule` | Plan 分诊关系 | 删除关系和旧来源引用 |
| `ontology/process/flow-act.md` | 六场景枚举 | Act 知识处置分支 | 改为全任务统一规则，工具动作由契约选择 |
| `ontology/concept/pdca-scenario-boundary-rule.md` | 场景边界、A 路径、development/research 裁决 | 任务分类和执行路径 | 删除节点，不设 alias/redirect |
| `ontology/concept/scenario-research-first-gate.md` | 六场景准入和 Act 分流 | 门禁控制 | 删除节点，不设 alias/redirect |
| `ontology/concept/tickets-leaf-exemption.md` | `非research` 叶票豁免 | parent/children 驱动门禁 | 删除节点；与 task 依赖仅调度的不变量冲突 |
| `ontology/concept/research-first-gate.md` | `scenario==research`、`非research` | 调研前置门禁 | 改为 `required_actions`/`work_product` 判定 |
| `ontology/concept/research-first-compliance.md` | 六场景逐类 verdict | 门禁符合性分类 | 改为契约条件符合性 |
| `ontology/concept/research-web-mandatory-gate.md` | `flow-do路径C` | A/B/C 路径依赖 | 改为契约选择工具/报告质量约束 |
| `ontology/domain/pdca/skill-triage-work.md` | 六值映射、`scenario-boundary-check`、`--scenario-type`、A 路径 | 分诊、创建和路径控制 | 输出三职责与四字段契约 |
| `ontology/domain/pdca/skill-triage.md` | research 分类/强制分支 | 分诊与 Grill 路由 | 改由契约动作和输入完整度判定 |
| `ontology/domain/pdca/skill-ask-matt.md` | 六类型用户映射 | 用户路由 | 统一路由到 triage，再输出职责与契约 |
| `ontology/concept/ask-matt.md` | 六类型用户映射 | 用户路由概念 | 统一路由到 triage，再输出职责与契约 |
| `ontology/domain/pdca/skill-context-orchestration.md` | `scenarios: [...]` | 上下文适用性分类 | 改为三职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-ai-execution-and-invocation-contracts.md` | 六值 `scenarios`、route contract、development/bugfix 路径 | 执行路径控制 | 改为职责、契约和工具调用边 |
| `ontology/domain/pdca/ai-efficiency-ai-friendliness-review-methodology.md` | 六值 `scenarios`、场景到路径 contract | 评测路由事实源 | 改为职责/契约一致性评测 |
| `ontology/domain/pdca/ai-efficiency-mattpocock-skills-enhancement-mechanisms.md` | 六值 `scenarios` | 上下文适用性分类 | 改为三职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-uplift-assessment-before-adoption.md` | 六值 `scenarios` | 上下文适用性分类 | 改为三职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-unified-entrypoint-discipline.md` | 六值 `scenarios` | 上下文适用性分类 | 改为三职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-lever-audit-limits.md` | `scenarios: [documentation, review]` | 上下文适用性分类 | 改为三职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-knowledge-assets-and-ai-workflow.md` | `scenarios`、按场景检索 | 上下文检索分类 | 改为职责/契约指纹 |
| `ontology/domain/pdca/workflow-code-review-dual-axis.md` | `scenarios` | 上下文适用性分类 | 改为职责/契约；保留 code-review 工具语义 |
| `ontology/domain/pdca/skill-context-retrieval.md` | `scenarios: [default]` | 上下文适用性分类 | 改为职责/契约检索 |
| `ontology/domain/pdca/skill-project-goal.md` | `scenarios: [default]` | 上下文适用性分类 | 改为职责 + 四字段契约 |
| `ontology/domain/pdca/workflow-skill-invocation-convention.md` | `scenarios: [default]` | 上下文适用性分类 | 改为职责 + 四字段契约 |
| `ontology/domain/pdca/ai-efficiency-writing-for-agents-levers.md` | `scenarios: [plan, do, act]` | 错置的阶段/场景分类 | 改为职责 + 四字段契约；保留 `phases` |
| `ontology/domain/pdca/ai-efficiency-skills-candidate-review.md` | `scenarios: [do, act]` | 错置的阶段/场景分类 | 改为职责 + 四字段契约；保留 `phases` |
| `ontology/domain/pdca/ai-efficiency-contract-scope-limiting.md` | `scenarios: [plan, check]` | 错置的阶段/场景分类 | 改为职责 + 四字段契约；保留 `phases` |
| `ontology/domain/pdca/ai-efficiency-frontier-batch-grilling.md` | `scenarios: [plan, check]` | 错置的阶段/场景分类 | 改为职责 + 四字段契约；保留 `phases` |
| `ontology/domain/pdca/ai-efficiency-contract-test-pattern.md` | `scenarios`、development/bugfix 范围 | 场景分类和门禁适用范围 | 改为契约是否声明可执行代码/测试接缝 |
| `ontology/decision/t2148-bugfix-specialization.md` | bugfix 特化、A 路径 | validator 发现的活跃旧控制决策 | 删除节点，不设 alias/redirect |
| `ontology/pitfall/research-plan-ontology-prompt-gap.md` | research 分类与旧边界关系 | validator 发现的活跃场景门禁描述 | 保留早期本体计划知识，改为契约触发 |
| `ontology/decision/t2153-opt-backlog.md` | 指向旧 bugfix 特化决策 | validator 发现的活跃决策链 | 删除关系，明确旧分类闸已被职责契约取代 |

## 工具名称（允许保留）

- `ontology:domain/skill-research`、`skill-web-research`、`research-report.md`：调研工具与其产物名；只能由 `execution_contract.required_actions`/`work_product` 选择。
- `ontology:domain/skill-code-review`、`workflow-code-review-dual-axis`、`review.md`、`--kind review`：审查工具、方法和证据类型；不承担任务分类或阶段转换。
- `ontology:domain/skill-codebase-design`、`skill-design-it-twice`、`design.md`：设计工具与产物名；不承担 Do 路由。
- `skill-tdd`、`skill-diagnosing-bugs`：执行动作工具；是否调用由 `required_actions` 决定。

## 证据类型（允许保留）

- `ontology/domain/pdca/skill-register-evidence.md` 中 `documentation` 支持型 kind 与 `review` evidence subtype 示例。
- `ontology/concept/pdca-evidence.md` 中 `review` 受识别证据子类型。
- `ontology/process/flow-check.md` 中 `arch-report`/review 报告登记描述。

## 普通描述（允许保留）

- `bug`/`bug report` 表示现有行为损坏，`enhancement` 表示请求性质；二者可用于沟通和事实核验，但不映射为 ontology_role 或执行路径。
- “研究/调研”“设计”“审查”“文档”作为自然语言工作动作、产物内容或专业方法描述时保留；必须由四字段契约确定是否执行。
- `design`、`review` 出现在接口设计、代码审查、标签、文件名或 skill id 中时属于普通描述或工具标识。

## 历史事实（允许保留）

- 旧任务曾被标为 research/development、旧报告曾按场景评估、旧实现曾存在 A/B/C 或六路由的叙述，仅在明确标注“历史”且不再提供当前规则、映射或门禁时可保留。
- `records/`、`pdca/journal/`、归档任务中的旧词是不可变历史，本任务不扫描修改；活跃核心节点若引用历史事实，必须同时明确当前权威模型已由 ontology_role + execution_contract 取代。

## 删除理由

- `pdca-scenario-boundary-rule` 与 `scenario-research-first-gate` 的唯一权威意义是旧六场景分类、路径和门禁，迁移后无独立语义，故删除而非保留兼容节点。
- `tickets-leaf-exemption` 用 parent/children 和 research 分类控制 Plan→Do，与 `pdca-task` 中“parent/dependencies 仅用于拆分和调度，不赋予生命周期控制”直接冲突，且属于后续 runtime projection 的旧实现描述，故从活跃本体删除。
- `t2148-bugfix-specialization` 把 bugfix 建模为 development 特化并绑定 A 路径，其当前语义全部依赖已退役分类，故删除；历史来源仍留在不可变 record。
