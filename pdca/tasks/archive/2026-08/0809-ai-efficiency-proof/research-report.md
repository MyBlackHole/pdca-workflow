# mattpocock/skills 实现优点审核报告

> 审核范围：仓库 36 个技能 + AGENTS.md + CONTEXT.md + 组织机制。结论用于确定本 PDCA 工作流可借鉴、可证明的提效点。

## 一、核心优点清单（按提效杠杆强度排序）

### 1. grilling 的 "frontier" 批量问法 ⭐ 最核心
- mattpocock grilling 每轮计算 **frontier**（所有当前可答的问题），一轮内问完整个 frontier，每个问题编号 + 附推荐答案，用户一次性回复后再重算。
- 对比 PDCA 现状：本仓库 `skills/grilling/SKILL.md:11` 强制 "一次只问一个，从不批量"。
- **效率差异**：N 个独立决策，批量法约 ceil(N/每轮容量) 轮（实测 2-3 轮），一次一问需要 N 轮。
- **可证明性**：交互轮数是可数、可断言、可回归验证的硬指标。

### 2. user-invoked 技能极简委托（薄壳模式）
- grill-me 7 行 = "Run a /grilling session"；grill-with-docs 7 行；handoff 16 行；implement 15 行。
- user-invoked 技能只做路由，逻辑全部委托给 model-invoked 技能。零上下文加载成本。
- 对比 PDCA：ask-matt 31 行、grilling 52 行偏重，仍有精简空间。

### 3. 模型/用户双通道调用分离
- `disable-model-invocation: true` = user-invoked（只有人能触发，零上下文成本）；无标记 = model-invoked（description 是常驻上下文指针，AI 可自动触发）。
- 描述写得好的 model-invoked 技能自动被 AI 发现调用 → 减少用户手动指定。

### 4. completion criteria 双维（clarity + demand）
- 每个步骤的完成准则必须清晰可判（clarity）且要求充分（demand，如 "every rule applied" 强制遍历）。
- diagnosing-bugs 用 checkbox 形式固化完成准则，防"过早完成"。
- 对比 PDCA：writing-great-skills 只有"完成标准"一句，无双维框架。

### 5. leading words（预训练词锚定）
- 用模型预训练中已有的词（red / tight / tracer bullet）锚定行为，比自定义词省 token 且更可靠。
- 重复 token 而非重复句子 → 累积分布定义。

### 6. 否定改肯定（negation → positive）
- "不要 X" 会把被禁行为拖进上下文，改为"做 Y"。
- PDCA writing-great-skills 已收录此条（第 3 条），保持一致。

### 7. CONTEXT.md 纯词汇表
- CONTEXT.md 只存词汇 + 关系 + flagged ambiguities，绝不含实现细节。
- ADR 严格三条件：hard-to-reverse + surprising + real trade-off，缺一不写。

### 8. context pointer / progressive disclosure
- 文档按信息层级组织：in-file step → in-file reference → disclosed reference（独立文件，按指针加载）。
- AGENTS.md 23 行纯路由（对比 PDCA 47 行含门禁细则）。

## 二、与 PDCA 现状对比

| 维度 | mattpocock | PDCA 现状 | 差距 |
|------|-----------|-----------|------|
| 追问节奏 | frontier 批量问（2-3 轮收尾） | 一次只问一个（N 轮） | **核心差距，直接决定交互轮数** |
| 技能体积 | grill-me 7 行委托 | ask-matt 31 行、grilling 52 行 | 中等，可量化 |
| 完成准则 | clarity + demand 双维 + checkbox | 一句"完成标准" | 中等 |
| leading words | 明确杠杆 | 未收录 | 低 |
| wait-what | 独立技能（7 行） | 缺失 | 低 |
| CONTEXT.md | 纯词汇 30 行 | domain-modeling-work 已对齐 | 已对齐 |
| ADR 三条件 | 严格 | 本仓库已要求"不可逆+非显然+有权衡" | 已对齐 |

## 三、可借鉴且可证明的修改候选

| 候选 | 修改 | 证明方式 |
|------|------|---------|
| **A. grilling 批量问法（本次核心）** | grilling 改为 frontier 批量问；flow-plan/flow-check 引用同步 | 轮数对比测试：N 决策 R 轮覆盖 vs 旧 N 轮 |
| B. 技能薄壳化 | ask-matt/grilling 精简 | 行数/bytes 对比 |
| C. writing-great-skills 扩展 | 纳入 completion criteria 双维、leading words | 内容审计 |
| D. 新增 wait-what | 新技能 | 用法演示 |

## 四、结论

本仓库与 mattpocock 最大、最可证明的差距是 **grilling 的追问节奏**（frontier 批量 vs 一次一问）。该修改直接减少 Plan 对齐的用户交互轮数，且轮数可断言、可回归验证，满足"对 AI 开发提升效率必须有证明"的硬要求。
