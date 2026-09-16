# Skills 横向对比：PDCA vs 热门方案

> **对比对象：** PDCA、Superpowers、mattpocock/skills、gstack
> **日期：** 2026-09-16（v3 — 全面探索四个项目完整结构 + 逐条读取所有 skill 文件后修订）
> **数据来源：** 本地安装文件（PDCA 仓库 + Superpowers）+ GitHub API 获取（mattpocock 37 个 skill + gstack 23+ 个 skill）
> **目的：** 评估 PDCA 在 AI 编码技能生态中的位置，识别可借鉴项与不适用项

---

## 1. 各方案概览

| 维度 | PDCA | Superpowers | mattpocock/skills | gstack |
|------|------|-------------|-------------------|--------|
| **定位** | 工作流管理/记录系统 + 代码开发补充技能 | 完整软件开发方法论 | 可组合的工程技能集 | 虚拟工程团队 |
| **核心理念** | 集中管理规则、本体、记录与资源预约；代码技能作为补充 | TDD + 子代理 + 验证优先 | 小而可组合，不控制流程 | 角色化专家团队 |
| **Skill 数量** | 9 核心（2 入口 + 4 阶段 + 3 场景）+ 8 补充（代码开发） | 14 | 37（18 工程 + 7 生产力 + 4 杂项 + 8 进行中） | 23+ skill + 8 tool + 11 iOS skill |
| **宿主** | OpenCode | Claude Code / OpenCode / Codex | Claude Code / OpenCode | Claude Code + 9 其他 |
| **安装方式** | 符号链接 + Git 工作副本 | Git 插件 / 符号链接 | `npx skills@latest add` / Claude 插件 | `git clone` + `./setup` |
| **架构模式** | 双层（核心工作流 + 代码开发补充）+ 双根（PDCA_ROOT + TARGET_ROOT） | 平铺 skill 目录 | 用户调用 + 模型调用分离 | 角色化 skill + power tool |
| **记录管理** | 31 种记录形状 + Git 跟踪 | 账本（progress.md） | Issue Tracker（GitHub/Linear/本地） | 无专用记录系统 |
| **授权模型** | 逐阶段用户授权 + 资源预约 | 审批门控（hard gate） | 无显式授权 | 无显式授权 |
| **领域建模** | pdca-model（本体建模） | — | grill-with-docs（CONTEXT.md + ADR） | design-consultation（DESIGN.md） |
| **代码开发** | 8 个补充 skill（提交格式、审查清单、TDD 策略、安全编码等） | TDD + 调试 + 审查全流程 | implement + code-review + diagnosing-bugs | ship + review + qa + investigate |
| **Stars** | — | ~20k | — | 133k |

### PDCA 双层架构说明

PDCA 的 skill 体系分为两层：

| 层 | Skill | 注册状态 | 职责 |
|----|-------|---------|------|
| **核心层（9 个）** | pdca, pdca-assist, pdca-plan, pdca-do, pdca-check, pdca-act, pdca-model, pdca-implement, pdca-verify | 已注册在 `catalog.json` | 工作流管理：规则、本体、记录、资源预约 |
| **补充层（8 个）** | bug-commit-format, feature-commit-format, build-config, chinese-environment, code-comments, code-review-checklist, secure-coding, testing-strategy | 未注册在 `catalog.json`，存在于 `skills/` 目录 | 代码开发辅助：提交规范、审查、测试、安全、构建 |

**关键区别：** 核心层遵循严格规则（切换 Skill 不换 Agent、逐阶段授权、不自动串联）；补充层是独立的代码开发参考技能，不参与 PDCA 四阶段流程。

### mattpocock 主流程（v3 补充）

mattpocock 的核心工作流是一条**主流程 + 两条接入路径 + 词汇层**：

```
主流程: idea → ship
  grill-with-docs → to-spec → to-tickets → implement(→ tdd[red-green] + code-review)
                                ↗
接入1: triage (bug/需求涌入)
接入2: diagnosing-bugs (硬 bug) → improve-codebase-architecture
      wayfinder (大型项目) → to-spec → to-tickets
词汇层: domain-modeling (CONTEXT.md + ADR) / codebase-design (深度模块设计)
阶段边界: continue / clear / handoff / subagent / compact（5 选 1）
```

### gstack 共享基础设施（v3 补充）

gstack 每个 SKILL.md 文件（65K-118K bytes）中约 70-80% 是**共享基础设施**，所有 skill 共用：

| 机制 | 说明 |
|------|------|
| **AskUserQuestion 格式** | 决策简报模板（D<N>、ELI10、Completeness 评分、Pros/Cons） |
| **Voice 规则** | Garry 风格的产品和工程判断 |
| **Context Recovery** | 会话恢复（最近工件、决策日志） |
| **Question Tuning** | 用户问题偏好学习（tune: never-ask / always-ask） |
| **Completeness Principle** | "煮沸湖泊"——修复爆炸半径内的一切 |
| **Confusion Protocol** | 高风险歧义处理 |
| **Repo Ownership** | solo vs collaborative 模式识别 |
| **Search Before Building** | 重用阶梯（仓库内→标准库→平台特性→已安装依赖→新代码） |
| **Operational Self-Improvement** | 每次技能结束时记录学习，未来调用时搜索相关学习 |
| **Telemetry** | 遥测数据收集 |

---

## 2. 能力维度深度对比

### 2.1 生命周期管理

| 子维度 | PDCA | Superpowers | mattpocock | gstack |
|--------|------|-------------|------------|--------|
| **问题定义** | `pdca-assist`（只读建议，含协作交接视角） | `brainstorming`（三条路径：Spike/Bounded/Architectural，HARD-GATE 审批） | `grill-me` / `grill-with-docs`（委托 grilling + domain-modeling，创建 ADR 和术语表） | `office-hours`（6 个强制问题，重新定义问题） |
| **计划制定** | `pdca-plan`（固定需求 + AC/oracle + 写域） | `writing-plans`（TDD 任务结构，禁止占位符，self-review） | `to-spec`（会话→规格，发布到 Issue Tracker） | `plan-ceo-review`（战略挑战）、`plan-eng-review`（架构锁定）、`autoplan` |
| **任务执行** | `pdca-do`（集中资源 + 写域 + 不自动 Check） | `subagent-driven-development`（每任务一代理 + 任务审查 + 最终审查，ledger 追踪） | `implement`（驱动 tdd[red-green] + code-review，提交到当前分支） | `ship`（TDD + 测试 + PR 全流程） |
| **检查验证** | `pdca-check`（核验产物 + 标准 + 证据） | `verification-before-completion`（证据先于声明，铁律） | `code-review`（双轴：标准 + 规格，并行子代理） | `review`（Staff Engineer 角色）、`qa`（QA Lead，真实浏览器） |
| **收尾发布** | `pdca-act`（归档/发布，用户批准） | `finishing-a-development-branch`（验证→检测→选项→执行→清理） | `implement` 内含 code-review + commit（无独立收尾 skill） | `land-and-deploy`（合并→CI→部署→验证）、`canary`（部署后监控） |
| **恢复机制** | 共同恢复入口（Git HEAD + 状态 + 任务绑定） | 账本 + `git log`（压缩后存活） | `handoff`（会话压缩→交接文档，保存到 OS 临时目录） | `context-save` / `context-restore` |

