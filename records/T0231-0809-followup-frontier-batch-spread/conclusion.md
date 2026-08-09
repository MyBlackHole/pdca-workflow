---
schema: pdca.asset/v1
id: T0231-0809-followup-frontier-batch-spread
phase: check
source_ids:
  - flow-act-source
  - flow-check-source
  - flow-plan-source-v2
  - grilling-source-contract-test
  - ac1-verification
  - full-test-result
  - doctor-check
  - clarification-schema
  - prd
  - research-report
---

## 上下文

T0231 是 T0230 的跟进任务。T0230 已将 grilling 改为 frontier 批量问法并落地于 flow-plan/flow-check，但审查发现两处 source 术语漂移（`flows/flow-act/SKILL.md`、`flows/flow-check/SKILL.md` 用 `"grill"`，与 grilling 技能规则 6 的 `"grilling"` 不一致）。本任务收窄为：修复 source 术语一致性 + 验证 flow-act Ac1 批量问法收益（轮数/bytes 双指标），不推广 flow-do/to-tickets（审查结论：二者无用户决策性 Grill）。

## 假设与结果

| # | 假设 | 结果 |
|---|------|------|
| H1 | flow-act/flow-check 存在 source 术语漂移（`"grill"` vs `"grilling"`） | **成立**。修复前两处均为 `source: "grill"`；顺带发现 flow-plan 用 `source=grilling` 等号语法，一并统一为冒号+引号 |
| H2 | flow-act Ac1 的 3 条独立追问可同轮批量问 | **成立**。batch_rounds(3, K)=1，一次一问为 3，轮数压缩 **3.0x** |
| H3 | 批量问法上下文成本更低（bytes 代理） | **成立**。bytes 压缩 **1.30x**（194 vs 252） |
| H4 | source 术语修改不影响门禁 | **成立**。`clarification.schema.json` 仅 `required: ["source","at"]`，validate-convergence valid=true，全量 102 passed 无回归 |

## 分析

**source 一致性修复**：`"grill"` 与 `"grilling"` 虽同为自由字符串（非 schema 枚举），但跨文件术语漂移会误导后续会话与日志解析。已统一为 grilling 技能规则 6 规定的 `source: "grilling"`，并新增 `SourceConsistencyContractTest` 5 项断言守护，任一文件回归旧术语即失败。

**Ac1 批量问法验证**：flow-act Ac1 的三条追问（适用范围/可复用知识/流程改进）相互独立、无依赖，属于"当前可答的决策 frontier"，应同轮批量问。轮数模型与 bytes 双指标验证：轮数 1 vs 3（3.0x），payload 194 vs 252 bytes（1.30x）。flow-act 引用 grilling 技能后，该批量行为自动成立。

**mattpocock 架构对齐**：全仓库审查确认 grilling 是"有用户决策才复用"的组合原语（被 grill-me/grill-with-docs/triage/wayfinder 复用），flow-do/to-tickets 无用户决策性 Grill，不推广符合 YAGNI 与来源架构哲学。

## 失败原因（仅 rejected/partial）

无。verdict 为 confirmed，无失败项。

## 适用边界

- source 术语一致性契约测试守护 flow-act/flow-check/flow-plan 与 grilling 技能对齐；新增 flow 若引入 grilling 引用需同步遵守。
- bytes 代理是零模型依赖的上下文成本近似，非真实 token 计数；在候选决策不因 tokenizer 改变的前提下适用。
- 批量问法适用于决策间独立或仅需按依赖分批的场景；强依赖链仍需串行（T0230 已覆盖）。

## 下一轮建议

- 未来新增交互型技能/flow 时，遵循 `source: "grilling"` 术语与 grilling 技能规则 6，避免再次漂移。
- 如确需真实 token 指标，由独立 runner 实测（沿用 R0138 结论），本任务不引入 tokenizer 依赖。
