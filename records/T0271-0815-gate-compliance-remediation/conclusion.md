# T0271 门禁合规存量修复 — 结论

- 任务：T0271-0815-gate-compliance-remediation
- 依赖：T0270-0815-gate-compliance-audit
- 日期：2026-08-15
- 阶段：check（产出本结论）

## 目标

清理 T0270 审计发现的存量门禁违规（gate_incomplete 6 组），修正 audit 误报，并让拒绝留痕机制生效后的数据真实反映合规状态。

## 验收对照

| AC | 标准 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | audit 修正：check 无 verdict 不判违规；识别 gate_exemption 并单列豁免清单 | Passed | ac1, ac7 |
| AC-2 | remediate 脚本存在，--dry-run 预览不实际改动 | Passed | ac2, ac7 |
| AC-3 | T0207/T0208/T0209 补 verdict（从 conclusion 提取） | Passed | ac3 |
| AC-4 | T0149/T0200 加 gate_exemption（历史无依据如实豁免） | Passed | ac4 |
| AC-5 | archive_dup 2 组嵌套副本删除、active_stale 2 组残留移除 | Passed | ac5 |
| AC-6 | 修复后 audit 对比：gate_incomplete 6→0、archive_dup 2→0、active_stale 2→0 | Passed | ac6 |
| AC-7 | 新增测试通过，全量 4 失败保持非回归 | Passed | ac7 |

## 关键结果

### 存量修复（9 项实际执行）

- **补 verdict ×3**：T0207/V-T0207-001、T0208/V-T0208-001、T0209/V-T0209-001，从各自 conclusion.md Verdict 段提取（outcome=confirmed），写入 task.json meta.verdict。
- **豁免 ×5**（超出 PRD 计划的 2 项）：T0149、T0200（原计划）之外，补 verdict 后发现 T0207/T0208/T0209 仍缺 final_confirmation/act-to-archive receipt——属门禁机制建立前记录不全（conclusion 已含完整 Verdict），按"如实豁免不伪造"原则一并标记，理由写入 reason。
- **删除嵌套副本 ×2**：0801-btree-split-proptest、0801-trans-enomem-restart（仅孤立 task.json，主目录完整）。
- **移除 active 残留 ×2**：0804-cdm-report-center-analyse（13 文件）、T0215-0804-report-subscheme-docs（12 文件），与 archive 无差异。

### 修复前后对比

| 指标 | 修复前（T0270） | 修复后（T0271） |
|------|----------------|----------------|
| gate_incomplete | 6 | **0** |
| archive_dup | 2 | **0** |
| active_stale | 2 | **0** |
| 豁免清单 | — | 5（T0149/T0200/T0207/T0208/T0209） |
| 拒绝留痕 receipts | 0 | **2** |

> 拒绝留痕 2 条为 T0270/T0271 计划→do 过渡被拒时真实写入（CLARIFICATIONS_INVALID + FINAL_CONFIRMATION_MISSING），证明 T0270 机制真实生效。

### 基线数据变化

删除 active 残留/嵌套副本后，triager-brief 总数 93→92、核心覆盖率 58.1%→57.6%、category 76.3%→76.1%（残留目录含已归档任务重复 brief）。`tests/test_triage_brief.py` 基线断言同步更新，属合理数据演进。

## 测试

- 全量：**256 passed / 4 failed / 13 subtests**（4 失败为既有 round62-67 外部任务缺失，非回归）。
- 新增：test_gate_remediation.py 4 项（audit 修正、dry-run 不改动、apply 效果、模式互斥）+ test_gate_compliance.py 6 项全绿。

## 遗留

- id 撞车 25 组：非本任务范围，建议独立任务清理。
- legacy_no_gate 29 组（门禁机制建立前任务）：按既定政策不回溯补建，仅如实统计。
