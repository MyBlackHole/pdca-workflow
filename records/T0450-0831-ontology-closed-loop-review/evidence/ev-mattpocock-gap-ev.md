# mattpocock/skills v1.2.3 差距审查报告

> 审查日期：2026-08-31
> 审查目标：对照 mattpocock/skills 最新版本（包含 v1.2.3 后的变更），识别本地 PDCA 工作流尚未覆盖的可借鉴内容
> 来源仓库：https://github.com/mattpocock/skills（main 分支，457 commits）

---

## 一、已覆盖内容对照表

以下本地 PDCA 技能已与 mattpocock/skills v1.2.3 对齐，但部分存在版本差距：

| 本地技能文件 | 对应远程技能 | 覆盖状态 | 差距说明 |
|-------------|-------------|---------|---------|
| `skill-grill.md` | `/grill-me` | 已覆盖 | 功能一致 |
| `skill-grilling.md` | `/grilling` | 已覆盖 | 已实现 frontier 批量问法、facts vs decisions 分离、子代理调度 |
| `skill-codebase-design.md` | `/codebase-design` | 已覆盖 | 深模块词汇一致 |
| `skill-domain-modeling.md` | `/domain-modeling` | 已覆盖 | 主动构建共享语言 |
| `skill-diagnosing-bugs.md` | `/diagnosing-bugs` | 已覆盖 | 诊断循环一致 |
| `skill-code-review.md` | `/code-review` | 已覆盖 | 双轴审查（Standards + Spec） |
| `skill-improve-codebase-architecture.md` | `/improve-codebase-architecture` | 已覆盖 | 已实现 YAGNI 热点扫描（近 30 天 git log） |
| `skill-to-spec.md` | `/to-spec` | 已覆盖 | 规格说明转化 |
| `skill-to-tickets.md` | `/to-tickets` | 已覆盖 | 已实现 wide refactor expand-contract 模式 |
| `skill-implement.md` | `/implement` | 已覆盖 | 实现流程一致 |
| `skill-wayfinder.md` + `skill-wayfinding-chart.md` + `skill-wayfinding-work.md` | `/wayfinder` | 已覆盖 | 决策地图机制一致，但缺少 "decision ticket" 术语和 HITL/AFK 分类 |
| `skill-resolving-merge-conflicts.md` | `/resolving-merge-conflicts` | 已覆盖 | 冲突解决一致 |
| `skill-handoff.md` + `skill-handoff-work.md` | `/handoff` | 已覆盖 | 交接文档一致 |
| `skill-research.md` | `/research` | 部分覆盖 | 缺少 subagent 并行 burn-down 机制和 throwaway `research/<name>` 分支 |
| `skill-prototype.md` | `/prototype` | 部分覆盖 | 仍描述终端 app 方式，远程已改为单 HTML 文件 + `prototype/<name>` throwaway branch |
| `skill-tdd.md` | `/tdd` | 部分覆盖 | 仍含"重构是循环一部分"的旧表述，远程已改为 reference-only，缺少 tautological-test 抗模式 |
| `skill-writing-great-skills.md` | `/writing-for-agents` | 部分覆盖 | 已覆盖 4 杠杆核心，但远程已重构为 `SKILL.md`（通用参考）+ `SKILL-MECHANICS.md`（技能机制），新增 Negative Space 失败模式和 cache 概念 |
| `skill-ask-matt.md` | `/ask-matt` | 部分覆盖 | 路由表基本覆盖，但缺少 phase boundaries 决策树、wayfinder 两种常见错误、missing routes |
| CONTEXT.md 共享语言 | CONTEXT.md | 已覆盖 | 共享语言机制一致 |

---

## 二、未覆盖的新内容清单（按优先级分级）

### P0 -- 核心架构级（影响技能体系完整性）

#### 2.1 writing-for-agents 重构（SKILL.md + SKILL-MECHANICS.md 拆分）

- **描述**：v1.2.3 将 `writing-great-skills` 重命名为 `writing-for-agents`，并拆分为两个文件：
  - `SKILL.md`：通用参考，覆盖任何 agent 消费文档（技能、AGENTS.md/CLAUDE.md、指针可达的文档），新增信息层级（步骤/引用/外部引用）、双负载（context load / cognitive load）、完成判据杠杆、拆分规则、leading words、pruning（含 cache 概念）
  - `SKILL-MECHANICS.md`：技能特有的机制参考 -- frontmatter、invocation 选择（model-invoked vs user-invoked 的精确机制）、router skills
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md
  - https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#763）
