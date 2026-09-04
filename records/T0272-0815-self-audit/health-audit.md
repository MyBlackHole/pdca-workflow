# PDCA 体系健康度自我审查报告

- 异常总数: 16

## 汇总

| 维度 | 计数 |
|------|------|
| gate_incomplete | 5 |
| id_collision | 1 |
| legacy_no_gate | 10 |

| 严重度 | 计数 |
|--------|------|
| blocking | 6 |
| noise | 10 |

| 根因 | 计数 |
|------|------|
| legacy | 10 |
| real-defect | 6 |

## 门禁覆盖率

- receipts 84.0% (137/163)，verdict 89.0%，rejected receipts 266 条

## 问题明细（按严重度）

### 阻断门禁 (6)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0428 | 0830-review-cleanup | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0444 | 0830-pdca-ai-eff-review-mapping | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0445 | 0830-pdca-ai-eff-review-gap | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0446 | 0830-pdca-ai-eff-review-plan | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0457 | 0831-ontology-fragment-scope / 0831-tls-keygen-followup-fix | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0468 | 0901-ontology-signal-completion | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |

### 仅统计噪音 (10)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0431 | 0830-add-matt-pocock-concepts | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0434 | 0830-pdca-ai-efficiency-review-2 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0435 | 0831-pdca-ai-efficiency-p0-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0436 | 0832-pdca-ai-efficiency-p1-integration | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0437 | 0833-pdca-ai-efficiency-p2-fill | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0440 | 0834-pdca-ai-efficiency-effectiveness | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0441 | 0835-pdca-ai-efficiency-fixture-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0442 | 0836-pdca-ai-efficiency-archive-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0447 | 0831-old-arch-refs-audit | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0539 | 0903-research-zfs-pcie-sm4 | legacy_no_gate | legacy | 机制前任务无 transition receipts |

## 修复候选清单（不执行，另立任务）

- **[high] ID 撞车清理**: 1 组 task_id 重复（跨目录），identity 歧义影响可追溯性 → 建议范围: 为每组冲突决定保留/重命名，更新依赖引用与记录
- **[high] 真违规门禁修复**: 5 项 gate_incomplete 非豁免（缺失 verdict/final_confirmation 等） → 建议范围: 按 T0271 remediate 模式补全或如实豁免