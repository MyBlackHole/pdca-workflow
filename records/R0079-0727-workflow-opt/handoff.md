# Handoff — PDCA 工作流全链路优化

## 当前状态
PDCA 工作流已完成核心改进：双轴 code-review、disable-model-invocation 标记、to-spec 标准化模板、残留 Rust 文件清理。所有验收标准通过，任务已记录 verdict "confirmed"。

## 未完成事项
1. **triage 技能** — 作为 Plan 前置步骤，用于 issue/PR 分类（参考 mattpocock/skills 的 triage 状态机模式）
2. **wayfinder 技能** — 用于多 session 大型规划的 map+ticket 模式
3. **prototype 技能** — 验证原型的两分支模式（LOGIC.md / UI.md）
4. **diagnosing-bugs 技能** — 结构化 BUG 诊断循环

## 已知约束
- `disable-model-invocation` 是约定性标记，opencode 不强制执行，依赖 AI 自觉遵守
- 项目仍无真实业务任务进行端到端流程验证

## 推荐的下一步
1. 创建新任务：实现 triage 技能（最有价值的 Plan 前置改进）
2. 创建新任务：实现 wayfinder 技能（多 session 支持，配合 Act→Plan 交接）
3. 创建真实业务任务，端到端跑一遍完整 PDCA 流程

## 关键上下文文件列表
- `AGENTS.md` — 项目入口，含技能调用约定
- `skills/code-review/SKILL.md` — 双轴审查（标准轴+规范轴）
- `skills/grill/SKILL.md` — AI 追问门禁（含 disable-model-invocation）
- `skills/domain-modeling/SKILL.md` — 领域建模（含 disable-model-invocation）
- `flows/flow-plan/SKILL.md` — Plan 阶段（含 to-spec 模板引用）
- `flows/flow-do/SKILL.md` — Do 阶段（含双轴代码审查）
- `flows/flow-check/SKILL.md` — Check 阶段
- `flows/flow-act/SKILL.md` — Act 阶段
- `templates/to-spec/SPEC.md` — 标准化规格模板
- `knowledge/workflow/code-review-dual-axis.md` — 可复用知识
- `knowledge/workflow/skill-invocation-convention.md` — 可复用知识
- `records/R0079-0727-workflow-opt/` — 完整实验记录