# skills 项目如何提升 AI 能力 — 深度研究报告

> 任务：T0370 | 场景：research | 分析对象：`/home/black/Documents/skills`（mattpocock/skills v1.2.3 "Skills For Real Engineers"）
> 日期：2026-08-23 | 方法：静态全量扫描 + 原文引用（`file:line`）

## 0. 执行摘要

该项目不是"提示词集合"，而是一套**以失效模式为纲的 AI 工程行为约束系统**。它把资深工程师的隐性工作纪律（先对齐再动手、测试先行、深模块设计、反馈回路优先）显式化为 36 个可被 AI 按需加载的指令模块，并用四条机制提升 AI 表现：

1. **对齐前置**：用 grilling 决策树在写码前穷尽用户决策（治"做出来的不是我想要的"）。
2. **共享语言压缩**：CONTEXT.md 术语表让 AI 少写 token、少猜语义（治冗长与歧义）。
3. **反馈回路强制**：TDD/diagnosing-bugs 把"想"变成"测"（治产出不可用代码）。
4. **设计词汇锚定**：codebase-design 的深模块词汇抑制 AI 加速的熵增（治泥球化）。

其编排哲学是"小而可改、可组合"：与 GSD/BMAD/Spec-Kit 这类接管流程的重框架相反，它刻意保持每个技能小、薄、无平台锁定（README.md:9-12）。下文按 PRD 六项验收标准逐条展开。

---

## 1. 全量清单与分类（AC-1）

### 1.1 数量统计

实测 `find skills -name SKILL.md | wc -l` = **36 个技能文件**，分布如下：

| 分类 | 数量 | 定位 | 成员 |
|------|------|------|------|
| engineering | 18 | 日常代码工程（promoted，随插件分发，含 docs 页） | ask-matt, codebase-design, code-review, diagnosing-bugs, domain-modeling, grill-with-docs, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder, wizard |
| productivity | 7 | 通用非代码工作流（promoted） | grilling, grill-me, handoff, teach, to-questionnaire, wait-what, writing-for-agents |
| in-progress | 7 | beta 通道，不分发 docs 页 | claude-handoff, implement-spec, loop-me, setup-ts-deep-modules, writing-beats, writing-fragments, writing-shape |
| misc | 4 | 一次性工具 | git-guardrails-claude-code, migrate-to-shoehorn, scaffold-exercises, setup-pre-commit |
| deprecated | 0 | 仅存 README 说明淘汰规则 | — |

### 1.2 调用关系图（谁调用谁）

```
                    ┌─────────────── 用户手动触发层 ───────────────┐
  on-ramp: triage   主流程: grill-me/grill-with-docs → to-spec → to-tickets → implement   on-ramp: wayfinder
       │                    │                  (handoff ⇄ prototype 支线)          │
       ▼                    ▼                                                     ▼
                    ┌─────────────── 模型自动触发纪律层 ─────────────┐
     grilling ◄──被上述全部调用      domain-modeling（与 grilling 成对）
     tdd ◄──implement               code-review ◄──implement
     research ◄──wayfinder          prototype ◄──wayfinder
                    ┌─────────────── 词汇底层（无流程，纯参考） ────────────┐
                     codebase-design（module/interface/seam/depth…）
                     writing-for-agents（如何写给 agent 读的文档）
```

调用约定（`.agents/invocation.md`）：依赖必须写成 `Call the Skill tool with "grilling"` 的显式工具调用措辞而非 `/name` 提及或跨目录链接，因为命名工具才能获得更高触发率（`.agents/invocation.md`）；需要两个技能就是两次调用（"Call the Skill tool twice, for 'grilling' and 'domain-modeling'"，见 grill-with-docs/SKILL.md:5）。**不变式**：user-invoked 技能永远不能被其他技能调用，只有人能触发（`.agents/invocation.md`）。

### 1.3 触发模型的双轨制

每个技能带两个元数据载体：Claude Code 的 frontmatter（`disable-model-invocation: true` 即仅人工触发）和 Codex 的 `agents/openai.yaml`（`policy.allow_implicit_invocation: false` 同义）。两平台必须同步标记（CHANGELOG v1.2.0 #551）。判断标准："模型能否有用地自主调用它？"——能复用才是抽成技能的理由，而不是抽取的原因（`.agents/invocation.md`）。这使编排型技能（triage/to-spec/implement）只能人来点火，纪律型技能（tdd/grilling/codebase-design）可在任务匹配时被模型自主拉起。

---

## 2. 四大失效模式 → 修复技能映射（AC-2）

README "Why These Skills Exist"（README.md:84）明确定义了四个要修的 AI 失效模式：

### 失效模式 #1：AI 没做我想要的（对齐失败）

- 原文："The most common failure mode in software development is misalignment…There is a communication gap between you and the agent."（README.md:94-96）
- 修复：grilling 追问会话 —— "getting the agent to ask you detailed questions about what you're building"（README.md:96）；入口为 grill-me（无仓库场景）与 grill-with-docs（有仓库场景，附带沉淀文档）（README.md:98-103）。
- 底层机制：grilling 把对话建模为**决策树**，以"轮次 × frontier"推进：frontier = 所有前置条件已定的当前可答问题，每轮整批询问并附推荐答案，答案重塑树形后再算下一轮 frontier（skills/productivity/grilling/SKILL.md:8,24）。退出条件是 frontier 清空、"nothing left silently assumed"（同文件 :28）。
- 提升原理：LLM 的失败多源于**过早填充未声明的假设**。批量问 frontier 迫使隐式假设显式化，且"每问必附推荐答案"把开放题降维成确认题，将用户的认知负担从"构思需求"减到"裁决选项"。

### 失效模式 #2：AI 太啰嗦（语言不对齐）

- 原文："Agents are usually dropped into a project and asked to figure out the jargon as they go. So they use 20 words where 1 will do."（README.md:111-113）
- 修复：共享语言文档 CONTEXT.md —— "a document that helps agents decode the jargon used in the project"（README.md:115），内建于 grill-with-docs（README.md:131）。
- 效果链（README.md:136-140）：命名一致 → 代码库更易导航 → **AI 思考耗 token 更少**。示例："lesson materialization cascade" 一个词替代一整段描述（README.md:122-127）。
- 执行者是 domain-modeling：挑战与词典冲突的用语（:44）、提出规范术语、用具体场景压测边界、与代码交叉验证矛盾（:56）、**当场更新 CONTEXT.md 不攒批**（:60）、ADR 三条件门槛——难逆转+无背景会惊讶+真实权衡（:66-73）。
- 补充修复 wait-what：消息没传达到位时的一句话纠正指令，用 ASD-STE100 简明英语 + CONTEXT.md 词汇重新表述。其 SKILL 全文仅三行——"Concision skills fail by growing"（CHANGELOG v1.2.0 #751）：简洁指令自身膨胀就会失效，所以只留一个精准引导词。