- **可借鉴价值**：P0 最高
  - 本地 `skill-writing-great-skills.md` 仍使用旧名称和旧结构，缺少 SKILL-MECHANICS.md 的 invocation 机制精确描述
  - 新的信息层级（步骤/引用/外部引用）比本地当前的"信息层级"表格更精细
  - cache 概念（"cache what the agent cannot find by looking"）是全新的 pruning 维度
- **映射建议**：
  - 将 `skill-writing-great-skills.md` 拆分为两个本体节点：`writing-for-agents`（通用写作参考）和 `skill-mechanics`（技能机制）
  - 在 `skill-mechanics` 中精确描述 model-invoked/user-invoked 的 frontmatter 差异
  - 在 `writing-for-agents` 中加入 cache 概念作为 pruning 的新维度

#### 2.2 SKILL-MECHANICS.md 内容（技能编写机制参考）

- **描述**：独立文档，定义技能编写的三种机制：
  - **Invocation**：model-invoked（省略 `disable-model-invocation`，description 面向模型带触发条件）vs user-invoked（设 `disable-model-invocation: true`，description 面向人类）
  - **Splitting by invocation**：当有独立触发词或另一技能需调用时，拆为 model-invoked
  - **Router skills**：user-invoked 技能过多时的路由模式，一个 user-invoked 技能命名其他技能及何时使用
  - 依赖表达方式：显式 `Call the Skill tool with "grilling"` 而非 deep cross-references
- **来源**：https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md
- **可借鉴价值**：P0 最高
  - 本地缺乏对 skill invocation 机制的精确形式化描述
  - router skills 模式对本地 ask-matt 路由设计有直接参考价值
- **映射建议**：新增本体节点 `skill-mechanics`，类型为 principle，覆盖 invocation 选择、router 模式、依赖表达

#### 2.3 .agents/invocation.md 双 harness 调用模型

- **描述**：定义 Claude Code 和 Codex 双 harness 的调用模型：
  - 每个 `SKILL.md` 旁放 `agents/openai.yaml`，含 Codex UI 元数据（`interface.display_name`、`interface.short_description`）
  - user-invoked 技能：Claude Code 设 `disable-model-invocation: true`，Codex 设 `policy.allow_implicit_invocation: false`
  - 依赖通过 `Call the Skill tool with "name"` 显式调用，而非 `/name` 风格的 hint
  - user-invoked 技能不能被其他技能通过 Skill tool 调用（包括通过名称）
- **来源**：https://github.com/mattpocock/skills/blob/main/.agents/invocation.md
- **可借鉴价值**：P1 高
  - 本地尚无双 harness 适配机制
  - 对本地 AGENTS.md/CLAUDE.md 体系和未来多 harness 扩展有架构参考价值
- **映射建议**：新增本体节点 `skill-invocation-contract`，覆盖双 harness 调用约定和 `openai.yaml` 元数据规范

#### 2.4 skills.sh 安装模式与 Claude Code plugin 模式

- **描述**：双安装哲学：
  - **Claude Code plugin**：`claude plugins install mattpocock-skills`，managed read-only bundle，自动更新
  - **skills.sh**：`npx skills@latest add mattpocock/skills`，复制可编辑文件到项目
  - `.claude-plugin/plugin.json` 携带完整插件元数据和 promoted skills 列表
- **来源**：README.md 和 CHANGELOG #536
- **可借鉴价值**：P2 中
  - 本地无 plugin 化安装机制
  - 对本地技能的版本管理和分发有参考价值
- **映射建议**：可映射到构建/分发相关本体节点，非核心知识资产

---

### P1 -- 重要功能增强（显著提升技能能力）

#### 2.5 ask-matt 重塑（phase boundaries、wayfinder 错误、缺失路由）

