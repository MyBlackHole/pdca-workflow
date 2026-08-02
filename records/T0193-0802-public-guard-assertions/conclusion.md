# T0193 结论

## 概述

公开守卫断言套件：`verify_guard_invariants`（单入口聚合，对齐
bch2_check_allocations pass 语义）+ `open_bucket_count`/`discard_queue_empty`
查询。T0189/T0191/T0192 既有测试全部切换到公共断言。

## 验证

- workspace：208 lib + 10 集成全绿（10.19s/37.51s，≤1min）
- fmt 通过；diff +160/-7 单文件（subvol 9e6d564）
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW

## 边界与发现

- 锁序 fs→open_buckets→rw_devs 与 reclaim/discard 一致；set_device_rw
  （open_buckets→rw_devs，无 fs）不形成环。
- 断言为纯只读快照式校验（pass 语义），持有 fs 锁期间完成扫描，与
  verify_bucket_indexes 行为一致。
- 属性测试逐 op 调用聚合断言，替换原有局部 open 检查（覆盖更广：
  open∧FREE 与 not_rw∧FREE 均由实现保证，模型不再重复实现）。

## 下一轮建议

1. 属性测试模型状态机与引擎对齐度提升：not_rw 设备 free 断言已由实现
   保证，可将 open/not_rw 不变量直接注入模型决策（T0189 模型 op 5/6）。
2. `verify_guard_invariants` 与 `verify_bucket_indexes` 可合并为单一
   verify_all 入口（对齐 check_allocations + check_btree 双 pass 聚合）。
3. worker 变体（T0191 建议的后续 worker）复用 discard_queue_empty 断言。