### 2.2 质量保障

| 子维度 | PDCA 核心层 | PDCA 补充层 | Superpowers | mattpocock | gstack |
|--------|-----------|------------|-------------|------------|--------|
| **测试策略** | — | `testing-strategy`（测试金字塔、5 语言覆盖、反合理化守卫） | `test-driven-development`（RED→GREEN→REFACTOR 铁律） | `tdd`（red-green loop，refactor 归 review 阶段） | `ship`（test-first）、`qa`（测试+修复循环） |
| **代码审查** | — | `code-review-checklist`（系统性审查清单，反合理化守卫，5 语言） | `requesting-code-review`（派遣审查子代理）+ `receiving-code-review`（技术验证优先，禁止表演性同意） | `code-review`（双轴并行子代理：标准 + 规格） | `review`（Staff Engineer）、`codex`（第二意见） |
| **验证门控** | `pdca-check`（证据优先，核验 AC） | — | `verification-before-completion`（铁律：NO COMPLETION CLAIMS WITHOUT EVIDENCE） | — | `qa`（真实浏览器测试） |
| **调试方法** | — | — | `systematic-debugging`（四阶段：根因→模式→假设→实现，铁律） | `diagnosing-bugs`（6 阶段纪律化诊断循环，REDACTED 输出） | `investigate`（根因方法，freeze 护栏） |
| **安全审计** | — | `secure-coding`（C/C++/Rust/Go/Python 安全编码，OWASP Top 10） | — | — | `cso`（OWASP + STRIDE 审计） |
| **架构审查** | — | — | — | `improve-codebase-architecture`（扫描深度机会） | `plan-eng-review`、`devex-review` |
| **提交规范** | — | `bug-commit-format`（10 要素）+ `feature-commit-format`（10 要素） | — | — | — |

### 2.3 工程实践

| 子维度 | PDCA | Superpowers | mattpocock | gstack |
|--------|------|-------------|------------|--------|
| **Git 工作流** | 集中 Git 工作副本 + 双根 | `using-git-worktrees`（隔离工作区，原生工具优先） | — | — |
| **子代理编排** | Agent 路由（切换 Skill 不换 Agent） | `subagent-driven-development` + `dispatching-parallel-agents` | `code-review`（并行子代理：标准 + 规格） | `pair-agent`（多代理协调） |
| **技能编写** | — | `writing-skills`（TDD for docs，SDO 优化，压力测试） | `writing-for-agents`（为代理写文档） | `skillify`（将流程转化为 skill） |
| **领域建模** | `pdca-model`（本体建模） | — | `domain-modeling`（挑战术语 + CONTEXT.md + ADR） | `design-consultation`（DESIGN.md） |
| **投影实现** | `pdca-implement`（本体→实体和映射） | — | — | — |
| **符合性验证** | `pdca-verify`（需求→模型、模型→投影、产物→行为） | — | — | — |
| **大任务规划** | — | — | `wayfinder`（共享地图 + 决策工单，逐个解决直到路径清晰） | `autoplan`（自动串联多轮审查：CEO→设计→DX→工程） |
| **任务分解** | — | — | `to-tickets`（tracer-bullet 工单 + 阻塞边声明） | — |
| **原型制作** | — | — | `prototype`（一次性 HTML 原型，抛即代码回答设计问题） | `design-shotgun`（4-6 变体）、`design-html`（生产级 HTML） |
| **文档生成** | — | — | — | `document-release`（更新文档）、`document-generate`（Diataxis 框架） |
| **知识管理** | ontology/（规则 + 本体 + 决策） | — | `CONTEXT.md` + ADR（领域词汇） | `learn`（跨会话学习记忆） |
| **代码注释** | `code-comments`（中文注释 + 业务逻辑图 + 技术原理） | — | — | — |
| **构建配置** | `build-config`（C/C++/Rust/Go/Python 速查） | — | — | — |
| **中文环境** | `chinese-environment`（全中文项目环境） | — | — | — |
| **研究调查** | — | — | `research`（后台代理调查原始来源，产出引用 Markdown） | — |
| **合并冲突** | — | — | `resolving-merge-conflicts`（逐 hunk 按意图解决，不 --abort） | — |
| **人类步骤向导** | — | — | `wizard`（生成交互式 bash 向导，引导人类完成基建/凭证/CI） | — |
| **教学** | — | — | `teach`（多会话学习工作空间，含 HTML 课程） | — |
| **模块设计** | — | — | `codebase-design`（深度模块词汇：接口/深度/接缝/适配器） | — |
| **代码健康** | — | — | `improve-codebase-architecture`（扫描深化机会，HTML 报告） | — |
| **问题澄清** | — | — | `wait-what`（消息未传达清楚时重新表述） | — |
| **代理文档** | — | `writing-skills`（SDO + 说服心理学） | `writing-for-agents`（上下文指针、前导词、信息层级） | `skillify`（将流程转化为 skill） |

### 2.4 管理与流程

