# 后续改进清单

## 状态说明

本清单记录 T0144 根因分析之外仍需要独立授权和新一轮 PDCA 验证的事项。它们不是本次
`confirmed` verdict 的缺口，也不代表已经实施。

## P1：目标内核回移植

- 状态：proposed
- 目标：在 3.10.0-1160.83.1.el7 对应源码中回移植与上游
  `b4459b11e84092658fa195a2587aff3b9637f0e7` 等价的 queue-rq suspend guard。
- 门槛：逐字段核对目标内核中的状态位、锁、返回码和 blk-mq 重试语义。
- 边界：本任务只证明静态故障路径可被该 guard 切断，没有修改或构建内核。

## P2：修复前后 A/B 运行验证

- 状态：proposed
- 目标：在相同 dm-multipath suspend/reload 并发负载下比较原内核与回移植内核。
- 验收：原版本可复现或呈现同类竞态证据，修复版本不再产生旧 target 引用；同时验证无
  请求丢失、无永久 requeue、无 suspend 卡死。
- 边界：需要测试环境、构建权限和明确的变更授权，应作为新的 Plan 任务启动。

## P3：外部触发链专项取证

- 状态：optional
- 目标：若业务仍需判断 iSCSI 是否间接促成窗口，采集 iSCSI session、multipath、
  dm reload/suspend 和请求派发的统一时间线。
- 验收：必须闭合“外部事件 → 故障 dm 设备 → 状态转换 → 越过隔离边界 → faulting
  completion”全部环节。
- 边界：没有完整状态转换链时继续保持 `inconclusive`。
