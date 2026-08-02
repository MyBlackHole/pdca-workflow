# T0189 Check Evidence

记录：`T0189-0802-discard-open-bucket-boundary`

## 对照上游源码（AC-1）

- 实现变更前对照记录：`ac1-source-anchors.md`（open bucket 定义 foreground.h:274-296；discard 跳过 discard.c:344-347/433-436/743；设备可写 discard.c:357-365、background.c:1650-1667；journal boundary discard.c:320-339；转 free 唯一路径 __discard_mark_free discard.c:163-219；重试循环 discard.c:429-557）。

## 实现证据（AC-2/AC-3）

- engine.rs:687-700 allocate 设备可写门禁（非 rw → -1）。
- engine.rs:774-806 reclaim open 门禁（-16）+ 设备可写门禁（-16），位于位置校验之后、backpointer 副作用之前。
- engine.rs:832-851 discard open 门禁（-11）+ 设备可写门禁（-11），位于 journal_seq 检查之后、reclaim 调用之前。
- engine.rs:771-820 open_bucket/close_open_bucket/set_device_rw 公共 API（open_buckets: BTreeSet<(u64,u64)>、rw_devs: BTreeSet<u64> 初始 [0]）。
- EngineState 新字段 engine.rs:435-436。

## 测试证据（AC-4/AC-5）

- `discard_worker_rejects_open_bucket_until_closed`：open 桶 reclaim -16、discard -11、close 后可回收，全程 verify_bucket_indexes。
- `discard_worker_requires_rw_device`：非 rw 设备 allocate -1、reclaim -16、discard -11，恢复 rw 后成功。
- `discard_reclaim_transaction_fault_leaves_no_half_state`：TransactionRestart 注入下 reclaim 成功（重试语义）、JournalWrite 注入下 flush_journal 失败后索引仍一致、恢复 rw/flush 后 discard 成功，重新打开持久化引擎 verify 一致。
- `discard_worker_skips_open_and_notrw_but_drains_ready_buckets`：open+ready 同设备，ready 被 drain、open 保留队列（-17），close 后 worker 成功。
- `discard_worker_rotates_notrw_device_buckets_until_rw_restored`：not_rw 桶轮转不阻塞，恢复 rw 后成功。
- `open_bucket_discard_model_protects_open_from_reuse`（proptest 16 cases）：op 集 queue/run/reclaim/allocate/flush+重启重建/open/close；不变量：open 桶不得转 free、state==2 必须 NEED_DISCARD、每 op 后 verify_bucket_indexes。

## 门禁证据（AC-6）

- `cargo test --workspace`：lib 200/200（10.16s）、集成 10/10（38.67s）。
- `cargo fmt --all --check` 通过。
- 单元测试单测时限：全部 < 1s，满足 1 分钟约束。
- 变更范围：仅 crates/subvol/src/engine.rs（+405）。

## 收敛

- convergence 目标 `T0189-0802-discard-open-bucket-boundary` 全部满足（见 convergence-map.md）。
- 审查：review-report.md，0 blocking。
