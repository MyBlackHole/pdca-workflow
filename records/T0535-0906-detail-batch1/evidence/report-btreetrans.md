# bcachefs btree 事务代码级精讲报告（扩充版）

> 根目录 `/home/black/Documents/bcachefs-tools`，只读核实。
> 精读 `fs/btree/iter.c`（4336行）、`fs/btree/commit.c`（1520行）、`fs/btree/update.c`（958行）、`fs/btree/update.h`（536行），辅以 `fs/btree/iter.h`（1310行）、`fs/btree/types.h`、`fs/btree/locking.c`、`fs/btree/write.c`、`fs/errcode.h`。
> 保留原报告八节结构，每节展开为逐函数精讲。所有函数名、签名均经 `grep`/`read` 核实，不编造行号，一律以“文件+函数名”定位。代码片段均≤10行。

---

## 一、全景：迭代器即事务

核心结论：bcachefs 没有独立 `transaction` 对象。`struct btree_trans`（`fs/btree/types.h`）即“一组持锁迭代器 + 更新队列 + bump内存 + journal/disk预留”。`begin` 取内存/清状态，`update` 排队，`commit` 一次落盘，失败按重启码重走。

### 1.1 `struct btree_trans` —— 事务即上下文容器

**签名（`fs/btree/types.h`）：**

```c
struct btree_trans {
  struct bch_fs *c;
  unsigned long *paths_allocated;
  struct btree_path *paths;
  btree_path_idx_t *sorted;
  struct btree_insert_entry *updates;
  void *mem; unsigned mem_top; unsigned mem_bytes;
  // ...锁/重启/预留/钩子/队列化bio...
  struct btree_trans_subbuf journal_entries;
  struct btree_trans_subbuf accounting;
  struct btree_trans_commit_hook *hooks;
  struct journal_res journal_res;
  struct bio *queued_write_bios;
  u32 restart_count; enum bch_errcode restarted:16;
};
```

**参数含义：** `c` 文件系统；`paths/updates` 迭代器与排队更新数组（与 `paths` 同一分配，见 `btree_paths_realloc`）；`mem/mem_top/mem_bytes` bump分配器；`journal_entries/accounting` 子缓冲；`hooks` 提交钩子单链表；`queued_write_bios` 队列化写；`restarted/restart_count` 重启码系状态。

**返回语义：** 无，类型定义。

**调用链位置：** 一切 `CLASS(btree_trans, trans)(c)`、`bch2_trans_run`、`for_each_btree_key*`、`commit_do` 的载体。

**关键片段（`types.h`注释，原样）：**

```c
/* bump allocator, invalidated on transaction restart */
void *mem;
unsigned mem_top;
```

```c
/* Entries before this are zeroed out on every bch2_trans_get() call */
```

**设计权衡：** 把锁、内存、更新、预留、钩子、bio队列塞进一个结构体，换来“事务边界=锁持有边界”，语义清晰但结构体庞大（700+行定义域）。零散分配全部收敛到 `mem`，重启即作废，避免跨重启悬垂指针。

### 1.2 `__bch2_trans_get` / `bch2_trans_put` —— 事务获取与释放

**签名（`fs/btree/iter.h` / `fs/btree/iter.c`）：**

```c
struct btree_trans *__bch2_trans_get(struct bch_fs *c, unsigned fn_idx);
void bch2_trans_put(struct btree_trans *trans);
```

**参数含义：** `c` 文件系统；`fn_idx` 事务命名索引（用于 `btree_transaction_stats` 与 `trans->fn` 追踪）；`trans` 待释放事务。

**返回语义：** `__bch2_trans_get` 返回已初始化事务（含 SRCU 读锁、`paths/updates` 指向内嵌数组、`mem` 按历史 `max_mem` 预热）；`put` 无返回，校验无泄漏 path、有更新必已提交/丢弃后归还 mempool/percpu缓存。

**调用链位置：** `CLASS(btree_trans)` → `__bch2_trans_get` … `bch2_trans_put`。最外层 RAII；中间可多次 `bch2_trans_begin` + `commit`。

**关键片段（`iter.c:__bch2_trans_get`）：**

```c
trans->nr_paths = ARRAY_SIZE(trans->_paths);
trans->paths = trans->_paths;
trans->updates = trans->_updates;
trans->srcu_idx = srcu_read_lock(&c->btree.trans.barrier);
trans->srcu_held = true;
```

**关键片段（`iter.c:bch2_trans_put`）：**

```c
trans_for_each_update(trans, i)
  __btree_path_put(trans, trans->paths + i->path, true);
if (trans->used_mempool)
  mempool_free(trans->mem, &c->btree.trans.malloc_pool);
```

**设计权衡：** `get` 预热 `mem`（按 `s->max_mem` 的 `roundup_pow_of_two`），用空间换重启次数；`put` 严格 `check_btree_paths_leaked` + `restarted` 必空，否则 panic。用 per-CPU `trans` 缓存 + mempool 避免高频 `kmalloc`，但要求调用方绝不跨 `put` 持有 `mem` 指针。

### 1.3 `bch2_trans_begin` —— 重启即重置

**签名（`fs/btree/iter.h` / `fs/btree/iter.c`）：**

```c
u32 bch2_trans_begin(struct btree_trans *trans);
```

**参数含义：** `trans` 当前事务。

**返回语义：** 返回本次 `restart_count`，供 `bch2_trans_verify_not_restarted(trans, restart_count)` / `trans_was_restarted` 对比。若期间发生重启则计数值不等，触发 `nested` 上报或 panic。

**调用链位置：** 所有 `lockrestart_do`、`for_each_btree_key*`、`commit_do` 循环头；`__bch2_trans_commit` 出错 `retry` 前亦经 `begin` 重建锁序。

**关键片段（`iter.c:bch2_trans_begin`）：**

```c
WARN_ON_ONCE(bch2_trans_has_updates(trans) &&
             !trans->restarted && !trans->in_traverse_all &&
             !trans->begin_may_drop_updates);
bch2_trans_reset_updates(trans);
trans->restart_count++;
trans->mem_top = 0;
```

**设计权衡：** `mem_top=0` 即“重启作废”，O(1) 回收，禁止 `free`。`WARN_ON_ONCE` 捕捉“忘记 commit 就 begin”丢更新 bug，以 loud-fail 换静默丢数据。非重启 `begin` 会丢弃空闲 path（除 `subvolumes`），以 path 重建成本换锁顺序确定性。

### 1.4 `lockrestart_do` / `nested_lockrestart_do` / `commit_do` —— 重启循环宏

**签名（`fs/btree/iter.h` 宏，`fs/btree/update.h` 宏）：**

```c
#define lockrestart_do(_trans, _do)
#define nested_lockrestart_do(_trans, _do)
#define commit_do(_trans, _disk_res, _journal_seq, _flags, _do)
#define nested_commit_do(_trans, _disk_res, _journal_seq, _flags, _do)
```

**参数含义：** `_trans` 事务；`_do` 本体表达式；`commit_do` 另带 `disk_res/journal_seq/flags`。

**返回语义：** 循环直到返回值不匹配 `BCH_ERR_transaction_restart` 类。`nested_*` 不预先 `begin`，成功但中间重启过则返回 `-BCH_ERR_transaction_restart_nested` 向外层报告“我重走过，外层缓存可能已 stale”。

**调用链位置：** 几乎所有 btree 读写模板：`for_each_btree_key`、`bch2_btree_insert`、`btree_node_write_update_key`。

**关键片段（`iter.h:nested_lockrestart_do`）：**

```c
_restart_count = _orig_restart_count = (_trans)->restart_count;
(_trans)->begin_may_drop_updates = true;
while (bch2_err_matches(_ret2 = (_do), BCH_ERR_transaction_restart))
  _restart_count = bch2_trans_begin(_trans);
_ret2 ?: trans_was_restarted(_trans, _orig_restart_count);
```

**设计权衡：** 把“重试”从业务代码抽离为宏，保证“任何 restart 码必重走”。`nested` 变体解决“内层提交丢弃外层排队更新”场景：fsck 计数、`reconcile` 等长事务必须显式传播 `nested`，否则外层用 stale 读做决策。

**可学：** 事务不必是独立抽象；迭代器+更新队列+重启计数器就是事务。边界清晰（锁持有期）则语义清晰。

---

