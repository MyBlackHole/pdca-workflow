---
schema: pdca.asset/v1
id: ontology:concept/pdca-phase
type: concept
layer: Knowledge
summary: PDCA 阶段元概念（经典四阶段 plan/do/check/act；archive 为工作流运维扩展）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-phase/1.0.0
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-phase

PDCA（Plan-Do-Check-Act，又称 Deming Cycle / Shewhart Cycle）的**阶段**元概念。

## 经典四阶段（PDCA 方法论本身）
- **plan（计划）**、**do（执行）**、**check（检查）**、**act（处理/标准化）** 四阶段（ASQ 称 four-step model；Wikipedia 列出此四阶段）。
- 这四个是 PDCA 方法论的**全部**阶段。**archive 不是 PDCA 方法论阶段**。

## archive 的定位（运维扩展，非方法论阶段）
- `phase-archive` 是**本工作流（pdca-workflow）**在单任务生命周期末尾加入的**运维扩展**节点，用于把已完成任务移出活跃区、保留不可变记录。
- 它**不计入** PDCA 方法论阶段集；其 `specializes: pdca-phase` 仅表示"它借用了阶段这一元概念的位置"，正文见 `ontology:entity/phase-archive`。

## PDCA 是环，不是线（见 pdca-continuous-improvement）
- 经典 PDCA 是持续改进**循环**：act 之后应回到 plan 开启新一轮（"a circle has no end… repeated again and again"，ASQ）。
- 本工作流把单任务生命周期建模为**有终点的流水线**（act→archive）；方法论层面的循环由 `ontology:concept/pdca-continuous-improvement` 承载。

## 术语注记：PDCA 与 PDSA
- Deming 本人更偏好 **PDSA**（Plan-Do-**Study**-Act），因 Study 强调深度学习与理论提炼；PDCA 的 Check（检查）是日方参与者简化后的通俗变体（Wikipedia、6Sigma）。
- 两者等价表达同一改进循环；**本工作流沿用 PDCA 命名**。

## 决策背景（PDCA 全流程生命周期要点，原 docs/pdca-workflow-full.md / pdca-workflow-detail.md）

操作级子步骤（P0-P7 → Z1-Z4 → Ch1-Ch6 → Ac0-Ac8）与各阶段脚本/产物/门禁以 `ontology/process/flow-*.md` 与 `ontology/process/flow-*.md` 为权威；本节点锚定单任务生命周期的转换约束：

- **生命周期（产物/门禁视角）**：`plan(P0 triage → P7 终审)` → `do(6 路由 → Z1 登记证据 → Z2 收敛映射 → Z4 推进)` → `check(Ch1 回顾 → Ch6 推进)` → `act(Ac0 读 verdict → Ac8 归档)` → `archive`（terminal）。
- **Plan→Do 门禁**：P6 为唯一签审门禁，须 `final_confirmation.response=confirmed`；`transition-phase plan→do` 强制校验。
- **Do 六条路由**（由 `meta.scenario_type` 决定）：development（测试优先/TDD）、bugfix（根因修复/TDD 回归）、research（调研报告）、documentation（文档双轴审查）、design（方案+评审+基线）、review（双轴审查+报告）。
- **Do→Check 门禁**：须 PRD + 有效 `evidence/manifest.jsonl`（digest+size+AC 映射）；Z2 收敛映射须 `validate-convergence valid:true`，且**映射本身不能作为验收证据**。
- **Check→Act 门禁**：须 `conclusion.md` + `meta.verdict`（outcome 经 `check_confirmation` 确认为 confirmed/rejected/partial 三者之一）；三分支一律进入 Act，仅处置不同。
- **Act 前置/门禁**：`Ac6 journal` 前置依赖 `meta.disposition`（projected/not_reusable/task_only）；`act→archive` 须 `disposition` 已写且 `active=false`，archive 时跑本体自检（ontology-validate + islands=0）。
- **P6 前的执行器边界**：P6 终审前禁止 `agent.spawn` 调度，能力不可用时由主 session 顺序执行。

