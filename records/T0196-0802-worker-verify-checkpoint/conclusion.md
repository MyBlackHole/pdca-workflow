# T0196 结论

## 概述

worker 变体最终一致性检查点矩阵：discard worker 与 reclaim worker 运行后
以测试级检查点运行 verify_all + discard_queue_empty（不新增公开 API，
遵守约束 8）。既有 worker 测试矩阵（T0190/T0191/T0194 切换）已带
verify_all，本次补全两个端到端缺口：drain 后重开验证、reclaim
checkpoint 后验证。

## 验证

- 新增 2 测试：
  `discard_worker_drained_persistent_image_reopens_verified`（drain→
  flush→drop→open_persistent→verify_all+discard_queue_empty 仍通过）；
  `background_reclaim_checkpoint_preserves_verified_state`
  （request_reclaim→wait_for_reclaim completed≥requested→verify_all→
  drop→open→verify_all+scan 数据完整）。
- 既有覆盖引用（AC-2/AC-3）：并发入队、EAGAIN 旋转、not_rw skip、
  NotRwBucketFree 非法态报错名。
- workspace 全绿：215 lib + 10 proptest + 3 fsck_cli = 228，单项 ≤40s
  （≤1min）；fmt 通过；提交 13535e2（+42/-0，生产代码零改动）。
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW。

## 边界与发现

- 既有测试矩阵已高度覆盖（T0194 切换 35 处断言），T0196 增量聚焦端到端
  与 reclaim 两个缺口；非法态语义（not_rw free 桶）由既有
  verify_guard_invariants_rejects_notrw_free_bucket 覆盖，未重复。
- 检查点形态为测试级：上游无"worker 后自动 verify"函数，不新增 API。
- 残留：lib 既有 never-used 警告（非本次引入）。

## 下一轮建议

1. 属性测试模型状态机注入守卫决策（T0193 建议延续，消除模型与实现
   重复）。
2. -f/--force 修复路径（T0195 建议延续，需上游 repair 语义设计）。
3. loom 风格并发交错测试（T0191 建议，若引入真实设备 I/O）。