## 二、内存：bump分配加重启作废

### 2.1 `bch2_trans_kmalloc_ip` / `bch2_trans_kmalloc_nomemzero_ip` —— 快道

**签名（`fs/btree/iter.h`）：**

```c
static __always_inline void *bch2_trans_kmalloc_ip(struct btree_trans *trans, size_t size, unsigned long ip);
static __always_inline void *bch2_trans_kmalloc_nomemzero_ip(struct btree_trans *trans, size_t size, unsigned long ip);
static __always_inline void *bch2_trans_kmalloc(struct btree_trans *trans, size_t size);
```

**参数含义：** `trans` 事务；`size` 请求字节（内部 `roundup(size,8)`）；`ip` 调用地址（`_THIS_IP_`，用于 kmalloc trace / debug 归因）。

**返回语义：** 成功返回 `trans->mem+mem_top` 并前移 `mem_top`（`kmalloc` 版附带 `memset 0`）；快道装不下则ตก入 `__bch2_trans_kmalloc` 慢道（可能返回 `ERR_PTR(-BCH_ERR_...)` 或触发重启）。

**调用链位置：** `bch2_bkey_make_mut`、`bch2_trans_update` 排队、`__bch2_insert_snapshot_whiteouts`、`bch2_trigger_get_mutable_new` 等一切事务内分配。

**关键片段（`iter.h`）：**

```c
size = roundup(size, 8);
if (likely(trans->mem_top + size <= trans->mem_bytes)) {
  void *p = trans->mem + trans->mem_top;
  trans->mem_top += size;
  memset(p, 0, size);
  return p;
} else {
  return __bch2_trans_kmalloc(trans, size, ip);
}
```

**设计权衡：** 8字节对齐换 `bkey` 的 u64 访问安全；`memset 0` 默认版防信息泄漏/`u64s`  widen 后尾部垃圾，`nomemzero` 版给 `subbuf` 这类马上全覆盖的路径省 memset。快道无锁、无失败（除重启态），代价是禁止 `free`、禁止跨 `begin` 持有指针。

### 2.2 `__bch2_trans_kmalloc` —— 慢道：扩容、重启、内存池

**签名（`fs/btree/iter.h` 声明，`fs/btree/iter.c` 定义）：**

```c
void *__bch2_trans_kmalloc(struct btree_trans *trans, size_t size, unsigned long ip);
```

**参数含义：** 同上，`size` 已对齐后大小。

**返回语义：** ① `new_bytes>BTREE_TRANS_MEM_MAX(1U<<16)` 直接 `ERR_PTR(-BCH_ERR_ENOMEM_trans_kmalloc)`；② `old_bytes!=0` 说明已持有缓冲需扩容 → 置 `realloc_bytes_required` 并返回 `ERR_PTR(BCH_ERR_transaction_restart_mem_realloced)`，由下次 `bch2_trans_begin` 真正 `krealloc`；③ `old_bytes==0` 首次分配 → `allocate_dropping_locks_norelock(kmalloc)`，失败则 `mempool_alloc(...malloc_pool)` + 置 `used_mempool` + `new_bytes=BTREE_TRANS_MEM_MAX`。

**调用链位置：** 仅快道溢出时进入；扩容重启后 `bch2_trans_begin` 接管 `krealloc`。

**关键片段（`iter.c`）：**

```c
unsigned new_bytes = roundup_pow_of_two(new_top);
if (trans->used_mempool || new_bytes > BTREE_TRANS_MEM_MAX)
  return ERR_PTR(-BCH_ERR_ENOMEM_trans_kmalloc);
if (old_bytes) {
  trans->realloc_bytes_required = new_bytes;
  return ERR_PTR(bch2_trans_restart_ip(trans,
    BCH_ERR_transaction_restart_mem_realloced, _RET_IP_));
}
```

```c
new_mem = allocate_dropping_locks_norelock(trans, lock_dropped,
            kmalloc(new_bytes, _gfp|__GFP_NOWARN));
if (!new_mem) {
  new_mem = mempool_alloc(&c->btree.trans.malloc_pool, GFP_KERNEL);
  new_bytes = BTREE_TRANS_MEM_MAX;
  trans->used_mempool = true;
}
```

**设计权衡：** 幂次扩容摊薄 `krealloc` 次数；“先重启、再扩容”避免持锁 `krealloc` 睡眠；`mempool` 保底 64K 但置 `used_mempool` 后此事务内不再扩容（防爆内存），后续超限直接 ENOMEM。`trans_maybe_inject_restart` 故障注入亦在此，便于压测重启路径。

### 2.3 `bch2_trans_begin` 中的 `mem_realloced` 分支

**签名：** 同 1.3，分支位于 `iter.c:bch2_trans_begin` 内：

```c
if (unlikely(trans->restarted == BCH_ERR_transaction_restart_mem_realloced)) { ... krealloc ... }
```

**参数/返回：** 无额外参数；若 `krealloc` 仍失败则退化为 mempool 64K。

**关键片段：**

```c
void *new_mem = allocate_dropping_locks_norelock(trans, lock_dropped,
          krealloc(trans->mem, new_bytes, _gfp));
if (!new_mem) {
  new_mem = mempool_alloc(&trans->c->btree.trans.malloc_pool, GFP_KERNEL);
  new_bytes = BTREE_TRANS_MEM_MAX;
  trans->used_mempool = true;
  kfree(trans->mem);
}
```

**设计权衡：** 把可能睡眠的 `krealloc` 推迟到 `begin`（已 `reset_updates`、锁已释放语义），避免在持有 btree 写锁时扩内存导致死锁。

### 2.4 `btree_trans_subbuf` 系 —— journal/accounting 子分配器

**签名（`fs/btree/update.h` / `fs/btree/update.c`）：**

```c
void *__bch2_trans_subbuf_alloc(struct btree_trans *trans, struct btree_trans_subbuf *buf, unsigned u64s, ulong ip);
int bch2_trans_subbuf_reserve(struct btree_trans *trans, struct btree_trans_subbuf *buf, unsigned u64s);
static inline void *bch2_trans_subbuf_alloc_ip(struct btree_trans *trans, struct btree_trans_subbuf *buf, unsigned u64s, ulong ip);
```

**参数含义：** `buf` 为 `trans->journal_entries` 或 `trans->accounting`；`u64s` 以 u64 为单位；`subbuf` 内 `base/u64s/size` 均为相对 `trans->mem` 的 u16 偏移（`BUG_ON(roundup_pow_of_two(new_top)>U16_MAX)`）。

**返回语义：** 快道 `buf->u64s+u64s<=buf->size` 直接返回 `top`；否则经 `bch2_trans_kmalloc_nomemzero_ip(new_size*sizeof(u64))` 整体搬迁（`memcpy` 旧内容），返回新 top。`reserve` 只预留不推进 `u64s`（供 atomic trigger 预增长）。

**调用链位置：** `bch2_trans_jset_entry_alloc`（write_buffer/日志）、`bch2_trans_log_str/bkey`、`do_bch2_trans_commit` 预增长 `extra_journal_u64s`。

**关键片段（`update.c:__bch2_trans_subbuf_alloc`）：**

```c
void *n = bch2_trans_kmalloc_nomemzero_ip(trans, new_size * sizeof(u64), ip);
unsigned offset = (u64 *) n - (u64 *) trans->mem;
if (buf->u64s)
  memcpy(n, btree_trans_subbuf_base(trans, buf), buf->u64s * sizeof(u64));
buf->base = (u64 *) n - (u64 *) trans->mem;
```

**设计权衡：** 子缓冲不独立 `kmalloc`，而是复用 bump 区，避免碎片；用 u16 偏移省空间，但限制单缓冲 64K u64s——与 `BTREE_TRANS_MEM_MAX` 自洽。搬迁时整体 `memcpy`，O(n) 但发生频率低（幂次增长）。

### 2.5 `bch2_trans_commit_lazy_if_full` —— 修复循环防爆内存

**签名（`fs/btree/update.h`）：**

```c
static inline int bch2_trans_commit_lazy_if_full(struct btree_trans *trans, struct disk_reservation *disk_res, u64 *journal_seq, unsigned flags);
static inline int bch2_trans_commit_lazy(struct btree_trans *trans, struct disk_reservation *disk_res, u64 *journal_seq, unsigned flags);
```

