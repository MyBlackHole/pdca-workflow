# T0203 上游锚点记录（AC-1）

修改前复核的本地 bcachefs-tools 源码提交/落盘边界，及
T0199/T0201/T0202 已核对锚点的复用与新增点。本轮**无新增业务逻辑**，
仅组合既有已验证设施（T0202 组合域模型 + T0201 并发崩溃框架），
故锚点以复核确认 + 复用表为主。

## 1. 提交/落盘边界（本轮复核）

| 边界 | bcachefs 锚点 | 结论 |
|------|--------------|------|
| journal replay 只回放已落盘记录 | fs/journal/read.c:61-128 `journal_replay_maybe_drop_overwrites`（按 seq_ondisk 边界丢弃未落盘记录） | 崩溃恢复 = 重放已落盘提交；未 flush 的提交丢弃。T0203 崩溃点 = 日志落盘 + engine.sync()（journal 落盘）后 abort ⇒ 全部已提交 op durable，与模型完全一致 |
| 事务提交顺序 = 持久化顺序 | T0199 并发矩阵实测（全局 fs 锁串行化提交）+ T0201 结论 | 多写者交错提交被 fs 锁串行化；T0203 提交日志在测试锁内追加 ⇒ 日志顺序 == 引擎提交顺序，是精确性的确定性来源 |
| 后台 alloc op 入口 | foreground.c 候选规则 / background.c 回收 / discard.c:643 darray / fast_work 单桶 / need_discard 树扫描 | 全部由 T0202 AC-1 锚点表固定，T0203 直接复用（组合 op 语义零改动） |

## 2. 复用锚点表（T0199/T0201/T0202 已核对，本任务直接继承）

| 设施 | 来源任务 | 锚点/模式 |
|------|---------|----------|
| BucketModel 三态（0=free/1=btree-owned/2=need-discard）+ VecDeque + queued[4] | T0202 | alloc 树 data_type 投影：value[1]>>48（bch_alloc_v4 布局），FREE=0、NEED_DISCARD=9；崩溃点重建 rebuild_bucket_state |
| 组合 op 语义（allocate/reclaim/queue/run_once/put/delete） | T0202 | foreground.c 候选规则（offset 升序第一个 free，-28 无候选）/ reclaim 守卫（-16/-11）+ 0↔2 toggle / queue 重复 -17 / once 空队 -11 回旋 |
| process_crash_child 子进程崩溃模式 | T0201 | 同二进制 env 分派 + Barrier + abort；崩溃点 = 日志落盘(sync_all) + engine.sync() + abort |
| 队列持久性语义 | T0202 | need_discard 树是持久队列（崩溃后树位保留）；darray 是纯内存态（open_persistent 不自动入队） |
| btree 内容精确断言 | T0201/T0202 | scan(DEFAULT) 全键 BTreeMap 对照 |

## 3. 新增点（仅测试侧，无引擎改动）

1. **并发组合计划生成器**：`plan_strategy`（WRITERS=3 × 6..=12 步，
   prop_oneof 六种 op）——测试设施，非运行逻辑。
2. **提交日志协议**：`encode_op/decode_op` 文本编码 + 日志行
   `<op> | <result>`；重放 `replay()` 依赖日志中的引擎实际结果
   （err 编码）做确定性模型转换——"日志 + 结果"二元组保证重放
   与真实提交序列同构（提交 = 日志追加与引擎提交在同一测试锁内，
   原子成对，锁序 == 引擎 fs 锁序）。
3. **alloc 树位投影**：rebuild_bucket_state 按 T0202 布局对齐
   （inode=0 且 offset∈[4,7] 过滤 + data_type 三态映射），崩溃后
   从持久 alloc 树重读。

## 4. 边界覆盖与上游对应

| 边界 | 触发方式 | 上游对应 |
|------|---------|---------|
| 空间耗尽 -28 | 4 桶域 × 并发 allocate 竞争 | foreground.c 无 free 候选 |
| 重复 queue -17 | 并发 Queue(0) 幂等 | discard.c darray 重复 in-flight EEXIST |
| worker 回旋 | 非 need-discard 队首（并发 reclaim/allocate 竞争状态） | discard.c fast_work 失败回旋队尾 |
| 空队 -11 | 无 queue 时 RunOnce | discard.c 空队列 |
