# PDCA 工作流 — 项目架构设计

## 1. 项目定位

PDCA（Plan-Do-Check-Act）是一个**基于 AI 代理的全流程项目执行协议**。它不是解决某个单一问题，而是用一个统一的协议体系，同时消除 AI 代理执行中六个维度的系统性缺陷。

### 1.1 六维缺陷与解决方案

#### 缺陷一：方向控制失灵

AI 在无约束对话中存在严重的**方向漂移**问题。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 需求理解偏差 | 用户说 A，AI 听到的是 A'，做着做成 B | grill 多轮追问直至 final_confirmation，在 clarifications.jsonl 中留下可达共识的证据 |
| 过度承诺 | AI 不管能不能做先答应，执行中失败 | triage 分诊阶段评估任务边界和可行性，不合适的路口直接挡回 |
| 目标丢失 | 长任务执行过程中逐步偏离原始目标 | Check 阶段对照 PRD 逐项核验，不满足则判定失败而非"部分完成" |
| 隐含假设 | 用户没说但 AI 自以为是的假设导致错误产出 | grill 显式追问边界条件，记录到 clarifications.jsonl |

**对应门禁：** Plan→Do 门禁（advance-phase 校验 clarifications.jsonl 中 source="final_confirmation"）

#### 缺陷二：执行路径混沌

AI 面对模糊任务时无法自主选择正确的执行路径。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 无标准流程 | bug 修复和 feature 开发走同一流程，边界模糊 | flow-do 按 scenario_type 路由到不同的执行路径（6 种场景） |
| 无执行顺序 | 不知道先做什么后做什么，随机试探 | flows/ 四阶段固定顺序：Plan→Do→Check→Act，不可打乱 |
| 无终止条件 | AI 永远在加功能，没有收敛判断 | Check 阶段的收敛条件（verify-convergence），明确"什么时候算做完" |
| 重复造轮 | 每个任务从零摸索，不调用已有经验 | skills/ 提供 37 个可复用技能，flow-plan 2a 检索历史知识 |

**对应组件：** flows/ 四阶段流程 + flow-do 场景路由 + skills/ 技能库

#### 缺陷三：质量不可信

AI 的"做完了"缺乏客观标准。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 无产出标准 | AI 说做完了但不知道"完"的标准是什么 | prd.md 明确定义验收条件 |
| 无检验环节 | 缺少对照原始需求的逐项核验 | check 阶段：对照 PRD + 证据 → conclusion.md，通过/失败明确判定 |
| 无证据链 | 做没做过全靠 AI 一句话 | register-evidence 登记每项产出到 evidence/manifest.jsonl |
| 无代码质量把关 | AI 写出 bug 不自知 | code-review 技能双轴审查（代码质量 + 需求对齐） |

**对应门禁：** flow-check 收敛检验 + register-evidence 证据登记

#### 缺陷四：记忆归零

这是 AI 代理最突出的结构化缺陷——**跨会话完全失忆**。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 跨会话失忆 | 上周修过的 bug，这周换个 session 又犯了 | records/ 不可变记录，knowledge/ 可复用知识，跨会话持久化 |
| 经验不传承 | T0100 发现的最佳实践，T0101 完全不知道 | 知识沉淀管线：Evidence→Experience→Knowledge→Skill |
| 知识不生长 | AI 不会从经验中抽象出可复用的模式 | flow-act 步骤 2：从经验提炼知识，从稳定知识创建 skill |
| 无从检索 | 即使有知识，AI 也找不到 | knowledge/manifest.jsonl 全文索引 + pdca/CONTEXT.md 术语统一 |

**对应组件：** knowledge/ + records/ + flow-act 知识处置

#### 缺陷五：黑箱执行

AI 决策过程完全不透明。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 不可审计 | AI 做了什么、为什么这么做、结果如何——一团黑 | task.json 记录完整阶段流转 + records/ 不可变追踪 |
| 不可解释 | 决策过程不透明，出错无法定位根因 | clarifications.jsonl 记录需求对齐过程 + prd.md 记录方案 + 证据链 |
| 不可回滚 | 做错了没有恢复路径 | rollback-phase.sh 阶段回滚脚本 + advance-phase 快照机制 |
| 无进展感知 | 不知道任务到哪一步了 | task.json meta.phase 字段 + journal 每日日志 |

**对应组件：** task.json 阶段跟踪 + rollback-phase.sh + write-journal

#### 缺陷六：多项目混乱

AI 同时服务多个项目时的数据隔离问题。