### 失效模式 #3：代码跑不起来（缺反馈回路）

- 原文引 Pragmatic Programmer："Always take small, deliberate steps. The rate of feedback is your speed limit."（README.md:144-146）；"Without feedback on how the code it produces actually runs, the agent will be flying blind."（README.md:148-150）
- 修复 a：tdd 红-绿循环（README.md:152-156）。关键约束是"只在预先约定的 seam 上测试"——写任何测试前先列出受测 seam 并与用户确认，未经确认的 seam 不写测试（skills/engineering/tdd/SKILL.md:22）。反模式三条：实现耦合测试、同义反复断言、水平切片（:24-28）。
- 修复 b：diagnosing-bugs 诊断循环。"Build a feedback loop. **This is the skill.** Everything else is mechanical."——有了对本 bug 变红的一次命令通过信号，二分/假设/插桩都只是消费它；没有它，盯着代码看多少都没用（skills/engineering/diagnosing-bugs/SKILL.md:18-20）。给出 10 种回路构造法（失败测试/curl/CLI 快照对比/无头浏览器/trace 重放/一次性 harness/property fuzz/bisect harness/差分/HITL bash），并要求"把回路当产品打磨"：更快、更锐、更确定（:52-58）。v1.2.3 增加 Redact 先行节防密钥泄漏（CHANGELOG #779）。
- 提升原理：LLM 生成代码的错误率无法靠"更努力地想"降低，只能靠**提高反馈频率与锐度**。seam 预约定则解决的是测试精力分配问题——落在关键路径而非每个边缘。

### 失效模式 #4：我们造了个泥球（熵增速化）

- 原文引 Kent Beck "Invest in the design of the system every day" 与 Ousterhout "The best modules are deep"（README.md:162-166）；"agents can radically speed up coding, they also accelerate software entropy"（README.md:170）。
- 修复：codebase-design 提供**强制词汇表** module/interface/implementation/depth/seam/adapter/leverage/locality，禁用 component/service/API/boundary 等松散替身（skills/engineering/codebase-design/SKILL.md:10-28）；深浅模块对照图（:30-44）；四原则含"删除测试"——想象删掉该模块：复杂度消失则是透传，在 N 个调用点重现则它在挣饭吃（:63）；"一个 adapter 意味着假想的 seam，两个才是真的"（docs/engineering/codebase-design.md）。
- 配套 survey：improve-codebase-architecture 按"近 20 条提交热点"聚焦扫描 deepening 候选——"没人动的代码里的深化机会是永远不会兑现的重构"（CHANGELOG v1.2.0 #533，YAGNI scoping filter）；to-spec 在规格期就 sketch seams 且"越少越好，理想是一条"（to-spec/SKILL.md:15）。
- 提升原理：AI 写码速度放大一切既有倾向，包括混乱。唯一对策是把"每天投资设计"变成 AI 可执行的检查动作，而**统一词汇本身即是约束**——当审查输出只能说"shallow interface / wrong seam location"时，模糊的"重构一下"就没有生存空间。

---

## 3. 核心技能机制拆解（AC-3）

以下 14 个技能按"输入 → 处理 → 输出 → 对 AI 的提升点"拆解（超过 PRD 要求的 8 个）：

### 3.1 grilling（interview 原语，28 行）

- 输入：一个计划/设计/想法。
- 处理：决策树建模 → 每轮计算 frontier → 整批提问附推荐 → 答案重塑树 → 重算。规则：事实自查不问人（派子代理查文件系统/工具），只问用户才能做的权衡决策（productivity/grilling/SKILL.md:26）。
- 输出：共享理解 + 用户确认；禁止在确认前行动（:28）。
- 提升点：把"猜需求"替换为"收敛决策树"；推荐答案机制让用户只需 yes/no+修正；事实/决策二分防止 AI 浪费用户注意力。

### 3.2 grill-me / grill-with-docs（组合器，7 行 / 3 行）

- 输入：同 grilling。处理：一行指令——调用 Skill tool with "grilling"；后者再加调 "domain-modeling"（engineering/grill-with-docs/SKILL.md:5）。
- 输出：前者无状态，后者落盘 CONTEXT.md + ADR。
- 提升点：示范了**薄组合器模式**——原语保持单一，场景差异用几行的包装表达。维护面极小，语义零漂移。

### 3.3 domain-modeling（主动建模纪律，74 行）

- 输入：会话中出现的领域用语。
- 处理：词典挑战 → 场景压测 → 代码交叉验证 → inline 更新 CONTEXT.md → ADR 三条件裁决（engineering/domain-modeling/SKILL.md:44-73）。CONTEXT.md 明确"只是词汇表，不是 spec/草稿本"（:60 附近约束）。
- 输出：持续精化的 CONTEXT.md + 稀少的 ADR。
- 提升点：术语歧义是 LLM 幻觉的高发源；"当场落盘"利用会话热上下文，避免事后补写失真。

### 3.4 codebase-design（设计词汇参考，114 行）

- 输入：模块设计/重构议题。
- 处理：无流程——纯参考（docs/engineering/codebase-design.md 开篇声明 "It is a reference, not a process"）；提供词汇表+深浅对照+四原则；两个按需加载的支撑文件：
  - **DEEPENING.md**：把候选模块的依赖分四类——in-process（进程内）/ local-substitutable(本地可替换)/ remote-but-owned（远程但自有）/ true-external（真外部）——**类别决定深化后的模块如何跨 seam 测试**。
  - **DESIGN-IT-TWICE.md**：并行子代理为同一模块产出 3+ 个根本不同的接口，再按 depth/locality/seam 位置对比（Ousterhout 技法）。
