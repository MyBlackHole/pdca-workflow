# bcachefs 分配器代码级精讲报告（扩充版，T0517）

> 只读精读范围：`fs/alloc/foreground.c`（2396行）、`fs/alloc/types.h`、`fs/alloc/buckets_types.h`、`fs/alloc/buckets.c`（1107行）、`fs/alloc/buckets.h`、`fs/alloc/foreground.h`、`fs/alloc/accounting.c`（1455行）、`fs/alloc/background.c`之`bch2_trigger_alloc/bch2_bucket_do_freespace_index`、`fs/alloc/lru.c`、`fs/alloc/discard.c`、`fs/sb/members.c`（1014行）、`fs/init/dev.c`之成员状态/增删流水线。原九节结构保留，每节展开为逐函数精讲。所有函数名均经 `grep/Read` 核实，不给行号，只给文件+符号，避免编造。

---

## 一、全景：按“死同穴”的写点隔离

### 1.0 顶层 DOC：`fs/alloc/foreground.c` 文件头 `DOC(foreground-allocator)`

**原文要旨（已 Read 核实）：**

```c
/* DOC(foreground-allocator)
 * bcachefs automatically reduces fragmentation by segregating ...
 * data written at the same time by the same file
 * tends to be deleted at the same time ...
 * User data write points are hashed by inode number ...
 * Separate write points also exist for btree nodes, copygc, and the reconcile subsystem ...
 */
```

**设计含义：** 这是全分配器的不变量声明。不是“分配空闲块”，而是“分配同死亡时间的块到同桶”。实现手段就是 `struct write_point` 隔离 + `writepoint_find()` 哈希分流。

**调用链位置：** 思想层 → 落到 `bch2_alloc_sectors_req()` 的 `writepoint_find(trans, write_point.v)` 选 `wp`，再到 `bucket_alloc_set_writepoint/partial/set_trans` 三级复用/新建。

**权衡：** 用写时分流换读时/GC时整桶回收。代价是写点过多会 stranded 容量（见 `too_many_writepoints()`），故有动态增减写点逻辑。

---

### 1.1 `struct write_point` — `fs/alloc/types.h`

**签名（类型定义）：**

```c
struct write_point {
  struct { struct hlist_node node; struct mutex lock; u64 last_used;
           unsigned long write_point; enum bch_data_type data_type;
           unsigned sectors_free; unsigned prev_sectors_free;
           struct open_buckets ptrs; struct dev_stripe_state stripe;
           u64 sectors_allocated; } __aligned(SMP_CACHE_BYTES);
  struct { struct work_struct index_update_work; struct list_head writes;
           spinlock_t writes_lock; enum write_point_state state;
           u64 last_state_change; u64 time[WRITE_POINT_STATE_NR];
           u64 last_runtime; } __aligned(SMP_CACHE_BYTES);
};
```

**参数/字段含义：**

- `node/lock/last_used/write_point`：哈希链节点 + 互斥 + LRU 时间戳 + 键（`1`最低位区分 hashed vs 直接指针，见 `foreground.h:writepoint_hashed/writepoint_ptr`）。
- `data_type/sectors_free/prev_sectors_free/ptrs/stripe`：本写点数据类型、当前可分配扇区、上一轮可分配扇区、已持有开桶集、 per-write_point WFQ 状态。
- 第二 cacheline：`index_update_work/writes/state` 是写路生产-消费异步落盘状态机，与分配热路分离，避免分配持锁做索引更新。

**返回/作用：** 所有前台分配的上下文容器。`bch_fs_allocator` 内含 `write_points[WRITE_POINT_MAX]`（32个）+ `btree_write_point` + `reconcile_write_point` + `copygc.write_point`，天然隔离 user/btree/copygc/reconcile。

**调用链：** `bch2_fs_allocator_foreground_init()` 初始化 → `bch2_alloc_sectors_req()` 中 `writepoint_find()` 选取/复用 → `bch2_alloc_sectors_append_ptrs_inlined()` 扣 `sectors_free` → `bch2_alloc_sectors_done_inlined()` 归还/丢弃。

**权衡：** 双 cacheline 对齐：第一行分配热路，第二行写回状态机，避免 false sharing。`WRITE_POINT_MAX=32` + `WRITE_POINT_HASH_NR=32` 固定数组，分配器自身零动态分配（防递归，见第二节）。

---

### 1.2 `writepoint_find()` — `fs/alloc/foreground.c`

**签名：**

```c
static struct write_point *writepoint_find(struct btree_trans *trans,
                                           unsigned long write_point)
```

**参数：**

- `trans`：btree 事务，用于 `bch2_trans_mutex_lock_norelock()` 可重入加锁（先 `mutex_trylock`，失败则 `bch2_trans_unlock` 后阻塞锁，避免与事务锁死锁）。
- `write_point`：`struct write_point_specifier.v`。最低位 `1` 表示 hashed（按 inode 等哈希），偶数表示直接指针（`writepoint_ptr()` 传 btree/copygc 等固定写点）。

**返回：** 已加 `wp->lock` 的 `write_point*`，并更新 `last_used = local_clock()`。

**调用链位置：** `bch2_alloc_sectors_req()` 入口第一步。分支：

```c
if (!(write_point & 1UL)) {
  wp = (struct write_point *) write_point;
  bch2_trans_mutex_lock_norelock(trans, &wp->lock);
  return wp;
}
```

否则 `writepoint_hash() → __writepoint_find() → （命中则 lock_wp / 未命中则选 oldest LRU 复用或 try_increase_writepoints() 扩容）`。

**关键片段（≤10行，复用 LRU 驱逐）：**

```c
wp = oldest;
hlist_del_rcu(&wp->node);
wp->write_point = write_point;
hlist_add_head_rcu(&wp->node, head);
```

**权衡：**

- 直接指针路径零哈希开销，保证 btree/copygc 关键路径确定性。
- Hashed 路径用 RCU 哈希 + LRU 复用最久未用写点，天然实现“不同文件分流，同文件聚合”。
- 扩容受 `too_many_writepoints()` 约束（见 1.5），防止写点膨胀 stranded 过多半满桶。

---

### 1.3 `__writepoint_find()` — `fs/alloc/foreground.c`

**签名：**

```c
static struct write_point *__writepoint_find(struct hlist_head *head,
                                             unsigned long write_point)
```

**参数/返回：** 在给定哈希桶 `head` 下 RCU 遍历比对 `wp->write_point`，命中返回指针，未命中 `NULL`。调用者需重检（`lock_wp` 后复检 `wp->write_point == write_point`，防并发复用竞态）。

**调用链：** 仅 `writepoint_find()` 内调用，`restart_find/restart_find_oldest` 双重循环处理并发插入/扩容 race。

**权衡：** RCU 读无锁快路 + mutex 写串行化，读多写少典型优化。重检-重试代替大锁，保证正确性。

---

### 1.4 `writepoint_hash()` — `fs/alloc/foreground.c`

**签名：**

```c
static inline struct hlist_head *writepoint_hash(struct bch_fs_allocator *a,
                                                 unsigned long write_point)
```

**关键片段：**

```c
unsigned hash = hash_long(write_point, ilog2(ARRAY_SIZE(a->write_points_hash)));
return &a->write_points_hash[hash];
```

**权衡：** `HASH_NR=32` 与 `MAX=32` 同阶，哈希分散 + 线性 LRU 兜底，简单可证明无饿死，不用动态哈希表（防递归分配）。

---

### 1.5 `too_many_writepoints() / try_increase_writepoints() / try_decrease_writepoints()` — `fs/alloc/foreground.c`

**签名：**

```c
static inline bool too_many_writepoints(struct bch_fs *c, unsigned factor)
static noinline bool try_increase_writepoints(struct bch_fs *c)
static noinline bool try_decrease_writepoints(struct btree_trans *trans, unsigned old_nr)
```

**参数含义：**

- `factor`：stranded 容忍倍数。`try_increase` 用 `32`（宽松，允许扩），`try_decrease` 用 `8`（严格，积极缩）。
- `old_nr`：进入 `bch2_alloc_sectors_req()` 时的写点数快照，用于失败回缩时比较。

**返回：** 是否“stranded 过多”/是否成功增减。

**关键片段（容量门）：**

```c
u64 stranded = c->allocator.write_points_nr * c->capacity.bucket_size_max;
u64 free = bch2_fs_usage_read_short(c).free;
return stranded * factor > free;
```

**调用链：** `writepoint_find()` 扩容时检查；`bch2_alloc_sectors_req()` 错误路径 `freelist_empty/bucket_alloc_blocked` 时调用 `try_decrease_writepoints()` 缩容并 `goto retry`。

**权衡：** 写点是碎片与并发的折中。扩容滞后（factor 32）、缩容激进（factor 8），迟滞避免抖动。缩容时将待删 `wp->ptrs` 经 `open_bucket_free_unused()` 挂半满链而非直接丢，保留利用率。

---

### 1.6 `bch2_alloc_sectors_req()` 主循环骨架 — `fs/alloc/foreground.c`

**签名：**

```c
int bch2_alloc_sectors_req(struct btree_trans *trans,
                           struct alloc_request *req,
                           struct write_point_specifier write_point,
                           struct write_point **wp_ret)
```

**参数：**

- `trans`：事务，提供 `trans_kmalloc_nomemzero` 分配 `alloc_request`、可重启语义。
- `req`：`alloc_request_get()` 预填的副本数/目标/水位/标志/`devs_have` 等。
- `write_point`：上述 hashed/直接两态。
- `wp_ret`：输出已锁定的写点，供调用者后续 `append_ptrs/done`。

**返回：** `0` 成功（`req->wp->ptrs/ptrs.nr/nr_effective/sectors_free` 就绪），负错误码失败（`freelist_empty/insufficient_devices/ec_alloc_failed` 等，调用者据 `will_retry_*` 决定降级/等待）。

**调用链位置（已核实的核心优先级链）：**

```c
ret = bucket_alloc_set_writepoint(c, req) ?:
      bucket_alloc_set_partial(c, req) ?:
      (req->ec ? bucket_alloc_from_stripe(trans, req)
               : bch2_bucket_alloc_set_trans(trans, req, &req->wp->stripe));
```

即：写点自带桶 → 全局半满桶 → 条带复用/EC新建 → 全新开桶。失败后按 `will_retry_all_devices → will_retry_target_devices → ec降级 → insufficient_devices欠复制容忍 → freelist_empty阻塞重试` 顺序降级。