**参数含义：** `trans/disk_res/journal_seq/flags` 同普通 commit；`lazy` 版成功后返回 `transaction_restart_commit` 而非 0，强制调用方重驱。

**返回语义：** `mem_top < BTREE_TRANS_MEM_MAX/4` 直接返回 0（不提交）；否则 `bch2_trans_commit_lazy` 提交部分批并返回 restart，调用方重走。注释明示“重驱必须收敛：已提交修复下次跳过，否则同点再触发无法前进”。

**调用链位置：** `__bch2_insert_snapshot_whiteouts` 的 fsck 分支（白洞扇出 unbounded）、`fs/check.c`、`check_extents.c` 批量修复。

**关键片段：**

```c
return likely(trans->mem_top < BTREE_TRANS_MEM_MAX / 4)
  ? 0
  : bch2_trans_commit_lazy(trans, disk_res, journal_seq, flags);
```

**设计权衡：** 1/4 阈值留足 `disk_accounting_mod` 幂次分配余量（注释明示 `max/2 too small`）；以多次小提交换单事务不爆 64K。要求调用方幂等可重入，否则 livelock。

**可学：** 事务内存 bump+重启作废，禁止事务内 free；快道对齐分配、幂次扩容、64K封顶转 mempool、修复循环 lazy 提交，四层防线缺一不可。

---

## 三、更新排队：trans_update

### 3.1 `bch2_trans_update_ip` / `bch2_trans_update` —— 唯一排队入口

**签名（`fs/btree/update.h` / `fs/btree/update.c`）：**

```c
int __must_check bch2_trans_update_ip(struct btree_trans *trans, struct btree_iter *iter, struct bkey_i *k, unsigned k_buf_u64s, enum btree_iter_update_trigger_flags flags, unsigned long ip);
static inline int bch2_trans_update(struct btree_trans *trans, struct btree_iter *iter, struct bkey_i *k, enum btree_iter_update_trigger_flags flags);
```

**参数含义：** `trans` 事务；`iter` 已 `traverse` 且 `should_be_locked` 的迭代器（`k->k.p` 必须等于 `iter->pos`，debug 下 `BUG_ON`）；`k` 新键（`trans->mem` 内，提交前仅为意图）；`k_buf_u64s` 缓冲实际容量（≥`k->k.u64s`，供 trigger 增长）；`flags` 如 `BTREE_UPDATE_internal_snapshot_node/overwrite_triggered/norun`；`ip` 分配点。

**返回语义：** extent 表自动分流 `bch2_trans_update_extent`；非 extent 走 `btree_trans_update_by_path` 排序插入 `trans->updates`。删除+快照过滤时自动转 `whiteout`。key-cache 表自动转 key-cache 路径并可能 `flush_new_cached_update`。错误返回负值（含 restart）。

**调用链位置：** 所有写入口的收敛点：`bch2_btree_insert_*`、`bch2_btree_delete_at`、`bch2_btree_bit_mod_iter`、`bch2_trans_update_extent_overwrite` 切片。

**关键片段（`update.c:bch2_trans_update_ip` 前分流）：**

```c
if (iter->flags & BTREE_ITER_is_extents)
  return bch2_trans_update_extent(trans, iter, k, k_buf_u64s, flags);
if (bkey_deleted(&k->k) &&
    !(flags & BTREE_UPDATE_key_cache_reclaim) &&
    (iter->flags & BTREE_ITER_filter_snapshots)) {
  int ret = need_whiteout_for_snapshot(trans, iter->btree_id, k->k.p);
  if (ret)
    k->k.type = KEY_TYPE_whiteout;
}
```

**设计权衡：** `__must_check` 强制检查返回值（漏检 restart 即 use-after-restart）；`k_buf_u64s` 与 `k->k.u64s` 分离，允许 trigger 原地增长而不重排队。快照/缓存/extent 三种特殊语义全部收敛于此，调用方无需分支。

### 3.2 `btree_trans_update_by_path` —— 有序排队与覆盖合并

**签名（`fs/btree/update.c`）：**

```c
static struct btree_insert_entry *btree_trans_update_by_path(struct btree_trans *trans, btree_path_idx_t path_idx, struct bkey_i *k, unsigned k_buf_u64s, enum btree_iter_update_trigger_flags flags, unsigned long ip);
```

**参数含义：** `path_idx` 以 `iter->update_path ?: iter->path` 解析（快照过滤时 `update_path` 才是真实写位置）；`k/k_buf_u64s/flags/ip` 同上。

**返回语义：** 返回队列中该条目指针（注意 trigger 可能使 `trans->updates` 搬迁，指针不可长期持有）。按 `btree_insert_entry_cmp(sort_order,cached,-level,pos)` 有序插入；同键覆盖则复用槽位（`overwrite`），并 `EBUG_ON` 已跑过 trigger 又被覆盖（除非 `overwrite_triggered`）。

**调用链位置：** `bch2_trans_update_ip`（非 extent）与 `bch2_trans_update_extent_overwrite` 的 back-split 分支。

**关键片段：**

```c
n = (struct btree_insert_entry) {
  .flags = flags,
  .sort_order = btree_trigger_order(path->btree_id),
  .bkey_type = __btree_node_type(path->level, path->btree_id),
  .level = path->level, .cached = path->cached,
  .k_buf_u64s = k_buf_u64s, .path = path_idx, .k = k,
};
for (i = trans->updates; i < trans->updates + trans->nr_updates; i++) {
  cmp = btree_insert_entry_cmp(&n, i);
  if (cmp <= 0) break;
}
```

```c
i->old_v = bch2_btree_path_peek_slot_exact(path, &i->old_k).v;
```

**设计权衡：** 排队时即抓 `old_k/old_v`，供 trigger 的 old/new 对比与 journal overwrite 日志。排序键把 `sort_order`（按 btree 分配条带）放首位，保证触发器按死锁安全序执行；`cached` 次之，保证 key-cache 刷新先行。用 `array_insert_item` O(n) 插入，`nr_updates` 通常小（`BTREE_ITER_INITIAL` 量级），以简单换正确。

### 3.3 `bch2_trans_update_extent` / `extent_front_merge` / `extent_back_merge` —— extent 排队前规整

**签名（`fs/btree/update.c`）：**

```c
static int bch2_trans_update_extent(struct btree_trans *trans, struct btree_iter *orig_iter, struct bkey_i *insert, unsigned k_buf_u64s, enum btree_iter_update_trigger_flags flags);
static noinline int extent_front_merge(struct btree_trans *trans, struct btree_iter *iter, struct bkey_s_c k, struct bkey_i **insert, unsigned *k_buf_u64s, enum btree_iter_update_trigger_flags flags);
static noinline int extent_back_merge(struct btree_trans *trans, struct btree_iter *iter, struct bkey_i *insert, struct bkey_s_c k);
```

**参数含义：** `orig_iter/insert` 待插 extent；`k` 相邻盘上 extent；`flags` 透传。

**返回语义：** 前向可合并则 `delete_at` 前邻 + 扩大 `insert`；重叠则逐个 `bch2_trans_update_extent_overwrite` 切片；后向可合并则原地 `bch2_bkey_merge`。有快照覆盖（`bch2_key_has_snapshot_overwrites`）则禁止合并。最终非删除 `insert` 走 `bch2_btree_insert_nonextent` 排队。

**调用链位置：** `bch2_trans_update_ip` 的 extent 分支独占。

**关键片段（`update.c`）：**

```c
if (bkey_eq(k.k->p, bkey_start_pos(&insert->k))) {
  if (bch2_bkey_maybe_mergable(k.k, &insert->k))
    try(extent_front_merge(trans, &iter, k, &insert, &k_buf_u64s, flags));
  goto next;
}
```

**设计权衡：** 合并前查快照覆盖，避免合并后快照语义丢失；`journal_replay_not_finished` 时跳过合并（回放期只求确定性）。`noinline` 将冷合并移出热路径，保 icache。

### 3.4 `need_whiteout_for_snapshot` / `__bch2_insert_snapshot_whiteouts` / `bch2_insert_snapshot_whiteouts` / `extent_whiteout_type` —— 白洞

**签名：**

