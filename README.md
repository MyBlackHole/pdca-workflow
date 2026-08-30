# PDCA 工作流 — AI 驱动的项目执行协议

> **人类读者入口**。AI 代理请阅读 [`AGENTS.md`](AGENTS.md) 获取执行路由和门禁规则。

PDCA（Plan-Do-Check-Act）是一个**基于 AI 代理的全流程项目执行协议**。通过 `flows/` 分阶段流程定义 + `skills/` 可复用技能库，让 AI 有序推进任务。

## 快速开始

### 前置要求

- [opencode](https://opencode.ai) 或其他兼容 AI 工具
- `PDCA_HOME` 环境变量指向本项目

```bash
# ~/.zshrc
export PDCA_HOME=~/pdca-workflow
```

### 模式 A：独立使用（本项目即为工作区）

直接在本项目内使用。所有任务、记录、流程都在 `pdca-workflow` 仓库中。

```bash
cd pdca-workflow
opencode .
```

AI 自动读取 `AGENTS.md` 并遵循 PDCA 协议。无活跃任务时提示创建。

### 模式 B：外部项目 + 管理中心

在外部项目中编码，管理数据集中到 `pdca-workflow`。

```bash
# 1. 在外部项目初始化 PDCA 引用
bash $PDCA_HOME/scripts/init-external.sh ~/projects/my-app

# 2. 在外部项目中启动 opencode
cd ~/projects/my-app
export PDCA_HOME=~/pdca-workflow
opencode .
```

外部项目的 `AGENTS.md` 告诉 AI 通过 `$PDCA_HOME` 找到流程、技能和任务跟踪。所有管理数据写入 `$PDCA_HOME/pdca/tasks/` 和 `$PDCA_HOME/records/`。

## 任务生命周期

每个任务经历 4 个阶段，AI 自主按流程推进：

```
plan → do → check → act → archive
```

| 阶段 | 流程定义 | 产出 |
|------|---------|------|
| **Plan** | `flows/flow-plan/SKILL.md` | `task.json` + `prd.md`，用户确认后方可进入 Do |
| **Do** | `flows/flow-do/SKILL.md` | 代码/文档/调研报告，按场景类型选择执行路径 |
| **Check** | `flows/flow-check/SKILL.md` | `conclusion.md` + 证据清单，判定通过/失败 |
| **Act** | `flows/flow-act/SKILL.md` | 知识沉淀 + journal 日志 + 归档 |

AI 在完成任务阶段后自主更新 `task.json` 中的 `meta.phase`。

## 任务结构

```
pdca/tasks/<MMDD-slug>/
├── task.json           ← 任务元数据（ID、阶段、优先级等）
├── prd.md              ← 需求文档（Plan 阶段产出）
├── clarifications.jsonl ← Q&A 日志（Grill 过程中记录）
├── design.md           ← 设计方案（复杂任务）
└── implement.md        ← 实施计划（复杂任务）
```

## 技能系统

`skills/` 目录包含 30 个可复用技能，分为两类：

| 类型 | 加载方式 | 示例 |
|------|---------|------|
| **model-invoked** | AI 在流程中自主加载 | `advance-phase`、`register-evidence`、`grilling` |
| **user-invoked** | 仅用户显式请求 | `ask-matt`（入口路由）、`handoff`（交接）、`grill`（追问） |

完整技能清单见 [`SKILLS-INDEX.md`](SKILLS-INDEX.md)。

### 关键技能速查

| 技能 | 作用 |
|------|------|
| `ask-matt` | （推荐入口）描述你想做什么，AI 推荐入口和路径 |
| `triage` | 将模糊输入分类为 bug/feature，查重后创建任务 |
| `grill` | 对你进行 relentless 追问，理清需求边界 |
| `code-review` | 双轴审查（代码质量 + 需求对齐） |
| `write-journal` | 自动或手动写入每日工作日志 |

## 关键约定

### PDCA_HOME

所有路径引用以 `$PDCA_HOME` 为基路径。在两种模式下都要求设置。

### Plan→Do 门禁

Plan 阶段必须完成用户确认才能进入 Do。`advance-phase` 会在 `clarifications.jsonl` 中校验 `final_confirmation` 记录。

### 记录不可变

`records/<record-id>/` 下的文件为不可变实验记录，不允许修改。证据通过 `manifest.jsonl` 登记。

### 提交格式

```bash
git commit -m "task <id>: <描述>"
```

## 常见场景

| 场景 | `scenario_type` | 执行路径 |
|------|----------------|---------|
| 开发新功能 | `development` | 原型→编码→TDD→审查→证据 |
| 修复 Bug | `bugfix` | 诊断→修复→TDD→审查→证据 |
| 技术调研 | `research` | Research→报告→证据 |
| 编写文档 | `documentation` | 文档编写→审查→证据 |
| 架构设计 | `design` | 方案→评审→ADR→证据 |
| 代码审查 | `review` | 审查→报告→证据 |

## 外部项目 FAQ

### 权限问题

新 opencode 会话访问 `$PDCA_HOME` 可能触发权限门禁。配置全局允许：

```json
// ~/.config/opencode/opencode.json
"permission": { "external_directory": "allow" }
```

### 多项目管理

同一 `PDCA_HOME` 下可管理多个外部项目的任务，通过 `task.json` 中的 `external_project` 字段标识。

### 更新 PDCA

```bash
cd $PDCA_HOME && git pull
```

flows/ 和 skills/ 更新后立即可用，无需重新初始化。

## 目录结构

```
├── flows/           # 阶段流程（plan → do → check → act）
├── skills/          # 可复用技能库（30 个）
├── pdca/
│   ├── tasks/       # 任务跟踪（MMDD-slug/task.json + 产物）
│   │   └── archive/ # 归档任务
│   ├── journal/     # 每日工作日志
│   └── CONTEXT.md   # 共享术语表
├── records/         # 不可变实验记录
├── templates/       # 文档模板
└── ontology/           # 本体（知识 + 流程唯一权威：concept/ process/ entity/ domain/）
```