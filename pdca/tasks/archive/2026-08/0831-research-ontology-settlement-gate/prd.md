# 建立 research 场景的本体沉淀门禁，避免知识仅留 records

## 背景

T0464 `调研生产级别工具开发应具备的要求与条件` 按 `research` 场景完成，产出 `research-report.md`（26347 bytes）与 `checklist.md` 并经 `register-evidence` 与 `validate-convergence` 校验通过，结论 `confirmed` 后归档。复盘发现：

- 任务 `meta.ontology_fragment=ontology` 指向根目录，`ontology-ready` 门禁对 `research` 无领域片段强约束（`ontology:concept/pdca-ontology-ready`）
- `skill-research` 的完成合约为“报告+证据”，未要求在 Act 阶段对“是否沉淀为本体”做显式决策
- 结果：高复用知识（12维分级、L1-L4成熟度、B1-B4清单）仅沉淀于 `records/T0464-.../evidence`，未进入 `ontology/` 图谱，AI 检索（`context-retrieval`）无法经本体召回

用户在 Check→Act 复盘中提出追问，要求“同时创建新任务处理这个问题，避免下次再次发生”。本任务即为该改进任务的 Plan。

已追补：`ontology:domain/tool-production-readiness` 已创建并经 `ontology-validate` + `ontology_graph`（350 nodes, 759 edges, 0 islands）校验，作为正例。

## 目标

为 `research` 场景建立**显式的本体沉淀门禁**，使得未来同类高复用研究不再“仅以 records 沉淀”而漏本体化，且漏本体化可被机器或 checklist 拦截。

## 范围

- **在内**：`skill-research` 与 `ontology/process/flow-act.md` 的本体沉淀指引补强；act 阶段的显式决策（ontology vs records-only）与处置记录；可回归的校验方式（脚本或 checklist + 用例）
- **不在**：对 `development`/`design` 等已有本体强约束的场景做额外改动；对 `ontology-validate` 本身的规则大改（仅衔接）

## 关联本体节点

- `ontology:concept/pdca-ontology-ready`
- `ontology:concept/pdca-task`
- `ontology:domain/skill-research`
- `ontology:domain/tool-production-readiness`（正例）
- `ontology/process/flow-act.md`
- `ontology/process/flow-do.md`

## 验收标准

- [ ] AC-1：在 `skill-research` 或 `flow-act` 中新增 research 场景的本体沉淀决策步骤与判定标准（何时必须本体化、何时可仅 records），且与 `ontology:concept/pdca-ontology-ready` 衔接
- [ ] AC-2：提供 checklist 或自动化校验（脚本/CI 片段），使得 research 任务在 act 阶段必须做出 `ontology vs records-only` 的显式决策并记录于 `meta.disposition` 或结论中，漏决策可被拦截
- [ ] AC-3：经回归验证：构造一个模拟 research 任务漏本体化的负例可被新门禁拦截；且 T0464 补建的 `ontology:domain/tool-production-readiness` 可作为正例通过校验
- [ ] AC-4：`ontology-validate` 与 `ontology_graph` 通过，无新增孤岛；相关文档（`SKILLS-INDEX.md` 若需）已同步

## 非目标

- 不将所有 research 任务一刀切强制本体化；需给出“高复用/方法论/可检索” vs “一次性/低复用” 的分流标准
- 不引入新的外部依赖或重型流程，仅在既有 Plan→Do→Check→Act 门禁上做最小补强

## 风险

- 判定标准过于宽松则门禁形同虚设，过于严格则增加 research 成本——需在 PRD 中明确分流阈值并经 Grill 收敛
- 自动化校验若仅做字符串匹配易误报，需结合 `task.json#meta.disposition` 与 `records/<id>/conclusion.md` 的结构化字段

## 开放问题（待 Grill）

- Q1：本体化的分流阈值如何定（例如“是否含可复用清单/模型/模式”）？
- Q2：门禁载体偏好：`skill-research` 内新增步骤 vs `flow-act` 统一 checklist vs 独立校验脚本 `scripts/check-research-ontology-settlement.py`？
- Q3：records-only 的显式理由是否需纳入 `conclusion.md` 的固定章节？
