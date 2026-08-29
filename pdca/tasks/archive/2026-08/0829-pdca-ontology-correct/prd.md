# T0410 PRD：校正 PDCA 元本体与经典方法论的偏差

## 背景
T0409 让执行指引层实时消费 PDCA 元本体；用户随即用网络资料（ASQ / Deming Institute / Wikipedia / Lean Enterprise Institute / iSixSigma）核验，发现我们的元本体与经典 PDCA 方法论有 2 处不符：

1. **archive 被误列为 PDCA 阶段**：经典 PDCA 只有 Plan/Do/Check/Act 四阶段（ASQ 称 four-step model；Wikipedia 列出四阶段）。`pdca-phase.md` 写"plan/do/check/act/archive"，把本仓库任务生命周期的运维扩展 archive 当成了方法论阶段。
2. **丢失循环语义**：经典 PDCA 是环，"a circle has no end… repeated again and again"（ASQ），act 后应回到 plan 形成持续改进环（Wikipedia："implemented in spirals"）。我们的转换图 `plan→do→check→act→archive` 是单向到终点。

附加（非错误，补强正确性）：Deming 本人更偏好 **PDSA**（Plan-Do-Study-Act），Study 强调深度学习；PDCA 的 Check 是日方简化后的通俗变体（Wikipedia、6Sigma）。可加注。

## 设计决策（关键）
- **循环用概念节点表达，不新增 transition 边**。理由：`test_ac2_no_cycle_dangling` 要求 `ontology-validate` 不含 `CYCLE`，单任务生命周期必须能终止（act→archive）。因此把"PDCA 是环"建模为 `pdca-continuous-improvement` 概念（relates_to phase-act / phase-plan），任务转换图保持无环。这是正确的双层模型：方法论是环，任务生命周期是终止流水线。
- 若未来确需把 act→plan 设为合法任务转换，需同时把该边加入 `ontology-validate` 的白名单（超出本任务范围，另行评估）。

## 验收标准
- [ ] AC-1 `pdca-phase.md` 正文明确：经典 PDCA = 四阶段（plan/do/check/act）；archive 是"本工作流的任务运维扩展，非 PDCA 方法论阶段"，并引用 `pdca-continuous-improvement`。
- [ ] AC-2 新增 `ontology/concept/pdca-continuous-improvement.md`：type=concept，specializes=pdca，正文描述 PDCA 循环（act→新 plan）、archive 为单任务终点；`relations` 含 `relates_to: [phase-act, phase-plan]`（不引入 transition 边，validate 仍无 CYCLE）。
- [ ] AC-3 `phase-act.md` 提及"采纳/标准化后开启新循环（见 pdca-continuous-improvement；方法论上 act→plan），本任务生命周期在归档后结束"；`phase-archive.md` 标注为运维扩展而非 PDCA 阶段。
- [ ] AC-4 `pdca-phase.md`（或 `pdca.md`）含 PDSA 注记：Deming 偏好 PDSA（Study），PDCA 的 Check 为通俗变体，本工作流沿用 PDCA 命名。
- [ ] AC-5 测试：`tests/test_ontology_reason.py`（或新建 `tests/test_pdca_ontology_correct.py`）断言 pdca-continuous-improvement 节点存在且其 relations 关联 phase-act/phase-plan；`ontology-validate` 通过且无 CYCLE；`pytest` 全绿。
- [ ] AC-6 `docs/ONTOLOGY_GUIDE.md` 第 10 节补充"PDCA 本体与经典方法论对齐说明"（2 处校正 + PDSA 注）；`verify-document` 自检 ok。

## 范围与边界
- 仅改元本体内容（正文/relations）、指南、测试；不改 `ontology_reason.py` 算法、schema、校验器逻辑、CI 门禁。
- 不新增 `transition-act-plan.md`（避免制造 CYCLE）。
- 不改 `pdca_context.py` 的 PHASES（archive 仍属本工作流阶段）；仅确保 `pdca-continuous-improvement` 概念可被读到（概念节点默认纳入，无需改脚本）。
