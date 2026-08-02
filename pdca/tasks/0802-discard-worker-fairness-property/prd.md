# T0191 多桶 discard worker 公平性与并发属性验证

## 问题陈述

T0190 已建立单桶 discard worker seam，但缺少多桶队列的确定性顺序、EAGAIN 重试公平性、
跨桶并发模型及重启后剩余队列的属性验证。

## 目标

建立多桶 discard worker 模型与并发测试，证明任何 bucket 不会因其他 bucket 的 EAGAIN 或
重复请求而永久饿死，且重启后队列可重新收敛。

## 验收标准

- [ ] AC-1: 修改前记录本地 discard worker 遍历、重试、going-ro 与 fastpath 源码锚点。
- [ ] AC-2: 多桶队列按确定性顺序处理，重复 bucket 不重复执行，跨桶请求不会互相覆盖。
- [ ] AC-3: 单桶 EAGAIN 重试不会阻塞其他 bucket；成功后队列和派生索引收束一致。
- [ ] AC-4: 并发 queue/run、JournalWrite/TransactionRestart fault 与 process-style restart 后模型一致。
- [ ] AC-5: 属性测试生成多桶请求/重试/重启序列，验证 alloc、need_discard、freespace、generation 集合。
- [ ] AC-6: 定向、并发/属性、workspace 全量、fmt 和 diff gate 通过；单项不超过一分钟。

## 实现决策

- 复用 T0190 的 `queue_discard_bucket`、`run_discard_worker_once` 与 `discover_discard_buckets`。
- 调度模型：新增 `run_discard_worker()`，一次 run 直到队列耗尽或出错，照搬
  `bch2_do_discards_fast_work`（discard.c:585-640）的 while 语义；保留
  `run_discard_worker_once` 作为单步测试入口。
- 确定性顺序：`discard_inflight` 改为 VecDeque FIFO（提交顺序即处理顺序，
  对应 fastpath 的 darray_pop，discard.c:607-610）+ BTreeSet 去重（queue 时
  拒绝重复，EEXIST 边界不变）。
- EAGAIN 处理：while 循环中遇到 EAGAIN（bucket 未就绪）的桶移到队尾轮转，
  继续处理下一个桶，保证单桶 EAGAIN 不阻塞其他桶；对应 bcachefs 主路径
  `-max_discards_in_flight` 时 advance 跳过继续遍历语义（discard.c:478-488）。
- 并发验证：属性测试用单线程交错序列验证收敛一致性；另加真实多线程定向
  测试（多线程 queue + 单 worker run，与 engine.rs:2887 惯例一致）。
- 测试模型只表达队列、bucket 状态、重试和持久化集合，不引入真实设备 I/O。
- 若发现调度语义不足，只增加 engine-local 最小状态，不扩展 GC/LRU。

## 范围外

真实 TRIM/discard bio、设备队列调优、完整 GC/LRU、stripe/EC、VFS、旧格式迁移和多格式兼容。

## 备注

前置：T0190 已归档并通过 Check/Act/Archive。