- **描述**：v1.2.3 对 ask-matt 进行了三项重大增强：
  1. **Phase boundaries 决策树**：定义 5 个选项（continue, /clear, /handoff, subagent, /compact），附带 `PHASE-BOUNDARIES.md` 详细推理。核心变化：/compact 是默认而非第一选择；continue 是第一个应排除的选项（保持主来源而非摘要）
  2. **Wayfinder 两种常见错误**：(a) over-reaching（过于密集，应保留给真正无法单 session 完成的任务）；(b) losing the way at handoff（地图清除后不应直接 /implement，应合并到 /to-spec）
  3. **Missing routes**：/grilling 和 /resolving-merge-conflicts 此前完全缺失，现在加入路由
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#751）
- **可借鉴价值**：P1 高
  - 本地 `skill-ask-matt.md` 路由表较简单，缺少 phase boundaries 的决策树
  - wayfinder 的两种常见错误对本地 wayfinder 技能有直接警示价值
- **映射建议**：
  - 在 `skill-ask-matt.md` 中扩展 phase boundaries 决策树
  - 新增本体节点 `phase-boundary-decision-tree` 或扩展 `skill-advance-phase.md`
  - 在 wayfinder 相关节点中加入"常见错误"章节

#### 2.6 prototype 改造（单 HTML 文件 + throwaway branch）

- **描述**：v1.2.3 重塑 prototype 技能：
  - Logic 分支：生成单个自包含 HTML 文件（plain HTML/CSS/JS，无构建），含标签面板和引导式 walkthrough
  - 不再删除原型：捕获为可运行证据在 `prototype/<name>` throwaway branch 上，在实现问题上留下 context pointer
  - 答案（verdict + question）持久化在 issue 或 ADR/commit 中
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#763）
- **可借鉴价值**：P1 高
  - 本地 `skill-prototype.md` 仍描述终端 app 方式
  - throwaway branch 机制比本地"throwaway 原型回答完即弃"更成熟
- **映射建议**：更新 `skill-prototype.md`，增加 HTML 原型分支和 throwaway branch 捕获机制

#### 2.7 grilling 轮次改革（frontier 批量问法 + facts vs decisions + confirmation gate）

- **描述**：本地已实现 frontier 批量问法，但远程有以下增强：
  - **Facts vs decisions 分离**：facts 是 agent 的职责（查找、探索、子代理调度），decisions 必须由用户回答。防止 grilling agent 自主回答自己的问题
  - **Confirmation gate**：agent 不会在用户确认共享理解达成前执行计划
  - **Sub-agent dispatch for facts**：运行中的探索是不确定的先决条件 -- 只有其下游问题等待，其他 frontier 问题照常询问
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#464, #593）
- **可借鉴价值**：P1 高
  - 本地 `skill-grilling.md` 已有较完整的 frontier 批量机制
  - facts vs decisions 的明确分离和 confirmation gate 是值得补充的增强
- **映射建议**：在 `skill-grilling.md` 中补充 facts vs decisions 分离规则和 confirmation gate

#### 2.8 tdd 改造为 reference-only

- **描述**：v1.2.3 将 TDD 重塑为纯参考型技能：
  - 移除 Workflow 和 per-cycle checklist（红绿循环已被 leading words 锚定）
  - 将垂直切片/示踪弹概念并入抗模式部分和简短的 Rules-of-the-loop
  - 引入 **seam** 作为测试位置的 leading word
  - 移除 refactor 阶段（TDD 现为红->绿；重构属于 review 阶段）
  - 新增 **tautological-test** 抗模式：断言以代码相同方式重算预期值
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#464）
- **可借鉴价值**：P1 高
  - 本地 `skill-tdd.md` 仍含"重构不是循环的一部分"的冗余表述
  - 缺少 tautological-test 抗模式
  - "seam" 作为 leading word 的引入值得借鉴
- **映射建议**：更新 `skill-tdd.md`，移除冗余 workflow 表述，增加 tautological-test 抗模式，强化 seam leading word

#### 2.9 triage 外部 PR 处理

- **描述**：扩展 triage 以处理外部 pull requests：
  - PR 视为带附件的 issue，走相同角色、状态机和流程
  - Discovery 仅暴露外部 PR
  - bug-only 的"reproduce"步骤泛化为"verify the claim"
  - 冗余检查解析已实现请求为 `wontfix`
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#472）
- **可借鉴价值**：P1 高
  - 本地 `skill-triage.md` 暂无 PR 处理
- **映射建议**：更新 `skill-triage.md`，增加 PR 处理逻辑

#### 2.10 researching subagent 并行 burn-down