| 子维度 | PDCA | Superpowers | mattpocock | gstack |
|--------|------|-------------|------------|--------|
| **记录管理** | 31 种记录形状 + Git 跟踪 | 账本（progress.md） | Issue Tracker | — |
| **资源预约** | 集中资源账本（文件/目录/设备/数据库） | — | — | — |
| **授权模型** | 逐阶段用户授权 + 写域控制 | 审批门控（hard gate） | — | — |
| **版本控制** | Git 跟踪记录 + `rules_git_head`/`rules_git_status` | Git 跟踪代码 | Git 跟踪 Issue | — |
| **交接** | — | — | `handoff`（会话压缩→交接文档，保存到 OS 临时目录） | — |
| **回顾** | — | — | `retro`（进行中，编码会话回顾） | `retro`（周回顾，跨项目，per-person breakdown，趋势追踪） |
| **部署** | — | — | — | `land-and-deploy`、`canary`（部署后监控）、`benchmark` |
| **浏览器控制** | — | — | — | `browse`、`scrape`、`setup-browser-cookies` |
| **多模型审查** | — | — | — | `codex`（第二意见）、`claude-code`（第二意见） |
| **安全护栏** | — | — | — | `careful`（警告）、`freeze`（范围锁定）、`guard`（组合）、`unfreeze` |
| **学习记忆** | — | — | — | `learn`（跨会话学习）+ Operational Self-Improvement（每次技能结束记录学习） |
| **问题偏好** | — | — | — | Question Tuning（用户可 tune: never-ask / always-ask） |

---

## 3. PDCA 独有能力（其他方案没有）

| 能力 | PDCA 实现 | 为什么其他方案没有 | 价值 |
|------|----------|------------------|------|
| **双根架构** | PDCA_ROOT（集中）+ TARGET_ROOT（业务） | 其他方案直接操作业务代码库 | 管理与业务隔离，规则不污染代码 |
| **31 种记录形状** | `ontology/contracts/record-shapes/` | 其他方案用自由文本或 Issue | 结构化记录，可机器处理 |
| **资源预约** | 集中资源账本 | 其他方案无资源冲突管理 | 避免多任务/多代理资源竞争 |
| **三场景分离** | pdca-model / pdca-implement / pdca-verify | 其他方案不区分建模/投影/验证 | 职责清晰，每个场景独立 PDCA |
| **逐阶段授权** | 每阶段用户明确启动 + 完成后等待 | 其他方案要么全自动要么全手动 | 用户保持控制权，不被代理接管 |
| **恢复入口** | 共同恢复入口（Git + 任务 + Agent 绑定） | 其他方案依赖会话上下文 | 上下文压缩后可恢复 |
| **本体管理** | `ontology/`（概念/实体/过程/原则...） | 其他方案无本体层 | 规则可追溯、可演进 |
| **投影映射** | pdca-implement（本体→实体） + pdca-verify（三向核验） | 其他方案直接写代码 | 模型与产物分离，可验证一致性 |
| **提交规范** | bug-commit-format + feature-commit-format（各 10 要素） | 其他方案无结构化提交规范 | 提交信息可追溯，含根因/影响/回滚 |
| **代码审查清单** | code-review-checklist（5 语言，反合理化守卫） | 其他方案的审查是流程性的，非清单驱动 | 系统性覆盖，不依赖审查者经验 |
| **中文开发环境** | chinese-environment + code-comments | 其他方案无中文支持 | 全中文文档/注释/提交，代码保持英文 |

---

## 4. PDCA 缺失能力分析

### 4.1 核心层缺失

| 缺失能力 | 谁有 | 重要性 | 是否值得补充 | 理由 |
|---------|------|--------|-------------|------|
| **TDD 铁律** | Superpowers / mattpocock / gstack | 中 | ⚠️ | PDCA 核心层不做代码，但补充层的 testing-strategy 可升级 |
| **调试方法论** | Superpowers / mattpocock / gstack | 中 | ⚠️ | 可融入 pdca-check 的异常处理，但非核心层职责 |
| **会话交接文档** | mattpocock（handoff） | 中 | ⚠️ | PDCA 已有恢复入口+协作交接，缺口较小 |
| **回顾机制** | gstack（retro） | 中 | ⚠️ | 可在 pdca-act 中增加回顾视角 |
| **文档 Diataxis 框架** | gstack（document-generate） | 低 | ⚠️ | 可改善 ontology 文档组织 |

### 4.2 补充层缺失

| 缺失能力 | 谁有 | 重要性 | 是否值得补充 | 理由 |
|---------|------|--------|-------------|------|
| **TDD 流程（RED→GREEN→REFACTOR）** | Superpowers（铁律）/ mattpocock / gstack | 高 | ✅ | testing-strategy 覆盖了"测什么"，但缺少"怎么测"的 TDD 工作流 |
| **调试方法论** | Superpowers（四阶段）/ mattpocock（6 阶段）/ gstack（根因） | 高 | ✅ | 补充层完全缺失调试 skill |
| **接收代码审查** | Superpowers（receiving-code-review） | 中 | ⚠️ | code-review-checklist 覆盖了"怎么审"，但缺"怎么接收审查反馈" |
| **验证门控** | Superpowers（verification-before-completion） | 中 | ⚠️ | pdca-check 已有验证框架，但补充层缺代码级验证门控 |
| **构建配置** | gstack | 低 | ❌ | build-config 已覆盖 5 语言速查 |

---

## 5. 可借鉴项与详细修改指南

### 5.1 [P1] TDD 工作流技能（补充层新增）

**来源：** Superpowers `test-driven-development`
**借鉴什么：** RED→GREEN→REFACTOR 铁律 + "先写测试再写代码"的纪律 + 反合理化守卫
**为什么需要：** PDCA 补充层的 `testing-strategy` 覆盖了"测什么"（测试金字塔、5 语言覆盖、反合理化），但缺少"怎么测"的 TDD 工作流——即 RED→GREEN→REFACTOR 的具体操作纪律。Superpowers 的 TDD skill 有完整的铁律："NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"。
**目标文件：** `skills/tdd-workflow/SKILL.md`（新增补充技能）

#### 当前状态

`skills/testing-strategy/SKILL.md`（337 行）：
- 覆盖测试金字塔、5 语言测试框架选择、反合理化守卫
- 缺少 TDD 工作流的 RED→GREEN→REFACTOR 循环
- 缺少"先写测试再写代码"的铁律
- 缺少"写了代码再补测试→删除代码重来"的纪律

Superpowers `test-driven-development/SKILL.md`（320 行）核心内容：
- 铁律："NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
- "写了代码再补测试？删掉。从头开始。"
- 三步循环：RED（写失败测试）→ GREEN（最小代码通过）→ REFACTOR（清理）
- 每步都有验证门控（确认失败正确 / 确认全部通过）
- 反合理化守卫表

#### 修改方案

**修改 1：** 新建 `skills/tdd-workflow/SKILL.md`，整合 Superpowers TDD 铁律与 PDCA testing-strategy 的语言覆盖：

