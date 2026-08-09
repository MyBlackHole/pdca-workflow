---
schema: pdca.asset/v1
id: T0230-0809-ai-efficiency-proof
phase: check
source_ids:
  - grilling-skill
  - flow-plan-ref
  - grilling-efficiency-test
  - research-report
  - full-test-result
  - clarifications-log
  - rounds-demo-script
  - grilling-test-result
---

## 上下文

本任务借鉴 mattpocock/skills 的 grilling 方法，审查 PDCA 工作流自身的 AI 提效空间，并落地有可证明效率收益的修改。核心借鉴点为 **frontier 批量问法**：每轮同时提出当前可答的全部决策问题（各附推荐答案），替代原"一次只问一个"的逐个问法。任务范围限定为 `skills/grilling/SKILL.md`、`flows/flow-plan/SKILL.md`、`flows/flow-check/SKILL.md` 与新增测试，不改 triage/wayfinding、不动 CONTEXT 术语、不新增技能。

## 假设与结果

| # | 假设 | 结果 |
|---|------|------|
| H1 | 批量问法能减少真实交互轮数 | **成立**。真实会话 11 条 clarifications：批量问法 8 轮 vs 一次一问 11 轮，压缩比 1.375x |
| H2 | 轮数压缩可通过确定性测试证明 | **成立**。`tests/test_grilling_efficiency.py` 6 个轮数模型测试 + 4 个文档契约测试 + 1 个 demo 脚本回归测试全部通过 |
| H3 | 同轮共用 round 号与现有门禁兼容 | **成立**。`append-confirmation.py` 只校验 `source`/`response`，`transition-phase.py` 不解析 round 字段，`clarification.schema.json` 仅 `required: ["source","at"]` |
| H4 | 修改不引入回归 | **成立**。全量 `pytest tests/` = 94 passed + 13 subtests；`pdca-doctor.py --json` valid=true；`validate-convergence.py` valid=true |

## 分析

**门禁兼容性（Q3 验证）**：批量问法不改变 clarifications 的 schema 合约——`round` 字段无 schema 约束，append-confirmation 与 transition-phase 均不解析它。同轮多条记录共用同一 round 号不影响最终确认（`final_confirmation`/`check_confirmation` 各自独立判定），因此批量问法不触发任何门禁误判。

**效率证明（Q1 补充）**：除轮数模型测试外，新增 `scripts/grilling-rounds-demo.py` 统计真实会话轮数。本任务 Plan+Check 阶段共 11 条 clarifications 记录，其中 round 1–6 为 Plan 阶段 6 轮（旧方式），round 7 一次覆盖 4 个问题（Q1–Q4，新方式）。演示脚本输出 batch_rounds=8 vs one_at_a_time=11，压缩 1.375x，已登记为证据 rounds-demo-script（脚本）与 grilling-test-result（测试输出），并有对应单测防回归。

**证据收敛（Q3 补充）**：convergence map 已更新为含全部 8 个证据 id 的最终版，manifest 中 convergence-map 唯一活跃，`validate-convergence.py` 返回 valid=true，AC-1 至 AC-6 均有非 map 证据覆盖。

## 失败原因（仅 rejected/partial）

本次 verdict 为 **partial**，非失败，而是 Q1/Q3 触发补充验证：
- Q1「需补充计时」：已通过 demo 脚本 + 单测 + 证据登记闭环，不构成缺陷。
- Q3「需额外验证」：已通过门禁兼容性确认 + 收敛校验闭环，不构成缺陷。
无失败项。

## 适用边界

- 批量问法适用于**决策间相互独立**或仅需按依赖分批的场景；强依赖链决策仍需串行轮次（模型测试 `test_dependency_chain_batches_by_dependency` 已覆盖）。
- round 号仅作轮次标识，不作为语义顺序的强契约。
- 本修改只影响 grilling 的提问组织方式，不改变 Plan/Check 的门禁判定逻辑。

## 下一轮建议

- 若未来引入新技能，遵循 skill 命名规范并同步 SKILLS-INDEX.md（本次修改已演示该流程）。
- 可考虑将 frontier 批量问法推广到 flow-do/flow-check 之外的更多交互点，但需先经 Improvement Candidate → Improvement Task 流程，本次不越权。
