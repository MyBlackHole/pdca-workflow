# mattpocock/skills 审查报告 — 批量问法推广评估（T0231）

## 审查范围

完整审查 https://github.com/mattpocock/skills（本地克隆于 `/tmp/opencode/mattpocock-skills/`），聚焦与 T0231 相关的交互设计机制。

## 仓库架构

约 30+ 技能，分 `engineering`（代码）/ `productivity`（通用）/ `misc` 三类。分两层：

- **用户级技能**（`disable-model-invocation: true`，仅用户显式触发）：grill-me、grill-with-docs、triage、to-spec、to-tickets、implement、wayfinder、ask-matt 等。
- **模型级技能**（Agent 自动调用）：grilling、domain-modeling、tdd、code-review、research、prototype 等。

## 核心交互原语：grilling

`skills/productivity/grilling/SKILL.md` 是唯一的采访引擎：

1. 把讨论映射为 **design tree**：每个决策分支为挂在其下的子决策。
2. 按 **rounds** 工作：**frontier** = 前置已解决的、现在就可问的决策集。
3. 一轮问完整个 frontier：每个问题编号、附推荐答案，等用户一次性回复。
4. 用户答案重塑决策树，重算 frontier 进下一轮；依赖另一问题的回答的问题属于更晚的轮次。
5. **事实自己查**（子代理/工具），绝不问用户能自己查的东西。
6. frontier 为空即结束；用户确认共享理解前不行动。

## 复用边界（关键洞察）

grilling 被 5+ 个用户级技能复用：grill-me、grill-with-docs、triage、wayfinder、improve-codebase-architecture。复用条件是**有用户决策交互**：

| 技能 | 是否用 grilling | 依据 |
|------|----------------|------|
| grill-me | 是 | 直接包装 `/grilling` |
| grill-with-docs | 是 | `/grilling` + `/domain-modeling` 组合 |
| triage | 条件用 | `verify 后 grill **if needed**`（`SKILL.md:76`） |
| wayfinder | 条件用 | 仅 HITL ticket 用 grilling（`SKILL.md:79`），AFK ticket 不用 |
| improve-codebase-architecture | 是 | 调查后 grill 所选候选 |
| **to-tickets** | **否** | 用自己轻量"Quiz the user"三问（粒度/阻塞边/合并拆分），非 grilling |

## 对 PDCA 的映射评估

| PDCA 交互点 | 是否有用户决策性 Grill | 是否适用批量问法 |
|------------|----------------------|----------------|
| flow-plan P2（grilling） | 是 | 已落地（T0230） |
| flow-check Ch2（grilling） | 是 | 已落地（T0230） |
| **flow-act Ac1（Grill 知识沉淀）** | **是**（适用范围/可复用知识/流程改进三问） | **适用，已引用 grilling** |
| flow-do（Seam/回归确认） | 否（事实核查） | 不适用 |
| to-tickets（拆解） | 否（subagent 不做用户对齐，`to-tickets/SKILL.md:56`） | 不适用 |

## 审查结论

1. **flow-act Ac1 已引用 grilling**，批量问法在 Act 阶段已生效。真实差距仅是 `source` 术语漂移（`"grill"` vs `"grilling"`）。
2. **flow-do / to-tickets 无用户决策性 Grill**，强行推广批量问法违背 YAGNI 与 mattpocock 的架构哲学（grilling 只在有用户决策时复用）。
3. mattpocock 的 to-tickets 第 4 步 "Quiz the user" 使用固定三问（粒度/阻塞边/合并拆分），是轻量确认，不是 grilling 的 frontier 机制——PDCA to-tickets 无需为此改动。

## 决策

- T0231 收窄为：修复 flow-act/flow-check 的 source 一致性 + 验证 Ac1 批量问法收益（轮数/token 双轨）。
- flow-do、to-tickets 不推广，维持现状。
