---
schema: pdca.asset/v1
id: T0370-0823-skills-ai-enhancement
phase: check
source_ids: [report-v3, evidence-manifest, convergence-map-v4]
---

## 上下文

任务源于用户请求"深度分析 /home/black/Documents/skills 项目是如何提升 ai 的"。采用 research 场景静态分析：全量扫描 36 个 SKILL.md、README 四大失效模式章节、docs/ 人工文档、.agents/ 创作约定与 CHANGELOG 演化记录，产出研究报告 `records/T0370-0823-skills-ai-enhancement/report.md`（经用户两轮反馈细化：v1 28.8KB → v3 终稿，含 23 个拆解条目、量化画像、支撑文件生态、grounding 写作套件、ts 深模块 lint 化、技能级对照表）

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 该项目存在系统性的 AI 提效设计而非零散提示词 | 成立：四大失效模式（README.md:88-172）驱动技能矩阵设计 |
| H2 核心机制可拆解为可复用原则 | 成立：归纳出 8 条横向机制、7 条可迁移原则 |
| H3 分析结论可迁移到 pdca-workflow | 部分验证：给出 7 条落地建议，实际效果需后续任务实施后判定 |

## 分析（逐 AC 判定）

- **AC-1 全量清单** ✅ 报告 §1：5 分类计数表 + ASCII 调用关系图 + 双轨触发模型 + 量化画像（user/model-invoked 21/15、bytes 分布 Top10）+ repo 级指令层分析。数字经 `find skills -name SKILL.md` 实测。
- **AC-2 失效模式映射** ✅ 报告 §2：4 大模式各含原文引用（README.md:94/111-113/148/170）与修复技能及行号级机制说明。
- **AC-3 核心技能拆解** ✅ 报告 §3：23 个条目（19 技能详拆 + 支撑文件生态 + 写作三件套 grounding + ts-deep-modules lint 化），远超 PRD 要求的 8 个。
- **AC-4 主流程推演** ✅ 报告 §4：Mermaid 流程图覆盖主流程/双 on-ramp/vocabulary 底层/原型支线，配 7 步文字推演与 smart zone 上下文卫生说明。
- **AC-5 可迁移原则** ✅ 报告 §6：9 条原则 + 附A技能级对照表（16 能力域逐项差距/动作）+ 附B结构性差异观察。
- **AC-6 证据登记** ✅ `evidence/manifest.jsonl` 含 report-all（映射 AC-1~5）、evidence-manifest（AC-6）、convergence-map-v2；`validate-convergence.py` 返回 valid: true。

## 结论可靠性自查

调研方法充分性、来源遗漏（GitHub issues 未直接抓取原文，已经 docs 页间接引用并在报告标注）、替代解释三项均已 grill 并记录于 clarifications.jsonl round 2。

## 适用边界

- 结论基于 v1.2.3 快照的静态分析；该项目活跃迭代（CHANGELOG 密集），具体技能细节可能随版本演化。
- "对 AI 的提升点"为机制层推理 + 作者自述证据，未做受控 A/B 实测量化——任何量化声明需另行实验任务。
- 落地建议的效果取决于 pdca-workflow 后续实施质量，本报告不构成验收承诺。

## 下一轮建议

1. P3（research 场景补可验证信号要求）与 P6（prototype-branch 证据类型）建议优先落地为 Improvement Task。
2. 若需深化，可创建 follow-up 任务直接抓取 GitHub issues #449/#458/#95 原文，补充"参考型技能误用"主题的一手事故样本。