```markdown
---
name: tdd-workflow
description: Use when implementing any feature or bugfix, before writing implementation code
---

# TDD 工作流（RED→GREEN→REFACTOR）

## 概述

先写测试。看它失败。写最小代码通过。

**核心原则：** 如果你没有看到测试失败，你就不知道它测的是不是对的。

**违反规则的字面意思就是违反规则的精神。**

## 铁律

```
无失败测试则无生产代码
```

写了代码再写测试？删掉。从头开始。

- 不要留着当"参考"
- 不要"边写测试边改"
- 不要看它
- 删就是删

从测试开始实现。句号。

## RED→GREEN→REFACTOR

### RED：写失败测试
1. 写一个测试，描述你期望的行为
2. 运行测试，确认它失败
3. 确认失败原因是"功能不存在"而非语法错误

### GREEN：写最小代码
1. 写刚好能让测试通过的代码
2. 运行测试，确认全部通过
3. 不要多写——最小即可

### REFACTOR：清理
1. 消除重复
2. 改善命名
3. 拆分过大的函数/类
4. 运行测试，确认仍然通过

## 语言支持

参考 `testing-strategy` 获取各语言测试框架选择。
```

**修改 2：** 在 `skills/testing-strategy/SKILL.md` 的 Companion skills 中增加引用：

将现有：
```
**Companion skills:** `test-driven-development` (TDD workflow), `code-review-checklist` (testing review items), `build-config` (test runner setup)
```
替换为（因为本地没有 `test-driven-development` skill，改为引用新增的 `tdd-workflow`）：
```
**Companion skills:** `tdd-workflow` (TDD workflow), `code-review-checklist` (testing review items), `build-config` (test runner setup)
```

#### 影响范围
- 涉及文件：新增 `skills/tdd-workflow/SKILL.md`、修改 `skills/testing-strategy/SKILL.md`
- 向后兼容：✅ 新增补充技能 + 修改引用，不影响核心层
- 测试验证：在代码开发任务中加载 tdd-workflow，验证 RED→GREEN→REFACTOR 流程

#### 风险与取舍
- 做：补充层获得完整的 TDD 工作流，与 testing-strategy 互补
- 不做：testing-strategy 仍是"测什么"的参考，缺少"怎么测"的操作纪律
- 替代：不新增 skill，仅在 testing-strategy 中增加 TDD 章节（更轻量但耦合）
- **注意：** 上述提案仅为骨架，实施时需补充 Superpowers 的反合理化守卫表（8 条合理化借口 + 真相）和 writing-good-tests.md 的测试规则（198 行）

---

### 5.2 [P1] 调试方法论技能（补充层新增）

**来源：** Superpowers `systematic-debugging` + mattpocock `diagnosing-bugs`
**借鉴什么：** "无根因调查则无修复"铁律 + 四阶段流程（根因→模式→假设→实现）
**为什么需要：** PDCA 补充层完全缺失调试 skill。Superpowers 和 mattpocock 都有成熟的调试方法论，核心是"先找根因再修复"的铁律。
**目标文件：** `skills/systematic-debugging/SKILL.md`（新增补充技能）

#### 当前状态

PDCA 补充层 8 个 skill 中没有调试相关技能。`pdca-check` 有异常处理能力但面向工作流层面，不是代码级调试。

Superpowers `systematic-debugging/SKILL.md`（283 行）核心：
- 铁律："NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
- 四阶段：根因调查 → 模式识别 → 假设 → 实现
- Phase 1 完成标准：tight loop（一个命令能复现 + 能捕获用户描述的症状）
- 每个 Phase 都有明确的完成标准和门控

mattpocock `diagnosing-bugs/SKILL.md`（8529 bytes）核心：
- 6 阶段：构建反馈循环 → 复现+最小化 → 假设 → 插桩 → 修复+回归测试 → 清理
- Phase 1 完成标准：tight loop + red-capable + deterministic + fast + agent-runnable
- 假设必须可证伪，3-5 个排名假设
- Phase 5 回归测试必须在修复之前写
- 输出必须 REDACTED（隐藏环境凭证）

#### 修改方案

**修改 1：** 新建 `skills/systematic-debugging/SKILL.md`，整合两者精华：

```markdown
---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# 系统性调试

## 概述

**核心原则：** 必须找到根因再尝试修复。修复症状就是失败。

## 铁律

```
无根因调查则无修复
```

如果你还没完成 Phase 1，你不能提出修复方案。

## 四阶段

### Phase 1：根因调查
1. 仔细阅读错误信息（不要跳过）
2. 稳定复现（不能稳定复现→收集更多数据，不要猜）
3. 检查最近改动
4. 构建 tight loop：一个命令能复现 + 能捕获症状

**完成标准：** 你能命名一个已经运行过的命令，它驱动了实际的 bug 代码路径并断言了用户的精确症状。

### Phase 2：模式识别
1. 错误分类（编译时/运行时/逻辑/集成）
2. 搜索已知模式
3. 检查相关代码

### Phase 3：假设
1. 生成 3-5 个排名假设
2. 每个假设必须可证伪
3. 格式："如果 <X> 是原因，那么 <Y> 会..."

### Phase 4：实现修复
1. 每次只改一个变量
2. 修复后重新运行 Phase 1 tight loop
3. 写回归测试
4. 清理：移除调试产物
```

#### 影响范围
- 涉及文件：新增 `skills/systematic-debugging/SKILL.md`
- 向后兼容：✅ 新增补充技能，不影响核心层
- 测试验证：遇到 bug 时加载 skill，验证四阶段流程

#### 风险与取舍
- 做：补充层获得系统性调试能力
- 不做：调试依赖开发者经验，可能跳过根因直接修复
- 替代：不新增 skill，在 code-review-checklist 中增加调试检查项（不充分）
- **注意：** 上述提案仅为骨架，实施时需补充 mattpocock 的 10 种反馈循环构建法（测试/Curl/CLI/浏览器/重放/临时工具/属性测试/二分/差分/HITL）和 REDACTED 输出要求，以及 Superpowers 的压力测试场景（紧急生产修复、沉没成本+疲劳、权威+社交压力）

---

### 5.3 [P1] 验证门控强化