- **描述**：research tickets 不再等待单独 session，而是：
  - 创建 tickets 后，charting session 对每个 research ticket 触发 `/research` subagent 并行 burn-down
  - 捕获发现到 throwaway `research/<name>` branch
  - Research tickets 是"一个 ticket per session"规则的唯一例外
- **来源**：
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#763）
- **可借鉴价值**：P1 高
  - 本地 `skill-research.md` 缺少 subagent 并行 burn-down 机制
  - 对本地 wayfinder 中 research 节点的处理有直接参考价值
- **映射建议**：更新 `skill-research.md`，增加 subagent 并行 burn-down 机制和 throwaway branch 捕获

---

### P2 -- 概念增强（提升理论深度）

#### 2.11 Negative Space 失败模式

- **描述**：与 Negation（大象 -- 否定式约束将禁止行为拖入上下文）并列的新失败模式：
  - **Negative Space**（虚空）-- 对"你省略了什么"的 steering 视而不见
  - 每个技能拒绝的决策都被委托给 agent 的 priors 而非保持中性
  - 修复：阅读草稿的沉默部分，逐个决定每个省略（填充或留作真实分支）
- **来源**：CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#463）
- **可借鉴价值**：P2 中
  - 本地 `skill-writing-great-skills.md` 已有否定约束的讨论，但缺少 Negative Space 的系统化分析
- **映射建议**：在 `skill-writing-great-skills.md` 的失败模式表中新增 Negative Space 条目

#### 2.12 cache 概念（"cache what the agent cannot find by looking"）

- **描述**：在 pruning 部分新增 cache 概念：
  - **Single source of truth** 延伸到环境 -- `package.json` scripts、config 文件、目录布局、`--help` 输出本身就是权威
  - 引用这些内容的文档是 lookups 的 cache，仅在 lookup 昂贵时才值得加载
  - **Positive target**：cache agent 无法通过查看找到的内容（未写明的惯例、选择背后的原因、config 不肯承认的 gotcha）
  - 将单文件、单命令的 lookups 留给环境
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md （Pruning 节）
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#763）
- **可借鉴价值**：P2 中
  - 本地 `skill-writing-great-skills.md` 有 pruning 原则但缺少 cache 概念
  - 对本地 CONTEXT.md 和 AGENTS.md 的维护策略有直接参考价值
- **映射建议**：在 `skill-writing-great-skills.md` 的 pruning 原则中新增 cache 条目

#### 2.13 Decision ticket 术语与 HITL/AFK 分类

- **描述**：wayfinder 的 ticket 被称为"decision tickets"（决策票），而非普通实现票：
  - 每个 ticket 类型分类为 **HITL**（human in the loop）或 **AFK**（agent alone）
  - HITL ticket 只通过 live exchange 解决 -- grilling agent 如果自己回答了问题，就违反了 HITL
  - Task 类型：必须在决策前完成的手工工作（唯一"做"而非"决定"的类型）
- **来源**：CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#763）
- **可借鉴价值**：P2 中
  - 本地 wayfinder 有类似的分类（Research/Prototype/Grilling/Task），但缺少 HITL/AFK 的形式化标签
- **映射建议**：在 wayfinder 相关本体节点中引入 HITL/AFK 分类标签

#### 2.14 to-questionnaire 技能

- **描述**：将无法独自回答的决策转化为 Markdown 问卷：
  - 采访的是**发送**（发给谁、需要什么回传），而非主题
  - 是 `/grill-me` 的逆运算：grill-me 面试主题，to-questionnaire 面试发送对象
  - 用户-invoked，独立于主流程
- **来源**：
  - https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#593）
- **可借鉴价值**：P2 中
  - 本地无此技能
  - "面试发送而非主题"的思路对本地 to-spec 流程有补充价值
- **映射建议**：新增本体节点 `skill-to-questionnaire`

#### 2.15 wait-what 技能

- **描述**：一句话纠偏 -- 当消息未传达时触发，agent 用 CONTEXT.md 词汇和 ASD-STE100 简化技术英语重新 pitch
  - 极短（3 行），避免冗长纠偏技能本身成为新的冗余
  - 复用 CLAUDE.md 中已有的 leading words
- **来源**：
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#751）
- **可借鉴价值**：P2 中
  - 本地有提及但无专用技能
  - "一句话纠偏"的设计哲学值得借鉴