```c
static int need_whiteout_for_snapshot(struct btree_trans *trans, enum btree_id btree_id, struct bpos pos);
int __bch2_insert_snapshot_whiteouts(struct btree_trans *trans, enum btree_id btree, struct bpos pos, snapshot_id_list *s);
static inline int bch2_insert_snapshot_whiteouts(struct btree_trans *trans, enum btree_id btree, struct bpos old_pos, struct bpos new_pos);
static inline enum bch_bkey_type extent_whiteout_type(struct bch_fs *c, enum btree_id btree, const struct bkey *k);
```

**参数含义：** `pos/old_pos/new_pos` 待删/覆盖位置；`s` 后代快照 id 列表（`bch2_get_snapshot_overwrites` 求得）；`k` 待插键（决定用 `whiteout` 还是 `extent_whiteout`）。

**返回语义：** `need_whiteout` 以 `for_each_btree_key_norestart(all_snapshots)` 查后代是否可见，返回 0/1；`__bch2_insert...` 对每个后代 `peek_slot`，若为 `deleted` 则排队一个 `KEY_TYPE_whiteout`；`extent_whiteout_type` 在 extents+快照+叶快照+旧版本无 `extent_snapshot_whiteouts` 特性时选 `extent_whiteout`，否则 `whiteout`。

**调用链位置：** 删除/覆盖排队时（`bch2_trans_update_ip`、`bch2_trans_update_extent_overwrite` 前/中/后切片）。

**关键片段（`update.c:__bch2_insert_snapshot_whiteouts`）：**

```c
if (test_bit(BCH_FS_in_fsck, &trans->c->flags))
  try(bch2_trans_commit_lazy_if_full(trans, NULL, NULL,
            BCH_TRANS_COMMIT_no_enospc));
pos.snapshot = *id;
CLASS(btree_iter, iter)(trans, btree, pos, BTREE_ITER_not_extents|BTREE_ITER_intent);
struct bkey_s_c k = bkey_try(bch2_btree_iter_peek_slot(&iter));
if (k.k->type == KEY_TYPE_deleted) {
  update->k.type = KEY_TYPE_whiteout;
  try(bch2_trans_update(trans, &iter, update,
            BTREE_UPDATE_internal_snapshot_node));
}
```

**设计权衡：** 白洞只在“祖先被覆盖但后代仍可见”时 emitted，避免白洞爆炸；fsck 扇出时 `lazy_if_full` 分段提交，以“重驱跳过已提交（`deleted` 检查）”保证收敛。`extent_whiteout` 让 `bkey_start_pos` 单调递增，使 `@end` 能终止扫描（见 `btree_iter_filter_snapshots` 注释），否则白洞海会拖慢范围扫描。

### 3.5 `bch2_trans_update_get_key_cache` / `flush_new_cached_update` —— 缓存一致排队

**签名：**

```c
static noinline int bch2_trans_update_get_key_cache(struct btree_trans *trans, struct btree_iter *iter);
static noinline int flush_new_cached_update(struct btree_trans *trans, struct btree_insert_entry *i, enum btree_iter_update_trigger_flags flags, unsigned long ip);
```

**参数含义：** `iter` 原 btree 迭代器；`i` 已排队条目。

**返回语义：** 若目标 btree 可缓存（`alloc/inodes/logged_ops/stripes/subvolumes`）且 path 非缓存，则建/定位 `key_cache_path` 并 `traverse`，脏则 restart（`key_cache_raced`）；若新键在缓存而 btree 无对应（或需立即刷），则把更新搬到 btree path 并标记 `key_cache_flushing`，保证“缓存有则 btree 必有”。

**关键片段：**

```c
if (test_bit(BKEY_CACHED_DIRTY, &ck->flags)) {
  event_inc_trace(trans->c, trans_restart_key_cache_raced, ...);
  return btree_trans_restart(trans, BCH_ERR_transaction_restart_key_cache_raced);
}
```

**设计权衡：** 读路径依赖“btree 存在性蕴含缓存可见性”，写路径必须反向维护该不变式。以一次额外 `traverse` + 偶发 restart 换读路径无锁快速。

### 3.6 `bch2_btree_insert_*` / `bch2_btree_delete_*` / `bch2_btree_bit_mod_*` —— 删插改统一入口

**签名（`fs/btree/update.c`）：**

```c
int bch2_btree_insert_nonextent(struct btree_trans *trans, enum btree_id btree, struct bkey_i *k, unsigned k_buf_u64s, enum btree_iter_update_trigger_flags flags);
int bch2_btree_insert_trans(struct btree_trans *trans, enum btree_id btree, struct bkey_i *k, enum btree_iter_update_trigger_flags flags);
int bch2_btree_insert(struct bch_fs *c, enum btree_id id, struct bkey_i *k, struct disk_reservation *disk_res, enum bch_trans_commit_flags commit_flags, enum btree_iter_update_trigger_flags iter_flags);
int bch2_btree_delete_at(struct btree_trans *trans, struct btree_iter *iter, enum btree_iter_update_trigger_flags flags);
int bch2_btree_delete(struct btree_trans *trans, enum btree_id btree, struct bpos pos, enum btree_iter_update_trigger_flags flags);
int bch2_btree_bit_mod_iter(struct btree_trans *trans, struct btree_iter *iter, bool set);
```

**参数/返回：** `nonextent` 自建 `not_extents+intent` 迭代器后 `traverse+update_ip`；`insert_trans` 同理但保留调用方 extent 语义；顶层 `insert` 自建 trans 并 `commit_do`；`delete_at` 构造空 `bkey_i`（`bkey_init`，`p=iter->pos`）再 `trans_update`；`bit_mod` 构造 `set/deleted` 单点键。

**设计权衡：** 删除即“插空键”，位修改即“插 set/白键”，三者统一为排队，提交、触发器、journal 日志全复用。顶层 `insert/delete_range` 自带 `commit_do`，事务内版（`*_trans`）只排队不提交，职责分离。

**可学：** 写必须排队，提交前全是意图，可审计（`bch2_trans_updates_to_text`）、可丢弃（`reset_updates`）、可排序（`sort_order`）。

---

## 四、提交：错误码驱动重启

### 4.1 重启码系总表（`fs/errcode.h:BCH_ERRCODES` 实测）

父类 `x(0, transaction_restart)`，子类全部 `x(BCH_ERR_transaction_restart, ...)`，`bch2_err_matches(ret, BCH_ERR_transaction_restart)` 匹配整个家族：

```
fault_inject / relock / relock_path / relock_path_intent
too_many_iters / lock_node_reused / fill_relock / fill_mem_alloc_fail
lock_waitlist_alloc / mem_realloced / in_traverse_all
would_deadlock / would_deadlock_write / deadlock_recursion_limit / deadlock_waitlist_alloc
upgrade / key_cache_fill / key_cache_raced / lock_root_race
split_race / split_with_interior_updates / write_buffer_flush
nested / commit / journal_overwrites_changed
```

另有 `ENOMEM_trans_kmalloc`（`bch2_trans_kmalloc` 封顶）、`btree_insert_btree_node_full / need_mark_replicas / need_journal_reclaim`（提交内部分流，非 restart 但会转 restart 或降锁重试）。

**设计权衡：** 重启原因必须编码为独立子码，而非裸 `-EAGAIN`。调用方凭码决策：`relock` 系可立即重走，`mem_realloced` 需先扩容，`nested/commit` 需向外层传播，`fault_inject` 仅测试。`bch2_trans_commit_error` 尾部 `BUG_ON(matches_restart != !!trans->restarted)` 强制“码与标志一致”，防漏置/误置。

### 4.2 `bch2_trans_restart_ip` / `bch2_trans_restart_foreign_task` —— 置码

**签名（`fs/btree/iter.c` / `fs/btree/iter.h`）：**

```c
int bch2_trans_restart_ip(struct btree_trans *trans, int err, unsigned long ip);
int bch2_trans_restart_foreign_task(struct btree_trans *trans, int err, unsigned long ip);
__always_inline static int btree_trans_restart(struct btree_trans *trans, int err);
```

**参数含义：** `err` 正错误码（如 `BCH_ERR_transaction_restart_relock`）；`ip` 重启发起点（`_THIS_IP_/_RET_IP_`）。

**返回语义：** 置 `trans->restarted=err`、`last_restarted_ip=ip`（debug 再存 backtrace），返回 `-err`。`BUG_ON(!matches_restart)` 保证只能用 restart 码置位。

**调用链位置：** 锁失败、内存扩容、key-cache 竞争、journal 改名、分裂带内更新等一切需重走处。