**权衡：** 复用优先于新建，保证“死同穴”持续命中；新建才走 WFQ 选盘，保证均衡。重试分层避免无谓阻塞，欠复制提交是可用性优先于耐久性的显式取舍（btree 例外，见第四节）。

---

## 二、开桶三级池：防递归分配

### 2.0 中枢结构：`struct open_bucket / struct bch_fs_allocator` — `fs/alloc/types.h`

**`struct open_bucket` 字段：**

```c
struct open_bucket {
  spinlock_t lock; atomic_t pin; open_bucket_idx_t freelist;
  open_bucket_idx_t hash; u8 ec_idx; enum bch_data_type data_type:5;
  bool valid:1; bool on_partial_list:1; bool do_discards_fast:1;
  u8 dev; u8 generation; u32 sectors_free; u64 bucket;
  struct ec_stripe_new *ec;
};
```

- `pin`：引用计数，`atomic_inc/dec_and_test` 决定是否归还。GC mark-sweep 靠 `pin>0 + hash` 找到存活引用，防止回收未落索引的桶。
- `freelist/hash`：空闲单链表指针复用 + `(dev,bucket)` 开放哈希链指针复用同一 `u16` 槽位，零额外内存。
- `valid/on_partial_list/do_discards_fast`：有效位/半满链成员位/快速 discard 标记位。
- `sectors_free/bucket/generation/dev`：本桶剩余扇区、桶号、代际、设备号。

**`struct bch_fs_allocator` 关键：**

```c
open_bucket_idx_t open_buckets_freelist; open_bucket_idx_t open_buckets_nr_free;
struct closure_waitlist open_buckets_wait;
struct open_bucket open_buckets[OPEN_BUCKETS_COUNT]; // 4096
open_bucket_idx_t open_buckets_hash[OPEN_BUCKETS_COUNT];
open_bucket_idx_t open_buckets_partial[OPEN_BUCKETS_COUNT];
open_bucket_idx_t open_buckets_partial_nr;
```

`OPEN_BUCKETS_COUNT=4096` 固定池是防递归的核心：分配器元数据永不 `kmalloc`，只在池内搬运。

---

### 2.1 `struct bucket` 1字节锁 — `fs/alloc/buckets_types.h`

**签名：**

```c
struct bucket {
  u8 lock; u8 gen_valid:1; u8 data_type:7; u8 generation;
  u32 dirty_sectors; u32 cached_sectors; u32 stripe_sectors;
} __aligned(sizeof(long));
```

**注释原文（已核实）：** `We need to cram a spinlock in a single byte, because that's what we have left in struct bucket, and we care about the size of these - during fsck, we need in memory state for every single bucket on every device.` 大小端分别用 `BUCKET_LOCK_BITNR 0 / (BITS_PER_LONG-1)`，`bit_spin_lock()` 实现。

**权衡：** fsck 需全盘每桶内存状态，省 7 字节 × 百万桶 = 省 GB 级内存。用位自旋锁换内存，锁粒度为单桶，竞争极低，可接受自旋开销。

---

### 2.2 `bch2_open_bucket_alloc()` — `fs/alloc/foreground.c`

**签名：**

```c
static struct open_bucket *bch2_open_bucket_alloc(struct bch_fs_allocator *c)
```

**参数/返回：** `c` 为分配器子结构（非全 `bch_fs`，最小依赖）。`BUG_ON(!freelist || !nr_free)` 前置断言，调用者 `__try_alloc_bucket()` 已在 `freelist_lock` 下检查水位预留。返回已 `atomic_set(pin,1)` 的裸桶，`data_type=0` 清零。失败不返回 NULL，以 `ERR_PTR(open_buckets_empty/open_bucket_alloc_blocked)` 区分“无等待者”与“已排队等待”。

**调用链：** `__try_alloc_bucket()` 持有 `freelist_lock` 时调用 → 初始化 `valid/sectors_free/dev/generation/bucket` → `ca->nr_open_buckets++` → `bch2_open_bucket_hash_add()` 入哈希。

**关键片段：**

```c
struct open_bucket *ob = c->open_buckets + c->open_buckets_freelist;
c->open_buckets_freelist = ob->freelist;
atomic_set(&ob->pin, 1);
```

**权衡：** 空闲链 O(1) 分配，无搜索、无分配、无睡眠，可在自旋锁下完成。`pin=1` 起始值让后续 `add_new_bucket/ob_push` 的引用语义统一（谁持有谁 `put`）。

---

### 2.3 `__try_alloc_bucket()` — `fs/alloc/foreground.c`

**签名：**

```c
static struct open_bucket *__try_alloc_bucket(struct bch_fs *c,
                                              struct alloc_request *req,
                                              u64 bucket, u8 gen)
```

**参数：** `bucket/gen` 来自 freespace/alloc btree 的空闲断言（`try_alloc_bucket_pos/bch2_bucket_alloc_early/bucket_alloc_scan` 已验证 data_type==free、journal_seq 已落盘、非 superblock、非 nouse）。

**返回：** `NULL` 可跳过继续扫（superblock/nouse/已 open 竞态），`ERR_PTR` 必须向上传播（open 池水位阻塞、事务重启）。

**关键片段（水位门，≤10行）：**

```c
if (unlikely(c->allocator.open_buckets_nr_free <= bch2_open_buckets_reserved(req->watermark))) {
  track_event_change(&c->times[BCH_TIME_blocked_allocate_open_bucket], true);
  if (req->cl) {
    closure_wait(&c->allocator.open_buckets_wait, req->cl);
    return ERR_PTR(alloc_trace_add(req, U8_MAX, bch_err_throw(c, open_bucket_alloc_blocked), 0, 0, false));
```

**权衡：** 二次检查 `bch2_bucket_is_open()` 在锁内重做，关掉 TOCTOU（并发两事务同抢一桶）。水位预留按 `watermark` 分档（见 4.2），`interior_updates=0` 永不挡（btree 分裂必须成功，否则死锁）。

---

### 2.4 `__bch2_open_bucket_put() / bch2_open_bucket_put() / bch2_open_bucket_get()` — `foreground.h/c`

**签名：**

```c
void __bch2_open_bucket_put(struct bch_fs *c, struct open_bucket *ob);
static inline void bch2_open_bucket_put(struct bch_fs *c, struct open_bucket *ob)
  { if (atomic_dec_and_test(&ob->pin)) __bch2_open_bucket_put(c, ob); }
static inline void bch2_open_bucket_get(struct bch_fs *c, struct write_point *wp,
                                        struct open_buckets *ptrs)
```

**参数/语义：** `put` 为引用计数释放，最后一个持有者才真正归还空闲链 + 删哈希 + `ca->nr_open_buckets--` + `wake open_buckets_wait`。`get` 为写点持有桶的批量 `pin++` 并拷贝到 `ptrs`（用于 `append_ptrs` 时多副本共享同一 `wp->ptrs`）。

**关键片段（EC 快路）：**

```c
if (ob->ec) {
  ec_stripe_new_put(c, ob->ec, STRIPE_REF_io);
  return;
}
```

EC 桶不走空闲链，由 stripe 生命周期托管，避免条带半满时被拆散。

**`do_discards_fast` 钩子：**

```c
if (ob->do_discards_fast)
  bch2_fast_discard_bucket_add(ca, ob->bucket);
```

写完即知整桶将空，提前挂快速丢弃队列，省一次后台扫描。

**权衡：** pin 让“分配-GC-落盘”三方无需大锁 rendezvous，GC 只需哈希查 `pin>0` 即视为存活。代价是调用者必须配对 `put`（`DEFINE_FREE` 等 RAII 辅助），漏 `put` 即开桶泄漏（`open_buckets_nr_free` 单调降，可经 `bch2_fs_open_buckets_to_text` 观测）。

---

### 2.5 `open_bucket_free_unused() / partial_bucket_alloc() / bucket_alloc_set_partial()` — `fs/alloc/foreground.c`

**签名：**

```c
static void open_bucket_free_unused(struct bch_fs *c, struct open_bucket *ob)
static int partial_bucket_alloc(struct bch_fs *c, struct alloc_request *req, unsigned idx)
static int bucket_alloc_set_partial(struct bch_fs *c, struct alloc_request *req)
```

**语义：** 未用完开桶不归还空闲池，挂 `open_buckets_partial[]` 待复用。`partial_bucket_alloc` 以 `array_remove_item + on_partial_list=false + nr_partial_buckets--` 原子摘除并 `add_new_bucket()` 计入本次请求。`bucket_alloc_set_partial` 在 `freelist_lock` 下每轮重算 `domain_keys`、选 `domain_key` 最小（故障域最空）的可用半满桶，而非 first-fit。

**关键片段（域最优而非首命中）：**

```c
bch2_dev_domain_keys_update(c, req);
for (int i = a->open_buckets_partial_nr - 1; i >= 0; --i) {
  struct open_bucket *ob = a->open_buckets + a->open_buckets_partial[i];
  if (!want_bucket(c, req, ob)) continue;
```

**权衡：** 半满复用是碎片治理的主力（steady-state 多数分配在此命中）。每轮重排序 O(P×D) 开销换故障域均衡，注释明言 `first-fit would undo the failure domain spreading`，正确性优先于微优化。

---

### 2.6 `bch2_open_buckets_stop() / bch2_writepoint_stop() / should_drop_bucket()` — `fs/alloc/foreground.c`

**签名：**

```c
void bch2_open_buckets_stop(struct bch_fs *c, struct bch_dev *ca, bool ec)
static void bch2_writepoint_stop(struct bch_fs *c, struct bch_dev *ca, bool ec, struct write_point *wp)
static bool should_drop_bucket(struct open_bucket *ob, struct bch_fs *c, struct bch_dev *ca, bool ec)
```

**参数：** `ca==NULL && ec==false` 表示关文件系统全杀；`ca!=NULL` 表示下线/移除单盘；`ec==true` 表示关闭纠删只杀 EC 桶（含经 `ob->ec->blocks[]` 间接关联盘的桶）。

**调用链：** 设备下线 `__bch2_dev_read_only() → bch2_dev_allocator_remove() → bch2_open_buckets_stop()`，以及 `bch2_ec_stop_dev()` 收尾。还清理 `btree.reserve_cache` 与 `open_buckets_partial[]`（后者需 `swap-remove + rcu nr_partial_buckets--`，中途解自旋锁做 `put` 防死锁）。

