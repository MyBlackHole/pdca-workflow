# T0402 收敛条件映射 (convergence-map)

## 收敛条件（来自 task.json meta.convergence）
- C0: task identity is unique and immutable（任务身份唯一且不可变）

## 映射与判定
- 条件 C0「task identity is unique and immutable」
  - 对应 AC：AC-6（source_task 回链 + record 路径保留 + 原位置 redirect 桩）
  - 证据：`ev-t0402-migration-manifest`（迁移清单含每条实例的 `source_task` 字段；原 `knowledge/` 16 文件改写为 redirect 说明，保留 `records/T0402-0829-onto-tls-pilot/` 壳与 `meta.record` 指向）
  - 判定：✅ 满足
- 整体收敛由 7 条 PRD AC 全 PASS 支撑（见 `ev-t0402-validate-pass` 与逐条 AC 判定），满足开发场景「对照 PRD 收敛条件」的 Check 要求。