**关键片段：**

```c
trans->restarted = err;
trans->last_restarted_ip = ip;
return -err;
```

### 4.3 `__bch2_trans_commit` —— 提交总驱

**签名（`fs/btree/commit.c`）：**

```c
int __bch2_trans_commit(struct btree_trans *trans, enum bch_trans_commit_flags flags, bool lazy);
```

**参数含义：** `trans` 排队事务；`flags` 含 watermark（低3位）+ `no_enospc/no_check_rw/no_journal_res/no_skip_noops/journal_reclaim/journal_replay/skip_accounting_apply`；`lazy` 为真则成功转 `transaction_restart_commit`。

**返回语义：** 0 成功（`lazy` 时为 `-transaction_restart_commit`）；restart 码经 `bch2_trans_commit_error` 处理后为 0 则 `goto retry`，否则带出由外层 `lockrestart` 重走；硬错（validate/fatal）直接返回。

**调用链位置：** `bch2_trans_commit/commit_flush/commit_lazy`（`update.h` 内联，负责填 `disk_res/journal_seq/flush`）→ `__bch2_trans_commit` → `run_triggers → 升级锁/noop裁剪/merge → do_bch2_trans_commit → commit_error/retry`。

**关键片段（`commit.c:__bch2_trans_commit` 骨架）：**

```c
if (!bch2_trans_has_updates(trans))
  goto out_reset;
ret = bch2_trans_commit_run_triggers(trans);
if (ret) goto out_reset;
// noop裁剪 + path升级 + merge + extra_disk_res
retry:
  ret = do_bch2_trans_commit(trans, flags, &errored_at, _RET_IP_);
  if (ret) goto err;
  trans->commit_count++;
err:
  ret = bch2_trans_commit_error(trans, flags, errored_at, ret, _RET_IP_);
  if (ret) goto out;
  goto retry;
```

**设计权衡：** `journal_u64s` 先算后用，`no_journal_res` 路径复用传入 `seq`；`lazy` 成功伪装成 restart，强迫长循环重驱，避免单事务无限膨胀。注释明示“真错不可伪装成 restart，否则无限重试”。

### 4.4 `__bch2_trans_commit_error` / `bch2_trans_commit_error` —— 分码处理

**签名（`fs/btree/commit.c`）：**

```c
static int __bch2_trans_commit_error(struct btree_trans *trans, unsigned flags, struct btree_insert_entry *i, int ret, unsigned long trace_ip);
static noinline int bch2_trans_commit_error(struct btree_trans *trans, unsigned flags, struct btree_insert_entry *i, int ret, unsigned long trace_ip);
```

**参数含义：** `i` 停滞条目（`stopped_at`，分裂/锁失败定位）；`ret` 负错误码；`flags` 提交标志。

**返回语义：**

- `journal_res_blocked` + `journal_reclaim` 且 watermark 不足 → `journal_reclaim_would_deadlock` 硬错；
- `btree_insert_btree_node_full` → 有 extent 则提 watermark 重试，`bch2_btree_split_leaf`，若 `has_interior_updates` 则 `split_with_interior_updates` 重启（分裂与内点更新不可同事务）；
- `need_mark_replicas` → 降锁 `bch2_accounting_update_sb` 后重试；
- `need_journal_reclaim` → 解锁等 `journal.reclaim_wait` 后 `relock`；
- `no_journal_res` 成功路径 → 强制 `nested` 重启（因此次用了别人的 journal_res）；
- 尾部一致性断言 + `no_enospc` 下 ENOSPC 即 `fs_inconsistent`。

**关键片段：**

```c
case -BCH_ERR_btree_insert_btree_node_full:
  if (trans_commit_has_extents(trans))
    flags = btree_update_set_watermark_hipri(flags);
  ret = bch2_btree_split_leaf(trans, i->path, i->k->k.u64s, flags);
  if (!ret && trans->has_interior_updates)
    return btree_trans_restart(trans,
             BCH_ERR_transaction_restart_split_with_interior_updates);
```

```c
BUG_ON(bch2_err_matches(ret, BCH_ERR_transaction_restart) != !!trans->restarted);
```

### 4.5 `bch2_trans_journal_res_get` / `journal_transaction_names_changed` / `trans_commit_to_journal_replay_*` —— 日志协同重启

**签名（`fs/btree/commit.c`）：**

```c
static __always_inline int bch2_trans_journal_res_get(struct btree_trans *trans, unsigned flags);
static int journal_transaction_names_changed(struct btree_trans *trans);
static int trans_commit_to_journal_replay_pre(struct btree_trans *trans, enum bch_trans_commit_flags flags);
static void trans_commit_to_journal_replay_post(struct btree_trans *trans, int ret);
```

**参数/返回：** `flags` 含 watermark；`pre` 持 `overwrite_lock` 后若 `journal_replay` 且覆盖集变化则 `journal_overwrites_changed` 重启；`journal_res_get` 后若 `has_overwrites != journal_transaction_names`（并发改名）则放预留并同码重启。

**关键片段：**

```c
try(bch2_journal_res_get(j, &trans->journal_res, trans->journal_u64s, flags, trans));
if (unlikely(trans->journal_res.has_overwrites != trans->journal_transaction_names))
  return journal_transaction_names_changed(trans);
```

**设计权衡：** 日志预留与覆盖语义是跨事务共享可变状态，必须以 restart 而非锁等待解决竞争，否则提交持 btree 写锁等 journal 会死锁。

### 4.6 `update_is_noop` / `trans_commit_merge` / `bch2_trans_commit_extra_disk_res` —— 提交前规整

**签名：**

```c
static inline bool update_is_noop(struct btree_insert_entry *i, enum bch_trans_commit_flags flags);
static int trans_commit_merge(struct btree_trans *trans, enum bch_trans_commit_flags flags, struct btree_insert_entry **ip, struct btree_insert_entry **dstp);
noinline __cold static int bch2_trans_commit_extra_disk_res(struct btree_trans *trans, enum bch_trans_commit_flags flags);
```

**参数/返回：** `is_noop` 比较 `old` 与 `new`（`bkey_and_val_eq`），`inodes` 永不裁（fsync 依赖 journal_seq 前进）、`no_skip_noops` 禁裁；`merge` 在 `btree_node_needs_merge` 时前台合并空节点；`extra_disk_res` 为压缩 extent 切片追加预留（`update.c` 切片时累加）。

**设计权衡：** 提交前裁 noop 省 journal 带宽，但 inodes 例外保留语义正确性；merge 与额外预留都放在“拿 journal 预留之前”，失败仍可无代价 restart。

**可学：** 重启原因必须编码，调用方凭码决策；提交内部分流（分裂/配额/journal回收）一律收敛到 restart 或降锁重试，绝不裸重试。

---

## 五、钩子链与定序

### 5.1 `bch2_trans_commit_hook` —— 单链表追加

**签名（`fs/btree/update.c`）：**

```c
void bch2_trans_commit_hook(struct btree_trans *trans, struct btree_trans_commit_hook *h);
```

**参数含义：** `trans` 事务；`h` 调用方栈上/堆上钩子（含 `fn/next`，`fn` 签名 `int (*)(trans, h)`）。

**返回语义：** 头插 `trans->hooks`，无失败。

**调用链位置：** 触发器、配额、reflink 等需在“拿 journal 预留后、落 bset 前”追加更新的路径；消费点在 `bch2_trans_commit_write_locked` 中 `h=trans->hooks; while(h){try(h->fn(trans,h)); h=h->next;}`。

**关键片段：**

```c
h->next = trans->hooks;
trans->hooks = h;
```

**设计权衡：** 头插 O(1) 但逆序执行——调用方若要求顺序需自行倒序注册。钩子内存由注册方保证（多为栈上 + 同步提交），`reset_updates` 置 `hooks=NULL` 不释放，零所有权转移。

### 5.2 `bch2_trans_commit_run_triggers` / `run_one_trans_trigger` —— 事务触发器定序

**签名（`fs/btree/commit.c`）：**

```c
static int bch2_trans_commit_run_triggers(struct btree_trans *trans);
static int run_one_trans_trigger(struct btree_trans *trans, struct btree_insert_entry *i);
```

**参数含义：** `trans` 事务；`i` 单条排队更新。

