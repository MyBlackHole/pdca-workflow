# T0151–T0157 遗留子任务归档说明

归档日期：2026-07-30

## 范围

- T0151 `0730-parquet-physical-structure`
- T0152 `0730-parquet-encoding-compression`
- T0153 `0730-parquet-tuning`
- T0154 `0730-parquet-schema-types`
- T0155 `0730-parquet-sdk-ecosystem`
- T0156 `0730-parquet-predicate-pushdown`
- T0157 `0730-parquet-production-cases`

## 原因

这些目录由父任务 T0150 的拆解步骤创建，但从未启动独立 PDCA 周期：它们一直处于
`plan/Pending/active=false`，没有 final confirmation、执行证据、Check 结论或 Act
disposition。相关研究内容已经由父任务 T0150 完成、验收并归档，继续保留这些目录在
active 区会造成“仍有七项待执行工作”的错误信号。

## 处置

原始 PRD 与任务快照完整保留在本目录。原 `task.json` 重命名为
`task.invalid.json`，明确表示它只是历史遗留快照，不是满足当前严格 task schema 和阶段
门禁的可恢复任务。未伪造阶段时间、用户确认、verdict 或 disposition。

父任务 T0150 位于 `pdca/tasks/archive/2026-07/0730-parquet-format-research/`，已通过
`scripts/validate-workflow.py` 的严格归档校验。