**来源：** Superpowers `verification-before-completion`
**借鉴什么：** "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE" 铁律
**为什么需要：** `pdca-check` 已有核验框架（"没有证据不能编造'已验证'"），但可强化"证据先于断言"的纪律，并补充证据格式要求
**目标文件：** `skills/pdca-check/SKILL.md`

#### 当前状态

`skills/pdca-check/SKILL.md` 第 24 行已有"没有证据不能编造'已验证'；不能靠多个模型赞同提升为事实"，但缺少对证据格式的具体要求。

Superpowers `verification-before-completion/SKILL.md`（120 行）核心：
- 铁律："NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
- Gate Function：IDENTIFY→RUN→READ→VERIFY→ONLY THEN claim
- 常见失败表：每种声明需要什么证据，什么不够
- "跳过任何步骤 = 在撒谎，不是在验证"

#### 修改方案

**修改 1：** 在 `skills/pdca-check/SKILL.md` 第 24 行后追加证据格式要求：

原文（第 24 行）：
```
3. 追踪可疑路径和上游保护、源与投影的双向覆盖，区分确定违例、unknown和纯建议。没有证据不能编造"已验证"；不能靠多个模型赞同提升为事实。
```
替换为：
```
3. 追踪可疑路径和上游保护、源与投影的双向覆盖，区分确定违例、unknown和纯建议。没有证据不能编造"已验证"；不能靠多个模型赞同提升为事实。每个结论必须附带：(a) 执行了什么命令/检查，(b) 输出是什么，(c) 输出如何支持结论。不能用"应该通过"替代实际运行。跳过任何验证步骤 = 在撒谎，不是在验证。
```

#### 影响范围
- 涉及文件：`skills/pdca-check/SKILL.md`
- 向后兼容：✅ 强化已有规则，不改变流程
- 测试验证：在 Check 阶段验证是否要求附带证据

#### 风险与取舍
- 做：Check 结论更可靠，有明确的证据格式要求
- 不做：Check 可能出现无证据的断言
- 替代：无，这是核心质量改进

---

### 5.4 [P1] 计划文档禁止占位符

**来源：** Superpowers `writing-plans`
**借鉴什么：** 计划文档中禁止 TBD/TODO/占位符，每个步骤必须有实际内容
**为什么需要：** PDCA 的 plan 记录可能出现模糊描述，影响 Do 阶段执行
**目标文件：** `ontology/contracts/record-shapes/task.md`（plan 相关部分）

#### 当前状态

`ontology/contracts/record-shapes/task.md` 定义了任务记录形状，但未显式禁止占位符。

Superpowers `writing-plans/SKILL.md`（171 行）核心：
- "Write comprehensive implementation plans assuming the engineer has zero context"
- "每个任务步骤必须包含：具体操作、预期结果、验证方法"
- 禁止占位符、禁止"添加适当的错误处理"之类的模糊描述
- self-review 机制

#### 修改方案

**修改 1：** 在 `ontology/contracts/record-shapes/task.md` 的 plan 相关部分，增加占位符检查规则：

```markdown
## 计划质量约束

计划文档中禁止以下占位符模式：
- "TBD"、"TODO"、"之后实现"、"填写细节"
- "添加适当的错误处理" / "添加验证" / "处理边缘情况"
- "为上述编写测试"（没有实际测试代码）
- "类似于任务N"（重复引用）

每个任务步骤必须包含：具体操作、预期结果、验证方法。
缺失项必须在 Plan 完成前补齐，不进入 Do 阶段。
```

#### 影响范围
- 涉及文件：`ontology/contracts/record-shapes/task.md`
- 向后兼容：✅ 约束新 plan，不影响已有 plan
- 测试验证：检查已有 plan 记录是否符合新约束

#### 风险与取舍
- 做：Do 阶段执行者有更清晰的指令
- 不做：plan 质量依赖编写者自觉
- 替代：在 `pdca-plan` 的 SKILL.md 中增加检查步骤（更轻量）

---

### 5.5 [P2] 代码审查双轴评估

**来源：** mattpocock `code-review` + Superpowers `receiving-code-review`
**借鉴什么：** 双轴审查（标准轴 + 规格轴）+ 接收审查反馈的技术验证模式
**为什么需要：** PDCA 补充层的 `code-review-checklist` 是单轴（代码质量），缺少"代码是否实现了规格"的第二轴。mattpocock 的双轴审查和 Superpowers 的接收审查模式可补充。
**目标文件：** `skills/code-review-checklist/SKILL.md`

#### 当前状态

`skills/code-review-checklist/SKILL.md`（253 行）：
- 系统性审查清单，覆盖错误处理、边界条件、资源管理等
- 反合理化守卫（"代码很小不需要清单"等借口表）
- 5 语言特定检查项
- **缺少：** 规格符合性审查轴（代码是否实现了 issue/spec 要求）

mattpocock `code-review/SKILL.md`（6589 bytes）核心：
- 双轴并行子代理：Standards（代码质量）+ Spec（规格符合）
- Standards 轴：Smell Baseline（12 种 code smell：Mysterious Name、Duplicated Code、Feature Envy 等）
- Spec 轴：对照 issue/spec 逐项检查
- 两个轴独立报告，不合并

Superpowers `receiving-code-review/SKILL.md`（205 行）核心：
- 技术验证优先，不表演性同意
- "NEVER: 'You're absolutely right!' / 'Great point!'"
- 未明确的反馈→停止→询问→确认后再实施
- YAGNI 检查：审查者建议是否过度设计

#### 修改方案

**修改 1：** 在 `skills/code-review-checklist/SKILL.md` 的 Review Flow 中增加规格轴：

在现有 Review Flow 后追加：

```markdown
## 双轴审查（可选增强）

当有明确的 issue/spec/需求文档时，使用双轴审查：

### 轴 1：标准（已有）
即上方的 Review Flow + 检查清单。

### 轴 2：规格符合性
对照 issue/spec 逐项检查：
1. 获取 fixed point（commit SHA / branch / tag）
2. 识别 spec 来源（issue 引用、spec 文件、用户参数）
3. 逐项检查：代码是否实现了 spec 要求的每个行为
4. 报告：spec 要求了但代码没实现的 / 代码实现了但 spec 没要求的

两个轴独立报告，不合并评分。
```

#### 影响范围
- 涉及文件：`skills/code-review-checklist/SKILL.md`
- 向后兼容：✅ 可选增强，不改变现有流程
- 测试验证：在有 spec 的代码审查中使用双轴模式