**权衡：** 驱逐而非等待：下线必须收回写点引用，否则新写持续落到将死设备。用“逐写点过滤保留”而非“全池扫描”，持有 `wp->lock` 即排他，无需停全分配器。

---

## 三、WFQ 选盘：虚拟时间加权

### 3.0 中枢结构：`struct dev_stripe_state` — `fs/alloc/types.h`

**定义（注释已核实为 WFQ 自述）：**

```c
struct dev_stripe_state {
  u64 next_alloc[BCH_SB_MEMBERS_MAX];
  struct bch_devs_mask cached_devs;
};
```

注释要点：`next_alloc[i]` 是设备 `i` 下次应被服务的虚拟时间，最小者胜；每选中一次增量为 `1/free_space[i]`，空闲多者增量小、胜率高；`cached_devs` 记录掩码有效性，掩码变化时新纳入盘抬到旧盘最小值，防从 0 开始饿死他盘。

**调用链：** 每个 `write_point.stripe` 独享一份（per-写点 WFQ，避免 btree 与 user 互相干扰），`bch2_bucket_alloc_set_trans()` 的 `stripe` 参数即它（`req->wp->stripe` 或 journal scratch）。

---

### 3.1 `dev_stripe_state_sync()` — `fs/alloc/foreground.c`

**签名：**

```c
static void dev_stripe_state_sync(struct dev_stripe_state *stripe,
                                  struct bch_devs_mask *devs)
```

**参数/返回：** 无返回，以 `bitmap_equal/bitmap_andnot` 求 `added = devs - cached`，若非空则求旧掩码内 `min_va`，对 `added` 执行 `next_alloc[i] = max(next_alloc[i], min_va)`，最后 `cached_devs = *devs`。只抬升不降低（注释：重回掩码的盘保留历史，`assign would erase it, letting the same device win every equal-hand tie forever`）。

**关键片段：**

```c
if (likely(bitmap_equal(stripe->cached_devs.d, devs->d, BCH_SB_MEMBERS_MAX)))
  return;
```

快路：掩码未变零开销，热路友好。

**权衡：** 新盘/重回盘“加入当前虚拟时间”而非 0，是 WFQ 无饿死三件套之二（加权增量是其一，溢出重缩放是其三）。只升不降保证单调性，虚拟时间可比。

---

### 3.2 `__dev_alloc_list() / bch2_dev_alloc_list() / bch2_dev_alloc_list_devs()` — `fs/alloc/foreground.c`

**签名：**

```c
static void __dev_alloc_list(struct bch_fs *c, struct dev_stripe_state *stripe,
                             struct bch_devs_mask *devs, const u64 *domain_keys,
                             struct dev_alloc_list *ret)
void bch2_dev_alloc_list(struct bch_fs *c, struct dev_stripe_state *stripe,
                         struct alloc_request *req)
void bch2_dev_alloc_list_devs(struct bch_fs *c, struct dev_stripe_state *stripe,
                              struct bch_devs_mask *devs,
                              const struct bch_devs_mask *devs_chosen,
                              u64 *domain_keys, struct dev_alloc_list *ret)
```

**参数：** `domain_keys` 为每盘故障域占有数（`bch2_dev_domain_key()` 求），`ret` 为 `u8 data[MAX]+nr` 小数组（栈上排序，无分配）。

**排序键（宏，已核实）：**

```c
#define dev_alloc_cmp(l, r) ((domain_keys ? cmp_int(domain_keys[l], domain_keys[r]) : 0) ?: \
                             __dev_stripe_cmp(stripe, l, r))
```

先比故障域（副本打散硬偏好），再比虚拟时间（空闲加权）。`bubble_sort` 小 N 排序，N≤ devices（通常 <16），分支简单胜过快排常数。

**调用链：** `bch2_bucket_alloc_set_trans()` 入口排序一次，每新增一副本后 `progress=true → bch2_dev_alloc_list()` 重排（故障域占有已变）。Journal 选盘用 `devs` 变体（无 `alloc_request`，scratch domain_keys）。

**权衡：** 两级比较把“正确性（域隔离）”放在“均衡（WFQ）”之前。EC 模式更进一步：`failure_domains_required` 时直接清掩码位（硬剔除，见 3.5），而非仅排序偏好。

---

### 3.3 `bch2_dev_stripe_increment_inlined() / bch2_dev_stripe_increment() / bch2_stripe_state_rescale()` — `fs/alloc/foreground.c`

**签名：**

```c
static inline void bch2_dev_stripe_increment_inlined(struct bch_dev *ca,
                                                     struct dev_stripe_state *stripe,
                                                     struct bch_dev_usage *usage)
void bch2_dev_stripe_increment(struct bch_dev *ca, struct dev_stripe_state *stripe)
static noinline void bch2_stripe_state_rescale(struct dev_stripe_state *stripe)
```

**参数：** `usage` 为调用者已读的 `bch_dev_usage`（`bch2_bucket_alloc_set_trans` 复用 `req->usage`，避免每副本重扫 per-cpu），`stripe` 为写点 WFQ 状态。

**关键片段（加权增量，≤10行）：**

```c
u64 *v = stripe->next_alloc + ca->dev_idx;
u64 free_space = __dev_buckets_free(ca, *usage, BCH_WATERMARK_normal);
u64 free_space_inv = free_space ? div64_u64(stripe_clock_hand_inv, free_space)
                                : stripe_clock_hand_inv;
u64 sum = *v + free_space_inv;
*v = sum >= *v ? sum : U64_MAX;
```

常量：`rescale=1ULL<<62` 触发，`max=1ULL<<56` 为缩放后上限，`inv=1ULL<<52` 为空盘最大步长。

**`rescale` 逻辑：** 求 `scale_max=min(非零 hands)`（不下溢上限）与 `scale_min=max(超 max 部分)`（不上溢下限），取 `max` 整体平移，零保持零（注释：`if clock hands go to 0 then we lose information`，尽量不把信息压成 0）。

**权衡：** 饱和加 + 阈值重缩放解决 `u64` 溢出与长期运行漂移。按 `BCH_WATERMARK_normal` 空闲算权重（而非实时水位），让 WFQ 基准稳定，不因单次高水位请求抖动。

---

### 3.4 `bch2_dev_domain_keys_update()` — `fs/alloc/foreground.c`

**签名：**

```c
static void bch2_dev_domain_keys_update(struct bch_fs *c, struct alloc_request *req)
```

**语义：** `rcu` 下对 `devs_may_alloc` 每盘重算 `domain_keys[i] = bch2_dev_domain_key(c, &req->devs_chosen, i)`。`devs_chosen = devs_have + 已分配桶`，每选一副本即变，故每次重排前必刷新。

**EC 硬剔除片段：**

```c
if (req->failure_domains_required)
  for_each_set_bit(i, req->devs_may_alloc.d, BCH_SB_MEMBERS_MAX)
    if (req->domain_keys[i])
      __clear_bit(i, req->devs_may_alloc.d);
```

**权衡：** EC 同域不可纠错，偏好不够，必须硬失败/缩窄（宁可 `insufficient_devices` 也不双押同域）。普通副本则软偏好（排序），兼顾成功率与隔离。

---

### 3.5 `bch2_bucket_alloc_set_trans()` — `fs/alloc/foreground.c`

**签名：**

```c
int bch2_bucket_alloc_set_trans(struct btree_trans *trans,
                                struct alloc_request *req,
                                struct dev_stripe_state *stripe)
```

**参数/返回：** `stripe` 为写点 WFQ；返回 `0` 集齐（`add_new_bucket` 返回 1 即终止），`ERR(transaction_restart/operation_blocked/open_buckets_empty)` 必须立即返回，`ERR(freelist_empty/insufficient_devices)` 由上层按 `will_retry_*` 降级。

**关键循环（≤10行骨架）：**

```c
darray_for_each(req->devs_sorted, i) {
  req->ca = bch2_dev_tryget_noerror(c, *i);
  if (!req->ca) continue;
  struct open_bucket *ob = bch2_bucket_alloc_trans(trans, req);
  if (!IS_ERR(ob))
    bch2_dev_stripe_increment_inlined(req->ca, stripe, &req->usage);
```

成功才推进虚拟时间，失败不推进（失败盘不惩罚，下次仍按原 hand 参与，避免失败放大）。

**`add_new_bucket()` 语义（同文件 static）：** 清 `devs_may_alloc` 位、置 `devs_chosen` 位、`nr_effective += durability`、`ob_push(&req->ptrs)`；`durability==0`（cache 盘）或 `BCH_WRITE_cached` 只取一副本即回 1；`nr_effective>=nr_replicas` 回 1。

**权衡：** `do {…} while(progress)` 外层保证每轮至少新增一副本才重排继续，否则 `insufficient_devices` 退出，避免空转。`will_retry_set_devices = i+1 < …` 记录“是否还有同集合盘未试”，供 `bch2_bucket_alloc_trans` 决定是否阻塞（未试完不 blocking，先试完）。

---

## 四、七档水位：清运死锁终结者

### 4.0 定义：`BCH_WATERMARKS()` — `fs/alloc/types.h`

**签名：**

```c
#define BCH_WATERMARKS() x(stripe) x(normal) x(copygc) x(btree) \
                         x(btree_copygc) x(reclaim) x(interior_updates)
enum bch_watermark { BCH_WATERMARK_stripe, ..., BCH_WATERMARK_NR };
#define BCH_WATERMARK_BITS 3
```

**语义：** 枚举值越小保留越多（`bch2_dev_buckets_reserved()` 按 fallthrough 累加，`stripe` 最苛刻，`interior_updates` 零保留）。`bch2_watermarks[]` 字符串表供 debug 输出（`foreground.c`）。

**权衡：** 多档语义而非满/空二值：前台 `normal`、条带预留 `stripe`、清运自举 `copygc`、btree 优先 `btree/btree_copygc`、回收保底 `reclaim`、分裂必成功 `interior_updates`。后台任务可用低水位欠账推进，打破“清运者等自己腾的空间”的死锁。

---

### 4.1 `bch2_dev_buckets_reserved() / __dev_buckets_free() / __dev_buckets_available()` — `fs/alloc/buckets.h`

**签名：**

