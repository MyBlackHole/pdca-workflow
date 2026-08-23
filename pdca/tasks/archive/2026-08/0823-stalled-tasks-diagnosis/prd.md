# 卡点诊断：check/act 停滞任务缺口分析 — PRD

## 来源

T0374 审查观察项：check(13)+act(7)=20 个停滞任务，已越触发线 15。本任务执行诊断并产出最小推进清单。

## 方案（research 场景）

逐任务扫描五类缺口：①evidence manifest 缺失/不完整 ②conclusion 缺失 ③verdict 缺失或未确认 ④disposition 缺失 ⑤clarifications 缺 check_confirmation。按"补什么能到 archive"产出每任务最小动作序列，并区分：可机械补齐（流程件）/需人工判断（verdict 类）/疑似废弃（建议关闭）。

## 验收标准

- [ ] AC-1: 20 个卡点任务全部有缺口画像（缺哪几类产物+最后状态时间）
- [ ] AC-2: 每任务有最小推进动作序列且标注 可机械补齐/需人工裁决/疑似废弃 三类
- [ ] AC-3: 汇总统计三类占比与预计工作量，给出批量推进策略建议
- [ ] AC-4: 报告登记 evidence 且 convergence valid

## 范围外

- 不实际推进任何卡点任务（推进含 verdict 人审，属后续批次）
- 不修改卡点任务文件

## 备注

诊断脚本可复用 T0374 扫描逻辑扩展。
