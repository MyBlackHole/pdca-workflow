# T0202 上游锚点记录（AC-1）

修改前逐段对照的本地 bcachefs-tools 源码与既有任务模式：

## 1. alloc 域 op 语义的上游对应

| 本项目 API | bcachefs 锚点 | 语义 |
|-----------|--------------|------|
| allocate_bucket（engine.rs:825） | foreground.c free-bucket 候选规则 | freespace 位 ∩ FREE 的 offset 升序第一个；置 BCH_DATA_BTREE、清 freespace 位；无候选 -28 |
| reclaim_bucket（engine.rs:978） | background.c 空桶回收 | 非 NEED_DISCARD → 置 NEED_DISCARD（gen/oldest_gen 递增）+ 清 freespace 位 + 置 need_discard 位；NEED_DISCARD 且 journal_seq_empty ≤ last_seq_ondisk → 回 FREE（置 freespace 位 + 清 need_discard 位）；守卫：open/非 rw/backpointer/脏扇区 → -16，NEED_DISCARD 且 seq 未落盘 → -11 |
| queue_discard_bucket（engine.rs:1195） | discard.c:643 bch2_fast_discard_bucket_add | 每设备 darray 入队；重复 in-flight → -17（EEXIST 边界）；**纯内存态** |
| run_discard_worker_once（engine.rs:1209） | discard.c fast_work 单桶路径 | pop_front → discard_bucket（守卫全过才 Ok）→ 失败 -11 回旋队尾；成功从 in-flight 集合移除 |
| discover_discard_buckets（engine.rs:1309） | discard.c for_each_btree_key 扫描 need_discard 树 | **need_discard 树是持久队列**（崩溃后树位保留）；discover 扫描树位并重新入队（insert + push_back），返回插入计数 |

## 2. alloc 键与 freespace 位维护（background.c:1113）

`alloc_freespace_pos(alloc_k.k->p, *a)` + `bch2_btree_bit_mod_iter(trans, &iter, set)`
——本项目 `add_free_bucket`（T0197 既有测试设施）等价：trigger_update_value
写 alloc_v4 记录（触发 alloc 触发器）+ bch2_btree_bit_mod 置 freespace 位。
data_type 常量：FREE=0、BTREE=3、NEED_DISCARD=9（engine.rs:84-86）。

## 3. T0197 模型结构（open_bucket_discard_model_protects_open_from_reuse）

- 影子状态 `[u8; 4]`（0=free/1=btree-owned/2=need-discard）+ `open [bool;4]` +
  `queued [bool;4]` + shadow_queue VecDeque + device_rw bool；op 0..8
  （queue/reclaim pass/allocate/reopen/open/close/set_rw）。
- ModelEngine Option 包装防 panic 遮蔽（引擎 panic 时模型不可见）、Drop 关闭 open 桶。
- **reopen 后队列重建**：discover 入队 → 模型 queued=true + push_back（树扫描键序
  = offset 升序）；alloc 树重读重建 state（1=btree-owned 保留）。
- 守卫裁决注入（T0197 核心）：open 不预判、由实现裁决（open_bucket 无守卫插入）。

## 4. crash_recovery_restores_sync_point_state 模式（btree_proptest.rs:294-326）

sync 点：`engine.sync().unwrap(); drop(engine); open_persistent; assert_model`——
journal 落盘后丢弃引擎模拟崩溃；恢复后 scan 必须精确等于快照时刻模型
（bcachefs：设备 btree + journal 窗口，read_btree_roots + bch2_journal_read）。

## 5. 组合模型设计推导

- 持久化引擎的 btree 数据全部走 journal（sync 只 flush journal，节点不写桶）→
  **桶 4..=7 状态仅由 alloc op 驱动，无 backpointer 干扰**（reclaim 的 -16 守卫
  恒不触发；T0201 并发测试实证 allocate+reclaim 并存）。
- 组合域守卫全不触发 → reclaim 恒成功（0↔2 toggle）；discard 恒成功（队首 state==2）。
- 崩溃恢复后 fast_discard 内存队列清空（darray 内存态），need_discard 树位保留
  → discover 是恢复入口（T0197 op4 模式）。
- 崩溃恢复精确断言成立（单线程顺序序列无注入，模型对照精确）。
