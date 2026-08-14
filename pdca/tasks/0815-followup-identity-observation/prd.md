# 跟进：观察统一 task/record identity 上线效果

## 问题陈述

- **现状**: T0262 已部署统一 task/record identity 原子创建事务（`scripts/task_identity.py`），并冻结 baseline：25 个 duplicate task IDs、4 个 duplicate slugs、5 条 event path mismatches、20 条 record_derived_mismatch（历史旧约定，只诊断不改写）。T0262 上线时刻：2026-08-14T23:46:16+08:00。
- **目标**: 用真实使用数据验证统一入口是否显著减少 identity 缺陷——经统一入口创建的新任务是否保持 ID/record 唯一、无新 mismatch、创建路径无失败或人工恢复。
- **差距**: T0262 仅证明实现正确性（测试+冻结 baseline），尚未积累真实使用观察数据；effectiveness verdict 未出具。

## 解决方案

不修改任何代码或任务。以 `records/T0262-0814-followup-atomic-task-record-identity/evidence/identity-baseline.json` 为对照基线，按观察窗触发条件采集真实新任务的 identity 健康度，出具 effectiveness verdict。

### 观察协议

1. **触发条件**：14 天或累计 20 个经统一入口创建的真实新任务，以先到者为准。
2. **数据采集**（触发时一次性执行）：
   - 跑 `python3 scripts/validate-workflow.py --all`，提取 identity 四维：duplicate_task_ids / duplicate_slugs / event_path_mismatches / record_derived_mismatches。
   - 与 T0262 baseline 四维（25/4/5/20）对比，统计新增量与新增发生的时间窗口。
   - 统计观察窗内创建的真实新任务：数量、创建失败次数、人工恢复次数、`meta.convergence` 为默认值（未显式填写）的缺失率。
3. **对照分析**：以 `knowledge/pdca-flow/real-usage-effectiveness-audit.md` 的分层判定（实现正确性 / 运行数据可用性 / 效果闭环）组织结论。
4. **verdict 出具**：观察窗触发后出具 effectiveness verdict（confirmed / partial / rejected）。

## 用户故事

1. 作为管理员，我希望确认统一入口上线后新任务不再产生重复 ID、重复 slug 或 record mismatch，以便信任该机制。
2. 作为执行者，我希望观察报告能说明新任务创建路径是否稳定（无失败、无人工恢复），以便判断是否可全面推广。

## 实现决策

- **无代码改动**：本任务只读观察，不引入被测模块，无测试产物（research 场景）。
- **观察脚本**：沿用 `validate-workflow.py --all` 的 identity 输出，不新建扫描逻辑（避免另立口径）。
- **convergence 填写检查**：统计观察窗内新任务中 `meta.convergence` 等于默认值 `"task identity is unique and immutable"` 的比例——T0264 修复 `--convergence` 参数后，默认值缺失率应下降。
- **基线配对**：观察数据与 T0262 baseline 存入 evidence，作对比序列。

## 验收标准

- [ ] AC-1: 明确记录观察窗起点（T0262 上线时刻）与触发条件（14 天或 20 任务先到者）。
- [ ] AC-2: 采集观察窗内全部经统一入口创建的真实新任务列表。
- [ ] AC-3: 报告 identity 四维（dup IDs/dup slugs/event path mismatch/record mismatch）与 T0262 baseline 的对比结果。
- [ ] AC-4: 报告观察窗内创建失败次数、人工恢复次数、convergence 默认值缺失率。
- [ ] AC-5: 按 real-usage-effectiveness-audit 分层（实现/数据/闭环）组织结论。
- [ ] AC-6: 观察窗触发后出具 effectiveness verdict，附证据。

## 范围外

- 不修改任何代码、task、record 或 occurrence。
- 不处置历史 25 个 duplicate IDs 或 20 条 record mismatch（T0262 建议的批量迁移/alias receipt 列为后续候选）。
- 不定义 `records/__quarantine/flow-audit.json` 事件的转正/废弃流程。
- 不评估 `seam_contract` 是否忽略外部项目 seam（doctor 环境问题）。

## 备注

- 本任务为 research 场景，无测试接缝，跳过 seam 确认。
- 观察窗内新任务包括 T0262、T0263、T0264（T0262 用默认 convergence 创建，T0263/T0264 也受默认值影响）；T0264 已修复 `--convergence` 参数，后续任务应显式传收敛值。
- 术语以 `knowledge/pdca-flow/task-record-identity-invariants.md` 为准；观察方法以 `knowledge/pdca-flow/real-usage-effectiveness-audit.md` 为准。
- 触发条件满足前，本任务保持 plan 阶段挂起；满足后进入 do/check。