```c
static inline u64 bch2_dev_buckets_reserved(struct bch_dev *ca, enum bch_watermark watermark)
static inline u64 __dev_buckets_free(struct bch_dev *ca, struct bch_dev_usage usage,
                                     enum bch_watermark watermark)
static inline u64 __dev_buckets_available(struct bch_dev *ca, struct bch_dev_usage usage,
                                          enum bch_watermark watermark)
```

**关键片段（fallthrough 累加）：**

```c
case BCH_WATERMARK_stripe:   reserved += ca->mi.nbuckets >> 6; fallthrough;
case BCH_WATERMARK_normal:   reserved += ca->mi.nbuckets >> 6; fallthrough;
case BCH_WATERMARK_copygc:   reserved += ca->nr_btree_reserve; fallthrough;
case BCH_WATERMARK_btree:    reserved += ca->nr_btree_reserve; fallthrough;
```

- `free = free_buckets - nr_open_buckets - reserved`（严格空闲，开桶已算占用）。
- `available = free + cached + need_gc_gens + need_discard - nr_open - reserved`（可回收也算，给 copygc/discard 决策用）。

**权衡：** `>>6`（1/64+1/64）为条带/前台保留，`nr_btree_reserve` 为 btree 双份保留（copygc 与 btree 各一份，fallthrough 叠加即 2×）。保留量与盘大小成比例，大盘大保留，小盘不饿死（`max(s64,0,…)` 钳零）。

---

### 4.2 `bch2_open_buckets_reserved() / bch2_open_buckets_journal_reserved()` — `fs/alloc/foreground.h`

**签名与映射（已核实）：**

```c
case BCH_WATERMARK_interior_updates: return 0;
case BCH_WATERMARK_reclaim:          return OPEN_BUCKETS_COUNT / 6;
case BCH_WATERMARK_btree:
case BCH_WATERMARK_btree_copygc:     return OPEN_BUCKETS_COUNT / 4;
case BCH_WATERMARK_copygc:           return OPEN_BUCKETS_COUNT / 3;
default:                             return OPEN_BUCKETS_COUNT / 2;
static inline unsigned bch2_open_buckets_journal_reserved(void)
  { return OPEN_BUCKETS_COUNT / 4; }
```

**语义：** 开桶池 4096 中的预留：普通请求只可用一半（2048），copygc 可用 2/3，btree 可用 3/4，reclaim 可用 5/6，`interior_updates` 全可用。`bch2_bucket_alloc_trans()` 成功开桶后若 `nr_free < journal_reserved` 则 `bch2_journal_set_watermark()` 提前节流 journal，避免回收路饿死。

**权衡：** 两级水位（设备桶数 + 开桶池数）正交：前者防容量耗尽，后者防元数据对象耗尽。Journal 联动是反压前移：在 reservation 时节流，而非在落盘时失败。

---

### 4.3 `req_alloc_should_bail() + req_dev_sizes_mismatched()` — `fs/alloc/foreground.c`

**签名：**

```c
static bool req_dev_sizes_mismatched(struct bch_fs *c, struct alloc_request *req)
static bool req_alloc_should_bail(struct bch_fs *c, struct alloc_request *req)
```

**`mismatched` 判定：** `nr_replicas<=1` 直接 false；否则 `total=sum(nbuckets)`，`max=max(nbuckets)`，`return max > (total-max)`。注释证明：`N*max <= total` 否则最大盘的一块的 N-1 副本无处安放（`Replicas can only fit when no single device exceeds 1/N of total`）。

**`should_bail` 三条件（注释已核实，欠复制提交即返回 `bucket_alloc_no_progress` 而非等待）：**

```c
return !req->copygc_can_make_progress ||
       (req->watermark == BCH_WATERMARK_copygc && req->data_type != BCH_DATA_btree) ||
       req_dev_sizes_mismatched(c, req);
```

前提 `have_replicas = nr_effective || devs_have->nr`（至少已有一副本才可欠账）。

**权衡：**

- `!copygc_can_make_progress`：等也无用，直接欠账返回，不占 `freelist_wait`。
- `copygc 水位 + 非 btree`：请求本身就是清运者，等自己即死锁，必须欠账。btree 排除：单指针 btree 落到坏盘会导致 `emergency_ro`，宁可等也不错写。
- `sizes_mismatched`：拓扑性不可能（如删盘后一大盘 + 多小盘），等/copygc 均无解，必须降副本或失败。

---

### 4.4 `bch2_bucket_alloc_trans()` 水位等待 — `fs/alloc/foreground.c`

**签名：**

```c
struct open_bucket *bch2_bucket_alloc_trans(struct btree_trans *trans,
                                            struct alloc_request *req)
```

**参数：** `req->ca` 为本轮候选盘（调用者 `bch2_bucket_alloc_set_trans` 已 `tryget`），`req->watermark/data_type/flags/cl` 决定阻塞语义，`req->btree_bitmap` 由 `data_type==btree` 初判（btree 优先落 btree_bitmap 区）。

**水位空分支（已核实）：** `avail==0` 时：恢复期 `watermark>normal` 直接 `goto alloc`（fsck 需强行推进）；否则查 `bch2_copygc_can_make_progress(ca)` 并 `wakeup copygc`；有 `cl` 且非 `alloc_nowait` 且无 `will_retry_*` 时，`should_bail→no_progress` 或 `closure_wait(freelist_wait)+goto again`（第一次）或 `bucket_alloc_blocked`（第二次）；无 `cl` 则 `freelist_empty`。

**`BTREE_ITER_committed` 约束（`bucket_alloc_scan` 注释）：** 分配是不可撤销副作用（开桶/btree 节点活过事务重启），只消费已提交状态。discard 路 `mark_free` 触发分裂时若读到本事务未提交释放，会分配到正被释放的桶并使其 open，导致重试永不释放。所有分配路状态读必须带 `COMMITTED`。

**权衡：** 等待是条件等待（trace 快照 + `alloc_wait_advanced` 过滤伪唤醒，见 4.5），不是无脑睡。`need_discard/need_gc_gens` 超阈异步踢 `discard/gc_gens/invalidates`，让等待期间有生产者。

---

### 4.5 `alloc_wait_advanced() / __bch2_wait_on_allocator() / bch2_alloc_wake_dev/all/unpark()` — `fs/alloc/foreground.c/h`

**签名：**

```c
static bool alloc_wait_advanced(struct bch_fs *c, struct alloc_request *req)
void __bch2_wait_on_allocator(struct btree_trans *trans, struct alloc_request *req,
                              int err, struct closure *cl)
void bch2_alloc_wake_dev(struct bch_dev *ca)
void bch2_alloc_wake_all(struct bch_fs *c)
void bch2_alloc_waiters_unpark(struct bch_fs *c)
```

**语义：**

- `wake_dev`：`atomic_inc(ca->alloc_wake_counter) + wake freelist_wait`（自旋锁提供 release/acquire，无需显式 barrier，注释明示）。
- `wake_all`：`atomic_inc(wake_all_counter)`，强制全重试（新盘等 trace 外事件）。
- `unpark`：只 wake 不 bump，用于自摘除（llist 只能 wake 全员再各自重 park）。
- `alloc_wait_advanced`：`wake_all` 变了 → true；`trace_alloc_failed`（trace 压栈失败）→ true 保守重试；否则逐 trace 条目比 `alloc_wake_counter`，盘消失 → true；计数前进了且 `free>1 或 copygc 无进展` → true（后者避免 copygc 活锁时空转）。
- `__bch2_wait_on_allocator`：先快检 `bucket_alloc_blocked && advanced → unpark 返回`（防 wake 与 `closure_wait` 间 race 丢唤醒）；`trans_closure_sync_timeout(allocator_stuck_timeout)` 超时则 CAS `last_stuck`（2 分钟节流）后 `bch2_print_allocator_stuck()` dump；`emergency_ro` 直接返回（关机排水时 `free>1` 永假，避免卡死 `read_only_work`）；非 `blocked` 错误直接返回；否则 `advanced→返回`，`!advanced→re-park` 双检。

**权衡：** fs-wide 等待队列 + per-dev 计数过滤 = 伪唤醒 O(1) 过滤，不用 per-dev 等待队列（省内存与唤醒风暴）。`trace`（`DARRAY_PREALLOCATED 16`）是诊断与正确性双用：stuck 打印 + 精准重唤醒。

---

## 五、双层预留：热点与作废

### 5.0 中枢结构：`struct disk_reservation / struct bch_fs_capacity(_pcpu)` — `buckets_types.h / types.h`

```c
struct disk_reservation { u64 sectors; u32 generation; unsigned nr_replicas; };
struct bch_fs_capacity_pcpu { struct bch_fs_usage_base usage; u64 sectors_available;
                              u64 online_reserved; };
struct bch_fs_capacity { u64 capacity; u64 reserved; u32 capacity_gen;
                         unsigned bucket_size_max; atomic64_t sectors_available;
                         spinlock_t sectors_available_lock;
                         struct bch_fs_capacity_pcpu __percpu *pcpu;
                         struct percpu_rwsem_noio mark_lock; };
```

- `sectors_available` 双层：全局 `atomic64`（慢池）+ per-cpu `sectors_available`（快池，热点无锁）。
- `online_reserved`：已预留未落盘量，计入 `__bch2_fs_usage_read_short().reserved`，短视图立即可见（防超卖）。
- `capacity_gen`：缩容代际，注释 `When capacity decreases … increment capacity_gen - invalidates outstanding reservations`。
- `mark_lock`：`percpu_rwsem_noio`，记账/预留读写的张弛锁（NOIO 防回收递归）。

---

### 5.1 `bch2_disk_reservation_add() / __bch2_disk_reservation_add() / disk_reservation_recalc_sectors_available()` — `buckets.h/c`

**签名：**

```c
static inline int bch2_disk_reservation_add(struct bch_fs *c, struct disk_reservation *res,
                                            u64 sectors, enum bch_reservation_flags flags)
int __bch2_disk_reservation_add(struct bch_fs *c, struct disk_reservation *res,
                                u64 sectors, enum bch_reservation_flags flags)
static int disk_reservation_recalc_sectors_available(struct bch_fs *c, struct disk_reservation *res,
                                                     u64 sectors, enum bch_reservation_flags flags)
```

**快路（`buckets.h`，`__KERNEL__` 内）：**