- 输出：设计对话中的统一措辞。
- 提升点：给模型一个**不可协商的术语集**，使设计批评变得可操作。已知坑（issue #449）：无停止规则的参考型技能会被 agent 当流程跑烧掉 100k token——workaround 是挂在 driver 技能之下（同 docs 页）。这条教训对 PDCA 直接适用：**参考型资产必须有明确的挂载点**。
- 边界坚守记录：issue #95 提议把深模块形式化为 fractal-tree 文件结构、#458 质疑 module 与文件系统绑定，作者两次拒绝："deep modules are about the design of the interface…no matter what the file system looks like"；glossary 刻意保持小——"a term nobody uses consistently is worse than no term"（#180/#303 提议 connascence/progressive disclosure 均未合并）。

### 3.5 tdd（测试纪律，38 行）

- 输入：要实现的特性/修复 + 预约定 seam。
- 处理：红→绿循环；垂直切片（一测一实现一重复），每片是响应上一循环教训的 tracer bullet；重构不属于循环、属于 review 阶段。
- 输出：存活于重构之外的行为测试。
- 提升点：三条反模式直指 LLM 测试坏味道高发区——mock 内部协作者/断言自算期望值/先写全部测试再写全部实现。期望值必须来自独立真理源（known-good 字面量、手算样例、spec）。

### 3.6 diagnosing-bugs（诊断循环，138 行，最长）

- 输入：难缠 bug / 性能回归。
- 处理：六阶段门禁式推进，每阶段有显式完成判据：
  - **Phase 1 构造反馈回路**（"This is the skill"，:18-20）：10 种回路构造法按序尝试——失败测试/curl 脚本/CLI 快照对比/无头浏览器/trace 重放/一次性 harness/property fuzz/bisect harness/差分回路/HITL bash 模板。完成判据是回路同时满足四条件：**Red-capable**（断言用户的精确症状，能对本 bug 变红而非"不报错"）、**Deterministic**（每次运行同一判定；flaky bug 则钉住高复现率）、**Fast**（秒级非分钟级）、**Agent-runnable**（可无人值守运行）。"如果你发现自己在命令存在之前读代码建理论，停下——直接跳到假设正是本技能要防止的失败。No red-capable command, no Phase 2."（:60-66）
  - **Phase 2 复现+最小化**：确认红的是用户描述的那个失败而非邻近失败（"Wrong bug = wrong fix"）；然后逐项削减输入/调用者/配置/数据，每削一项重跑一次回路，直到"每个剩余元素都是承重的"（:70-88）。最小化同时缩小 Phase 3 假设空间并成为 Phase 5 的干净回归测试。
  - **Phase 3 假设**：先产出 **3–5 个排序假设再测任何一个**——单一假设生成会锚定在第一个看似合理的想法上。每个假设必须可证伪："若 X 是因，则改 Y 会让 bug 消失/改 Z 会让它更糟"；说不出预测的假设是 vibe，弃或磨。排序列表先给用户过目（领域知识常能瞬间重排），AFK 则不阻塞（:90-104）。
  - **Phase 4 插桩**：每个探针映射到 Phase 3 的具体预测，一次只改一个变量。工具优先级：调试器/REPL > 区分假设的定向日志 > "全打日志再 grep"（明令禁止）。**每条调试日志打唯一前缀标签**如 `[DEBUG-a4f2]`，清理时单次 grep 即净。性能分支例外：先建基线测量（计时/profiler/查询计划）再二分，"Measure first, fix second"（:106-120）。
  - **Phase 5 修复+回归测试**：回归测试写在修复之前，但**只在存在 correct seam 时**——correct seam 是能在调用点真实复现 bug 模式的接缝；接缝太浅（单调用者测试装不下多调用者链路）会给出虚假信心。**若无正确 seam，这本身就是发现**：是代码库架构阻止了 bug 被锁死，移交架构审查（:122-134）。五步：最小化 repro 变失败测试→看它红→修复→看它绿→对未最小化原始场景重跑 Phase 1 回路。
  - **Phase 6 清理**：原始 repro 不再复现、回归测试通过（或 seam 缺失已记录）、全部 `[DEBUG-...]` 已 grep 移除、一次性原型删除、**正确假设写进 commit/PR message 让下一个调试者学习**（:136-138）。
- 密钥治理：所有展示的命令/输出/工件先 `<REDACTED>`，回路的凭据走环境变量使其停留在环境中而非展示物里（v1.2.3 #779）。
- 输出：根因 + 回归测试 + 干净工作区 + 可传承的结论记录。
- 提升点：把 debugging 从"直觉艺术"转为"回路消费"；"Be aggressive. Be creative. Refuse to give up."针对 LLM 遇阻即放弃的倾向给出显式韧性指令；多假设并行防锚定、证伪格式防空谈、seam 缺失即架构发现的反哺设计尤为精彩。

### 3.6b improve-codebase-architecture（架构体检，71 行）

- 输入：一个想保养的代码库。
- 处理三步：①**YAGNI 定界探索**——用户点名方向则直接用，否则回溯 `git log --oneline` 找热点路径，让"最近常改动的地方"优先获得扫描权重（v1.2.0 #533）；派子代理有机游走，寻找四类摩擦：理解一个概念要在多个小模块间弹跳、接口几乎和实现一样复杂的 shallow module、纯函数被抽出来测但真 bug 藏在调用方式里（无 locality）、紧耦合模块跨 seam 泄漏。对疑似 shallow 的对象施加删除测试。②**HTML 视觉报告**——自包含文件写 OS 临时目录不进仓库，Tailwind CDN + Mermaid CDN，每个候选渲染卡片（Files/Problem/Solution/Benefits/before-after 手绘图/推荐强度徽章 Strong·Worth exploring·Speculative），末尾给 Top recommendation；ADR 冲突的候选只在摩擦足够大时以警告框形式呈现（"contradicts ADR-0007, but worth reopening because…"）。③**Grilling 循环**——用户选定候选后进决策树：约束、依赖、深化后模块形状、seam 后面放什么、哪些测试存活；inline 副作用交 domain-modeling（新术语进 CONTEXT.md、load-bearing 的拒绝理由 offer ADR 防"下次审查重新提议同一件事"）。
- 输出：候选清单 + 用户选定方向的深化设计起点（明确"Do NOT propose interfaces yet"）。
- 提升点：survey-not-rescue 定位（README.md:206 "It is a survey, not a rescue"）；YAGNI 热点定界直接回应"没人动的代码里的深化机会是永远不会兑现的重构"。

