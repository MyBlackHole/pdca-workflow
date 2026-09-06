---
schema: pdca.asset/v1
id: T0513-0906-ontology-mandatory
phase: check
source_ids: [process-diff, validate-output, ac4-verify, convergence-map-v4]
---

## 上下文
用户要求修改 PDCA 流程使本体 Act 强制产生，范围全部任务，立项改进任务。Do 改 4 处并回归验证；convergence 三版迭代（顺序误写→证据支撑规则澄清）后 valid。

## 假设与结果
- 假设 1：4 处改动关闭通道且保留豁免。结果：成立，diff 145 行，回归验证通过。
- 假设 2：历史任务不受追溯影响。结果：成立，门禁只校验当前转换。
- 假设 3：convergence 证据支撑规则。结果：所列证据须至少其一支持该 AC（源码 Expenditures 确认），已按此修正。

## 分析
- **AC-1** ✅ flow-act/skill-research 取消 records-only（process-diff）
- **AC-2** ✅ pdca_core/settlement 拒收 records-only，自举豁免通过（validate-output 回归输出）
- **AC-3** ✅ 全量 validate 0 issues；既有归档不追溯（validate-output）
- **AC-4** ✅ T0512 归档路径验证记录，同构逻辑已验证（ac4-verify）

关键结论：4 处改动完成，回归验证通过；T0512 需取消 exempt 并补本体节点后归档。
复核途径：process-diff逐行审；回归命令重跑。

## 适用边界
- 新门禁只影响新转换，不重跑历史归档。
- T0512 仍在 check，需按新流程补本体后归档。

## 下一轮建议
- T0512 补 SIX 学习本体节点后归档；20 轮规划后续轮次按新流程执行（每轮必产本体）。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，4处改动+回归验证通过", "verdict_id": "vt0513-confirmed", "at": "2026-09-06T00:00:00+08:00"}
