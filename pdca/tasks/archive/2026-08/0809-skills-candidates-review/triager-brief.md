# T0242 Triage Brief — mattpocock/skills 新候选系统化审查

## 来源
T0233 conclusion："mattpocock/skills 可证明空间经 T0230-T0233 四轮已系统
收割，后续新候选需重新审查其技能更新。"用户要求对 mattpocock/skills
README 中尚未覆盖的 4 个候选做系统化评估。

## P0 关键发现（候选实际状态）

审查前先核实本地现状，发现**候选大多已存在**：

| 候选 | 本地现状 | 差距判断 |
|------|---------|---------|
| diagnosing-bugs | 仓库 skills/diagnosing-bugs 完整存在（Phase1-5+） | 已覆盖，需审查与 mattpocock 版差距 |
| code-review 双轴 | ~/.config/opencode/skills/code-review-checklist 存在 | 已有清单式，mattpocock 是双轴并行子代理 |
| CI 基础设施 | 仓库无 .github/ | 缺失，但 T0241 用 doctor 兜底 |
| handoff/wayfinder | 仓库 skills/handoff、handoff-work、wayfinder 存在 | 已覆盖（wayfinder 甚至更结构化） |

**结论修正**：评估对象从"引入缺失技能"变为"审查已有技能 vs mattpocock 版的
差距 + 可证明性"。

## 评估方法（复用 T0230 方法论）
对每个候选：现状证据 → 差距 → 可证明收益假设 → 落地成本 → 门禁兼容 → 建议
（落地/不落地/增强）

## 后续
P2 Grill（评估标准 + 范围）→ P3 → Check（conclusion 含各候选判定）
