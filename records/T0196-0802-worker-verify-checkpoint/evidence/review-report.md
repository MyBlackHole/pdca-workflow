# T0196 双轴代码审查报告（review-report）

审查范围：subvol 提交 `13535e2`（engine.rs 新增 2 个测试：
`discard_worker_drained_persistent_image_reopens_verified`、
`background_reclaim_checkpoint_preserves_verified_state`）。

## A 轴：上游语义对齐

| 检查点 | 上游锚点 | 本实现 | 结论 |
|---|---|---|---|
| worker 维护派生状态可被校验 | alloc/check.c:323-345 `check_freespace_key_async`（fsck 校验 freespace/alloc 一致性） | discard drain 后 verify_all + discard_queue_empty；重开后仍通过 | 对齐 |
| discard fast_work 循环 | discard.c:598-633（逐桶 discard、max_discards_in_flight 重试） | run_discard_worker 既有实现（T0190 对齐），本次仅加检查点 | 对齐 |
| reclaim checkpoint 驱动 | journal/reclaim.c（空间回收驱动 checkpoint） | request_reclaim→wait_for_reclaim（completed≥requested）→verify_all；数据完整（scan 核对） | 对齐 |
| 非法态语义保留 | fsck 对损坏态报错 | not_rw free 桶 verify 报 NotRwBucketFree（既有测试引用，未重复构造） | 对齐 |
| 无新增行为分支 | — | 生产代码零改动，仅测试断言；无上游不存在逻辑 | 符合约束 8/12 |

## B 轴：安全/健壮性

- 测试资源：`prepared_bucket_engine` 持久化引擎 + `persistent_test_path`
  唯一命名（pid+nonce）；每测试 end drop + `fs::remove_file` 清理，无泄漏。
- 时序：reclaim 测试用 `wait_for_reclaim(1s)` 显式等待 completed≥requested，
  无忙等/无竞态假设；last_error=None 断言覆盖失败路径。
- 断言完整性：重开路径（open_persistent）后 verify_all + scan 数据核对，
  覆盖恢复一致性；flush_journal 确保清除/checkpoint 持久化后再 drop，
  避免假阳性。
- 无 panic 新增路径；既有锁序/错误处理未触碰。

## 结论

两轴通过；0 blocking / 0 MEDIUM / 0 LOW。残留：lib 既有 never-used
警告（非本次引入）。