**返回语义：** 按 `sort_order`（`btree_trigger_order(btree_id)`）分组，外层按 `sort_id` 递增，内层 `do{...}while(trans_trigger_run)` 跑到不动点（触发器可追加同组更新）。同 btree 内先 insert 后 overwrite（注释：FALLOCATE 搬 extent 时先加引用再 drops，避免悬空）。`insert_trigger_run/overwrite_trigger_run` 两位标记防重跑/漏跑，debug 下 `BUG_ON` 未跑全。

**调用链位置：** `__bch2_trans_commit` 首步（journal 预留之前），此时可安全排队新更新；mem 触发器（`run_one_mem_trigger`）则在写锁+预留之后跑（见 5.3）。

**关键片段：**

```c
while (sort_id_start < trans->nr_updates) {
  unsigned sort_id = trans->updates[sort_id_start].sort_order;
  do {
    trans_trigger_run = false;
    for (idx = sort_id_start;
         idx < trans->nr_updates && trans->updates[idx].sort_order <= sort_id;
         idx++) {
      if ((i->flags & BTREE_TRIGGER_norun) || ... ) continue;
      try(run_one_trans_trigger(trans, i));
      trans_trigger_run = true;
    }
  } while (trans_trigger_run);
  sort_id_start = idx;
}
```

**关键片段（`run_one_trans_trigger` 分片）：**

```c
if (!i->insert_trigger_run && !i->overwrite_trigger_run &&
    old_ops->trigger == new_ops->trigger) {
  i->overwrite_trigger_run = i->insert_trigger_run = true;
  op.flags |= BTREE_TRIGGER_insert|BTREE_TRIGGER_overwrite;
} else if (!i->overwrite_trigger_run) { ... overwrite ... }
else if (!i->insert_trigger_run) { ... insert ... }
```

**设计权衡：** 以“按 btree 分配条带定序 + 同键 insert 先行”换触发器级联不死锁、不丢引用。注释明示不可传 `i` 指针给 trigger（数组会搬迁），只传值语义 `op`。`BTREE_TRIGGER_norun` 给 key-cache 刷新等内部搬运豁免，避免递归触发。

### 5.3 `run_one_mem_trigger` / `bch2_trans_commit_run_gc_triggers` —— 内存触发器与 GC 触发器

**签名：**

```c
static int run_one_mem_trigger(struct btree_trans *trans, struct btree_insert_entry *i, unsigned flags);
static noinline int bch2_trans_commit_run_gc_triggers(struct btree_trans *trans);
```

**参数含义：** `i` 条目；`flags` 含 `atomic/gc` 等。

**返回语义：** `mem_trigger` 按新旧类型分发：同 trigger 合并为 `insert|overwrite` 一次调用，否则新键走 `insert`（old 填 deleted 桩）、旧键走 `overwrite`（new 填 deleted 桩）；快照键计数 `bch2_trigger_snapshot_nr_keys` 先行。`gc_triggers` 仅 `gc.pos.phase` 非零且 `gc_visited` 时跑。失败即 `trans_commit_fatal_err`（文件系统 fatal，非 restart）。

**调用链位置：** `bch2_trans_commit_write_locked` 内，journal 预留之后、journal 组装之前。此时 `journal_entries` 布局已定，trigger 禁止增长（`bch2_trigger_get_mutable_new` 的 mem 期禁增长注释）。

**关键片段：**

```c
if (old_ops->trigger && old_ops->trigger == new_ops->trigger) {
  op.flags = flags|BTREE_TRIGGER_insert|BTREE_TRIGGER_overwrite;
  return old_ops->trigger(trans, op);
}
```

### 5.4 `bch2_trigger_get_mutable_new` —— 触发器增长新键

**签名（`fs/btree/update.c`）：**

```c
int bch2_trigger_get_mutable_new(struct btree_trans *trans, struct btree_trigger_op op, unsigned needed_u64s, struct bkey_s *out);
```

**参数含义：** `op` 触发器操作（含 `btree/level/new/new_buf_u64s/flags`）；`needed_u64s` 需要容量；`out` 返回可写视图。

**返回语义：** 够大直接回 `op.new`；不够则按 `(btree,level,pos)` 重找 `trans->updates`（每次重找，因嵌套更新可致数组搬迁），`kmalloc` 新缓冲、`bkey_copy`、重接 `i->k/k_buf_u64s`。`atomic` 期禁止增长（`BUG_ON`），无 `insert` 标志禁止变异。

**关键片段：**

```c
if (needed_u64s <= op.new_buf_u64s) { *out = op.new; return 0; }
BUG_ON(op.flags & BTREE_TRIGGER_atomic);
trans_for_each_update(trans, e)
  if (e->btree_id == op.btree && e->level == op.level &&
      bpos_eq(e->k->k.p, op.new.k->p)) { i = e; break; }
```

**设计权衡：** 快慢道分离：绝大多数 trigger 原地改，零查找；增长路径 O(n) 重找换指针失效安全。

### 5.5 `nested_commit_do` 防丢

**签名（`fs/btree/update.h`）：**

```c
#define nested_commit_do(_trans, _disk_res, _journal_seq, _flags, _do)
```

**语义：** 内层提交丢弃外层排队更新时，外层凭 `transaction_restart_nested` 感知并重走。`bch2_trans_commit_error` 在 `no_journal_res` 成功后强制 `nested` 即此理：用了别人的 journal_res，必须让外层重取。

**可学：** 提交钩子允许级联，但必须定序（`sort_order`）+ 不动点 + 防丢上报（`nested`）。mem 期与 trans 期两阶段划分，本质是“journal 布局冻结前/后”。

---

## 六、队列化写与锁协同

### 6.1 `bch2_trans_lock_write_inlined` / `bch2_trans_lock_write` / `trans_lock_write_fail` / `bch2_trans_unlock_updates_write`

**签名（`fs/btree/commit.c`）：**

```c
__always_inline static int bch2_trans_lock_write_inlined(struct btree_trans *trans);
static int bch2_trans_lock_write(struct btree_trans *trans);
static noinline int trans_lock_write_fail(struct btree_trans *trans, struct btree_insert_entry *i, int ret);
static inline void bch2_trans_unlock_updates_write(struct btree_trans *trans);
```

**参数/返回：** `trans` 事务。按排队顺序逐叶加写锁，同叶跳过（`same_leaf_as_prev`）；成功置 `write_locked` 并对每叶 `bch2_btree_node_prep_for_write`（just-written 清理 + `want_new_bset` 开新 bset）。失败回滚已加写锁（逆序解同叶首项）并返回 restart。解锁仅解 `WRITE_LOCKED` 层级。

**调用链位置：** `do_bch2_trans_commit` 首步，journal 预留之前。

**关键片段：**

```c
trans_for_each_update(trans, i) {
  if (same_leaf_as_prev(trans, i))
    continue;
  int ret = bch2_btree_node_lock_write(trans, trans->paths + i->path, &insert_l(trans, i)->b->c);
  if (unlikely(ret))
    return trans_lock_write_fail(trans, i, ret);
  if (!i->cached)
    bch2_btree_node_prep_for_write(trans, trans->paths + i->path, insert_l(trans, i)->b);
}
```

**设计权衡：** 按 `trans->updates` 已排序顺序加锁，与 trigger 定序同源，天然防 ABBA。`prep_for_write` 必须在写锁下判断 `want_new_bset`，否则并发改叶大小导致误判。

### 6.2 `btree_key_can_insert` / `btree_key_can_insert_cached` —— 写锁下验空

**签名：**

```c
static inline int btree_key_can_insert(struct btree_trans *trans, struct btree *b, unsigned u64s);
static inline int btree_key_can_insert_cached(struct btree_trans *trans, enum bch_trans_commit_flags flags, struct btree_path *path, unsigned u64s);
```

**参数/返回：** `b/path` 目标叶；`u64s` 同叶累计。同叶多插累计 `u64s` 后一次验 `bch2_btree_node_insert_fits`，不满回 `btree_insert_btree_node_full` 走分裂路径。缓存版快道 `u64s+1<=ck->u64s && dirty` 直接 0，否则慢道扩 `ck->k`（降锁 `kmalloc`）或 `need_journal_reclaim`。

**调用链位置：** `bch2_trans_commit_write_locked` 首循环，注释明示“必须持写锁验，否则他线程改叶大小”。

**关键片段：**