```c
old = this_cpu_read(c->capacity.pcpu->sectors_available);
do {
  if (sectors > old) return __bch2_disk_reservation_add(c, res, sectors, flags);
  new = old - sectors;
} while (!this_cpu_try_cmpxchg(c->capacity.pcpu->sectors_available, &old, new));
this_cpu_add(c->capacity.pcpu->online_reserved, sectors);
res->sectors += sectors;
return 0;
```

per-cpu 足够即 CAS 快扣 + `online_reserved+=`，无全局锁、无关中断（`preempt guard` 在慢路）。

**慢路（`buckets.c:991`）：** `guard(preempt)` 取 `this_cpu_ptr`，若 `sectors > pcpu->sectors_available` 则从全局 `atomic64` 批量搬 `get=min(sectors+SECTORS_CACHE(1024), old)`；`get<sectors`（全局也不够）则进 `recalc`（持 `sectors_available_lock`、清 per-cpu 为 0、重算 `avail_factor(free)`、PARTIAL 则 `min` 部分满足、NOFAIL 则强制成功、否则 `ENOSPC_disk_reservation`）。

**权衡：** 热点分散（per-cpu）+ 批量补充（+1024 摊销全局 CAS）+ 慢路重算（全局真相）。`SECTORS_CACHE` 是预取窗口：搬多 1024 减少下次全局往返，代价是 per-cpu 滞留少量可用量（`sectors_available` 求和时需全扫，见 5.2）。

---

### 5.2 `__bch2_fs_usage_read_short() / bch2_fs_usage_read_short()` — `fs/alloc/buckets.c`

**签名：**

```c
static struct bch_fs_usage_short __bch2_fs_usage_read_short(struct bch_fs *c)
struct bch_fs_usage_short bch2_fs_usage_read_short(struct bch_fs *c)
```

**关键片段：**

```c
struct bch_fs_capacity_pcpu b = {};
acc_u64s_percpu((u64 *) &b, (u64 __percpu *) c->capacity.pcpu, sizeof(b) / sizeof(u64));
ret.capacity = c->capacity.capacity - b.usage.hidden;
u64 data = b.usage.data + b.usage.btree;
u64 reserved = b.usage.reserved + b.online_reserved;
ret.used = min(ret.capacity, data + reserve_factor(reserved));
ret.free = ret.capacity - ret.used;
```

外层包 `guard(percpu_read_noio)(&mark_lock)`，一次扫每 cpu 一 cacheline（注释：`One sweep … while its cache lines are hot`），`sectors_available` 求和进 throwaway 忽略（短视图只关心 used/free）。

**`reserve_factor/reserve_factor/avail_factor`（`buckets.c/h`）：** `reserve_factor(r)=r+(round_up(r,1<<6)>>6)`（约 ×1.0156，元数据膨胀预留），`avail_factor(r)=(r<<6)/65`（约 ×0.9846，`recalc` 时打折可用量，留安全边际）。一加一减形成迟滞，避免边界抖动超卖。

**权衡：** 短视图是 O(Ncpu) 近似真相，供 `too_many_writepoints/stranded` 与 `recalc` 快判，不走 btree。`hidden`（sb/journal）从容量扣减，保证用户可见 `free` 不含元数据黑洞。

---

### 5.3 `bch2_disk_reservation_put() / bch2_disk_reservation_init/get()` — `fs/alloc/buckets.h`

**签名：**

```c
static inline void bch2_disk_reservation_put(struct bch_fs *c, struct disk_reservation *res)
static inline struct disk_reservation bch2_disk_reservation_init(struct bch_fs *c, unsigned nr_replicas)
static inline int bch2_disk_reservation_get(struct bch_fs *c, struct disk_reservation *res,
                                            u64 sectors, unsigned nr_replicas, int flags)
```

**语义：** `put` 为 `this_cpu_sub(online_reserved, res->sectors)+res->sectors=0`（只还 per-cpu 预留，不直接还全局 `sectors_available`，全局在 `trans_account` 或 `recalc` 时统一校准，避免双还）。`init` 置零（`generation` 段 `#if 0` 保留未启用，说明代际作废已收敛到 `capacity_gen` 全局而非逐 reservation 比较）。`get = init + add(sectors*nr_replicas)`。

`DEFINE_CLASS(disk_reservation, … bch2_disk_reservation_put…)` 提供 RAII 自动归还，事务/写路可 `CLASS(disk_reservation,…)` 防漏。

**权衡：** 预留生命周期与事务绑定：`bch2_trans_account_disk_usage_change()` 提交时 `disk_res->sectors -= added + this_cpu_sub(online_reserved, added)` 冲销，多退少补；`should_not_have_added>0`（用超了）则直接扣全局 `sectors_available` 并 `warn` 一次（`warned_disk_usage` 单次打印防刷屏）。

---

### 5.4 `bch2_trans_account_disk_usage_change()` — `fs/alloc/buckets.c`

**签名：**

```c
void bch2_trans_account_disk_usage_change(struct btree_trans *trans)
```

**参数：** 无返回，操作 `trans->fs_usage_delta`（触发器累积的 `btree+data+reserved` 增量）与 `trans->disk_res`（本事务预留）。要求调用者持有 `mark_lock`（`lockdep_assert_held`）。

**关键片段（超用扣全局，≤10行）：**

```c
s64 should_not_have_added = added - (s64) disk_res_sectors;
if (unlikely(should_not_have_added > 0)) {
  old = atomic64_read(&c->capacity.sectors_available);
  do { new = max_t(s64, 0, old - should_not_have_added);
  } while (!atomic64_try_cmpxchg(&c->capacity.sectors_available, &old, new));
```

**调用链：** 事务提交路径（`commit_do`）在传播内存计数器时调用，是预留→记账的交割点。`added>0` 则 `disk_res->sectors-=added + online_reserved-=added`（预留转实耗），再 `acc_u64s(dst per-cpu usage, src delta)` 落快照。

**权衡：** 允许“先欠账后扣全局”（`should_not_have_added`），保证提交不因预留竞态失败，事后校准 + 一次性 `inconsistent` 告警。不阻断前台，以可观测性换可用性。

---

## 六、成员全周期：槽位到流水线

### 6.0 槽位：`bch2_sb_member_find_slot() / bch2_sb_member_alloc() / bch2_sb_members_clean_deleted()` — `fs/sb/members.c`

**签名：**

```c
static int bch2_sb_member_find_slot(struct bch_fs *c)
int bch2_sb_member_alloc(struct bch_fs *c)
void bch2_sb_members_clean_deleted(struct bch_fs *c)
```

**`find_slot` 策略：**

```c
if (c->sb.nr_devices < BCH_SB_MEMBERS_MAX &&
    c->sb.nr_devices != BCH_SB_MEMBER_INVALID) return c->sb.nr_devices;
```

未满直接尾部分配（O(1)）；满则扫 `BCH_SB_MEMBERS_MAX` 跳过哨兵 `BCH_SB_MEMBER_INVALID`（该槽永不分配，`INVALID` 亦作 `devs_mask` 终止符与 `alloc_trace` 无盘标记），统计 `nr_deleted`（DELETED_UUID 需 fsck 清理，不可直接复用），在全零 UUID 槽中选 `last_mount` 最老者（最不可能仍被旧挂载引用）。

**`alloc`：** `find_slot` 成功后 `bch2_sb_field_resize(members_v2, …)` 扩 `nr_devices=max(dev_idx+1, nr_devices)`。`EBUG_ON(dev_idx==INVALID)` 硬断言哨兵。

**`clean_deleted`：** 持 `sb_lock` 将 `DELETED_UUID → 零 UUID` 并 `bch2_write_super()`，是删除双态（DELETED→空闲）的,I终态；在 fsck/删盘完成后调用。

**权衡：** 哨兵保留 + 双态删除 + 最老复用：哨兵防越界与终止歧义；双态让“删盘未完成崩溃”可恢复（DELETED 仍占槽，不会被新盘顶掉）；最老复用降低 UUID 重用误认。

---

### 6.1 变长升级：`sb_members_v2_resize_entries() / bch2_sb_members_v2_init() / bch2_sb_members_cpy_v2_v1()` — `fs/sb/members.c`

**签名：**

```c
static int sb_members_v2_resize_entries(struct bch_fs *c)
int bch2_sb_members_v2_init(struct bch_fs *c)
int bch2_sb_members_cpy_v2_v1(struct bch_sb_handle *disk_sb)
```

**语义：** `member_bytes < sizeof(struct bch_member)` 时 `DIV_ROUND_UP` 重算 `u64s` 后 `bch2_sb_field_resize`，再从高到低 `memmove + 补零` 原地拓宽（倒序防覆盖）。`v2_init` 在无 `members_v2` 时从 `members_v1` `memcpy(BCH_MEMBER_V1_BYTES*nr)+member_bytes=V1` 创建，再调 `resize_entries` 拓到全尺寸。`cpy_v2_v1` 在旧元数据版本回写 `members_v1`（新版本 `> extent_flags` 则直接 `resize(v1,0)` 删段）。

**权衡：** 超块字段变长向前兼容：老内核读新盘见 `member_bytes` 小则按小解析，新内核见小则拓宽补零。`memmove` 倒序是原地升级无额外分配（超块上下文不可递归分配）。

---

### 6.2 合法性：`validate_member() / bch2_sb_members_v1/v2_validate()` — `fs/sb/members.c`

**签名：**

```c
static int validate_member(struct printbuf *err, struct bch_member m,
                           struct bch_sb *sb, int i)
static int bch2_sb_members_v1_validate(struct bch_sb *sb, struct bch_sb_field *f,
                                       enum bch_validate_flags flags, struct printbuf *err)
static int bch2_sb_members_v2_validate(struct bch_sb *sb, struct bch_sb_field *f,
                                       enum bch_validate_flags flags, struct printbuf *err)
```

**`validate_member` 四门（已核实）：**

```c
nbuckets > BCH_MEMBER_NBUCKETS_MAX → invalid
nbuckets - first_bucket < BCH_MIN_NR_NBUCKETS → invalid
bucket_size < block_size / bucket_size < BTREE_NODE_SIZE → invalid
btree_bitmap_shift >= MAX → invalid
FREESPACE_INITIALIZED && no_alloc_info → invalid
```

`v1/v2_validate` 先验段大小（`members_v1_get_mut(nr_devices) > vstruct_end` / `__members_v2_get_mut(nr_devices)-mi > vstruct_bytes`），再逐盘调 `validate_member`。

