# T0191 Check Evidence — 多桶 discard worker 公平性与并发属性验证

## 验证摘要

- 定向测试 6/6 通过（discard 系列）；workspace lib 194/194、集成 10/10 通过。
- `cargo fmt --all --check` 通过；diff 仅含 `crates/subvol/src/engine.rs` 预期变更。

## AC 覆盖

### AC-1 源码锚点
- 证据：`ac1-source-anchors.md`（本任务目录）。
- 锚点：`bch2_do_discards`（discard.c:455-557）按 journal_seq 遍历；重试
  advance 跳过（discard.c:478-491）；`bch2_do_discards_going_ro`
  （discard.c:560-577）；fastpath FIFO darray + while 耗尽
  （discard.c:598-641）；engine-local 现状（engine.rs:434 BTreeSet、无提交序）。

### AC-2 确定性顺序 / 去重 / 互不覆盖
- `discard_worker_fifo_pass_drains_entire_queue`：3 桶 FIFO 提交，
  `run_discard_worker()` 一次 pass 全部出队，队列清空后重新 queue 成功。
- `discard_worker_deduplicates_and_retries_eagain`（T0190 回归）：重复
  queue 返回 -17（EEXIST 边界不变）。
- `discard_inflight` 改为 `Mutex<(VecDeque, BTreeSet)>`：FIFO 提交顺序
  对应 fastpath darray（discard.c:607-610），去重由 BTreeSet 保持。

### AC-3 EAGAIN 不阻塞
- `discard_worker_eagain_rotates_to_tail_without_blocking_ready_buckets`：
  就绪桶队首被处理；未就绪桶返回 -11 且保留在队列（重新 queue 仍 -17）；
  桶就绪后下一轮 run 完成，索引收束一致。

### AC-4 并发 queue/run、重启收敛
- `discard_worker_concurrent_queue_single_worker_drains_all`：Barrier 同步
  4 线程并发 queue，单 worker 一次 run 全部处理，无丢失/重复，索引一致。
- `discard_worker_rediscovers_need_discard_after_restart`（T0190 回归）：
  process-style 重启后 discover 重新入队并收束。

### AC-5 属性测试
- `multi_bucket_discard_worker_model_converges`：16 cases × 1..=40 交错
  操作（queue/run/reclaim/allocate/restart），影子状态机（4 桶
  free/btree/need-discard + FIFO 队列镜像）与引擎公共 API 结果逐 op
  对齐；restart 后从磁盘重建模型并与 discover 数量一致；每 op 后
  `verify_bucket_indexes`（alloc/need_discard/freespace/generation 派生
  集合）通过。0.89s。

### AC-6 门禁
- 定向 6/6、workspace lib 194/194、集成 10/10（10.16s + 37.82s）。
- `cargo fmt --all --check` 通过。
- diff gate：仅 `engine.rs` 变更，无调试残留。

## 对齐依据（约束 3/10/12）

- while 直到耗尽 ← `bch2_do_discards_fast_work` while(1)（discard.c:605-633）。
- FIFO 提交序 ← `bch2_fast_discard_bucket_add` darray_push（discard.c:643-655）。
- EAGAIN 移队尾不阻塞 ← 主路径 `-max_discards_in_flight` advance 跳过
  继续遍历（discard.c:478-491）；engine-local EAGAIN 语义来自 T0190 既定
  seam（bucket 未就绪，不可立即重试）。
- 未新增 bcachefs 不存在的结构体；`VecDeque`/`BTreeSet` 为 std 容器，
  FIFO 对应 darray、去重对应 in_flight 集合。