```c
trans_for_each_update(trans, i) {
  if (!same_leaf_as_prev(trans, i))
    u64s = 0;
  u64s += i->k->k.u64s;
  ret = !i->cached
    ? btree_key_can_insert(trans, insert_l(trans, i)->b, u64s)
    : btree_key_can_insert_cached(trans, flags, trans->paths + i->path, u64s);
}
```

### 6.3 `__bch2_btree_node_write` 队列化 + `bch2_trans_submit_write_bios` + `__bch2_trans_unlock`

**签名（`fs/btree/write.c` / `fs/btree/locking.c`）：**

```c
void __bch2_btree_node_write(struct btree_trans *trans, struct btree *b, unsigned flags);
void bch2_trans_submit_write_bios(struct btree_trans *trans);
static inline void __bch2_trans_unlock(struct btree_trans *trans);
void bch2_trans_unlock(struct btree_trans *trans);
void bch2_trans_unlock_long(struct btree_trans *trans);
```

**参数/返回：** `trans/b` 待写节点。`__bch2_btree_node_write` 组 bio 后不提交，而是 `wbio->bio.bi_next=trans->queued_write_bios; trans->queued_write_bios=&wbio->bio`。`__bch2_trans_unlock` 解全部 path 锁后，若队列非空则 `bch2_trans_submit_write_bios` 逐个 `btree_write_do_submit`。`unlock_long` 另释 cannibalize 锁 + SRCU（长持警告）。

**关键片段（`write.c`）：**

```c
/*
 * Queue the bio on the trans — no block layer work while we hold
 * btree node locks. Submitted when the trans unlocks, or before
 * waiting on btree node IO.
 */
wbio->wbio.bio.bi_next = trans->queued_write_bios;
trans->queued_write_bios = &wbio->wbio.bio;
```

**关键片段（`locking.c`）：**

```c
trans_for_each_path(trans, path, i)
  __bch2_btree_path_unlock(trans, path);
if (unlikely(trans->queued_write_bios))
  bch2_trans_submit_write_bios(trans);
```

**设计权衡：** 持锁禁直接 IO，一律队列化：块层可睡眠/分配，若持 btree 锁进块层则锁序倒置死锁。解锁时集中下发摊薄 `submit_bio` 开销；等 IO 前亦先刷队列（`bch2_btree_node_wait_on_write` 路径），防“等自己队列里的 IO”自死锁。

### 6.4 `bch2_trans_downgrade` / `__bch2_trans_relock` —— 提交后降级与重锁

**签名：**

```c
void bch2_trans_downgrade(struct btree_trans *trans);
int __bch2_trans_relock(struct btree_trans *trans, bool trace);
void bch2_trans_revalidate_updates_in_node(struct btree_trans *trans, struct btree *b);
```

**参数/返回：** `downgrade` 把 path 锁降到 `level+intent` 最小需求（`__bch2_trans_commit` 成功后调用，读后仍可用迭代器）；`relock` 按 `should_be_locked` 重取，失败即 `__bch2_trans_unlock` + restart（`relock/releq_path` 码）。

**设计权衡：** 提交成功不全解锁而降级，兼顾“迭代连续性”与“锁持有时长”（`BTREE_TRANS_MAX_LOCK_HOLD_TIME_NS` 1ms 超限即 `unlock+cond_resched`）。`trans->locked` 与 SRCU 状态机由 `trans_set_locked` 统一维护，debug 下 `verify_locks` 全检。

**可学：** 锁与 IO/内存回收协同声明：持锁禁 IO（队列化）、持 SRCU 禁长睡（`unlock_long`）、持 cannibalize 禁睡眠（`unlock` 即释）。

---

## 七、迭代器：peek与槽位

### 7.1 `bch2_btree_iter_traverse` / `bch2_btree_path_peek_slot` —— 定位与槽读

**签名（`fs/btree/iter.c` / `fs/btree/iter.h`）：**

```c
int bch2_btree_iter_traverse(struct btree_iter *iter);
struct bkey_s_c bch2_btree_path_peek_slot(struct btree_path *path, struct bkey *u);
```

**参数含义：** `iter` 迭代器（含 `trans/btree_id/pos/snapshot/flags`）；`path/u` 路径与拆包暂存（`u` 多为 `iter->k`）。

**返回语义：** `traverse` 按 `search_key` 重定 `path` 并下钻加锁，成功置 `should_be_locked`；`peek_slot` 返回精确槽位：非缓存经 `node_iter_peek_all` 拆包，若 `pos` 无覆盖则合成空 `deleted` 键（`bkey_init(u); u->p=path->pos`），而非报错。

**关键片段（`iter.c:bch2_btree_path_peek_slot`）：**

```c
_k = bch2_btree_node_iter_peek_all(&l->iter, l->b);
k = _k ? bkey_disassemble(l->b, _k, u) : bkey_s_c_null;
if (!k.k || !bpos_eq(path->pos, k.k->p)) {
  bkey_init(u);
  u->p = path->pos;
  return (struct bkey_s_c) { u, NULL };
}
```

**设计权衡：** “无覆盖合成空洞”让上层写路径（白洞/切片）无需区分“无键”与“删键”，读路径亦天然表达空洞。但要求调用方永不假设 `peek_slot` 非空（`!k.k` 仍可能：无节点/缓存缺失）。

### 7.2 `__bch2_btree_iter_peek` —— 多源叠加读

**签名：**

```c
static struct bkey_s_c __bch2_btree_iter_peek(struct btree_iter *iter, struct bpos *search_key, const struct bpos *end);
```

**参数含义：** `search_key` 输入输出游标（遇删键/白洞前移到 `k.p/successor` 重扫）；`end` 叶界。

**返回语义：** 循环内按序叠加：`btree_path_level_peek_all` → key-cache（`with_key_cache`）→ journal（`with_journal`）→ 本事务排队（`trans->nr_updates && !committed`）。删键不返回，推进 `search_key` 继续；跨叶则 `search_key=successor(leaf_max)`；到 `end` 返回 null。

**关键片段：**

```c
k = btree_path_level_peek_all(trans->c, l, &iter->k);
if (unlikely(iter->flags & BTREE_ITER_with_key_cache) &&
    btree_trans_peek_key_cache(iter, &k))
  break;
if (unlikely(iter->flags & BTREE_ITER_with_journal))
  btree_trans_peek_journal(trans, iter, *search_key, &k);
if (unlikely(trans->nr_updates) &&
    !(iter->flags & BTREE_ITER_committed))
  bch2_btree_trans_peek_updates(trans, iter, *search_key, &k);
if (likely(k.k)) {
  if (!bkey_deleted(k.k)) break;
  *search_key = !bpos_eq(*search_key, k.k->p)
    ? k.k->p : bpos_successor(k.k->p);
}
```

**设计权衡：** 读己之写（`peek_updates`）是事务语义基石；journal/key-cache 叠加顺序固定为“btree→cache→journal→trans”，后者覆盖前者，保证同一事务内多次更新可见最新。`committed` 标志供绕过本事务意图的特殊扫描。

### 7.3 `bch2_btree_iter_peek_max` / `btree_iter_filter_snapshots` —— 快照过滤

**签名：**

```c
struct bkey_s_c bch2_btree_iter_peek_max(struct btree_iter *iter, const struct bpos *end);
static enum filter_snapshots_ret btree_iter_filter_snapshots(struct btree_trans *trans, struct btree_iter *iter, struct bkey_s_c *k, struct bpos *search_key, const struct bpos *end);
```

**参数含义：** `end` 范围上限（非 extent 用 `bkey_gt`，extent 用 inode 比较 + `bkey_ge`）；`filter` 内 `iter->snapshot` 为视角快照。

**返回语义：** `peek_max` 在 `__peek` 外包快照循环：`snapshot` 不等/`extent_whiteout`/`update_path` 未建时进 `filter`，`OK` 接受、`CONTINUE` 重扫、`END` 终止、`ERR` 带错退出。成功后 `iter->pos` 单调前移（非 extent 置 `k.p`，extent 取 `max(pos,start)`），`pos.snapshot` 强制回视角快照。

**关键片段（`iter.c:btree_iter_filter_snapshots`）：**