**权衡：** 挂载前强校验，错盘早拒（`invalid_sb_members`），不让非法几何进入分配器（否则 `sector_to_bucket/bucket_to_sector` 越界）。

---

### 6.3 分诊恢复：`bch2_dev_missing_bkey_msg/missing_bkey/missing_atomic/bucket_missing()` — `fs/sb/members.c`

**签名：**

```c
int bch2_dev_missing_bkey_msg(struct bch_fs *c, struct bkey_s_c k, unsigned dev,
                              struct printbuf *out)
int bch2_dev_missing_bkey(struct bch_fs *c, struct bkey_s_c k, unsigned dev)
void bch2_dev_missing_atomic(struct bch_fs *c, unsigned dev)
void bch2_dev_bucket_missing(struct bch_dev *ca, u64 bucket)
```

**语义：** `INVALID` 直接 0（EC 占位指针合法）；否则区分 `removed（devs_removed）→ ptr_to_removed` 与 `nonexistent → ptr_to_invalid`，打印 key + `count_fsck_err + run_explicit_recovery_pass(check_allocations)`。`atomic` 变体用于不可睡眠上下文（`printbuf_atomic + backtrace + inconsistent`）。`bucket_missing` 报 `bucket%llu valid range first-nbuckets` 越界。

**调用链：** `bch2_trigger_pointer()` 中 `!ca / !bucket_valid` 时调用，是触发器路的分诊入口。

**权衡：** 区分“删过”与“从未存在”：前者可修（重建分配信息），后者多为灾难（需 fsck）。限流日志（`bch_log_msg_ratelimited` 在调用者）防坏盘刷屏。

---

### 6.4 CPU 侧镜像：`bch2_sb_members_to_cpu() / bch2_sb_members_from_cpu()` — `fs/sb/members.c`

**签名：**

```c
void bch2_sb_members_to_cpu(struct bch_fs *c)
void bch2_sb_members_from_cpu(struct bch_fs *c)
```

**`to_cpu` 三步：** `for_each_member_device → ca->mi = bch2_mi_to_cpu(m) + mod_bit(rotational)`；故障域字符串 intern 为小 id（`0=unset`，`id=1-based index into distinct strings`，`DARRAY` 瞬态表，`ENOMEM` 则留 unset 安全降级）；`DELETED_UUID → mod_bit(devs_removed)`。

**`from_cpu`：** `rcu` 下回写 `errors[]`（`atomic64_read → cpu_to_le64`），超块落盘前调用，保证错误计数持久化。

**权衡：** 字符串比较在热路不可接受，intern 为 `u16 id` 后 `domain_keys` 只比整数。`to_cpu` 在持 `state_lock`/恢复期调用，不在分配热路。

---

### 6.5 只读切换时序：`__bch2_dev_read_only() / __bch2_dev_read_write()` — `fs/init/dev.c`

**签名：**

```c
static void __bch2_dev_read_only(struct bch_fs *c, struct bch_dev *ca)
static void __bch2_dev_read_write(struct bch_fs *c, struct bch_dev *ca)
```

**`read_only` 时序（已核实注释顺序即正确性）：**

```c
bch2_journal_flush_dev_ro(&c->journal, ca->dev_idx); // 先推 journal reclaim，防 journal_full  stranded
bch2_dev_allocator_remove(c, ca); bch2_recalc_capacity(c); // 摘 rw_devs + 等开桶排空
bch2_dev_io_ref_stop(ca, WRITE); // 开桶排空才停写 ref（在途 submit 仍持开桶 ref）
bch2_dev_journal_stop(&c->journal, ca); bch2_do_discards_async(c);
bch2_fs_ec_flush_outstanding(c); // stripe_new_list 在途提交排空，data-drop 才能见全 backpointers
```

**`read_write` 逆序：** `allocator_add + recalc + io_ref start + discards_async`，要求 `state==rw`（`BUG_ON`）。

**权衡：** 时序即正确性：journal→分配器→io_ref→条带，每步都等前步的在途引用排空。用 `nr_open_buckets/nr_partial_buckets` 与 `io_ref` 双重排空，不用大栅栏停机。

---

### 6.6 状态机：`__bch2_dev_set_state() / bch2_dev_set_state()` — `fs/init/dev.c`

**签名：**

```c
int __bch2_dev_set_state(struct bch_fs *c, struct bch_dev *ca,
                         enum bch_member_state new_state, int flags,
                         struct printbuf *err)
int bch2_dev_set_state(struct bch_fs *c, struct bch_dev *ca,
                       enum bch_member_state new_state, int flags,
                       struct printbuf *err)
```

**逻辑：** 同态早回（`evacuating` 重入则补 `set_reconcile_needs_scan`）；`bch2_dev_state_allowed()` 门禁；非 `rw` 先 `__read_only`；`notice + reconcile_scan（rw/evacuating 触发 device/pending 扫描）`；`sb_lock` 下 `SET_BCH_MEMBER_STATE + write_super`；`rw && online` 则 `__read_write`；RW 进出均补 `stripes` 扫描（EC widening 目标变了，`can_widen` 需收敛）。

**权衡：** 状态变更是“分配器摘除 + reconcile 扫描 + 超块落盘”三联动，不是单字段赋值。`state_lock(rwsem_write)` 串行化，外层 `bch2_dev_set_state` 还检查 `removing`（删盘中拒变状态）。

---

### 6.7 移除全流水线：`__bch2_dev_remove() / bch2_dev_remove()` — `fs/init/dev.c`

**签名：**

```c
static int __bch2_dev_remove(struct bch_fs *c, struct bch_dev *ca,
                             bool fast_device_removal, int flags,
                             struct printbuf *err)
int bch2_dev_remove(struct bch_fs *c, struct bch_dev *ca, int flags,
                    struct printbuf *err)
```

**流水线（已核实，需 `state_lock`）：** `put_outer（消费调用者 ref，防死锁）→ removing=true（栅栏条带新建）→ set_state(evacuating) → ec_flush → data_drop（fast 用 backpointers，否则 data_drop+remove_stripes）→ interior_flush → 查非空非隐藏 data_type 仍有桶则 EBUSY → journal_flush_outstanding_pins/flush_device_pins/flush → offline（禁读）→ remove_alloc（删 alloc keys）→ journal_flush（alloc 删除落盘）→ replicas_gc_accounted → dev_has_data 复检 → c->devs[idx]=NULL → ref drain → 外层 state_lock 外 `dev_free`。`

**失败回滚：**

```c
WRITE_ONCE(ca->removing, false);
if (rw && state==rw && !io_ref_zero(READ)) __bch2_dev_read_write(c, ca);
```

设备留下则重加回分配器，`removing` 清零允许新引用。

**权衡：** 全流水线 + 双重 `has_data` 检查（删 alloc 前后各一次）+ 三次 journal flush（pins→alloc 删除→replicas），每步失败都可回滚留盘。用 `fast_device_removal（compat no_stale_ptrs && !incompat fast_removal）` 选择 backpointers 快路，否则全量 data_drop，兼容老盘。

---

### 6.8 添加四阶段：`bch2_dev_add_initialize() / bch2_dev_add() / bch2_dev_online()` — `fs/init/dev.c`

**签名：**

```c
int bch2_dev_add_initialize(struct bch_fs *c, struct bch_dev *ca)
int bch2_dev_add(struct bch_fs *c, const char *path, struct printbuf *err)
int bch2_dev_online(struct bch_fs *c, const char *path, struct printbuf *err)
```

**`add_initialize` fallthrough 四阶段（`initialized` 状态机可重入，恢复可续跑）：**

```c
pre_dev_usage → dev_usage_init(false) → pre_mark_sb
pre_mark_sb → trans_mark_dev_sb → pre_freespace_init
pre_freespace_init → fs_freespace_init → pre_journal_alloc
pre_journal_alloc → dev_journal_alloc → initialized
```

**`add` 要点：** `read_super + member_get(dev_idx) + label + may_add + __dev_alloc`，多设备首次 `fs_list` 注册防 UUID 双开。

**权衡：** 初始化幂等（`dev_usage_init` 注释：`Set, not add … idempotent, safe to re-run when half-finished add resumed during recovery`，用 `nbuckets - cur` 差值置数而非累加）。阶段落盘（`dev_set_initialized`）保证崩溃续跑不重不漏。

---

## 七、记账双轨与自愈

### 7.0 总纲注释 — `fs/alloc/accounting.c:21-67`

已核实双轨自述：

- 盘上：`accounting btree + write buffer deltas`（新 key 作 delta 合并到旧值），读贵。
- 内存：`percpu counters + eytzinger keys`，读廉价，不持久。
- 触发器（transactional triggers）比较 old/new 产 delta；提交路径经 `bch2_accounting_mem_mod()` 推内存 + 赋版本（journal seq + buffer offset，replay 去重）；`replicas` 更新联动超块标记（mount 可用性）。

**11 种类型**由 `BCH_DISK_ACCOUNTING_TYPES()` 定义（`disk_accounting_type_strs/nr_counters` 双表驱动，`replicas` 需 `bubble_sort(devs)` 归一化）。

---

### 7.1 写路增量：`bch2_disk_accounting_mod_normal() / bch2_disk_accounting_mod_gc()` — `fs/alloc/accounting.c`

**签名：**

```c
int bch2_disk_accounting_mod_normal(struct btree_trans *trans,
                                    struct disk_accounting_pos *k, s64 *d, unsigned nr)
int bch2_disk_accounting_mod_gc(struct btree_trans *trans,
                                struct disk_accounting_pos *k, s64 *d, unsigned nr)
```

**`normal`：** `BUG_ON(nr>MAX / type>=NR)` + `EBUG_ON(nr!=nr_counters[type])`，`replicas.devs` 排序归一后转 `bpos`，在 `trans->accounting` subbuf 内同 `pos+nr` 合并（`acc_u64s` 累加，归零则 `memmove_down` 删条目），否则 `subbuf_alloc + __accounting_key_init` 新条目。纯暂存，提交时才进 write buffer + 内存。

**`gc`：** 同归一后直接 `__accounting_key_init(stack k_i)`，`percpu_read` 下 `accounting_mem_add_inlined(GC)`，`need_mark_replicas` 则 `drop_locks_do(accounting_update_sb_one)` 重试。GC 计数器独立 `v[1]`（见 7.3），不污染前台。