### 3.7 code-review（双轴审查，87 行）

- 输入：HEAD 与固定点的 diff + spec 来源 + 标准 来源。
- 处理：钉住固定点并预验 ref 有效（:23）→ **两条并行子代理**分别审 Standards（仓库标准+Fowler 坏味基线 12 条，repo 标准覆盖基线，坏味永远是 judgement call）与 Spec（缺失/范围蔓延/疑似错实现，逐条引 spec 原文）→ 聚合时**禁止合并或重排**两轴发现（:76）。
- 输出：并排双报告 + 每轴各自的最差问题。
- 提升点：并行子代理**互不污染上下文**；双轴分离因为"合规但做错事"和"做对事但不合规范"都会发生，合并评分会让一轴掩盖另一轴（Why two axes，:80-88）。

### 3.8 research（调研委派，12 行）

- 输入：一个问题。处理：后台子代理执行；只查 primary sources（官方文档/源码/spec/第一方 API），"Follow every claim back to the source that owns it"（engineering/research/SKILL.md:10）；产出单 Markdown 并逐条注引（:11）。
- 提升点：主会话不被阅读阻塞（:6）；一手来源规则直接压制 LLM 引用二手转述时的失真累积。

### 3.9 prototype（一次性原型回答设计问题，26 行）

- 输入："这个状态模型/逻辑感觉对吗""UI 该长什么样"类问题。
- 处理：逻辑问题产单个自包含 HTML（无构建无服务器，非开发者可双击打开）；UI 问题产一条路由可切换的多个根本不同变体。**弃用≠删除**：完成后折叠有效决策进真代码，原型提交到 `prototype/<name>` 游离分支作为 primary source，并在实现 issue 留上下文指针（engineering/prototype/SKILL.md:26）。
- 提升点：把"纸上争论"换成"可运行证据"；分支留证让探索历史可回溯而不污染主线。

### 3.10 wayfinder（超大会话决策地图，128 行）

- 输入：大于单 session 容量的迷雾需求。
- 处理：定 destination（先 grill）→ 广度优先 grill 出 frontier → 建 map issue + 子 decision ticket（native blocking 边）→ fog of war 记录"还说不尖锐的问题"不强行切票（:86-91）→ 每 session 只解一张票：claim→resolve→记录 resolution comment→close→地图 Decisions-so-far 追加指针→雾毕业成新票。research 票例外：charting 时立即并行发 research 子代理烧掉（CHANGELOG v1.2.0 #763）。
- 输出：**决策而非交付物**——"Plan, don't do"（:11）；路清后交接给 to-spec 收敛成可建计划。
- 提升点：fog-or-ticket 判据（能否现在精确陈述问题）防止过度规划；HITL 票禁止 agent 代答用户侧（"a grilling agent that answers its own questions has broken this"，:75 附近）。

### 3.11 to-spec（会话→规格合成，75 行)