```c
if (k->k->p.snapshot < iter->snapshot) {
  *search_key = bpos_with_snapshot(k->k->p, iter->snapshot);
  return FILTER_SNAP_CONTINUE;
}
if (!bch2_snapshot_is_ancestor(trans, iter->snapshot, k->k->p.snapshot)) {
  *search_key = bpos_successor(k->k->p);
  return FILTER_SNAP_CONTINUE;
}
if (!(iter->flags & BTREE_ITER_nofilter_whiteouts) &&
    bkey_extent_whiteout(k->k)) {
  *search_key = bkey_successor(iter, k->k->p);
  return FILTER_SNAP_CONTINUE;
}
return FILTER_SNAP_OK;
```

**关键片段（intent 写路径缓存）：**

```c
if ((iter->flags & BTREE_ITER_intent) &&
    !(iter->flags & BTREE_ITER_is_extents) &&
    !iter->update_path) {
  __btree_path_get(trans, trans->paths + iter->path, ...);
  iter->update_path = iter->path;
  iter->update_path = bch2_btree_path_set_pos(trans, iter->update_path,
              &with_snapshot, ..., _THIS_IP_);
}
```

**设计权衡：** 快照过滤在迭代器层而非 btree 层，祖先判定（`is_ancestor`）+ 白洞跳过 + `update_path` 缓存三合一。`update_path` 解决“读到祖先键但写要在视角快照处”的错位：读游标继续扫，写槽位另存，避免读写同槽假设。`extent_whiteout` 推进 `iter->pos` 防重启后重扫白洞海（大快照树扫描性能关键）。

### 7.4 `bch2_btree_iter_peek_slot` —— 槽语义集大成

**签名：**

```c
struct bkey_s_c bch2_btree_iter_peek_slot(struct btree_iter *iter);
struct bkey_s_c bch2_btree_iter_next_slot(struct btree_iter *iter);
struct bkey_s_c bch2_btree_iter_prev_slot(struct btree_iter *iter);
```

**参数/返回：** `iter` 迭代器。快道（`cached` 或非 extent 非过滤）按 `btree→cache→journal→trans_updates` 叠加，`extent_whiteout+filter` 转 `deleted` 桩；慢道（extent/过滤）用 `nofiIter_whiteouts` 拷贝迭代器 `peek_max` 到 `end=pos`，无覆盖则合成空洞（extent 按 `next-start` 算 `size`）。`next/prev_slot` 即 `advance/rewind+peek_slot`。

**关键片段（顺序注释，原样）：**

```c
/*
 * Consult sources in the same order as bch2_btree_iter_peek_max():
 * btree, then key cache, then journal, then the transaction's own
 * updates - each overlaying the last, so an in-transaction update
 * wins. Crucially the key cache is peeked before trans updates, so
 * the key_cache_path is established even when we already have an
 * update for this key ...
 */
k = bch2_btree_path_peek_slot(btree_iter_path(trans, iter), &iter->k);
```

```c
if (bkey_lt(iter->pos, next)) {
  bkey_init(&iter->k);
  iter->k.p = iter->pos;
  if (iter->flags & BTREE_ITER_is_extents)
    bch2_key_resize(&iter->k, min_t(u64, KEY_SIZE_MAX, ...));
  k = (struct bkey_s_c) { &iter->k, NULL };
}
```

**设计权衡：** peek（范围）与 peek_slot（定点）语义分离：前者跳删键找下一键，后者定点合成空洞。key-cache 先于 trans 更新 peek 的微妙排序，防同事务二次更新跳过缓存致 `key_cache_raced` 活锁——读顺序即写正确性依赖。

### 7.5 `bch2_btree_iter_advance` / `bch2_btree_iter_rewind` / `bch2_btree_trans_peek_*` —— 推进与本事务覆盖

**签名：**

```c
inline bool bch2_btree_iter_advance(struct btree_iter *iter);
inline bool bch2_btree_iter_rewind(struct btree_iter *iter);
static void bch2_btree_trans_peek_updates(struct btree_trans *trans, struct btree_iter *iter, struct bpos search_key, struct bkey_s_c *k);
static void bch2_btree_trans_peek_slot_updates(struct btree_trans *trans, struct btree_iter *iter, struct bkey_s_c *k);
```

**参数/返回：** `advance/rewind` 按 `is_extents` 与 `all_snapshots` 选后继/前驱（extent 用 `bkey_successor/predecessor` 语义，非 extent 用 `bpos` 语义），到 `SPOS_MAX/POS_MIN` 返回 false。`peek_updates` 在 `[search_key, leaf_max]` 取最优覆盖，`peek_slot_updates` 精确匹配 `iter->pos` 且 `level==min_depth`。

**设计权衡：** 推进不读盘只改 `pos`，下次 peek 重 `traverse`；本事务覆盖线性扫 `updates`（n 小），以 O(n) 换“读己之写”零索引成本。

**可学：** 读分 peek（跳删找下键）与 peek_slot（定点合成空洞）两种语义；快照过滤缓存写位（`update_path`）防误写祖先槽；多源叠加顺序即正确性。

---

## 八、设计启示

1. **迭代器即事务。** `btree_trans` 只是持锁 path 数组 + 有序 `updates` + bump 内存。`__bch2_trans_get/begin/commit/put` 四步即生命周期。不另设立事务日志对象，journal 组装只是提交尾段的 `memcpy_u64s`。
2. **bump加作废。** `bch2_trans_kmalloc_ip(__always_inline快道)` + `__bch2_trans_kmalloc(幂扩容/重启/mempool)` + `begin(mem_top=0)` 三件套。`BTREE_TRANS_MEM_MAX=64K` 封顶，`subbuf(u16偏移)`、`lazy_if_full(1/4阈值)` 分层设防。禁止 `free` 是有意为之：重启即全废比精细回收更易证正确。
3. **写排队。** `bch2_trans_update_ip(__must_check)` 唯一入口，extent/白洞/缓存三路分流后收敛于 `btree_trans_update_by_path(排序+抓old)`。`insert/delete/bit_mod` 皆为排队特例。提交前全是意图，故可 `updates_to_text` 审计、`reset_updates` 丢弃、`sort_order` 定序。
4. **重启编码。** `errcode.h` 的 `transaction_restart` 家族20+子码 + `commit_error` 的 `BUG_ON(码与标志一致)` + `nested/commit` 向上传播，构成“失败即码、码即策略”。任何裸重试都是 bug。
5. **钩子定序。** `commit_hook(头插单链表)` + `run_triggers(按sort_order分组不动点)` + `mem_trigger(journal冻结后)` 两阶段。`get_mutable_new(快道原地/慢道重找)` 解决 trigger 增长与数组搬迁矛盾。
6. **队列化写。** `queued_write_bios` + `unlock时集中submit` + `等IO前先刷队列`，持锁期零块层动作。锁（`lock_write`按序加）、内存（扩容推迟到begin）、回收（SRCU/cannibalize在unlock释放）三者协同声明。
7. **读写语义分离。** `peek/peek_max/next/prev`（范围跳删） vs `peek_slot/next_slot`（定点合成空洞）；`filter_snapshots` 另存 `update_path` 解决读写槽错位；叠加顺序 `btree→cache→journal→trans` 即正确性本身。

### 复核途径（只读，均已验证存在）

- `grep -n "bch2_trans_kmalloc_ip\|__bch2_trans_kmalloc\|bch2_trans_begin" fs/btree/iter.h fs/btree/iter.c` 看 bump 分配与重启作废。
- `grep -n "bch2_trans_update_ip\|btree_trans_update_by_path\|need_whiteout_for_snapshot\|__bch2_insert_snapshot_whiteouts" fs/btree/update.c fs/btree/update.h` 看排队、白洞、过滤。
- `grep -n "bch2_trans_commit_run_triggers\|run_one_mem_trigger\|bch2_trans_commit_hook\|nested_commit_do" fs/btree/commit.c fs/btree/update.*` 看钩子链与定序。
- `grep -n "queued_write_bios\|bch2_trans_submit_write_bios\|__bch2_trans_unlock" fs/btree/write.c fs/btree/locking.c` 看队列化写。
- `grep -n "bch2_btree_iter_peek_slot\|bch2_btree_iter_peek_max\|btree_iter_filter_snapshots\|__bch2_btree_iter_peek" fs/btree/iter.c` 看 peek 与槽位。
- `grep -n "transaction_restart" fs/errcode.h` 看重启码系全表（父类+20余子类）。

</task_result>