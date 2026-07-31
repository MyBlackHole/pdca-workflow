# T0122 审查报告：辅助技能和元数据的 AI 友好度

## 审查范围

| 文件 | 行数 | 职责 |
|------|------|------|
| skills/triage/SKILL.md | 54 | 任务分诊 |
| skills/domain-modeling/SKILL.md | 83 | 领域建模 |
| skills/wayfinder/SKILL.md | 37 | 大型需求拆解 |
| pdca/CONTEXT.md | 27 | 共享术语表 |
| SKILLS-INDEX.md | 44 | 技能索引 |
| docs/adr/ADR-0001.md | 27 | 架构决策记录 |
| templates/ 全部 | ~70 | 文档模板 |
| README.md | 161 | 项目文档 |

## 逐项评分

### 1. 人机分工清晰度 — 总分：3.3/5

| 文件 | 评分 | 分析 |
|------|------|------|
| triage | 4 | 分类逻辑由 AI 自主执行，grill 才需用户参与，分工清晰 |
| domain-modeling | 4 | AI 负责即时落地 CONTEXT.md + ADR，用户确认定义即可 |
| wayfinder | 3 | 地图和决策票由 AI 绘制，但"大小是否适合单 session"的判断标准主观 |
| CONTEXT.md | 4 | 明确由 domain-modeling 维护，分工清楚 |
| SKILLS-INDEX.md | 3 | 声明为自动生成但无维护脚本引用 |
| ADR-0001.md | 3 | 定义了「什么决策写 ADR」但实践中 16 个任务零 ADR，门槛可能过高 |
| templates/ | 3 | 模板结构清晰，但部分模板（template.json 仅 5 行）过于精简 |
| README.md | 3 | 与 AGENTS.md 功能重叠，AI 可能混淆哪个是实际入口 |

### 4. 工具对齐 — 总分：3.6/5

| 文件 | 评分 | 分析 |
|------|------|------|
| triage | 4 | 搜索 task.json 需 Glob+grep 组合；grill 委托需 skill 加载 |
| domain-modeling | 4 | 编辑 CONTEXT.md（edit）和写 ADR（write）对齐良好 |
| wayfinder | 3 | 创建目录+文件链较长，需 glob/bash/write 组合 |
| CONTEXT.md | 4 | 直接 edit，简清明细 |
| SKILLS-INDEX.md | 3 | 声明"自动生成"但无对应脚本 |
| templates/ | 4 | 引用路径明确，模板格式清晰 |

### 引用链完整性 — 总分：3.5/5

| 文件 | 评分 | 分析 |
|------|------|------|
| AGENTS.md→flows/ | 5 | 引用路径完整 |
| flows/→skills/ | 4 | 多数引用完整，但部分使用 `disable-model-invocation` 而非路径加载 |
| README→SKILLS-INDEX | 5 | 链接正确 |
| SKILLS-INDEX→skills | 3 | 部分技能名为空（code-review/commit-format 等 description 为空或不全） |
| flow-plan→domain-modeling | 3 | 带 `disable-model-invocation: true` 的加载语义不明确 |

## 不友好之处定位与严重程度

| # | 位置 | 问题 | 影响 | 严重度 |
|---|------|------|------|--------|
| A01 | triage:6, domain-modeling:6, wayfinder:6, handoff:4 | `disable-model-invocation: true` 在 4 个文件中出现，非标准 frontmatter | 部分 AI 工具可能忽略此标记，导致自动加载不应加载的技能 | **高** |
| A02 | SKILLS-INDEX.md:6-43 | 部分技能描述为空或格式不一致（英文/中文混杂） | AI 难以判断何时加载哪些技能 | 中 |
| A03 | README.md vs AGENTS.md | 二者功能重叠，AI 可能不清楚哪个是入口权威来源 | AI 首次进入时路径困惑 | 中 |
| A04 | docs/adr/ | 16 个任务零 ADR，ADR 创建门槛对 AI 来说过高 | 跨任务决策丢失 | 中 |
| A05 | SKILLS-INDEX.md | 声明自动生成但无对应维护脚本引用 | AI 无法自行刷新索引 | 低 |
| A06 | templates/task-artifact/template.json | 仅 5 行，几乎无实际内容 | 模板未发挥作用 | 低 |

## 改进建议

### 高优先级
1. **A01**：将 `disable-model-invocation: true` 替换为行业通用的 `x-model-invocation: disabled` 或 `load: manual` 等明确标记，并确保 AI 工具识别

### 中优先级
2. **A02**：统一 SKILLS-INDEX.md 中所有技能描述的语言为中/英，补全空描述
3. **A03**：明确区分 AGENTS.md（AI 入口路由）和 README.md（人类文档）的职责，减少重叠
4. **A04**：降低 ADR 创建门槛，在 flow-plan 中增加"是否产生 ADR"的自动检查点

### 低优先级
5. **A05**：提供刷新 SKILLS-INDEX 的脚本或命令
6. **A06**：充实 template.json 或考虑废弃