- 输入：已对齐的会话上下文。处理：明确**不再采访**，只综合（frontmatter description）；先 sketch seams 并与用户确认（:15）；模板含 Problem/Solution/长编号 User Stories/Implementation Decisions/**禁写文件路径与代码片段**（会过时）——例外：若原型产出比散文更精确的决策编码（状态机/reducer/schema），可内联并注明来源。
- 提升点：durability over precision——规格里不写易腐细节，延长产物寿命。

### 3.12 to-tickets（规格→tracer-bullet 票集，105 行）

- 输入：spec 或计划。处理：垂直切片规则——每片窄而完整地穿过所有层、独立可演示、**单片适配单个新鲜上下文窗口**（vertical-slice-rules，:29-36）；每票声明 blocking edges（:38）；宽重构例外走 expand–contract 序列保 CI 绿（:40)；发布前 quiz 用户粒度与边正确性；本地 tracker 一票一文件。
- 提升点："fit in one fresh context window" 把上下文极限当作一等设计约束；frontier 工作法（blockers 全完成即可抓取）天然支持并行 implement。

### 3.13 triage（issue 状态机分诊，112 行）

- 输入：原始 issue/外部 PR（"a PR is an issue with attached code"）。
- 处理：gather context（解析既往 triage notes 防重问；按**领域概念**而非请求措辞搜已有实现= redundancy 检查；读 `.out-of-scope/` 做 prior rejection surfacing）（:70）→ 推荐 category+state → **grilling 之前先 verify the claim**（bug 复现/PR checkout 跑测试；确认过的 claim 造就更强的 agent brief）（:74）→ 按结果落地：ready-for-agent 发 AGENT-BRIEF；wontfix 分"已实现"（指向位置，禁写 out-of-scope 防污染 dedup）与"拒绝"（enhancement 才写 out-of-scope KB）。
- 提升点：claim 验证前置把"听信描述"改为"实证复核"；out-of-scope 概念级聚合让重复请求在分诊早期就被拦截。

### 3.14 implement（薄执行编排，15 行）

- 输入：spec 或 tickets。处理：尽量用 tdd 于预约定 seam；定期 typecheck/单测文件，最后全量一次；完成后 code-review；提交当前分支。
- 提升点：自身几乎无逻辑，全部纪律外包给 tdd/code-review——再次示范组合器哲学。in-progress/implement-spec 则展示多子代理并发实现形态：task graph frontier 驱动 implementer 子代理（各自 worktree/branch）+ merger 子代理汇流（in-progress/implement-spec/SKILL.md）。

### 3.15 wizard（人机分工向导，44 行 + template.sh）

- 输入：只有人能执行的流程（开控制台点按钮、配密钥、跑一次性割接）。
- 处理：①scope——先读仓库（`.env*`、`docker-compose*`、framework config、`.github/workflows/*` 中每个 `secrets.*`/`vars.*` 引用都是必须产出的值），列出有序 stage 清单与每 stage 捕获的值请用户增删排序；②为每 stage 写"陌生人也能照做"的精确路径（Dashboard → Developers → API keys → Reveal → copy），不知道当前 UI 就问或查文档，**绝不编造可能不存在的步骤**；③复制 template.sh 逐 stage 填充——模板库已解决全部 UX（stage 清屏、确认门、跨平台开 URL 含 WSL、隐藏式密钥输入、幂等 `.env` upsert、`gh secret` 写入降级、收尾摘要），"marker 之上的库永不手编，一致性本身就是意义"；④验证只做静态：`bash -n` + shellcheck，**不代跑端到端**（会开浏览器阻塞在人类输入上）。
- 输出：一次性 bash 向导脚本；可重复的 setup 路径才提交进仓库。
- 提升点：精确划出 agent 的能力边界——"Work an agent can do, an agent should do; the wizard is for the clicks, approvals and dashboard trips you would not hand to one."（CHANGELOG #680）。把"AI 给人列一堆编号步骤指望人照做"升级为"AI 生成带进度/确认/防错的交互脚本牵着人走"。

### 3.16 writing-for-agents（写给 AI 读的文档学，元技能，~120 行）

这是整套体系的**元层**：其他技能约束 AI 做工程，这个技能约束人类如何写出 AI 能可靠执行的文档。核心理论：

- **Context pointer（上下文指针）**：指针的措辞而非目标决定 agent 何时到达材料。措辞弱的必达指针是 variance bug——先磨措辞，磨不动再内联。指针干两件事：说明材料是什么+列举应触发到达的**分支**。"One trigger per branch"：同义词改名单一分支=一个分支写两遍，合并。
- **双负载模型**：每个文档花费两种预算之一——**Context load**（常驻窗口的 token 与注意力成本，每轮都在烧）与 **Cognitive load**（人类的记忆成本："human is the index"，这是人的能动性价格，不是要最小化的成本）。经指针按需到达的材料逃掉 context load 只付指针一行；没有指针的材料全压认知负载。
- **信息层级阶梯**：in-file step（主层，按序动作）→ in-file reference（按需查阅）→ disclosed reference（推出文件外由指针点亮）。渐进披露不是 token 优化而是层级保护；**分支是干净的披露判据**：所有分支都需要的内联，只有部分分支到达的推到指针后。
- **Completion criterion（完成判据）**：每步以"agent 如何分辨 done/not-done"收尾。模糊边界招致 **premature completion**（提前宣布完成，注意力滑向"已完成"状态）；防御顺序：先锐化边界（局部便宜），不可约模糊且观察到赶工时用拆分隐藏后续步骤（只在真实上下文边界有效）。**Demand** 维度："every modified model accounted for" 强制彻底工作而"produce a change list"不能；demand 驱动 **legwork**（措辞中潜藏的挖掘量）且不限于步骤——"every rule applied" 同样约束扁平参考体，这就是纯参考文档仍能携带穷尽性标准的原因。
- **Leading words（引导词）**：复用预训练中已有的紧凑概念（_lesson_、_fog of war_、_tracer bullets_）作为 token 反复出现，积累分布式定义，用最少 token 锚定整片行为区域——自造词不招募先验，"你付定义 token 买预训练词免费送的东西"。双重锚定：正文里锚执行，指针里锚调用。典型重构："fast, deterministic, low-overhead" → _tight_；"a loop you believe in" → _red_（把模糊门变成二元可观状态）。
- **Negation 禁令**：用禁止 steering 会把被禁行为拉进上下文使其**更**可用（"Don't think of an elephant"效应）；提示**正面**目标行为让被禁者永不被说出；禁令只配做无法正面表述的硬护栏，且须与正面目标并列。
- **Pruning 四刀**：单一真理源（重复=维护+token+ prominence 虚高三重代价）；**环境也是真理源**（重述 `package.json`/目录布局的文档是 lookup 缓存，只为昂贵查找保留——缓存 agent 查不到的：未成文约定、选择背后的理由、配置不自白的坑）；逐行 relevance 审查（默认命运是 **sediment**：加感觉安全删感觉风险，陈旧层沉积到必须挖穿才能找到活内容）；逐句 no-op 猎杀（模型默认就遵守的指令白付负载；判据是 model-relative 的，靠跑文档验证而非辩论；失败句整句删除而非削词；弱引导词的修复是更强的词如 _relentless_ 而非换技术）。
- 提升点：这是"提示工程"的系统化为**文档工程学**——双负载/阶梯/引导词/完成判据四个概念可直接迁移到任何 agent 文档体系（含 PDCA 的 SKILL.md 编写规范 writing-great-skills 的对标升级）。

### 3.17 wait-what（一句话纠偏器，3 行正文）

- 输入：一条没传达到位的 AI 消息。
- 处理：全文仅一句——"Re-pitch that: give me a little bit of context, talk in ASD-STE100 Simplified Technical English, and use the ubiquitous language from CONTEXT.md"。
- 提升点：机制即名字——命名**听者的状态**（wait-what="我没跟上"）同时索要两样东西：更少词+缺失的上下文；命名输出（/tldr /no-fluff）只会让模型削词丢义（CHANGELOG #751）。它修一条消息不预防下一条——治本仍是 grill-with-docs 建共享语言。

### 3.18 handoff（会话压缩交接，12 行）

- 处理：把当前对话浓缩成交接文档存 OS 临时目录（非工作区）；附"suggested skills"节点名下一个 agent 应调用的技能；**不复述已被其他工件捕获的内容**（spec/plan/ADR/issue/commit/diff 一律引用路径或 URL）；脱敏密钥与 PII；有参数则按下一 session 焦点裁剪。
- 提升点：与 PHASE-BOUNDARIES 决策树联动（见 §4.3）；context-pointer 原则的应用典范——交接的是索引不是副本。

### 3.19 to-questionnaire（问卷化决策外包，~60 行）

- 输入：用户答不了的决策，但某个人知道答案。
- 处理："**Grill the send, not the subject**"——只追问用户永远能答的发件侧两件事：发给谁（角色/专长/关系→定语气与背景量）和要回什么（具体决策/事实清单）；然后写问卷瞄准**收件人所知与用户所需之间的 gap**。结构强制：most-important-first（异步可能只有一轮机会）、每题一个 idea 不复合、答案 stub 直接置于题下、可选 why-this-matters 行、结尾 Anything else 兜底。
- 提升点：grilling 原语的镜像应用——面试方向从"审自己"翻转为"借他人之口补盲区"，展示了原语的正交复用价值。

### 3.20 teach（多 session 教学工作区，~60 行）

- 处理：目录即教学工作区（MISSION.md 定使命/reference HTML 速查卡/RESOURCES.md 高信任资源清单/learning-records 序号化学习记录≈教学版 ADR/lessons 单文件 HTML 课）。方法论三条硬规则：知识取自高质量资源"Never trust your parametric knowledge"；区分 fluency strength（临场提取）与 storage strength（长期留存），用检索练习/间隔/交错制造 desirable difficulty；课程短小绑定使命且落在 zone of proximal development。
- 提升点：把学习科学（检索练习、间隔效应）编码进 AI 教学行为；learning-record ≈ ADR 的类比展示了"不可变经验记录"模式跨域复用。

### 3.21 其余技能速览

| 技能 | 行数 | 一句话机制 |
|------|------|-----------|
| ask-matt | 90 | 技能路由器：主流程+on-ramp+standalone 地图；phase boundaries 五选项树；smart zone 卫生规则 |
| resolving-merge-conflicts | 14 | 按 intent 解冲突：找每方 primary source、逐 hunk 保全双方意图、永不 --abort |
| setup-matt-pocock-skills | 116 | 每仓库一次性配置：tracker 类型/triage 标签映射/docs 位置 |
| grill-me | 7 | grilling 无状态包装（无仓库场景） |
| claude-handoff (in-progress) | 18 | handoff 的 Claude 特化实验版 |
| loop-me (in-progress) | 32 | grilling 状态化变体：唯一产出是 workflow spec；"Push right"推迟 checkpoint、"Brief"呈现决策摘要而非草稿 |
| git-guardrails 等 misc 4 项 | ~90×4 | 一次性环境工具，不入主流程 |

---

## 4. 主流程端到端推演（AC-4）

### 4.1 Mermaid 流程图

```mermaid
flowchart TD
    IDEA[模糊想法] --> GWD{/grill-with-docs<br/>stateful 追问}
    NO_REPO[无工作目录] --> GM[/grill-me 无状态追问/]
    GWD --> DM{{domain-modeling<br/>术语→CONTEXT.md<br/>硬决策→ADR}}
    GWD --> Q1{所有问题都能<br/>对话内敲定?}
    Q1 -- 需要 runnable 答案 --> HO1[/handoff 导出/] --> PROTO[/prototype 单HTML或多变体/] --> HO2[/handoff 回收结论/] --> GWD
    Q1 -- 多session大活 --> WF[/wayfinder 决策地图<br/>fog-of-war + decision tickets/]
    WF -- 路清 --> TS
    Q1 -- 否 --> TS[/to-spec 综合规格<br/>sketch seams/]
    Q1 -- 单session小活 --> IMP
    TS --> TT[/to-tickets tracer-bullet 票<br/>blocking edges/]
    TT --> IMP[/implement 每票新上下文<br/>内部: tdd@seam → code-review 双轴/]
    BUGS[线上坏了] --> DB[diagnosing-bugs<br/>feedback loop 优先]
    REQ[外部 issue 堆积] --> TRI[triage 状态机<br/>verify claim → AGENT-BRIEF]
    TRI -- ready-for-agent --> IMP
    HEALTH[(日常保养)] --> ICA[improve-codebase-architecture<br/>热点扫描 deepening 候选]
    ICA -- 选定候选 --> GWD
    subgraph 词汇底层 [vocabulary 层]
        CD[[codebase-design 深模块词汇]]
        WFA[[writing-for-agents 文档写法]]
    end
    CD -.被引用.- GWD & TT & IMP & ICA
    DM -.同层.- CD
```

### 4.2 文字推演（一次典型旅程）

1. **对齐段**（同一不间断上下文窗口内完成）：用户抛出想法 → grill-with-docs 启动，与 domain-modeling 成对运行；每轮 frontier 批量问答，术语当场进 CONTEXT.md，难逆决策进 ADR。
2. **原型支线**（可选）：遇到"说不清但要看得见"的问题 → handoff 导出到新 session → prototype 产单 HTML → 用户把玩 → handoff 回收 verdict → 原型上 `prototype/<name>` 分支留证。
3. **规格段**：to-spec 不再采访，直接综合；先 sketch seams（理想一条）确认；产出规格发布到 issue tracker 打 ready-for-agent 标签。
4. **拆解段**：to-tickets 切 tracer-bullet 票 + blocking 边，quiz 用户后发布。
5. **实现段**（每票全新上下文）：implement 驱动 tdd 在预约定 seam 上红绿循环 → 完成后 code-review 双轴并行子代理审查 → 合规才提交。
6. **上下文卫生贯穿全程**：smart zone（~150k token 推理锐度边界）之前不 compact/clear，直到 to-tickets 完成（ask-matt/SKILL.md:28-32）；phase boundary 五选项决策树见 §4.3。
7. **双 on-ramp 汇入**：triage 产出的 agent-ready brief 与 wayfinder 收敛的决策地图都在 to-spec/implement 处并入主流程；diagnosing-bugs 的 post-mortem 若发现"没有好 seam 锁住这个 bug"则移交 improve-codebase-architecture。

### 4.3 Phase Boundaries 决策树（PHASE-BOUNDARIES.md 全文机制）

**phase** 是 session 内一段工作（grilling、实现、QA），定义刻意模糊——"你觉得 ok done with that 时它就结束"。决策只允许发生在 **boundary**：mid-phase 没有决策可做，只能 continue 或把剩余拆给子代理；中途 compact 会让 agent 丢线。

五个选项按序自上而下问，第一个 yes 获胜：

1. **能继续在本 session 吗？** 下一 phase 需要本 phase 作 primary source（grilling→implementation 是标准 yes：实现要推理的原文而非摘要），或 smart zone 余量足够 → **Continue**。零成本零损失，最先排除其他选项。
2. **上下文与后续无关吗？** 本 session 的探索/决策/死胡同全可弃 → **`/clear`**。棋盘上最便宜的一手；且 clear 不 terminal，旧 session 可恢复。错删相关上下文的代价是单向的：why 丢了读 diff 也回不来。
3. **需要交接吗？** `/handoff` 很窄，仅四种情况：换 harness（Claude→Codex）/换目录或仓库/发给同事/mid-phase 分叉支线任务。它买到的是 **portability**；没有东西在旅行就不需要它。
4. **任务能 AFK 吗？** scope 够紧可无人值守 → **Subagent**，主 session 原封不动。自动化 review 是标准场景。
5. **否则 `/compact`**。相关上下文+同 harness+同目录+需要你留在环里——树在这里着陆且经常着陆。传指令（如 `/compact we're going to QA this area`）让摘要保住下一 phase 需要的东西。它是**默认不是首选**：先问的四个问题都更便宜或更精确；从 compact 开始的失败模式是新 session 对被摘要压扁的决策自信地错。

底层模型是**一手/二手源交换表**：除 Continue 外每个动作都把 primary source（session 本身：信息全、噪声大、腾挪空间小）换成 secondary source（摘要：有损、噪声低、空间大）。这就是问题 1 排第一的原因——只有当留下的成本大于收益时才付有损代价。五问都是 judgement call，价值在于**按序、在 boundary 问**。

---

## 5. 提升机制的横向归纳（为什么会生效）

| 机制 | 实现手段 | 对应 AI 弱点 |
|------|---------|-------------|
| 隐性知识显式化 | 36 个 SKILL.md 把专家纪律写成可加载指令 | 参数化知识泛化、缺项目特定纪律 |
| 行为空间收窄 | 状态机（triage roles）、循环规则（tdd）、门禁（claim 验证） | 自由发挥导致的漂移 |
| 上下文工程 | 共享语言压缩 token、最小相关加载、context pointers 而非复制 | 上下文窗口有限、噪声敏感 |
| 人机决策分界 | facts=agent 自查 / decisions=user 裁决；HITL 票禁代答 | 越权代答、浪费用户注意力 |
| 反馈优先 | TDD、feedback loop 10 法、verify the claim | 无实证的自信推理 |
| 隔离防污染 | 双轴并行子代理、background research、per-ticket 新窗口 | 上下文串扰、注意力稀释 |
| 组合器架构 | 薄封装（grill-with-docs 3 行）+ 单一原语（grilling） | 重复指令语义漂移、维护爆炸 |
| 双负载触发 | frontmatter 描述面向模型触发 / README 面向人类路由 | 技能发现率低 |

值得强调的两个反直觉设计：
- **简洁技能不许长大**：wait-what 只有 3 行，理由是"简洁技能因增长而失效"（CHANGELOG #751）。
- **参考型技能必须挂载在 driver 之下**：codebase-design 被 agent 当流程乱跑的事故（issue #449）催生了"词汇层/流程层"分离纪律。

### 5.1 写作学元层：文档即运行时（writing-for-agents 的理论贡献）

该项目的深层竞争力不在单个技能而在**如何写技能**。writing-for-agents 把"给 AI 写文档"系统化为五组杠杆，与 §3.16 拆解对应后可提炼为：

1. **双负载核算**：每行字要么烧 context load（常驻窗口）要么烧 cognitive load（人类记忆），写作前先选预算——这是 token 经济学的工程化。
2. **引导词复利**：一个预训练词（_tight_/_red_/_fog of war_）招募模型既有先验，比三句解释便宜且更可靠；同一词在 prompt/docs/codebase 三处出现时形成共享语言闭环，调用可靠性随使用次数上升。
3. **正面表述定律**：negation 把禁止的行为拉进注意力场；所有护栏尽量改写为正向目标。这直接解释了为什么优秀 SKILL.md 几乎不用"don't"开头（tdd 反模式节先立正面标准再列反例）。
4. **完成判据双重性**：clarity 防 premature completion，demand 驱动 legwork——纯参考文档也能通过 "every rule applied" 类措辞携带穷尽性要求，这是扁平参考体不退化为摆设的关键。
5. **环境优先真理源**：能从 `package.json`/目录布局/`--help` 读到的就不要写进文档（写了就是会过期的缓存）；文档只保留 agent 查不到的东西——约定背后的 why、不自白的坑。

### 5.2 分发与工程化机制

- **双通道安装**：Claude Code 官方 marketplace 插件（托管只读、自动更新、订阅制）vs skills.sh 文件复制（自有可编辑、手动 pull 更新）。两条路线互斥——"Installing both leaves the user with every skill twice: always say 'pick one'"（.agents/writing-docs.md canonical install block）。README/changeset/docs 全部引用同一 canonical 措辞块，杜绝漂移。
- **docs 镜像树**：engineering/productivity 两 bucket 每个 promoted 技能在 `docs/<bucket>/<name>.md` 有人工向 docs 页（发布于 aihero.dev，绝对链接），misc/in-progress/deprecated 不配页——"docs 页不是 SKILL.md 的副本"，职责是缓解认知负载："Most of these skills are user-invoked…you are the index that has to remember they exist. The job of a docs page is to relieve it."（.agents/writing-docs.md）
- **双 harness 元数据同步**：每个 SKILL.md 旁配 agents/openai.yaml（Codex 显示名+策略），user-invoked 状态必须两平台一致（v1.2.0 #551；#766 曾因 Codex 过滤导致 writing-for-agents 失去隐式触发而回滚策略）。
- **changesets 版本治理**：CHANGELOG 每条目绑定 PR 号+commit hash，技能演化全程可溯——本报告多处直接引用 CHANGELOG 作为设计决策证据。

---

## 6. 可迁移原则与 pdca-workflow 落地建议（AC-5）

以下 9 条原则超出 5 条底线，均标注落地路径：

### P1 决策树批量追问（frontier + 推荐答案）
- 原则：每轮把当前可答的全部决策一次性问完且每问带推荐，事实自查、决策归用户。
- pdca 现状：flow-plan P2 已引入 grilling 且 clarifications.jsonl 记录 round。
- 落地建议：**Check 阶段写 conclusion.md 前增加一轮 Do→Check viewpoints 的 frontier 追问**（grilling SKILL 已内置该 viewpoint 清单，但 flow-check 未强制调用）；把"每问必附推荐"写入 register-evidence 的验收映射生成逻辑。

### P2 共享语言即压缩
- 原则：模糊术语当场落定进 CONTEXT.md，一词替换一段描述，token 与歧义双降。
- pdca 现状：pdca/CONTEXT.md 已存在且由 domain-modeling 维护，但近期新增条目集中在 CDM 报表中心域，工程通用词（如"握手""帧"）定义良好。
- 落地建议：对 rpc/tls 高频任务族建立**子域术语块**（类似 CONTEXT-MAP 多上下文方案）；grilling 中命中新术语时强制即时更新（目前依赖自觉，可加 gate 提示）。

### P3 反馈回路优先于推理
- 原则：先构造对本问题变红的一命令信号，再允许假设/修复；把回路当产品打磨（更快/更锐/更确定）。
- pdca 现状：development/bugfix 走 TDD + 声明测试接缝（ADR-0018），已是同类思想。
- 落地建议：**research 场景补"可验证信号"要求**——调研结论须附至少一条可复核的验证途径（命令、SQL、可复现实验），否则不得登记 evidence；这与 triage-work 的边界判定规则（T0273）呼应。

### P4 事实代理化、决策人主化
- 原则：凡文件系统/工具可查的事实绝不问用户；凡权衡取舍绝不替用户决定。
- pdca 现状：门禁体系已强制 final_confirmation/check_confirmation 人审。
- 落地建议：在 flow-do 执行器容错节补充显式二分清单（哪些异常属 Blocking 需人裁、哪些可自动跳过），减少主会话临场判断。

### P5 双轴分离审查
- 周则：标准轴与规范轴并行独立、聚合时不重排，防一轴掩盖另一轴。
- pdca 现状：skills/code-review 已移植双轴（SKILLS-INDEX 第 18 行）。
- 落地建议：补齐 Fowler 坏味基线的"repo overrides"规则说明（当前版本未明确 repo 标准覆盖基线的优先级条款）。

### P6 原型作为一手证据留存
- 原则：弃用原型不上 main，但以游离分支+上下文指针形式永久可溯。
- pdca 现状：skills/prototype 存在，但 evidence 登记惯例未包含原型分支指针。
- 落地建议：register-evidence 增加 evidence kind `prototype-branch`，字段含分支名与 verdict 摘要；A1 步骤的原型产物按此登记。

### P7 上下文卫生与阶段边界
- 原则：smart zone 内不 compact；阶段边界才选择 continue/clear/handoff/subagent/compact 五选项。
- pdca 现状：handoff/write-journal 技能在，但无"何时清窗"的操作指引。
- 落地建议：flow-do 通用收尾处加一段 phase-boundary 决策树（五选项顺序与理由可直接翻译自 PHASE-BOUNDARIES.md），并把"每子任务新窗口"写入 P4 拆解后的调度约定。

### P8 文档双负载核算（新增，源自 writing-for-agents）
- 原则：写任何 SKILL.md/流程文档前先选预算——常驻上下文的行按 context load 审查（引导词前置、一分支一触发词），按需加载的行按 cognitive load 审查（人类是否需要记住它的存在）。
- pdca 现状：内容预算机制管 bytes 增长，但不区分"常驻 vs 指针后"两类成本；writing-great-skills 已有极简原则但无 leading words/negation/completion criterion 理论。
- 落地建议：将 writing-for-agents 的四组杠杆（双负载/引导词/正面表述/完成判据双重性）合入 `$PDCA_HOME/skills/writing-great-skills/SKILL.md`；对 flows/ 下四个 SKILL.md 的 description 做"一分支一触发词"审查。

### P9 完成判据 demand 化（新增）
- 原则：每个步骤以可检验且带穷尽性要求的判据收尾（"every rule applied"而非"produce a change list"），防 premature completion。
- pdca 现状：门禁脚本已强校验（schema/digest/convergence），但技能正文内的步骤完成判据多为叙述式。
- 落地建议：flow-do 六路径的每步补"Done when"句式；register-evidence 的 AC 映射要求已是良好示范，推广到 triage-work/grilling。

### 附：结构性差异观察（供 Act 阶段知识处置）
- mattpocock/skills **轻流程重纪律**：状态外置 issue tracker，无 schema 校验；pdca-workflow **重流程强门禁**：records/evidence/receipt 内聚。两者互补——pdca 可借鉴其"薄组合器+词汇层"控制技能体积，其可借鉴 pdca 的"内容预算+确定性夹具"控制技能质量。
- 该项目的失效模式驱动开发法（先列失效再设计技能，README.md:84）与 pdca 的 Flow Issue Occurrence→Improvement Candidate 机制同构，可互相印证。

---

## 7. 引用文件清单

| 文件 | 用途 |
|------|------|
| README.md:84-232 | 四大失效模式原文、技能双轨分类 |
| skills/productivity/grilling/SKILL.md:8,24,26,28 | frontier/rounds/事实决策二分 |
| skills/engineering/domain-modeling/SKILL.md:44-73 | 建模纪律五步 |
| skills/engineering/codebase-design/SKILL.md:10-63 | 强制词汇表/深浅/删除测试 |
| docs/engineering/codebase-design.md | reference-not-process、issue #449/#458/#95、DEEPENING 依赖四分类 |
| skills/engineering/tdd/SKILL.md:22-38 | pre-agreed seams、反模式、循环规则 |
| skills/engineering/diagnosing-bugs/SKILL.md:18-138 | feedback loop 本体论、六阶段门禁、DEBUG 标签、correct seam |
| skills/engineering/code-review/SKILL.md:11,23,76-88 | 双轴并行、不重排、Fowler 基线 |
| skills/engineering/research/SKILL.md:6-11 | 一手来源、后台代理 |
| skills/engineering/prototype/SKILL.md:1-26 | 双分支选择、六条通用规则、留证分支 |
| skills/engineering/improve-codebase-architecture/SKILL.md:1-71 | YAGNI 定界、HTML 报告卡、grilling 循环、ADR 冲突处理 |
| skills/engineering/wayfinder/SKILL.md:7-99 | decision ticket、fog of war、frontier |
| skills/engineering/to-spec/SKILL.md:15 | seam sketching |
| skills/engineering/to-tickets/SKILL.md:29-40 | 垂直切片、expand–contract |
| skills/engineering/triage/SKILL.md:70-74 | claim 验证前置、dedup |
| skills/engineering/wizard/SKILL.md:1-44 | 人机分工边界、stage 授权流程 |
| skills/productivity/writing-for-agents/SKILL.md | 双负载/信息阶梯/引导词/negation/pruning 全文理论 |
| skills/productivity/wait-what/SKILL.md:1-7 | 一句话纠偏器 |
| skills/productivity/handoff/SKILL.md:1-12 | 交接文档约定 |
| skills/productivity/to-questionnaire/SKILL.md | grill-the-send 镜像应用 |
| skills/engineering/ask-matt/PHASE-BOUNDARIES.md | 五选项决策树全文、一手/二手源表 |
| .agents/invocation.md | Skill tool 调用约定、双轨不变式 |
| .agents/writing-docs.md | canonical install block、docs 镜像树职责 |
| CHANGELOG.md (#551,#533,#536,#680,#751,#763,#766,#779) | 设计演化证据 |