#### 风险与取舍
- 做：审查更全面，覆盖"做对了"和"做好了"两个维度
- 不做：审查只覆盖代码质量，不检查规格符合性
- 替代：不修改 code-review-checklist，仅作为知识参考（不强制）

---

### 5.6 [P2] 技能描述精简（SDO 优化）

**来源：** Superpowers `writing-skills`（SDO - Skill Discovery Optimization）
**借鉴什么：** 技能描述应聚焦触发条件，不总结工作流；但保留必要的边界条件
**为什么需要：** PDCA 的 skill description 中部分功能描述可精简，但边界条件（如"不自动创建任务"）必须保留——它们是防止代理越权的关键规则
**目标文件：** `skills/*/SKILL.md`（所有 skill 的 YAML frontmatter）+ `skills/catalog.json`

#### 当前状态

逐条审查所有 9 个核心 description：

| Skill | 当前 description | 分析 |
|-------|-----------------|------|
| `pdca` | "用户显式选择 PDCA、绑定项目、查询状态或恢复已有任务时使用。定位集中 Git 工作副本与原会话，不自动创建任务或执行四阶段。" | ✅ 触发条件明确 + 边界条件"不自动创建任务"必须保留 |
| `pdca-assist` | "仅在用户显式调用 pdca-assist，为当前已绑定项目选择下一步工作建议时使用。普通请求不自动启用。" | ✅ 触发条件明确 + "不自动启用"是边界条件 |
| `pdca-plan` | "用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。与用户确认问题和目标，在原 Agent 内制定计划并等待 Do 授权。" | ⚠️ 后半句"与用户确认...等待 Do 授权"是工作流概述，可精简 |
| `pdca-do` | "用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。核对批准计划、集中资源和原会话，只实施当前 run，不自动 Check。" | ⚠️ "核对批准计划...不自动 Check"混合了工作流和边界条件 |
| `pdca-check` | "用户明确启动现有 PDCA 任务的 Check 时使用。核验固定产物、标准和证据，在原会话完成，不修改业务对象或自动返工。" | ⚠️ "核验固定产物...不自动返工"是边界条件，应保留 |
| `pdca-act` | "用户明确批准现有 PDCA 任务的 Act 处置时使用。按批准范围交付、归档或发布，记录资源结清后停止，不启动下一场景。" | ⚠️ "按批准范围...不启动下一场景"是边界条件，应保留 |
| `pdca-model` | "用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。定义领域模型与工作实例交付；不以知识地图冒充模型，不自动开始 Plan。" | ⚠️ "定义领域模型...交付"是工作流概述，可精简；"不以知识地图冒充模型"是边界条件 |
| `pdca-implement` | "用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。从固定模型产生目标产物和映射，不脱离模型或自动启动符合性验证。" | ⚠️ "从固定模型产生...映射"是工作流概述，可精简 |
| `pdca-verify` | "用户明确选择本体符合性验证，或该任务需要核验方法时使用。分别检查需求到模型、模型到投影、产物到行为，不把链接检查当语义证明。" | ⚠️ "分别检查...语义证明"是工作流概述，可精简 |

#### 修改方案

**原则：** 保留触发条件 + 边界条件（防越权规则），精简工作流概述（代理会在 SKILL.md 正文中看到）。

| Skill | 建议修改 |
|-------|---------|
| `pdca` | ✅ 无需修改 |
| `pdca-assist` | ✅ 无需修改 |
| `pdca-plan` | "用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。" |
| `pdca-do` | "用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。不自动 Check。" |
| `pdca-check` | "用户明确启动现有 PDCA 任务的 Check 时使用。不修改业务对象或自动返工。" |
| `pdca-act` | "用户明确批准现有 PDCA 任务的 Act 处置时使用。不启动下一场景。" |
| `pdca-model` | "用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。不以知识地图冒充模型。" |
| `pdca-implement` | "用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。不脱离模型。" |
| `pdca-verify` | "用户明确选择本体符合性验证，或该任务需要核验方法时使用。不把链接检查当语义证明。" |

#### 影响范围
- 涉及文件：`skills/*/SKILL.md`（9 个）、`skills/catalog.json`
- 向后兼容：✅ 只改描述，不改行为
- 测试验证：加载技能时验证 description 是否正确触发

#### 风险与取舍
- 做：description 更聚焦，代理不会跳过阅读 SKILL.md 正文
- 不做：description 过长可能误导代理走捷径
- 替代：保持现状——当前 description 已经包含有价值的边界条件

---

### 5.7 [P3] 会话交接格式

**来源：** mattpocock `handoff`
**借鉴什么：** 会话压缩为结构化交接文档，供另一个代理继续工作
**为什么需要：** PDCA 已有恢复入口+协作交接视角，但缺少标准化的交接文档格式
**目标文件：** 如需实施，`ontology/contracts/record-shapes/handoff.md`

#### 当前状态

PDCA 已有以下交接/恢复机制：

1. **共同恢复入口**（`ontology/contracts/entry-recovery.md`）：基于 Git HEAD + 任务绑定 + Agent 绑定的恢复机制
2. **pdca-assist 协作交接视角**（第 28 行）："标明接收对象与信息范围；发送消息/交接须明确授权，恢复任务仍回原 Agent"
3. **task 记录**：记录任务状态、阶段、尝试次数
4. **event 记录**：记录每次操作的输入/输出/决策

#### 评估结论

| 维度 | 现有机制覆盖 | 缺口 |
|------|-------------|------|
| 会话恢复 | ✅ 共同恢复入口 | — |
| 任务状态 | ✅ task 记录 | — |
| 决策记录 | ✅ event 记录 | — |
| 跨 Agent 交接 | ⚠️ pdca-assist 有协作交接视角 | 缺少标准化的交接文档格式 |
| 上下文压缩 | ❌ 无 | 会话过长时缺少压缩机制 |

**判断：** PDCA 的架构是"切换 Skill 不换 Agent"，跨 Agent 交接场景极少。新增 handoff 记录形状的 ROI 较低。但 mattpocock 的 handoff 有一个值得注意的设计：**保存到 OS 临时目录而非项目目录**，避免敏感信息泄露。

#### 修改方案（如需实施）

**修改 1：** 新建 `ontology/contracts/record-shapes/handoff.md`：

