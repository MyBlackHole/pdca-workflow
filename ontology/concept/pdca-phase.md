---
schema: pdca.asset/v1
id: ontology:concept/pdca-phase
type: concept
layer: Knowledge
summary: PDCA 阶段元概念（经典四阶段 plan/do/check/act；archive 为工作流运维扩展）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-phase/1.0.3
relations:
  specializes:
  - ontology:concept/entity
  testable_signal: "引用存活：test $(grep -rl 'ontology:concept/pdca-phase' ontology/ tests/ scripts/ | wc -l) -ge 16"
---
# pdca-phase

PDCA（Plan-Do-Check-Act）的**阶段**元概念。部分资料使用 Deming Cycle / Shewhart Cycle 作为常见别名；本体不把这些称呼当作无保留的历史归因。

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
- Deming 明确采用并强调 **PDSA**（Plan-Do-**Study**-Act）；其 Study 与 PDCA 的 Check 不应在历史或方法语义上无条件等同。
- **本工作流沿用 PDCA 命名**，并把 PDSA 视为相关但有区别的改进循环表述。

## 决策背景（PDCA 全流程生命周期要点，原 docs/pdca-workflow-full.md / pdca-workflow-detail.md）

操作级子步骤（P0-P7 → Z1-Z4 → Ch1-Ch6 → Ac0-Ac8）与各阶段脚本/产物/门禁以 `ontology/process/flow-*.md` 与 `ontology/process/flow-*.md` 为权威；本节点锚定单任务生命周期的转换约束：

- **生命周期（产物/门禁视角）**：`plan(P0 triage → P7 终审)` → `do(专业职责 + execution_contract → Z1 登记证据 → Z2 收敛映射 → Z4 推进)` → `check(Ch1 回顾 → Ch6 推进)` → `act(Ac0 读 verdict → Ac8 归档)` → `archive`（terminal）。
- **Plan→Do 门禁**：P6 为唯一签审门禁，须 `final_confirmation.response=confirmed`；`transition-phase plan→do` 强制校验。
- **Do 核心路由**（由 `meta.ontology_role` 决定）：本体建模、本体投射、本体符合性验证；具体行为由 `meta.execution_contract` 声明。
- **Do→Check 门禁**：须 PRD + 有效 `evidence/manifest.jsonl`（digest+size+AC 映射）；Z2 收敛映射须 `validate-convergence valid:true`，且**映射本身不能作为验收证据**。
- **Check→Act 门禁**：须 `conclusion.md` + `meta.verdict`（outcome 经 `check_confirmation` 确认为 confirmed/rejected/partial 三者之一）；三分支一律进入 Act，仅处置不同。
- **Act 前置/门禁**：`Ac6 journal` 前置依赖 `meta.disposition`（projected/not_reusable/task_only）；`act→archive` 须 `disposition` 已写且 `active=false`，archive 时跑本体自检（ontology-validate + islands=0）。
- **P6 与执行器边界**：当前任务 P6 终审前禁止 `agent.spawn` 调度；确认后，协调 Agent 为当前 PDCA 任务一次性启动一对一的全新子 Agent/子智能体并立即进入 `suspended_waiting_agent`。子 Agent 自主执行；协调 Agent 恢复后只读当前任务持久化产物并执行 `ontology_conformance_verification`，再决定是否满足进入 Check 的条件。能力不可用时 fail-closed 并保持当前任务未执行。`suspended_waiting_agent` 和确认所用 `awaiting_confirmation` 都是执行状态，不是新增 phase。