- **映射建议**：新增本体节点 `skill-wait-what` 或作为 `skill-grilling.md` 的补充

#### 2.16 wizard 技能

- **描述**：生成交互式 bash wizard 引导人类完成仅人类可执行的步骤：
  - Model-invoked，agent 在遇到仅人类可过的墙时自动 reach
  - 模板内置进度显示、确认门、URL 打开、密钥条目等
  - 四种触发分支：基础设施置备、凭证/CI 密钥设置、第三方 dashboard 导航、一次性迁移
- **来源**：
  - CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#680）
- **可借鉴价值**：P3 低
  - 本地无此技能
  - 对本地工作流中需要人工介入的场景有参考价值
- **映射建议**：新增本体节点 `skill-wizard`

#### 2.17 teach 技能

- **描述**：多 session 教学，使用当前目录作为状态化教学 workspace：
  - 课程从 `./assets/` 的可复用组件构建（样式表、quiz widgets、simulators、diagram helpers）
  - 复用是默认：agent 先读 `./assets/`，再构建，提取新的可复用组件
- **来源**：CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#101）
- **可借鉴价值**：P3 低
  - 本地无此技能
  - 对本地知识资产积累有间接参考价值
- **映射建议**：新增本体节点 `skill-teach`

---

### P3 -- 退役技能（已吸收，无需单独实现）

#### 2.18 六个退役技能

远程仓库已退役 6 个技能，全部被更优技能吸收：

| 退役技能 | 吸收者 | 说明 |
|---------|-------|------|
| `ubiquitous-language` | `/domain-modeling` | 构建和维护完整领域模型而非倾倒单次会话词汇表 |
| `design-an-interface` | `/codebase-design` | "设计两次"技术已内置于 `DESIGN-IT-TWICE.md` |
| `qa` | `/triage` + `/to-tickets` | 质量和验收已融入 triage 和 ticket 拆分 |
| `request-refactor-plan` | `/to-spec` + `/improve-codebase-architecture` | 重构规划和 spec 已覆盖 |
| `edit-article` | -- | 仅限个人使用，已删除 |
| `obsidian-vault` | -- | 硬编码个人 Obsidian vault 路径，已删除 |

- **来源**：CHANGELOG: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md （#752）
- **可借鉴价值**：低
  - 确认了这些技能已被吸收，无需单独实现
  - 但 `design-an-interface` 的"设计两次"模式值得确认本地 `skill-design-it-twice.md` 是否完整覆盖

---

## 三、docs page 模式

远程仓库采用 **docs page 模式**：每个 promoted 技能在 `docs/engineering/<skill>.md` 或 `docs/productivity/<skill>.md` 有一个文档页面。

- **结构**：`docs/engineering/` 和 `docs/productivity/` 两个目录
- **作用**：作为技能的独立文档页面，供人类阅读，不直接参与技能执行
- **来源**：https://github.com/mattpocock/skills/tree/main/docs
- **可借鉴价值**：P2 中
  - 本地无此模式，但可通过 AGENTS.md 和 ontology 节点实现类似功能
  - 对本地文档组织有参考价值

---

## 四、总结：优先级行动建议

### 立即行动（P0）

1. **重构 writing-for-agents**：将 `skill-writing-great-skills.md` 拆分为通用写作参考 + 技能机制两个本体节点
2. **新增 skill-mechanics 节点**：形式化 invocation 选择、router 模式、依赖表达
3. **新增 skill-invocation-contract 节点**：双 harness 调用约定

### 近期增强（P1）

4. **更新 ask-matt**：扩展 phase boundaries 决策树，加入 wayfinder 常见错误
5. **更新 prototype**：增加 HTML 原型分支和 throwaway branch 机制
6. **更新 tdd**：改为 reference-only，增加 tautological-test 抗模式
7. **更新 research**：增加 subagent 并行 burn-down 机制
8. **更新 triage**：增加外部 PR 处理

### 概念补充（P2）

9. **补充 Negative Space 失败模式**
10. **补充 cache 概念**
11. **新增 to-questionnaire 和 wait-what 技能**
12. **引入 HITL/AFK 分类到 wayfinder**

### 确认无需实现（P3）

13. **确认 6 个退役技能已被吸收**，无需单独实现

---

*本报告基于 mattpocock/skills v1.2.3（main 分支，457 commits）审查生成。*
