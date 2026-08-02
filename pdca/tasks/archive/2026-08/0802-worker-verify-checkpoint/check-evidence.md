# T0196 检查证据（check-evidence）

## AC-1：修改前逐段记录上游锚点

证据：`ac1-source-anchors.md`（实现前撰写）。
- discard worker：`fs/alloc/discard.c:598-633` `bch2_do_discards_fast_work`
  fast_work 循环；engine-local `run_discard_worker`（engine.rs:1216）。
- journal reclaim：`fs/journal/reclaim.c`；engine-local `request_reclaim`
  （engine.rs:1337）、`reclaim_worker_loop`（engine.rs:1814）。
- worker 维护状态与 fsck 校验的验证关系：`fs/alloc/check.c:323-345`
  `check_freespace_key_async`；engine-local `verify_bucket_indexes`
  （verify_all 内部）。

## AC-2：discard worker 正常路径后 verify_all 通过且 discard_queue_empty

- 新增 `discard_worker_drained_persistent_image_reopens_verified`：
  queue→run_discard_worker→verify_all Ok + discard_queue_empty→flush→
  drop→open_persistent→verify_all Ok + discard_queue_empty 仍通过
  （worker 维护的 derived 状态持久化后可校验，端到端检查点）。
- 既有覆盖（T0190/T0191/T0194）：并发入队后 verify_all
  （`discard_worker_concurrent_queue_single_worker_drains_all`）、正常
  drain（`discard_worker_deduplicates_and_retries_eagain`、
  `discard_worker_fifo_pass_drains_entire_queue` 等）。

## AC-3：边界路径后一致性正确

- EAGAIN 旋转（合法非空队列）：`discard_worker_eagain_rotates_to_tail_
  without_blocking_ready_buckets` run 后 verify_all Ok（既有）。
- not_rw 设备 skip：`discard_worker_requires_rw_device`（既有，worker
  行为）与 `verify_guard_invariants_rejects_notrw_free_bucket`（既有，
  not_rw free 桶非法态 verify 报 NotRwBucketFree 错误名，T0193/T0194
  语义保留）；恢复 rw 后 verify_all Ok。

## AC-4：reclaim worker checkpoint 完成后 verify_all 通过

- 新增 `background_reclaim_checkpoint_preserves_verified_state`：
  put_sync→request_reclaim→wait_for_reclaim（completed≥requested、
  last_error=None）→verify_all Ok→flush→drop→open_persistent→
  verify_all Ok + scan 数据完整。
- 既有覆盖：`high_watermark_kicks_background_reclaim_and_preserves_the_
  tail`（触发路径与 tail 保留，未含 verify_all，本次补全端到端验证）。

## AC-5：库 API 不变

- 生产代码零改动（提交 13535e2 仅 +42 行测试）；复用既有公开 API
  verify_all / discard_queue_empty / request_reclaim / wait_for_reclaim。

## AC-6：workspace 全量测试、fmt、diff gate

- `cargo fmt` 通过；`cargo test --workspace` 全绿：215 lib + 10
  btree_proptest + 3 fsck_cli = 228；单项 ≤40s（AC 上限 1min）。
- 提交：subvol `13535e2`（1 file, +42/-0）。

## 结论

六项 AC 全部达成；既有测试矩阵已带 verify_all（T0194 切换），本次补全
端到端重开与 reclaim checkpoint 两个缺口，形成 worker 生命周期最终
一致性检查点矩阵。
