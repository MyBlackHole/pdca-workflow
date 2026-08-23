# 深度分析 skills 项目如何提升 AI 能力 — PRD

## 问题陈述

用户需要系统性理解 `/home/black/Documents/skills`（Matt Pocock Skills For Real Engineers）项目通过何种机制提升 AI（Claude Code / Codex 等编码代理）的工程能力，以便判断其设计思想对 `pdca-workflow` 的可复用价值。

当前缺乏：
- 对该项目全量 skill 清单、分类、调用关系的量化扫描
- 对“失效模式 → 修复技能”映射的原理级解释
- 对核心技能内部机制（输入/处理/输出）及对 AI 具体提升点的拆解
- 对整体工作流编排的端到端推演
- 可迁移到通用 AI 提效的抽象原则

## 目标

产出一份深度研究报告 `records/T0370-0823-skills-ai-enhancement/report.md`，达到可直接作为决策依据的质量：事实可验证、引用到文件行号、含流程图、含可落地建议。

## 用户故事

1. 作为 PDCA 工作流维护者，我希望看到 skills 项目的全量清单与分类，以便快速对标自身 skills 缺口
2. 作为 AI 代理使用者，我希望理解每个核心 skill 解决了什么失效模式，以便按需选用
3. 作为架构师，我希望看到 idea→ship 主流程的端到端推演，以便复用其流程编排思想
4. 作为团队负责人，我希望获得 5 条以上可迁移原则及在 pdca-workflow 的落地建议，以便制定改进路线图

## 方案

采用 `research` 场景路径（flow-do Path C）：
- C1 调研：全量扫描 skills 目录、阅读关键 SKILL.md、docs、agents 配置、CHANGELOG、README 四大失效模式章节
- C2 综合：按“失效模式→技能→机制→提升点→证据”结构撰写报告，含 Mermaid 图、表格、引用

不涉及代码实现，不产生测试接缝。

## 验收标准

- [ ] AC-1: 报告包含全量 skill 清单表（按 engineering/productivity/misc/in-progress/deprecated 分类，含数量统计与调用关系），数据与 `skills/` 目录实际文件一致
- [ ] AC-2: 报告完整阐述 4 大失效模式（对齐失败/冗长/不可用/泥球化）与对应 skill 的映射，每项有原文引用与文件行号
- [ ] AC-3: 报告对 ≥8 个核心技能（grilling、grill-with-docs、domain-modeling、codebase-design、tdd、code-review、diagnosing-bugs、research、prototype、wayfinder、to-spec、to-tickets、implement、triage 等中至少 8 个）进行机制拆解（输入-处理-输出-对AI提升点）
- [ ] AC-4: 报告包含 idea→ship 主流程及双 on-ramp 的 Mermaid 流程图，并配文字推演
- [ ] AC-5: 报告提炼 ≥5 条可迁移原则，并每条给出在 pdca-workflow 的具体落地建议
- [ ] AC-6: 报告已写入 `records/T0370-0823-skills-ai-enhancement/report.md` 并通过 `register-evidence` 完成证据登记，证据可在 `evidence.jsonl` 中检索到

## 范围外

- 不修改 skills 项目或 pdca-workflow 的任何代码
- 不执行 skills 的真实安装与运行验证（仅静态分析）
- 不产出可执行脚本或测试用例（纯研究报告）

## 备注

- 权威来源：`skills/` 下各 SKILL.md、`README.md` 四大失效模式章节、`docs/engineering/*.md`、`.agents/*.md`、`CLAUDE.md`、`CONTEXT.md`
- 引用规范：涉及具体 skill 机制时标注 `file_path:line_number`
- 内容预算：报告 UTF-8 控制在 30KB 以内，必要时豁免需记录
