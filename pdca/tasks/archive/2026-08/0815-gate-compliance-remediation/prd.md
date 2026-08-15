# 门禁合规存量修复：真违规补 verdict + 归档一致性清理（第七轮）

## 问题陈述

- **现状**: T0270 审计发现存量门禁异常：gate_incomplete 6 个（T0248/T0149/T0200/T0207/T0208/T0209）、archive_dup 2 组（嵌套副本）、active_stale 2 组（active 残留）、id 撞车 25 组。T0270 明确"修复动作交后续任务"。
- **目标**: 修复可依据项（补 verdict、归档一致性清理），对无依据项如实豁免标记，并修正 audit 脚本误报（check 阶段误判），使合规度可量化提升且修复可复现。
- **差距**: 无既有修复机制；audit-gate-compliance.py 对 phase=check 无 verdict 误判为违规（check 阶段进行中本就无 verdict，check→act 前才要求）；无豁免识别机制。

## 解决方案

### 增量一：audit 脚本逻辑修正

修改 `scripts/audit-gate-compliance.py`：

- **check 阶段修正**: phase=check 且无 verdict 不再判 gate_incomplete（仅 act/archive 要求 verdict）。→ T0248（round62 check 进行中）不再误报。
- **豁免识别**: 识别 `meta.gate_exemption`（结构：`{reason, at}`），存在则该任务的 gate_incomplete 相关项不计入异常，报告单列"豁免"。
- 新增 `gate_exemption` 字段 + 报告"豁免清单"。

### 增量二：修复执行（scripts/remediate-gate-compliance.py）

新增修复脚本（`--dry-run` 预览 + 执行，原子写）：

1. **补 verdict（有依据）**: T0207/T0208/T0209 从 `records/<record>/conclusion.md` 的 Verdict 段提取（outcome=complete、verdict_id=V-T0xxx-001），补 `meta.verdict`。
2. **豁免标记（无依据，如实）**: T0149（record=None 无 conclusion）、T0200（早期缺 act-to-archive）加 `meta.gate_exemption`（reason 说明历史无依据，非可修复违规）。
3. **嵌套副本删除**: archive_dup 2 组（0801-btree-split-proptest、0801-trans-enomem-restart）的嵌套孤立副本（仅 task.json）删除，保留完整主目录。
4. **active 残留移除**: active_stale 2 组（0804-cdm-report-center-analyse、T0215-0804-report-subscheme-docs）移除 active 目录残留（archive task.json 相同，确认完整）。

### 增量三：可验证的提升作用

- 修复后 `audit-gate-compliance.py` 扫描对比：gate_incomplete 6→0（3 补 verdict + 2 豁免 + 1 脚本修正）、archive_dup 2→0、active_stale 2→0。
- 前后报告对照 + 豁免清单单列。

**硬指标**：
- **行为级**: 修复脚本 dry-run/执行 fixture 测试；audit 修正（check 阶段/豁免识别）测试。
- **数据级**: 修复前后异常计数对比可复现。
- **判定级**: 合规修复报告（修复项清单、豁免依据、前后对比）。

## 测试决策

- 被测模块: `scripts/audit-gate-compliance.py`（修正逻辑）、`scripts/remediate-gate-compliance.py`（修复执行）。
- 好测试: check 阶段不误报、豁免识别、修复 dry-run 预览、补 verdict 从 conclusion 提取、嵌套副本删除（dry-run 不实际删）。
- 场景: research（审计修复主导）。
- 明确不做: id 撞车 25 组修复（范围过大，独立任务）；active 中真正进行中任务（T0248 等）不动；伪造 verdict/receipt（无依据任务走豁免非伪造）。

## 用户故事

1. 作为流程负责人，我希望门禁异常可安全修复，以便合规度量化提升。
2. 作为流程负责人，我希望无依据历史项被如实豁免而非伪造，以便审计诚实性。
3. 作为审计者，我希望修复前后对比可复现，以便证明修复有效。

## 实现决策

- 语言: Python 3，单文件脚本，subprocess 调用。
- 修复脚本: `--dry-run` 默认（预览），`--apply` 执行；原子写（atomic_json）；git 管理保证可回滚。
- 补 verdict: 从 conclusion.md Verdict 段解析（正则），无法解析则报告跳过。
- 豁免: `meta.gate_exemption = {reason, at}`。
- 范围外: id 撞车修复、T0263 观察、拒收率回读。

## 备注

- 前置确认：T0207/T0208/T0209 conclusion.md 均有 Verdict（complete/V-T0xxx-001）→ 补 verdict 有依据。
- 嵌套副本均为孤立 task.json（主目录含 prd/clarifications/triager-brief）→ 删副本安全。
- active 残留 task.json 与 archive 相同（diff 无差异）→ 移除安全。
- T0270 报告 gate_incomplete 6 中含 T0248（check 进行中）——本任务修正为误报。

## 验收标准

- [ ] AC-1: audit-gate-compliance.py 修正：phase=check 无 verdict 不判 gate_incomplete；识别 meta.gate_exemption 并在报告单列豁免清单。
- [ ] AC-2: remediate-gate-compliance.py 存在，`--dry-run` 预览修复计划（补 verdict/豁免/删副本/移残留），不实际改动。
- [ ] AC-3: 执行后 T0207/T0208/T0209 补 verdict（从 conclusion 提取，outcome/verdict_id 正确）。
- [ ] AC-4: T0149/T0200 加 meta.gate_exemption（reason 说明历史无依据）。
- [ ] AC-5: archive_dup 2 组嵌套副本删除、active_stale 2 组 active 残留移除（主目录/archive 完整保留）。
- [ ] AC-6: 修复后 audit 扫描对比：gate_incomplete 6→0、archive_dup 2→0、active_stale 2→0，报告含前后对照。
- [ ] AC-7: 新增测试通过（audit 修正/豁免识别/修复 dry-run），全量 4 失败保持非回归。