**权衡：** 写路合并同 key deltas（一次提交多次改同一 replicas 只发一条 write buffer），`trans->accounting` 为事务私有 subbuf，无锁。GC 路同步改内存（fsck 比对基准），失败可补超块标记后重试。

---

### 7.2 触发器双轨：`bch2_trigger_extent() / __trigger_extent() / bch2_trigger_pointer() / bch2_trigger_stripe_ptr()` — `fs/alloc/buckets.c`

**签名：**

```c
int bch2_trigger_extent(struct btree_trans *trans, struct btree_trigger_op op)
static int __trigger_extent(struct btree_trans *trans, enum btree_id btree_id,
                            unsigned level, struct bkey_s_c k,
                            enum btree_iter_update_trigger_flags flags)
static int bch2_trigger_pointer(struct btree_trans *trans, enum btree_id btree_id,
                                unsigned level, struct bkey_s_c k,
                                struct extent_ptr_decoded p,
                                const union bch_extent_entry *entry, s64 *sectors,
                                enum btree_iter_update_trigger_flags flags)
```

**`trigger_extent` 快路：** 新旧指针字节全等则 0 返回（`memcmp ptrs`），无 delta。否则 `transactional|gc` 才跑：`overwrite` 跑 old（取负），`insert` 跑 new；`extent whiteout` 等由 `snapshot_key_counted` 过滤（见 7.6）。

**`__trigger_extent` 三路记账：** 逐指针 `trigger_pointer → disk_sectors`，`cached → mod_dev_cached_sectors`，`!ec → replicas_sectors+= + entry_add_dev`，`ec → trigger_stripe_ptr`（`nr_required=0`，EC 不计普通 replicas）；压缩类型变化即时结算 `compression` 三元组；`snapshot` 自记 `[nr,bytes,sectors]`；`level>0` 记 `btree[id]` 三元组，`level==0` 记 `inum[inode]` 三元组。

**`trigger_pointer` 双 flag：** `transactional` 走 `trans_start_alloc_update + __mark_pointer(bucket_ref_update) + backpointer_mod`（alloc btree 真值）；`gc` 走 `bucket_lock(gc_bucket) + mark + alloc_key_to_dev_counters`（GC 影子值）。`INVALID dev` + EC 则清 stripe backpointer；`!ca` 则 `trigger_pointer_dev_missing` 分诊；桶越界 `insert→missing+throw，delete→0`（删容忍，防删不掉）。

**权衡：** 同一触发函数产两套记账（trans 写 buffer deltas + gc 影子 counters），`flags` 显式分支，无隐式耦合。指针级增量 + extent 级聚合，避免每指针一次 btree 更新。

---

### 7.3 预留触发：`bch2_trigger_reservation() / __trigger_reservation() / bch2_trigger_snapshot_nr_keys()` — `fs/alloc/buckets.c`

**签名：**

```c
int bch2_trigger_reservation(struct btree_trans *trans, struct btree_trigger_op op)
int bch2_trigger_snapshot_nr_keys(struct btree_trans *trans, struct btree_trigger_op op)
```

**`reservation`：** `trigger_run_overwrite_then_insert` 拆 old/new，`sectors=size（overwrite 取负）→ mod(persistent_reserved[nr_replicas])`，`snapshot` 自记 `[nr,bytes,sectors*nr_replicas]`（预留无指针，extent 的 snapshot sectors  sum 不含它，必须此处补）。

**`snapshot_nr_keys` 通用钩子：** `level||atomic` 跳过；`snapshot_key_counted = snapshot && !whiteout && type!=extent/reservation`（后两者自记，防双记）；`delta = new-old` 发 `[nr,bytes,0]`。注释明言 `atomic phase only applies already-staged deltas`，故跳过。

**权衡：** 热点（extent/reservation）自记合批发一次 delta，冷门走通用钩子。`whiteout` 不计与迭代语义对齐（迭代视 whiteout 为 absent，删空检查才对得上）。

---

### 7.4 内存表：`__bch2_accounting_mem_insert() / bch2_accounting_mem_insert() / bch2_accounting_mem_add()` — `fs/alloc/accounting.c`

**签名：**

```c
static int __bch2_accounting_mem_insert(struct bch_fs *c, struct bkey_s_c_accounting a)
int bch2_accounting_mem_insert(struct bch_fs *c, struct bkey_s_c_accounting a,
                               enum bch_accounting_mode mode)
int bch2_accounting_mem_add(struct btree_trans *trans, struct bkey_s_c_accounting a,
                            enum bch_accounting_mode mode, bool write_locked)
```

**`__insert`：** `eytzinger0_find` 存在即 0（竞态幂等）；否则按 `nr_counters[type]` `alloc_percpu(v[0])`，`gc_running` 则再配 `v[1]`，`darray_push + eytzinger0_sort`。失败 `free_percpu + ENOMEM_disk_accounting`。

**`insert` 包装：** 非 `read` 模式且为 `replicas` 则先 `replicas_marked_locked` 门禁（未标记超块 → `need_mark_replicas`，调用者补 `accounting_update_sb_one` 后重试，避免记账先于超块 durability 声明）。`raw up_read → percpu_write → __insert → down_read` 临时升级写锁（注释：`PF_MEMALLOC_NOIO stays set`，只动锁不动 memalloc 域）。

**权衡：** eytzinger 静态排序数组：查 O(log N) 无指针追逐，`mem` 读快路友好；插入 O(N log N) 但只在新 replicas 组合出现时发生（低频），读写分离。

---

### 7.5 启动归并：`bch2_accounting_read() / accounting_read_key() / accumulate_newer_accounting_keys() / accumulate_and_read_journal_accounting()` — `fs/alloc/accounting.c`

**签名：**

```c
int bch2_accounting_read(struct bch_fs *c)
static int accounting_read_key(struct btree_trans *trans, struct bkey_s_c k)
static struct journal_key *accumulate_newer_accounting_keys(struct btree_trans *trans,
                                                            struct journal_key *i)
static struct journal_key *accumulate_and_read_journal_accounting(struct btree_trans *trans,
                                                                  struct journal_key *i)
```

**`read` 五步（已核实）：** `free_counters(false)+k.nr=0+per-cpu usage/dev usage 清零`（可重跑，rewind 拓扑修复/节点扫描后结果可变，故不跳过）；journal keys `move_gap + 二分定 accounting [POS_MIN,SPOS_MAX]` 区间；btree（`!with_journal + prefetch + all_snapshots`）与 journal 双指针归并：`journal>btree→accumulate_and_read`，`journal==btree && journal ver<=btree ver→overwritten++`（旧 delta 丢），`== && 新→accumulate_and_read`（delta 叠 btree 基值）；非 `is_mem` 类型跳段（`set_pos(predecessor(next_type_bpos))`，`for_each` 仍会前进一步）；收尾 journal 扫尾 + `overwritten` 压缩 + `eytzinger_sort + duplicate BUG_ON` + `read_mem_fixups`（后者可提交，故不可持 `mark_lock`）。

**`read_key` 合并：** 非 `accounting` 跳过；`replicas 非零 + degraded` 门禁（`very→FORCE_IF_DEGRADED|LOST，yes→DEGRADED`，不够则 `insufficient_devices_to_start` 拒挂载）；非 `is_mem` 跳过；同 `bpos` 相邻合并（btree 基值 + journal delta 累加，依赖 bpos 有序故相邻断言）；否则 `alloc_percpu + push + percpu_set`。

**`accumulate_newer`：** 同一 bpos 后续 journal keys 逐个 `accounting_accumulate(k,n)+overwritten=true`，`ver 倒序则 fsck_err(version_out_of_order)`。版本（journal seq+offset）是去重与新旧判据。

**权衡：** 重建不删（归并只加不减，零值在 `fixups` 才滤），保证崩溃 replay 幂等。btree/journal 双流 + 版本去重 + 旧 delta 早 drop，mount 时间 O(有效 keys) 而非 O(journal 全量)。

---

### 7.6 自愈：`accounting_read_mem_fixups() / bch2_gc_accounting_start/done() / bch2_verify_accounting_clean()` — `fs/alloc/accounting.c`

**签名：**

```c
static int accounting_read_mem_fixups(struct btree_trans *trans)
int bch2_gc_accounting_start(struct bch_fs *c)
int bch2_gc_accounting_done(struct bch_fs *c)
void bch2_verify_accounting_clean(struct bch_fs *c)
```

**`fixups` 前向过滤（注释强调 O(N) 替代 O(NR) `darray_remove_item`）：** 零值 `→ -remove_entry → free_percpu 跳过`（零值视为不存在，复加时重走超块标记）；否则 `lockrestart_do(validate_late)`（`invalid dev → neg + mod + commit + remove_entry`，`replicas_not_marked → mark_replicas + commit`）；错误 tail 下移保持连续；`sort` 后 `underflow_check（s64<0→count+check_allocations）` + 落 `fs_usage_base/dev_usage`（`persistent_reserved×nr_replicas / replicas→data_type→base / dev_data_type→buckets/sectors/fragmented + sb/journal→hidden`）。

**`gc_start/done`：** `start` 配 `v[1]` 影子；`done` 逐 `eytzinger_find_ge` 比 `dst(v0) vs src(v1)`，失配 `fsck_err(accounting_mismatch→commit mod(src-dst, skip_accounting_apply))`，`!may_go_rw`（恢复期）还同步内存 + per-cpu usage。`gc_free` 释放 `v[1]`。

**`verify_clean`（DEBUG）：** btree 真值 vs 内存快照逐 key `memcmp + base 五项（hidden/btree/data/cached/reserved）`，失配 `pr_err + WARN_ON`，不自动修（只断言）。

**权衡：** 失配显式调度修复（`fsck_err` 返回 true 才 `commit_do`），不静默覆盖。GC 双计数器让“在线值 vs 重算值”可比对，自愈有据。`dev_usage_remove/init`（`accounting.c:1263/1303`）为删盘/加盘提供 `neg 全删 / 置数 init（幂等差值法）` 原语，与第六节流水线对接。

---

## 八、后台三件套：触发器·位图·丢弃

### 8.1 `bch2_trigger_alloc()` — `fs/alloc/background.c`

**签名：**

```c
int bch2_trigger_alloc(struct btree_trans *trans, struct btree_trigger_op op)
```

**参数/返回：** `op.{old,new,flags}`，`transactional` 才做状态机变迁 + 索引维护，`0` 成功，错误触发 fsck/recovery。

