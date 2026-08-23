# 历史任务审查与自我提升 — PRD

## 问题陈述

PDCA 体系已积累大量历史任务（活跃目录 57 个、归档数百个），但从未系统审查过：
1. 流程机制执行质量——门禁、证据链、conclusion 覆盖率的真实水位
2. AI 执行者的操作性失误模式——近期任务中已观察到多起门禁拒绝（手写时间戳、字段格式错误等）
3. 可沉淀的自我提升点未被结构化收集

## 目标

产出审查报告 `records/T0374-0823-history-review-self-improve/review-report.md`：
全量扫描量化 + 抽样审读 + AI 自身失误清单，每项失误给出防再发措施。

## 方案（review 场景 F1-F3）

- F1 双轴审查适配：标准轴 = 本仓库 AGENTS.md 门禁规则 + task.schema.json；规范轴 = 各任务自身 PRD 验收承诺
- 全量扫描脚本化：phase 分布、schema 合规分代统计（严格 schema 冻结 T0135 前后）、evidence/conclusion/verdict/disposition 覆盖率
- 抽样审读：archive 中按年代分层抽 6 任务人工核读 conclusion 质量
- AI 自查：本会话 T0370-T0373 的全部门禁拒绝事件复盘（clarifications.jsonl 与 transition receipt 留有痕迹）

## 验收标准

- [ ] AC-1: 全量扫描完成——所有 task.json 的 phase 分布、schema 合规率（T0135 前/后分层）、evidence/conclusion/verdict/disposition 覆盖率有量化数字
- [ ] AC-2: 抽样审读 ≥6 个归档任务的 conclusion 质量（AC 判定完整性/证据回链/适用边界）有逐个结论
- [ ] AC-3: AI 操作性失误清单 ≥5 条，每条含事件、根因、防再发措施
- [ ] AC-4: 审查发现分级为 立即修复/改进立项/记录观察 三层并给出处置去向
- [ ] AC-5: review-report.md 登记 evidence 且 convergence map valid:true

## 范围外

- 不修改任何历史任务文件（旧格式清理属既有 dry-run 清单机制）
- 不实施防再发措施（措施落地走后续 Improvement Task 或知识沉淀）

## 备注

已知边界：CONTEXT.md 载明"严格 schema 冻结后以 dry-run 清单清理不合规任务"——冻结前旧任务的 schema 违规属已接受状态，审查需分代统计而非一律计为违规。