| 具体问题 | 表现 | PDCA 方案 |
|----------|------|-----------|
| 项目混杂 | 项目 A 的任务和项目 B 的任务混在一起 | external_project 字段标识 + init-external.sh 解耦 |
| 知识隔离 | 一个项目学到的经验其他项目不知道 | 共享 $PDCA_HOME 的知识库，跨项目可检索 |
| 权限混淆 | 外部项目访问 PDCA 资源无控制 | permission.external_directory 配置 + template 强制规则 |
| 环境依赖 | 每个新项目都需要配置 PDCA | init-external.sh 一键初始化 AGENTS.md |

**对应组件：** init-external.sh + external_project 字段 + 权限配置

### 1.2 核心收益

| 收益 | 对应缺陷 | 实现方式 |
|------|---------|---------|
| **方向可控** | 缺陷一 | grill + final_confirmation 门禁 + Check 核验 |
| **路径有序** | 缺陷二 | flows/ 四阶段 + scenario_type 场景路由 |
| **质量可信** | 缺陷三 | 证据登记 + Check 收敛检验 + code-review |
| **经验传承** | 缺陷四 | Evidence→Experience→Knowledge→Skill 沉淀管线 |
| **全程透明** | 缺陷五 | 不可变记录 + 阶段跟踪 + 回滚能力 |
| **多项目解耦** | 缺陷六 | 外部项目模式 + 集中管理 |

PDCA 不是解决其中一个问题——它的价值在于**用一套协议同时解决这六个维度的系统性缺陷**。每个门禁、每个阶段、每种产物，都对应至少一个具体缺陷。去掉任何一个维度，AI 执行协议都是不完整的。

---

## 2. 系统架构

### 2.1 五层结构

```
┌──────────────────────────────────────────────────────────┐
│                     用户交互层                            │
│   ask-matt → triage → grill（需求对齐）                   │
│   入口路由    任务分诊    追问确认                        │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                     执行引擎层                            │
│                                                          │
│   Plan ──→ Do ──→ Check ──→ Act ──→ archive             │
│    │         │         │         │                        │
│    │   按场景路由       │         │                        │
│    │   ├─ development  │         │                        │
│    │   ├─ bugfix      │         │                        │
│    │   ├─ research    │         │                        │
│    │   ├─ documentation│        │                        │
│    │   ├─ design      │         │                        │
│    │   └─ review      │         │                        │
│    │                  │         │                         │
│    └── [Plan→Do] ─────┘         │                         │
│         final_confirmation      │                          │
│              └──────────────────┴── [收敛检验] ──┘       │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                     技能指令层                            │
│                                                          │
│   model-invoked（AI 自主加载）                            │
│   ├─ advance-phase       阶段推进门禁                     │
│   ├─ register-evidence   证据登记                         │
│   ├─ grilling            追问执行                         │
│   ├─ write-conclusion    结论撰写                         │
│   ├─ write-journal       日志写入                         │
│   └─ verify-convergence  收敛检验                         │
│                                                          │
│   user-invoked（用户请求触发）                             │
│   ├─ ask-matt           入口路由                          │
│   ├─ triage             任务分诊                          │
│   ├─ grill              追问对齐                          │
│   ├─ code-review        代码审查                          │
│   ├─ handoff            会话交接                          │
│   ├─ to-tickets         任务拆解                          │
│   └─ ...（37 个技能）                                      │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                     数据存储层                            │
│                                                          │
│   pdca/tasks/         活跃任务（task.json + prd + 产物）  │
│   pdca/tasks/archive/ 归档任务                            │
│   records/            不可变记录（conclusion + 证据）     │
│   knowledge/          可复用知识（按域分层）              │
│   pdca/journal/       每日工作日志                        │
│   docs/adr/           架构决策记录                        │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                     合约层                                │
│                                                          │
│   AGENTS.md           AI 执行入口合约                     │
│   pdca/CONTEXT.md     共享术语表                          │
│   templates/*         文档模板                            │
│   scripts/*           工具脚本                            │
│   （init-external.sh / validate-gate.sh /                │
│    rollback-phase.sh）                                   │
└──────────────────────────────────────────────────────────┘
```

### 2.2 职责说明

| 层 | 职责 | 主要对应缺陷 | 关键约束 |
|----|------|-------------|---------|
| **用户交互层** | 需求入口、任务创建、需求对齐 | 缺陷一（方向控制）、缺陷二（执行路径） | 必须先经过 triage + grill 才能进入 Plan |
| **执行引擎层** | 4 阶段有序推进，场景路由 | 缺陷二（执行路径）、缺陷三（质量可信） | 必须通过 final_confirmation 门禁才能 Plan→Do |
| **技能指令层** | 提供可复用的执行指令模块 | 缺陷四（记忆归零）、缺陷五（黑箱执行） | flow skill 不可修改，agent skill 可按需创建 |
| **数据存储层** | 任务/记录/知识/日志的持久化 | 缺陷四（记忆归零）、缺陷五（黑箱执行） | records/ 不可变；新增资产需更新 manifest.jsonl |
| **合约层** | AI 行为契约和工具支持 | 全部六维度 | AGENTS.md 是 AI 唯一入口 |

