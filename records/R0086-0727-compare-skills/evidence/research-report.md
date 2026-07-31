# mattpocock/skills 对比分析报告

## 调研方法
审查 mattpocock/skills 仓库的全部 15+ 个核心技能文件，逐项对比其设计理念与本 PDCA 工作流。

---

## 1. 核心设计差异

| 维度 | mattpocock/skills | 本 PDCA 工作流 |
|------|------------------|----------------|
| **哲学** | 小而可组合的技能单元 | 全生命周期流程（PDCA 四阶段） |
| **技能粒度** | 极细。`grill-me` = 3 行，`implement` = 6 行 | 较粗。一个技能文件涵盖所有细节 |
| **调用方式** | 用户 `/command` 手动触发 | 流程自动编排（AI 自主推进阶段） |
| **组合方式** | 技能互相调用（`grill-me`→`grilling`，`implement`→`tdd`→`code-review`） | 流程文件内联步骤（flow-plan 包含所有子步骤） |
| **上下文负载** | 低。user-invoked 零负载 | 高。flow 文件每次都要完整加载 |
| **元技能** | `writing-great-skills` 保证质量 | 无 |

## 2. 可借鉴的优点

### 2.1 技能极简原则

Matt 的 `grill-me` 全文只有 3 行（不算 YAML）：

```yaml
---
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
---
Run a `/grilling` session.
```

核心逻辑全部委托给 `grilling`（model-invoked）。模式：**user-invoked = 薄壳**，只负责描述和委托；**model-invoked = 逻辑体**，包含真正步骤。

对比我们的 `skills/grill/SKILL.md`（60 行）：既描述自身又被流程引用，同时承担了"用户调用"和"流程执行"两种角色，职责不清晰。

### 2.2 技能组合优于流程嵌入

Matt 没有 flow 文件。技能之间通过名字互相调用：
- `implement` → 调 `tdd` + `code-review`
- `to-spec` → 调 issue tracker 写入
- `wayfinder` → 调 `grilling` + `domain-modeling`

我们相反：flow-plan/do/check/act 把所有内容硬编码在流程里。比如 flow-do 的"原型→编码→TDD→审查→证据→提交"全写在 197 行里，而不是拆成可独立重用的技能调用。

### 2.3 writing-great-skills（元技能）

Matt 有一个 `writing-great-skills` 技能，定义了：
- 信息层级（in-skill step → reference → external reference）
- 渐进披露原则
- 过早完成的防御
- 无操作（no-op）/ 否定（negation）/ 重复（duplication）的识别

这保证了整个仓库的技能质量。我们没有这等质量守门人。

### 2.4 ask-matt（路由器）

Matt 有一个 `ask-matt` 技能，用户输入模糊问题时路由器决定调用哪个技能。我们缺少类似入口——用户需要知道 `/triage`、`/grill-me`、`/wayfinder` 等确切名字。

### 2.5 用户/模型双通道分离

Matt 明确区分两种技能：
- **user-invoked**（`disable-model-invocation: true`）：用户手动触发，零上下文负载
- **model-invoked**（无标记）：AI 自动触发，需考虑上下文负载成本

我们的 `disable-model-invocation` 标记只用于 grill/domain-modeling/triage/wayfinder，但 flow-plan 又让 AI 自动加载它们（矛盾已修复过一次）。这个区分还可以做得更彻底。

## 3. 本流程的独特优势

| 特性 | mattpocock/skills | 本 PDCA 工作流 |
|------|------------------|----------------|
| **PDCA 生命周期** | 无 | ✅ 完整的四阶段循环 |
| **不可变实验记录** | 无（靠 issue tracker 记录） | ✅ `records/<record-id>/` + manifest |
| **结论+判定** | 无 | ✅ verdict (confirmed/rejected/partial) + disposition |
| **知识沉淀** | 隐式（靠 `CONTEXT.md` + ADR） | ✅ 显式 `knowledge/<topic>/` |
| **场景类型** | issue tracker 标签隐式区分 | ✅ 6 种 `scenario_type` 显式标记 |
| **跨会话桥接** | 无（仅 `handoff` 技能） | ✅ handoff.md + 归档机制 |
| **任务跟踪** | 依赖外部 issue tracker | ✅ 本地 `task.json` + phase 状态机 |

**核心差异**：mattpocock/skills 是**技能集合**，本 PDCA 是**流程引擎**。他的目标是"在任何代码库中即装即用"，我们的目标是"管理从问题到知识的完整闭环"。

## 4. 优化建议（按优先级）

### 🔴 P0：提取可复用循环为独立技能

当前问题：flow-do/SKILL.md 的 6 条路径里都内联写了"登记证据"步骤，flow-check 也内联写了"回顾实验"步骤——这些应该在 skills/ 下独立存在，各流程引用而不是复制。

**方案**：将重复出现的子流程提取为 model-invoked 技能：
- `skills/register-evidence/SKILL.md`（登记证据）
- `skills/verify-convergence/SKILL.md`（验证收敛条件）
- `skills/write-conclusion/SKILL.md`（写结论文档）

### 🔴 P0：创建 ask-matt 路由器

用户首次进入项目时不知道应该输入什么。需要一个路由器技能：

```yaml
name: ask-matt
description: 根据用户描述，推荐合适的技能或流程入口。
disable-model-invocation: true
```

### 🟡 P1：极简化 user-invoked 技能

`skills/triage/SKILL.md`（121 行）、`skills/wayfinder/SKILL.md`（很长的技能）的流程细节可以委托给 model-invoked 子技能，保持顶层技能足够薄。

### 🟡 P1：创建 writing-great-skills 元技能

定义 PDCA 工作流的技能编写规范，包括：
- 信息层级（继承自 Matt 的三层模型）
- 渐进披露原则
- 过早完成的识别和防御
- 每行必须通过"必要性测试"

### 🟢 P2：flow 文件引用技能而非内联步骤

flow-do 的"登记证据"改为调用 `skills/register-evidence/SKILL.md`，而不是内联全文。

### 🟢 P2：引入 legwork / 过早完成 术语

在流程中明确使用这些概念：步骤的完成标准要"可检查"，明确禁止"跳过 legwork 直接收工"。

## 5. 总结

| 方面 | 谁更强 | 原因 |
|------|--------|------|
| 技能简洁度 | **mattpocock** | 极简+委托+渐进披露 |
| 质量保障体系 | **mattpocock** | 有元技能规范 |
| 生命周期完整性 | **本 PDCA** | Plan→Do→Check→Act 四阶段 |
| 可追溯性 | **本 PDCA** | 不可变记录+证据清单+判定 |
| 场景适配 | **本 PDCA** | 6 种场景类型 |
| 学习成本 | **mattpocock** | 更少的概念和文件 |
| 流程自动化 | **本 PDCA** | AI 自主推进阶段流转 |

**建议**：保留 PDCA 四阶段和记录体系的核心骨架，用 Matt 的技能极简原则重构 skills/ 目录下的技能文件，实现"流程稳重、技能轻巧"的最佳组合。