```markdown
# Handoff 记录形状

> 用于会话中断或代理切换时的上下文传递

## 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 关联任务 |
| `completed_items` | list | 已完成的工作项 |
| `pending_items` | list | 待完成的工作项 |
| `decisions_made` | list | 已做的决策（含理由） |
| `context_summary` | string | 上下文摘要（<500 字） |

## 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `blockers` | list | 阻塞项 |
| `next_agent_instructions` | string | 给下一个代理的指令 |
| `evidence` | list | 关键证据路径 |
```

#### 影响范围
- 涉及文件：新增 `ontology/contracts/record-shapes/handoff.md`（如实施）
- 向后兼容：✅ 新增形状，不影响已有
- 测试验证：创建一个 handoff 记录，验证格式正确

#### 风险与取舍
- 做：跨 Agent 交接时上下文更清晰
- 不做：依赖现有恢复机制，跨 Agent 场景极少
- 替代：扩展现有的 task 记录增加交接字段（更轻量）

---

### 5.8 [P3] 结构化回顾格式

**来源：** gstack `retro`
**借鉴什么：** 结构化的回顾输出格式（做得好/可改进/后续建议）
**为什么需要：** pdca-act 已有经验记录能力，但缺少标准化的回顾输出格式
**目标文件：** 如需实施，`skills/pdca-act/SKILL.md`

#### 当前状态

pdca-act SKILL.md 第 24 行："经验记录来源、版本、环境、反证、未验证范围和重评条件；没有新经验就说明没有，不把失败结论改为成功。"

**已有能力：** 经验记录（来源、版本、环境、反证、未验证范围、重评条件）
**缺少：** 结构化的回顾格式（做得好/可改进/后续建议）

**注意：** gstack 的 retro 是**跨项目**的周期性回顾（per-person breakdown、timeline、learnings），而 PDCA 的 Act 是**单任务**的收尾——场景不同。PDCA 不需要跨项目回顾机制。

#### 修改方案（如需实施）

**修改 1：** 在 `skills/pdca-act/SKILL.md` 第 24 行的经验记录中，补充可选的回顾格式：

原文：
```
3. 经验记录来源、版本、环境、反证、未验证范围和重评条件；没有新经验就说明没有，不把失败结论改为成功。
```
替换为：
```
3. 经验记录来源、版本、环境、反证、未验证范围和重评条件；没有新经验就说明没有，不把失败结论改为成功。用户要求回顾时，补充：(a) 本次做得好的（保留），(b) 可改进的（记录到 ontology/decision/），(c) 对后续任务的建议（写入 project-context.md）。
```

#### 影响范围
- 涉及文件：`skills/pdca-act/SKILL.md`
- 向后兼容：✅ 可选补充，不改变流程
- 测试验证：在 Act 阶段验证回顾格式是否生效

#### 风险与取舍
- 做：经验记录更结构化，便于后续任务引用
- 不做：经验记录保持自由格式，依赖编写者自觉
- 替代：保持现状——当前经验记录已覆盖核心需求

---

### 5.9 [P3] 记录文档 Diataxis 框架

**来源：** gstack `document-generate`（Diataxis 框架）
**借鉴什么：** 文档按四个象限组织：Reference / How-to / Tutorial / Explanation
**为什么需要：** PDCA 的 ontology 文档目前按概念/实体/过程组织，可借鉴 Diataxis 改善可发现性
**目标文件：** `ontology/README.md` 或 `ontology/INDEX.md`

#### 当前状态

PDCA 的 ontology 按概念类型组织（concept/ entity/ process/ principle/...），INDEX.md 提供索引。

#### 修改方案

**修改 1：** 在 `ontology/INDEX.md` 增加 Diataxis 视角的交叉索引：

```markdown
## 按使用方式索引（Diataxis 视角）

### Reference（参考）
- 记录形状：`contracts/record-shapes/`
- 概念定义：`concept/`
- 实体定义：`entity/`

### How-to（操作指南）
- 入口恢复：`contracts/entry-recovery.md`
- 流程方法：`process/flow-*.md`

### Tutorial（教程）
- 安装指南：`INSTALL.md`
- 使用说明：`README.md`

### Explanation（解释）
- 设计原则：`principle/`
- 已知陷阱：`pitfall/`
- 模式：`pattern/`
```

#### 影响范围
- 涉及文件：`ontology/INDEX.md`
- 向后兼容：✅ 只增加索引，不改内容
- 测试验证：检查索引是否正确引用

#### 风险与取舍
- 做：文档更易发现和使用
- 不做：维护两套索引
- 替代：保持现有组织方式，不增加复杂度

---

## 6. 不建议借鉴的项

| 项目 | 来源 | 不建议理由 | 如果强行做的后果 |
|------|------|-----------|----------------|
| **子代理驱动开发** | Superpowers | PDCA 核心层已有自己的 Agent 路由体系（切换 Skill 不换 Agent） | 架构冲突 |
| **Git Worktree** | Superpowers | PDCA 核心层已有集中 Git 工作副本 + 双根架构 | 重复 |
| **浏览器控制** | gstack | PDCA 是记录系统 | 完全不适用 |
| **安全审计（CSO）** | gstack | PDCA 补充层已有 secure-coding，核心层不直接审计代码 | 重复 |
| **多模型审查** | gstack | PDCA 不做独立代码审查，补充层 code-review-checklist 是清单参考 | 无实际价值 |
| **部署流程** | gstack | PDCA 不做部署 | 完全不适用 |
| **iOS 测试** | gstack | PDCA 不做移动端测试 | 完全不适用 |
| **设计变体生成** | gstack（design-shotgun） | PDCA 不做 UI 设计 | 完全不适用 |
| **Issue 状态机** | mattpocock（triage） | PDCA 核心层已有自己的任务生命周期 | 重复 |
| **原型制作** | mattpocock（prototype）/ gstack（design-html） | PDCA 不做原型 | 完全不适用 |
| **人类步骤向导** | mattpocock（wizard） | PDCA 不做基建/凭证/CI 配置 | 完全不适用 |
| **教学工作空间** | mattpocock（teach） | PDCA 不做教学 | 完全不适用 |
| **后台研究代理** | mattpocock（research） | PDCA 核心层不做研究，补充层无此场景 | 不适用 |
| **学习记忆** | gstack（learn + Operational Self-Improvement） | PDCA 已有 ontology/ 知识管理 + event 记录 | 机制不同，不直接适用 |
| **Question Tuning** | gstack | PDCA 核心层不收集用户偏好 | 不适用 |
| **遥测** | gstack（Telemetry） | PDCA 不做遥测 | 完全不适用 |
| **代码健康扫描** | mattpocock（improve-codebase-architecture） | PDCA 补充层无代码库架构扫描场景 | 不适用 |
| **深度模块设计** | mattpocock（codebase-design） | PDCA 有 pdca-model 本体建模，不面向代码模块设计 | 不适用 |

