# grilling source 一致性修复 + Ac1 批量问法验证 — 规格文档

## 问题陈述

- **现状**: T0230 将 grilling 改为 frontier 批量问法并落地于 flow-plan/flow-check，但 `flows/flow-act/SKILL.md:47` 与 `flows/flow-check/SKILL.md:61` 的 Q&A 记录仍用 `source: "grill"`，与 `skills/grilling/SKILL.md` 规则 6 规定的 `source: "grilling"` 不一致（术语漂移）。`source` 字段虽非 schema 枚举，但跨文件不一致会误导后续会话与日志解析。
- **目标**: 修复该一致性漂移，并验证 flow-act Ac1 Grill（知识沉淀质量追问）在批量问法下的效率收益（轮数 + 上下文 token 双指标）。
- **差距**: ① source 术语跨文件漂移；② flow-act Ac1 的三条追问是否实际以"同一轮批量问"呈现、收益可量化，尚无验证。

## 解决方案

1. 将 `flows/flow-act/SKILL.md` 与 `flows/flow-check/SKILL.md` 的 Q&A 记录统一为 `source: "grilling"`，与 grilling 技能规则 6 对齐。
2. 在 `tests/test_grilling_efficiency.py` 新增契约测试：断言 flow-act/flow-check/flow-plan 引用 grilling 的文案与 source 术语一致（防漂移回归）。
3. 新增 Ac1 效率验证：以轮数模型断言 flow-act Ac1 的 3 条追问（适用范围/可复用知识/流程改进）可同轮批量问；以 token 双指标统计批量问法相比一次一问答询的上下文节省。

## Seam 分析

### 测试接缝
- 测试目标：`flows/flow-act/SKILL.md`、`flows/flow-check/SKILL.md` 与 `skills/grilling/SKILL.md` 的契约一致性；批量问法轮数/token 推导。
- 现有测试先例：`tests/test_grilling_efficiency.py`（T0230 已建，含轮数模型与文档契约测试）。
- Mock/Stub：纯逻辑 + 文件断言，无外部依赖。

### 验收可测性
- 每个 AC 有明确 pass/fail 信号（见验收标准）。
- 边界：flow-act Ac1 恰有 3 条独立追问（无依赖），应同轮批量问 → 轮数 1 vs 一次一问 3。

## 用户故事

1. 作为 PDCA 维护者，我想要 flow-act/flow-check 的 Q&A source 与 grilling 技能术语一致，以便日志可统一解析、避免误导。
2. 作为 PDCA 用户，我想要 Act 阶段的知识沉淀追问也采用批量问法，以便减少交互往返。
3. 作为 PDCA 维护者，我想要轮数/token 双指标验证 Ac1 批量收益，以便证明并守护效率。

## 实现决策

- 修改 `flows/flow-act/SKILL.md`：Ac1 的 Q&A `source: "grill"` → `"grilling"`。
- 修改 `flows/flow-check/SKILL.md`：Q&A `source: "grill"` → `"grilling"`。
- 扩展 `tests/test_grilling_efficiency.py`：新增 source 一致性契约测试 + Ac1 轮数/token 验证。
- 技术澄清：
  - `clarification.schema.json` 的 `source` 为自由字符串（不校验枚举），此修复是术语治理，非 schema 变更。
  - token 指标用 UTF-8 bytes 作为零模型依赖代理（沿用 `knowledge/ai-efficiency/ai-friendliness-review-methodology.md` 的内容成本约定，不引入真实 tokenizer，因候选相同）。

## 测试决策

- 被测模块：flow-act/flow-check 文案契约、batch_rounds 轮数模型对 Ac1 3 追问的应用。
- 现有先例：`tests/test_grilling_efficiency.py`。
- 好的测试定义：仅测外部契约行为（文件包含正确的 source 术语），不测实现细节。

## 验收标准

- [ ] AC-1: `flows/flow-act/SKILL.md` Ac1 的 Q&A 记录使用 `source: "grilling"`。
- [ ] AC-2: `flows/flow-check/SKILL.md` 的 Q&A 记录使用 `source: "grilling"`。
- [ ] AC-3: `tests/test_grilling_efficiency.py` 新增契约测试，断言 flow-act/flow-check/flow-plan 与 grilling 技能对 `"grilling"` source 术语一致（任一漂移即失败）。
- [ ] AC-4: Ac1 效率验证：batch_rounds 模型对 flow-act Ac1 的 3 条独立追问断言轮数 == 1（同轮批量）而一次一问为 3；token(bytes) 双指标统计批量 vs 一次一问的上下文节省，断言压缩 > 1。
- [ ] AC-5: 既有测试套件全部通过（无回归），`python3 scripts/pdca-doctor.py --json` 健康。
- [ ] AC-6: 门禁不受影响：`source` 术语修改不改变 `clarification.schema.json` 校验行为（仅 `required: ["source","at"]`），验证方式为 schema 校验与 transition 门禁仍通过。

## 范围外

- 不推广批量问法到 flow-do/to-tickets（审查结论：二者无用户决策性 Grill，硬推广违背 YAGNI 与 mattpocock 架构哲学）。
- 不引入真实 tokenizer 依赖（bytes 代理已足够，避免 tokenizer 改变决策的额外复杂度）。
- 不改动 grilling 技能的 frontier 机制本体（T0230 已定稿）。

## 备注

- 审查来源：mattpocock/skills 全仓库（grilling/grill-me/grill-with-docs/triage/wayfinder/to-tickets/domain-modeling），结论为 grilling 是"有用户决策才复用"的组合原语，flow-act Ac1 属适用场景，flow-do/to-tickets 不适用。
- 完整审查记录见 `research-report.md`（本任务 Plan 阶段产物）。
