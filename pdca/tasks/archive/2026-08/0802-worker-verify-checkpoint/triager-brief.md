# T0196 Triage Brief

## 分类

- 类型：feature（验证型）
- 场景：development
- 父任务：T0195

## 本地源码核验

- 上游 discard worker：`fs/alloc/discard.c:598-633`
  `bch2_do_discards_fast_work`——fast_work 循环逐桶 discard，
  `max_discards_in_flight` 边界、EAGAIN 旋转；engine-local 对应
  `run_discard_worker`（engine.rs:1216）与 `run_discard_worker_once`
  （engine.rs:1171，T0190 已对齐 in-flight/重试语义）。
- 上游 journal reclaim：`fs/journal/reclaim.c`；engine-local 对应
  `request_reclaim`（engine.rs:1337）+ `reclaim_worker_loop`
  （engine.rs:1814，checkpoint 驱动）。
- 上游 worker 维护状态与 fsck 校验的验证关系：`fs/alloc/check.c:323-345`
  `check_freespace_key_async` 校验 freespace 与 alloc 一致性；engine-local
  对应 `verify_bucket_indexes`（verify_all 内部，T0194 聚合）。
- T0193 公开断言 `discard_queue_empty`、`verify_guard_invariants` 已就绪，
  T0191 建议「run 后队列空不变量提升为公开断言工具供 worker 变体复用」。

## 查重

T0195 conclusion 建议「verify_all 作为 worker 变体最终一致性检查点
（T0191 建议延续）」；无同范围活动任务。既有 worker 测试（T0190 七项、
T0191 属性）未在 run 后做 verify_all 全量校验。

## 推荐

以测试级检查点实现（不新增公开 API，遵守约束 8）：为 discard worker 与
reclaim worker 生命周期建立「运行后 verify_all + discard_queue_empty」
一致性矩阵——正常 drain、并发入队、EAGAIN 旋转（合法非空队列）、
not_rw 设备、非法态（open bucket 未关）下 worker 行为与 verify 结果。
范围外：真实 TRIM、GC/LRU、-f force 修复路径。