---

## 7. 外部文档质量评估（附录）

### 7.1 superpowers-analysis.md

| 维度 | 评价 |
|------|------|
| **结构** | ✅ 清晰，有目录和表格 |
| **准确性** | ⚠️ 对 Superpowers 技能描述基本准确 |
| **偏差** | ❌ 将 PDCA 理解为"代码开发框架"，所有借鉴点都假设 PDCA 写代码 |
| **遗漏** | ❌ 未分析 PDCA 的独有能力（双根、记录形状、资源预约等） |
| **实用性** | ⚠️ 借鉴点大部分不适用 |

### 7.2 superpowers-skills-deep-analysis.md

| 维度 | 评价 |
|------|------|
| **结构** | ✅ 详细，逐技能分析 |
| **准确性** | ✅ 对 Superpowers 9 个核心技能的描述准确 |
| **偏差** | ❌ 同上，假设 PDCA 是代码开发框架 |
| **遗漏** | ❌ 未考虑 PDCA 与 Superpowers 的定位差异 |
| **实用性** | ⚠️ 借鉴点需要大量改造才能适用 |

### 7.3 综合评价

两份外部分析文档对 Superpowers 本身的分析质量较高，但对 PDCA 的适用性分析有**系统性偏差**——它们都假设 PDCA 是一个代码开发框架，而实际上 PDCA 是一个工作流管理系统（核心层）+ 代码开发参考技能（补充层）的双层架构。本对比文档基于逐条读取所有四个框架的完整 skill 文件后重写，纠正了这些偏差。

---

## 8. 总结

### PDCA 的生态定位

PDCA 在 AI 编码技能生态中是一个**独特的双层存在**：
- **核心层**是工作流管理系统——聚焦于规则、记录、资源预约和阶段授权，其他三个方案完全没有这一层
- **补充层**是代码开发参考技能——覆盖提交规范、审查清单、测试策略、安全编码、构建配置、中文环境等，与外部方案在同一维度可比

### 核心结论

1. **PDCA 核心层的独有能力是其核心价值**：双根架构、31 种记录形状、资源预约、三场景分离、逐阶段授权——这些在其他方案中完全没有
2. **PDCA 补充层与外部方案在同一维度可比**：testing-strategy vs TDD、code-review-checklist vs code-review、secure-coding vs security audit
3. **补充层的真正缺口是 TDD 工作流和调试方法论**：testing-strategy 覆盖了"测什么"但缺"怎么测"；完全缺失调试 skill
4. **核心层的验证门控和计划质量值得强化**：从 Superpowers 借鉴铁律和反占位符规则
5. **mattpocock 的可组合设计哲学值得学习**：小 skill、显式阶段边界、主流程+接入路径的架构
6. **gstack 的角色化专家团队和共享基础设施模式**：AskUserQuestion 格式、Question Tuning、学习记录——但大部分不适用于 PDCA 的记录系统定位
7. **两份外部分析文档的价值有限**：对 Superpowers 分析准确，但对 PDCA 有系统性偏差

| P1 | TDD 工作流技能 | 补充层 | 中 | 高 | **新增**——testing-strategy 缺 RED→GREEN→REFACTOR 工作流 |
| P1 | 调试方法论技能 | 补充层 | 中 | 高 | **新增**——补充层完全缺失调试 skill |
| P1 | 验证门控强化 | 核心层 | 小 | 高 | 维持——在 pdca-check 上追加证据格式要求 |
| P1 | 计划文档禁止占位符 | 核心层 | 小 | 中 | 维持——pdca-plan 有质量约束但无显式占位符禁令 |
| P2 | 代码审查双轴评估 | 补充层 | 中 | 中 | **新增**——code-review-checklist 缺规格符合性轴 |
| P2 | 技能描述精简（SDO） | 核心层 | 小 | 低 | 维持——大部分 description 已聚焦触发条件+边界条件 |
| P3 | 会话交接格式 | 核心层 | 中 | 低 | 维持——PDCA 已有恢复入口+协作交接，缺口极小 |
| P3 | 结构化回顾格式 | 核心层 | 小 | 低 | 维持——pdca-act 已有经验记录，只缺格式模板 |
| P3 | 记录文档 Diataxis 框架 | 核心层 | 小 | 低 | 维持——纯文档组织优化 |

### 优先级排序（v3 — 自我审查后修订）

| 优先级 | 借鉴项 | 层 | 工作量 | 收益 | v3 修订说明 |
|--------|-------|---|--------|------|-----------|
| P1 | TDD 工作流技能 | 补充层 | 中 | 高 | 同 v2，提案需补充反合理化守卫和语言特定示例 |
| P1 | 调试方法论技能 | 补充层 | 中 | 高 | 同 v2，提案需补充 mattpocock 的 REDACTED 输出和 10 种反馈循环构建法 |
| P1 | 验证门控强化 | 核心层 | 小 | 高 | 同 v2 |
| P1 | 计划文档禁止占位符 | 核心层 | 小 | 中 | 同 v2 |
| P2 | 代码审查双轴评估 | 补充层 | 中 | 中 | 同 v2 |
| P2 | 技能描述精简（SDO） | 核心层 | 小 | 低 | 同 v2 |
| P3 | 会话交接格式 | 核心层 | 中 | 低 | 同 v2 |
| P3 | 结构化回顾格式 | 核心层 | 小 | 低 | 同 v2 |
| P3 | 记录文档 Diataxis 框架 | 核心层 | 小 | 低 | 同 v2 |

---

*文档生成时间：2026-09-16（v3 全面修订版）*
*分析工具：OpenCode + PDCA Skills*
*数据来源：全面探索四个项目完整结构 + 逐条读取所有 skill 文件*
- PDCA：17 个 skill（9 核心 + 8 补充）+ ontology/（573+ 文件）
- Superpowers：14 个 skill + 30+ 支撑文件（prompts、scripts、examples）
- mattpocock/skills：37 个 skill（18 工程 + 7 生产力 + 4 杂项 + 8 进行中）
- gstack：23+ skill + 8 tool + 11 iOS skill（核心工作流完整读取）