**已核实行为（`background.h:91` 注释 + 代码）：**

- 空→非空：`io_time[READ/WRITE]=now + NEED_INC_GEN=true + NEED_DISCARD=true`（gen 递增防旧指针复活，compat 位供老内核判 need_discard）。
- 非空→空：`new=data_type=need_discard`（sb/journal 除外），`freespace/discard` 索引经 `bucket_do_freespace/discard_index` 维护；`going empty but not open && !nouse → fsck_err(nonempty_to_empty_not_open)`（序号未知延迟定址：落盘前靠开桶哈希 `is_open_safe` 事实核对，而非序号预判）。
- `free` 合法路径白名单（fsck 重建 `need_discard→parity` 等由 alloc-info 驱动，不 WARN，`in_fsck` 豁免）。
- `gen` 未知时延迟定址：`io_time` 与 `need_inc_gen` 在触发时才固化，索引更新走 write buffer 异步，不阻塞前台。

**调用链：** `alloc:{v1,v2,v3,v4}` 四版本 btree 的 `.trigger`（`background.h:264-286`），`bch2_alloc_unpack/unpack_v1-3 + validate_v1-4` 先归一校验，再进触发。

**权衡：** 生产（前台 mark）与消费（后台索引/GC）分离：触发只置状态 + 缓冲索引写，`need_discard` 粘性（`background.h:91: need_discard is sticky`）保证丢弃前不复用。

---

### 8.2 `bch2_bucket_do_freespace_index() / bch2_bucket_do_discard_index()` — `fs/alloc/background.c`

**签名：**

```c
int bch2_bucket_do_freespace_index(struct btree_trans *trans, struct bch_dev *ca,
                                   struct bkey_s_c k, const struct bch_alloc_v4 *a, bool insert)
static int bch2_bucket_do_discard_index(struct btree_trans *trans, struct bkey_s_c k,
                                        const struct bch_alloc_v4 *a)
```

**语义：** freespace btree 按 `(genbits, bucket)` 排序供 `bucket_alloc_scan` 双向就近扫；need_discard btree 经 `btree_bit_mod_buffered` 异步置位（`atomic` 上下文缓冲，注释 `Update need_discard btree via write buffer. Done from the atomic …`）。`check.c:793` 在 fsck 时重建索引。

**权衡：** 索引写缓冲化：前台不等待 freespace 落盘（`BTREE_ITER_committed` 读已提交旧索引仍可分配，误差由 `try_alloc_bucket_pos` 的 `check_freespace_key_async + journal_seq` 二次核对兜底）。

---

### 8.3 LRU：`bch2_lru_set() / __bch2_lru_change() / bch2_lru_check_set() / bch2_dev_remove_lrus()` — `fs/alloc/lru.c`

**签名：**

```c
int bch2_lru_set(struct btree_trans *trans, u16 lru_id, u64 dev_bucket, u64 time)
int __bch2_lru_change(struct btree_trans *trans, u16 lru_id, u64 dev_bucket,
                      u64 old_time, u64 new_time)
int bch2_lru_check_set(struct btree_trans *trans, u16 lru_id, u64 dev_bucket, u64 time,
                       struct bkey_s_c referring_k, struct wb_maybe_flush *last_flushed)
int bch2_dev_remove_lrus(struct bch_fs *c, struct bch_dev *ca)
```

**`check_set` 缺失自愈（≤10行）：**

```c
if (lru_k.k->type != KEY_TYPE_set) {
  try(bch2_btree_write_buffer_maybe_flush(trans, referring_k, last_flushed));
  /* ... fsck_err(alloc_key_to_missing_lru_entry) ... */
  try(bch2_lru_set(trans, lru_id, dev_bucket, time));
```

alloc key 指向的 LRU 缺失则先刷 write buffer（防“在途未落”误判），仍缺则 fsck 记错 + 补写。`lru_pos_to_bp` 反向归位（`read/fragmentation→alloc，stripes→stripes`），`dev_remove_lrus_scan/range` 按 `bp.btree==alloc && inode==dev_idx` 删盘清理。

**权衡：** 位图点操作 + 引用反查：LRU 是 alloc 的二级索引，不一致可重建（`check_lrus/check_alloc_to_lru_refs`），删盘必须扫清否则悬指。

---

### 8.4 丢弃：`bch2_discard_one_bucket() / bch2_do_discards() / bch2_do_discards_async() / bch2_fast_discard_bucket_add()` — `fs/alloc/discard.c`

**签名：**

```c
static int bch2_discard_one_bucket(struct btree_trans *trans, struct bpos bucket,
                                   u32 bucket_size, struct discard_state *s, bool fastpath)
static void bch2_do_discards(struct bch_fs *c)
void bch2_do_discards_async(struct bch_fs *c)
void bch2_fast_discard_bucket_add(struct bch_dev *ca, u64 bucket)
```

**`discard_one` 三水位门（已核实）：** `nouse→0`；`in_flight_add EEXIST→eexist， else→eagain`；`alloc_to_v4_mut` 后 `fastpath && journal_seq_empty→need_journal_commit`；`journal_seq_empty > flushed_seq→need_journal_commit`；`>= rewind_seq→need_rewind_advance`；`data_type!=need_discard→bad_data_type`（write buffer 竞态预期内）；`is_open_safe→open`；`!ioref(WRITE)→not_rw`；`discard_opt && max_discard && !nochages` 才发 TRIM，否则记 `discarded/committed`。计数全部进 `discard_state.seen/not_rw/eexist/eagain/open/…`（`discards_to_text` 可观测）。

**双工：** `do_discards`（need_discard btree 扫）+ `fast_discard`（`open_bucket_put(do_discards_fast)` 直加队列，`fast_work` 消费），慢扫保底、快路低延迟。`do_invalidates/invalidates_work` 处理 `need_gc_gens` 类不可 TRIM 盘的失效复用。

**三水位门 + 反压：** `bch2_bucket_alloc_trans` 中 `need_discard > min(avail, nbuckets>>7) → do_discards_async`，`need_gc_gens > avail → gc_gens_async`，`should_invalidate_buckets → dev_do_invalidates`，分配压力直接转后台生产力。

**权衡：** 丢弃永不挡分配（门控全是计数跳过，非阻塞），`journal_seq/rewind_seq` 双门保证 TRIM 的桶的旧数据已无 journal 可 replay 引用，崩溃安全优先于丢弃及时性。

---

## 九、设计启示（可复用模式清单）

1. **死同穴隔离：** 写点按死亡时间分流（inode 哈希 + btree/copygc/reconcile 独立），复用链 `writepoint→partial→stripe→new` 优先命中旧桶。学：碎片在分配时预防，不在 GC 时补救；代价是 stranded，需 `stranded×factor>free` 动态缩写点。
2. **零递归分配：** 开桶 4096 固定池 + 空闲链 O(1) + 哈希复用 `u16` + 超块变长原地 `memmove`。学：分配器元数据永不动态分配；内存省到按位借（bucket 首字节自旋锁）。
3. **加权无饿死三件套：** `1/free` 虚拟时间增量 + 新盘抬到最小值（只升不降）+ `1<<62/56` 溢出重缩放。学：缺一则饿死；故障域先于时间，EC 则硬剔除。
4. **多档水位 + 欠账：** 设备/开桶双级水位，`copygc 非 btree 欠复制提交` 打破自等死锁，`btree` 永不欠（防单点落坏盘 `emergency_ro`），`interior_updates` 零保留（分裂必成功）。学：水位是语义（谁可欠），不是阈值。
5. **双层预留：** per-cpu 快扣 + 全局批量补（+1024）+ 锁内重算（`avail_factor` 打折），`online_reserved` 短视图立即可见，`capacity_gen` 缩容作废，提交时 `trans_account` 冲销。学：热点无锁，真相重算，欠超事后扣全局 + 单次告警。
6. **全流水线成员变更：** 槽位哨兵 + 双态删除 + 最老复用 + 变长原地升级 + 挂载前强校验 + `read_only` 五步时序 + `set_state` 三联动 + 移除十步流水线 + 失败回滚重加 + 添加四阶段幂等续跑。学：成员变更是分布式事务，不是函数调用。
7. **双轨记账：** 盘上 deltas（write buffer）+ 内存 percpu（eytzinger），触发器双 flag（trans/gc）同源双写，启动 btree/journal 版本归并（旧 delta 早丢），零值延后滤，失配显式 `fsck_err + commit` 自愈。学：重建归并不删除，自愈显式调度；热点自记合并，冷门走通用钩子。
8. **生产消费分离：** 触发器只置 `need_discard` 粘态 + 缓冲索引，前台 `committed` 读旧索引 + 二次核对；LRU 缺失先刷 buffer 再补写；丢弃快慢双工 + 三水位门异步踢。学：未知延迟定址（落盘前哈希事实核对），后台双工（快路延迟 + 慢扫保底）。

---

## 复核途径（只读命令，均已执行验证）

- `sed -n 6,18p fs/alloc/foreground.c` 读死同穴 DOC。
- `grep -n "BCH_WATERMARKS\|dev_stripe_state\|open_buckets" fs/alloc/types.h` 看水位/开桶/WFQ 中枢。
- `grep -n "bch2_open_bucket_alloc\|__try_alloc_bucket\|bucket_alloc_scan\|bch2_bucket_alloc_freelist\|bch2_bucket_alloc_target\|req_alloc_should_bail" fs/alloc/foreground.c` 走开桶→扫描→水位全链。
- `grep -n "disk_reservation\|fs_usage_read_short\|sectors_available" fs/alloc/buckets.c fs/alloc/buckets.h` 看双层预留。
- `grep -n "bch2_trigger_extent\|bch2_trigger_reservation\|bch2_trans_account_disk_usage_change" fs/alloc/buckets.c` 看触发器双轨。
- `grep -n "bch2_accounting_read\|accounting_read_mem_fixups\|bch2_gc_accounting_done" fs/alloc/accounting.c` 看归并自愈。
- `grep -n "bch2_sb_member_alloc\|validate_member\|bch2_sb_members_to_cpu" fs/sb/members.c` 看槽位/校验/镜像。
- `grep -n "__bch2_dev_remove\|bch2_dev_add_initialize\|__bch2_dev_set_state\|__bch2_dev_read_only" fs/init/dev.c` 看增删流水线。

</task_result>