---

## 3. 核心数据流

### 3.1 单次任务生命周期

```
User: "做 X"
  │
  ▼
[ask-matt 入口路由]
  判断任务类型 → 路由到 triage
  │
  ▼
[triage 分诊]
  分类（bug/feature/research...）→ 查重 → 创建 task.json（phase: plan）
  │
  ▼
[grill 追问 + grilling 执行]
  逐轮需求对齐 → 记录到 clarifications.jsonl
  循环直到用户确认（final_confirmation）
  │
  ▼
[Plan 阶段]
  输出：prd.md（需求文档）
  如复杂任务：design.md（设计方案）
  │
  ▼
═══ [Plan→Do 门禁] ═══
  advance-phase 校验 clarifications.jsonl 中
  是否存在 source="final_confirmation" 记录
  通过 → 进入 Do；不通过 → 返回 grilling
  │
  ▼
[Do 阶段]
  按 task.json meta.scenario_type 选择执行路径：
  ├─ development → 原型 → 编码 → TDD → 审查
  ├─ bugfix     → 诊断 → 修复 → TDD → 审查
  ├─ research   → 调研 → 报告
  ├─ documentation→ 写作 → 审查
  ├─ design     → 方案 → 评审 → ADR
  └─ review     → 审查 → 报告
  产出：register-evidence 登记证据 → evidence/manifest.jsonl
  │
  ▼
[Check 阶段]
  对照 PRD + 证据清单 → 逐项核验
  产出：conclusion.md（通过/失败 + 收敛条件判定）
  │
  ▼
[Act 阶段]
  1. 知识处置（经验→knowledge，稳定知识→skill）
  2. write-journal（每日工作日志）
  3. 更新 task.json meta.disposition
  │
  ▼
═══ [Archive 门禁] ═══
  validate-gate.sh 校验：
  ├─ 所有阶段完成 + 结论确认
  ├─ 证据完整
  └─ disposition 完成
  通过 → 移入 pdca/tasks/archive/
```

### 3.2 知识沉淀管线

```
原始事实（事实/数据）
  │
  ▼
Evidence（证据登记）—— manifest.jsonl
  │  register-evidence 技能
  ▼
Experience（单次经验）—— records/ 中的结论
  │  写入 conclusion.md
  ▼
Knowledge（可复用知识）—— knowledge/ 下的 .md
  │  由 flow-act 步骤 2 提炼
  ▼
Skill（可复用指令模块）—— skills/ 下的 SKILL.md
  │  由 writing-skills 技能创建
  ▼
所有新资产 → 同步更新 manifest.jsonl
```

---

## 4. 组件详解

### 4.1 执行引擎——flows/

| 流程 | 文件 | 阶段产出 |
|------|------|---------|
| flow-plan | `flows/flow-plan/SKILL.md` | task.json + prd.md + clarifications.jsonl |
| flow-do | `flows/flow-do/SKILL.md` | 代码/文档/报告 + evidence/manifest.jsonl |
| flow-check | `flows/flow-check/SKILL.md` | conclusion.md |
| flow-act | `flows/flow-act/SKILL.md` | journal + 归档 |

流程文件**不可修改**，是整个协议的核心标准。

### 4.2 技能系统——skills/

两类技能。区分方式通过 skill 自身的 `frontmatter` 元数据声明：

```yaml
# model-invoked skill 示例
---
schema: pdca.asset/v1
layer: skill
invoke: model           # ← 声明 AI 自主加载
phases: [plan]          # ← 在 plan 阶段触发
triggers: [grilling]    # ← 当 grilling 动作发生时
---
```

```yaml
# user-invoked skill 示例
---
schema: pdca.asset/v1
layer: skill
invoke: user            # ← 声明需用户请求
---
```

**model-invoked 技能**在 `phases` + `triggers` 条件满足时由 flow 流程自动加载，用户无感知。**user-invoked 技能**仅在用户显式调用 skill 工具或口头请求时加载。

**model-invoked（AI 自主加载）**：AI 在执行流程中按需加载，用户无感知。

| 技能 | 触发时机 |
|------|---------|
| advance-phase | 阶段推进时，校验门禁并更新 phase 字段 |
| register-evidence | Do/Check 阶段需证明有产出时 |
| grilling | Plan 阶段执行 grill 追问时 |
| write-conclusion | Check 阶段撰写结论时 |
| verify-convergence | Check 阶段判定收敛条件 |
| write-journal | Act 阶段写入日志 |

**user-invoked（用户请求触发）**：需要用户显式发起。

