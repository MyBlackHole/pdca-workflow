# 改进：research 场景结论补可验证信号要求 — PRD

## 来源

T0371 评估报告 E-1（立即层），用户批准立项。

## 问题陈述

research 任务结论缺乏"可复核验证途径"要求。回溯抽查（2026-08-23）：T0295/T0298/T0311/T0333 四个已归档 research conclusion 均无系统验证途径章节（仅适用边界含部分线索），Check 阶段无法快速复核调研真伪。

## 方案

documentation 场景，两处一行级增补 + baseline 豁免：

1. skills/research/SKILL.md：Exit 前新增规则——每条关键结论须附至少一条可复核验证途径（命令/SQL/复现步骤/可回看引用），不可复核的结论降级标注置信度。
2. flows/flow-do/SKILL.md C2：审查项追加"且结论含可复核验证途径"半句。
3. pdca/skill-content-baseline.json 两文件条目同步豁免。

## 回溯抽查结果（Do 前置验证，T0371 设计）

| 样本 | 现状 | 可补出验证途径 |
|------|------|---------------|
| T0295 | 无系统章节 | 是：git log v65..v101 重跑 |
| T0298 | 无系统章节 | 是：nvim 配置 diff 重放 |
| T0311 | 失败原因节含部分验证 | 是：POC 脚本重跑 |
| T0333 | 无 | 是：容器构造脚本重跑 |
| T0370 | 引用行号可回看 | 是：按 file:line 复核 |

达标 5/5（PRD 承诺 ≥4/5），证明规则可执行且历史确有缺口。

## 验收标准

- [ ] AC-1: skills/research/SKILL.md 含可验证信号规则（关键结论附可复核途径+不可复核降级标注）
- [ ] AC-2: flow-do C2 审查项含该要求
- [ ] AC-3: baseline 两文件更新且 audit 零 budget issue
- [ ] AC-4: 本 PRD 的回溯抽查表作为规则可行性证据登记 evidence

## 范围外

- 不改 write-conclusion/register-evidence 脚本逻辑
- 不追溯补写历史任务 conclusion

## 备注

flow-do 持平 baseline 将被打破约 +60B——豁免 reason 引用本任务与 T0371 E-1。
