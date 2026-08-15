---
schema: pdca.asset/v1
id: T0274-0815-id-collision-remediation
phase: check
source_ids: [impl, tests, report, ac2-records, ac5-doctor-json, convergence-map]
---

# T0274 结论：ID 撞车清理

## 判定结论

**CONFIRMED** — 12 组可处置 ID 撞车全链路重分配已实现并验证通过，上下文感知引用替换精确解决 CDM/报表树 与 RPC 树 纠缠。

## 验收标准逐项

| AC | 描述 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | 新增 `scripts/remediate-id-collisions.py`，输入裁决表对 12 组重分配方改写 task.json 的 id/meta.record | ✅ PASSED | impl |
| AC-2 | 同步 records 目录重命名 | ✅ PASSED | ac2-records |
| AC-3 | 同步归档目录重命名（5 个含旧 ID 前缀目录） | ✅ PASSED | impl + 目录验证 |
| AC-4 | parent/children/dependencies 引用链上下文感知替换，完整性通过校验 | ✅ PASSED | impl + ac4 引用验证 |
| AC-5 | doctor `duplicate_task_ids` 23 → ≤12 | ✅ PASSED（23 → 11） | ac5-doctor-json |
| AC-6 | 处置报告列明 12 组裁决 + 11 组待办 | ✅ PASSED | report |
| AC-7 | 测试覆盖幂等性与裁决表完整性，全量无回归 | ✅ PASSED | tests |

**7/7 AC Passed**

## 关键发现

1. **上下文感知引用替换是必要的**：T0214 撞车组内同时存在 CDM/报表树与 RPC 树，两树子任务 parent 均指向 T0214，字符串级替换会误伤。按引用者 slug 特征词（CDM：report/cdm/collection/deployment/acceptance；RPC：rpc/worker/epoll）判定归属，实现精确替换。
2. **替换精确性验证**：CDM 链子任务（report-subscheme-docs→T0278、cdm-data-cli→T0279）parent 改向 T0277；RPC 链（rpc-epoll-multireactor、worker-adaptation）parent 保持 T0214；11 组含活跃任务撞车（DEFERRED_IDS）整组未改写。
3. **flow-events 同步补全**：records 目录重命名后，flow-events 内部 `record_id`/`task_id` 字段须同步，否则 doctor `event_path_mismatches` 新增 22 项。已补全 `_sync_record_flow_events` 并修复 7 组 22 个 flow-events，`event_path_mismatches` 恢复至既有 5 项基线（T0252 遗留）。
4. **doctor 改善显著**：duplicate_task_ids 从 23 组降至 11 组，全部为含活跃任务的待办组（T0216/T0218/T0219/T0220/T0221/T0222/T0228/T0229/T0248/T0250/T0252）；event_path_mismatches 无新增。
5. **幂等性**：重复 apply 无二次改写（digest 一致）；新 ID T0275-T0286 无冲突。
6. **全量测试 280 passed / 4 failed**：4 个失败均为既有（2 harness + 2 doctor seam），无新增回归。新增 8 个测试全部通过（含上下文引用归属判定、flow-events 同步）。
7. **无新增悬空引用**：全库 142 任务中 7 处悬空引用为既有遗留（T0150→T0151-T0157），与本次重分配无关。

## 影响与范围

- 新增：`scripts/remediate-id-collisions.py`、`tests/test_remediate_id_collisions.py`（7 测试）
- 重分配：12 组重分配方 task.json id/meta.record、12 组 records 目录、5 组归档目录、2 个引用文件（T0277 children、T0278/T0279 parent）
- 未改：11 组含活跃任务的撞车（待办）、保留方 task.json、任务内容本身

## 建议（Act 阶段知识处置）

- 将"ID 撞车重分配 + 上下文感知引用判定"方法论沉淀至知识库，供后续撞车组（11 组活跃）归档后处理参考。
- doctor `identity.valid` 仍为 False（record_derived_mismatches 17 项、event_path_mismatches 27 项等），待 T0272 诊断的其他修复候选推进。