| 技能 | 作用 |
|------|------|
| ask-matt | 入口路由，判断任务类型推荐路径 |
| triage | 任务分诊，分类 + 查重 |
| grill | 对用户进行追问对齐需求 |
| code-review | 双轴审查（代码质量 + 需求对齐） |
| handoff | 跨会话交接 |
| to-tickets | 任务拆解 |
| wayfinder | 导航，判断当前阶段和下一步 |
| verify-convergence | 收敛条件检验（也属 model-invoked） |
| writing-great-skills | 创建新 skill 的最佳实践 |
| brainstorming | 创意探索 → 设计方案 |
| ... 37 个技能 | 持续增长 |

### 4.3 数据存储

**任务目录（pdca/tasks/）：**
```
pdca/tasks/<MMDD-slug>/
├── task.json              ← 元数据（ID / 阶段 / 场景类型）
├── prd.md                 ← 需求文档
├── clarifications.jsonl   ← Q&A 日志
├── design.md              ← 设计方案（复杂任务）
├── implement.md           ← 实施计划（复杂任务）
├── implement.jsonl        ← 实施日志
├── check.jsonl            ← 检验日志
└── triager-brief.md       ← 分诊摘要
```

**不可变记录（records/）：**
```
records/<record-id>/
├── conclusion.md          ← 结论
├── handoff.md             ← 交接文档
├── evidence/
│   ├── manifest.jsonl     ← 证据清单
│   └── ...                ← 证据文件
```

### 4.4 合约层

| 文件 | 角色 | 关键内容 |
|------|------|---------|
| AGENTS.md | AI 执行合约 | PDCA 入口路由、阶段门禁、技能索引 |
| pdca/CONTEXT.md | 共享术语表 | 跨任务术语一致性，由 domain-modeling 维护 |
| templates/PDCA_HOME.md | 外部项目模板 | 外部项目 AGENTS.md 模板，包含强制规则 |
| scripts/init-external.sh | 外部项目初始化 | 为外部项目生成 AGENTS.md |
| scripts/validate-gate.sh | 归档门禁校验 | 验证任务完整性后方可归档 |

---

## 5. 外部项目模式（模式 B）

### 5.1 架构

```
~/.zshrc:
  export PDCA_HOME=~/pdca-workflow

~/.config/opencode/opencode.json:
  "permission": { "external_directory": "allow" }

~/projects/my-app/          ← 外部项目（代码工作区）
├── AGENTS.md               ← init-external.sh 生成，引用 $PDCA_HOME
└── src/                    ← 业务代码

$PDCA_HOME/                 ← 管理中心（本仓库）
├── pdca/tasks/             ← 任务跟踪
├── records/                ← 不可变记录
├── knowledge/              ← 知识沉淀
└── flows/ + skills/        ← 流程协议 + 技能库
```

### 5.2 数据流向

```
外部项目 AGENTS.md
  │ 引用 $PDCA_HOME
  ▼
AI 读取 $PDCA_HOME/AGENTS.md（权威入口）
  │
  ▼
执行 PDCA 流程 → 任务、记录写入 $PDCA_HOME/pdca/tasks/
  │                     和 $PDCA_HOME/records/
  ▼
代码写入外部项目自身目录
  │
  ▼
知识沉淀写入 $PDCA_HOME/knowledge/
```

---

## 6. 架构决策原则

| 原则 | 说明 |
|------|------|
| **Flow skill 不可修改** | 标准流程写入 flows/，不可自定义；业务逻辑写入 agent skill |
| **Asset 分层提升** | 原始数据→Evidence→Experience→Knowledge→Skill，逐级提炼 |
| **门禁保护** | Plan→Do 门禁（final_confirmation）和 Archive 门禁（validate-gate） |
| **记录不可变** | records/ 下的文件创建后不可修改 |
| **ADR 只记录跨任务决策** | 单任务决策写入任务文档，跨任务决策写入 ADR |
| **YAGNI** | 不提前引入不需要的复杂性 |

---

## 7. 未来演进方向

- **场景类型扩展**：增加 devops、security-audit、performance-optimization 等新场景，flow-do 自动路由
- **Skill 质量评分与推荐**：根据历史成功率、执行耗时、用户反馈为 skill 打分，新任务推荐最优 skill
- **Skill 市场**：跨项目/跨组织共享技能，版本管理和依赖声明
- **跨 AI 平台适配**：从 opencode 扩展到 Claude Code、Codex CLI、Cursor 等平台，统一 PDCA 协议层
- **跨任务依赖管理**：任务 A 依赖于任务 B 的产出，自动检测并阻止乱序执行
- **Records 统计看板**：可视化项目健康度——任务吞吐量、阶段耗时分布、收敛率、回归率
- **自动知识提炼**：从多条相似记录中自动提取 Knowledge 资产，减少人工干预
- **多 Agent 协作**：同一任务拆分为多个子 Agent 并行执行，父 Agent 协调收敛
