# T0193 Do 阶段双轴代码审查报告

## 审查范围

- `crates/subvol/src/engine.rs`：新增 `verify_guard_invariants`（688）、
  `open_bucket_count`（736）、`discard_queue_empty`（749）、
  `DerivedStateMismatch::OpenBucketFree/NotRwBucketFree` 变体；既有测试切换
  （drop 泄漏查询、队列空断言、属性测试聚合断言）。
- diff：+160/-7，单文件。

## 轴一：上游语义对齐（对照本地 bcachefs-tools）

| 检查点 | 结论 |
|--------|------|
| verify_guard_invariants ↔ bch2_check_allocations（check.c:1097-1160）单入口 pass | ✅ 一致：一次调用聚合全部守卫不变量，失败返回 errno 风格错误（DerivedState），不修改状态 |
| open 桶不 free ↔ bch2_bucket_is_open_safe（discard.c:344-347,433-436,743） | ✅ 一致：断言 FREE 桶 ∩ open_buckets == ∅，正是上游 skip 语义的不变式 |
| not_rw 桶不 free ↔ bch2_dev_get_ioref(WRITE)（discard.c:349-357,654,871） | ✅ 一致：断言 FREE 桶设备 ∈ rw_devs，正是 ioref 失败 skip 语义的不变式 |
| open_bucket_count ↔ bch2_open_buckets_stop（fs.c:324,foreground.c:1171-1230） | ✅ 一致：查询无泄漏，不改变 Drop panic 行为（T0192 保留） |
| discard_queue_empty ↔ fast_work while（discard.c:605-633） | ✅ 一致：纯查询，无 hook，-11 轮转合法路径不误报 |
| 错误编码 | ✅ OpenBucketFree/NotRwBucketFree 复用既有 DerivedState 通道，无新错误码 |

## 轴二：安全与并发

| 检查点 | 结论 |
|--------|------|
| 锁序 | ✅ fs → open_buckets → rw_devs，与 reclaim_bucket（840-860）、discard_bucket（1010-1025）一致；set_device_rw（open_buckets→rw_devs 无 fs）不形成环 |
| 锁持有范围 | ✅ 断言在 fs 锁内持有 open/rw 快照并完成扫描，与 verify_bucket_indexes 行为一致（只读校验，可接受阻塞） |
| 只读性 | ✅ 三个 API 均不修改状态，与 pass 语义一致 |
| 死锁风险 | ✅ 无新增锁序；open_bucket_count/discard_queue_empty 单锁无嵌套 |
| 测试切换完整性 | ✅ 属性测试逐 op 聚合断言（替换局部 open 检查）、drop 泄漏测试前置 count 查询、三处队列空断言 |

## 结论

0 blocking，0 MEDIUM，0 LOW。实现与上游语义、既有锁序完全一致，可进入 Check。
