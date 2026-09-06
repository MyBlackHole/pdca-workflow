# bcachefs 数据搬迁专题学习报告（T0530）：代码级精讲

> 事实源：`fs/data/move.c`（1310 行）、`fs/data/copygc.c`（830 行）、`fs/data/move.h`（145 行）、`fs/data/ec/create.c`（`may_reuse_stripe` 相关）。
> 行号函数名均经 `grep -n` / `Read` 核实。七节结构保留原报告，每节逐函数精讲（签名/参数/返回/调用链/≤10 行片段/权衡）。

---

## 一、全景：搬迁是空间再平衡

搬迁服务清运、疏散、均衡、修复四方。核心矛盾：搬迁本身耗 IO，不能影响前台；搬错不如不搬。

### 1.1 `struct moving_context` —— 在途 IO 记账中心（`fs/data/move.h:31`）

- 签名：`struct moving_context { trans/list/fn/rate/stats/wp/wait_on_copygc/cl/lock/reads/ios/io_seq/read_sectors/write_sectors/read_ios/write_ios/wait; }`
- 参数/语义：`trans` 为复用的 btree 事务；`rate` 限速器（可空）；`stats` 进度统计（可空）；`wp` 写点；`wait_on_copygc` 是否等 copygc；`cl:closure` 为全部在途 IO 的引用计数；四计数器 `read/write_sectors/ios` 为限流依据。
- 返回：无（类型定义）。
- 调用链：`bch2_moving_ctxt_init → __bch2_move_extent/bch2_move_data_btree/__bch2_move_data_phys → bch2_moving_ctxt_exit`。
- 片段（`move.h:49-55`，7 行）：
```c
atomic_t read_sectors;
atomic_t write_sectors;
atomic_t read_ios;
atomic_t write_ios;
wait_queue_head_t wait;
```
- 权衡：四计数器分离读写/字节数/IOPS，限流精确但需处处配对增减（`__bch2_move_extent` 加、`move_read_endio`/`move_write_done` 减），漏配对即限流失灵或卡死；用 `EBUG_ON` 在 exit 断言归零兜底。

### 1.2 `bch2_moving_ctxt_init / _exit`（`move.c:186 / :161`）

- 签名：`void bch2_moving_ctxt_init(ctxt, c, rate, stats, wp, wait_on_copygc)`；`void bch2_moving_ctxt_exit(ctxt)`。
- 参数：`c` 文件系统；`rate/stats/wp` 同上；`wait_on_copygc` 传给 `bch2_move_ratelimit` 的等待开关。
- 返回：无；`exit` 先 `flush_all` 再 `list_del`、`trans_put`、`memset` 清零。
- 调用链：`bch2_move_data_phys:783-784`、`bch2_copygc_thread:695`、`bch2_scrub_journal:1027-1028` 建栈上 `ctxt __cleanup(exit)` → 自动 exit。
- 片段（`move.c:202-210`，9 行）：
```c
closure_init_stack(&ctxt->cl);
mutex_init(&ctxt->lock);
INIT_LIST_HEAD(&ctxt->reads);
INIT_LIST_HEAD(&ctxt->ios);
init_waitqueue_head(&ctxt->wait);
scoped_guard(mutex, &c->moving_context_lock)
    list_add(&ctxt->list, &c->moving_context_list);
```
- 权衡：栈上 `__cleanup` 保证异常路径必 flush，避免泄漏在途 IO；代价是 `exit` 隐含 `closure_sync` 可能阻塞，调用者必须可睡眠。

### 1.3 `bch_move_stats`（`move.c:217 bch2_move_stats_init / :1237 _to_text`）

- 签名：`void bch2_move_stats_init(stats, name)`；`__cold void bch2_move_stats_to_text(out, stats)`。
- 参数：`name` 如 `"copygc"`/`"journal_scrub"`；统计 `keys_moved/sectors_moved/sectors_seen/sectors_raced/sectors_error_*`。
- 调用链：各入口 init → `__bch2_move_extent:317-320` 累加 → `bch2_fs_moving_ctxts_to_text:1290` 展示。
- 片段（`move.c:317-320`，4 行）：
```c
atomic64_inc(&ctxt->stats->keys_moved);
atomic64_add(size, &ctxt->stats->sectors_moved);
```
- 权衡：`sectors_seen` 同步累加、`sectors_moved` 异步完成，`bch2_copygc:541` 用 `sectors_seen!=0` 判实做功，区分空转；代价是阅读时勿把 moved 当进度唯一口径。

**可学**：搬迁是后台再平衡，不是前台加速；统一 `moving_context + stats` 记账是全部搬迁的底座。

---

## 二、统一引擎：谓词注入（策略与管线解耦）

谓词只决策搬/跳与目标，异步读→写管线全共享；整单元优先；调度契约是纯函数 `move_pred_fn`。

### 2.1 `move_pred_fn` 类型（`move.h:92`）

- 签名：`typedef int (*move_pred_fn)(trans, arg, btree_id, k, io_opts, data_opts*)`。
- 参数：`arg` 策略私有（如 `evacuate_bucket_arg`）；`k` 当前 extent/btree_ptr；双出参 `io_opts`（读的副本策略）、`data_opts`（目标/`ptrs_kill`/`type`/`read_dev`）。
- 返回：`<=0` 跳过（0 跳过，负错），`>0` 执行搬迁。
- 调用链：各类 `*_pred` → `bch2_move_extent_pred:439` 调用 → `bch2_move_extent`。
- 片段（`move.h:92-93`，2 行）：
```c
typedef int (*move_pred_fn)(struct btree_trans *, void *, enum btree_id, struct bkey_s_c,
```
- 权衡：谓词不持有 IO，只填 `data_opts`，管线可复用；代价是谓词必须无副作用且可重入（事务重启会重调）。

### 2.2 `bch2_move_extent_pred`（`move.c:418`，静态调度契约）

- 签名：`static int bch2_move_extent_pred(ctxt, bucket_in_flight, snapshot_io_opts, pred, arg, iter, level, k)`。
- 参数：`snapshot_io_opts` 可空（phys 路径传 NULL）；`level` btree 层级；`k` 当前 key。
- 返回：透传谓词 `<=0`；否则透传 `bch2_move_extent`。
- 调用链：`bch2_move_data_btree:524,568`、`__bch2_move_data_phys:739` 唯一调用点。
- 片段（`move.c:431-439`，9 行）：
```c
try(bch2_bkey_get_io_opts(trans, snapshot_io_opts, k, &opts));
try(bch2_update_reconcile_opts(trans, snapshot_io_opts, &opts, iter, level, k,
                   SET_NEEDS_RECONCILE_other));
CLASS(disk_reservation, res)(c);
try(bch2_trans_commit_lazy(trans, &res.r, NULL, BCH_TRANS_COMMIT_no_enospc));
struct data_update_opts data_opts = { .read_dev = -1 };
int ret = pred(trans, arg, iter->btree_id, k, &opts, &data_opts);
```
- 权衡：先取 IO 选项+reconcile 校正+懒提交预留，再调谓词，保证谓词看到的是最终选项；`bkey_get_io_opts` 失败直接 `try` 返回，不进谓词，避免无效决策。

### 2.3 `__bch2_move_extent`（`move.c:226`，异步读发射）

- 签名：`static int __bch2_move_extent(ctxt, bucket_in_flight, iter, k, io_opts, data_opts)`。
- 参数：`bucket_in_flight` 可空（copygc 传桶，非空则 `atomic_inc(&b->count)`  pin 住桶）；`iter` 定位用事务迭代器。
- 返回：0 已发射；`BCH_ERR_data_update_done` 转 0；其余错（含 restart）上抛。
- 调用链：`bch2_move_extent:366`（direct data）→ 本函数 → `bch2_data_update_init` → `__bch2_read_extent` 异步读 → `move_read_endio` → `move_write` → `move_write_done`。
- 片段（`move.c:254-262`，9 行）：
```c
u->op.end_io = move_write_done;
u->rbio.bio.bi_end_io = move_read_endio;
u->rbio.bio.bi_ioprio = IOPRIO_PRIO_VALUE(IOPRIO_CLASS_IDLE, 0);
u32 size = k.k->size;
if (bucket_in_flight) {
    u->b = bucket_in_flight;
    atomic_inc(&u->b->count);
}
```
- 权衡：`IOPRIO_CLASS_IDLE` 让搬迁读最低优先级，不抢前台；`bucket_in_flight` 引用计数防“桶被回收而 IO 仍在飞”；同步失败路径（`280-310`）手工回滚 read 记账+`closure_put`，因 `endio` 不会跑，细致但易漏。

### 2.4 `bch2_move_extent`（`move.c:351`，extent/btree_ptr 分流）

- 签名：`int bch2_move_extent(ctxt, bucket_in_flight, opts, data_opts, iter, level, k)`。
- 参数：`level` 仅 btree_ptr 分支用；`data_opts->type` 决定 scrub/copygc/普通。
- 返回：0 成功/跳过；`ENOMEM` 转 `transaction_restart_nested` 并先 `wait_for_io`。
- 调用链：`pred` 之后唯一出口；btree_ptr 分支调 `bch2_btree_node_rewrite_pos:390` 或 `bch2_btree_node_scrub:401`。
- 片段（`move.c:365-368`，4 行）：
```c
if (!bkey_is_btree_ptr(k.k))
    ret = __bch2_move_extent(ctxt, bucket_in_flight, iter, k, opts, data_opts);
else if (data_opts->type != BCH_DATA_UPDATE_scrub) {
```
- 权衡：btree 节点重写不走 `data_update`，用 `move_btree_node_trace:331` 补 trace，保持可观测；`copygc` 类型跳过 `bch2_can_do_data_update` 预检（`368`），因桶疏散目标已定，省一次判据开销。

### 2.5 异步三件套：`move_read_endio:121 / move_write:90 / move_write_done:69`

- 签名：`static void move_read_endio(bio*)`；`static void move_write(u*)`；`static void move_write_done(op*)`。
- 参数/返回：无返回；靠 `container_of` 从 bio/op 反查 `data_update`。
- 调用链：读完成 → `read_done=true + wake_up(wait)` → `move_ctxt_wait_event` 被唤醒调 `do_pending_writes:134` → `move_write` 发写 → 写完成 `move_write_done` 减计数、`call_rcu` 释放。
- 片段（`move.c:126-131`，6 行）：
```c
atomic_sub(u->k.k->k.size, &ctxt->read_sectors);
atomic_dec(&ctxt->read_ios);
u->read_done = true;
wake_up(&ctxt->wait);
closure_put(&ctxt->cl);
```
- 权衡：读→写解耦（读完成不直接写，由等待循环批量 `do_pending_writes` 驱动），可摊销事务锁获取；`EC_ALLOC_FAILED` 特判（`82-83`）转 pending 重试而非丢弃，保证 EC 条带最终仍被编码。

### 2.6 双扫描入口：`bch2_move_data_btree:507` 与 `__bch2_move_data_phys:615 / bch2_move_data_phys:772`

- 签名：`int bch2_move_data_btree(ctxt, start, end, pred, arg, btree_id, level)`；`int bch2_move_data_phys(c, dev, start, end, data_types, rate, stats, wp, wait_on_copygc, pred, arg)`。
- 参数：前者按逻辑 btree 区间扫（含 root key + 全迭代两遍：`523` 处理 root，`546` 主循环）；后者按物理设备扇区扫 backpointer（`bp_walk` 区分 `BP_WALK_DEV/EC_ORPHAN:597-613`）。
- 返回：0 完成；`EROFS/EIO` 提前 break；`data_update_fail` 吞掉继续（`525-526,571-572`）。
- 调用链：`bch2_data_job:1220`（scrub）调 phys；`bch2_evacuate_*:839,898,949` 调 `__bch2_move_data_phys`；copygc 只用 phys 系。
- 片段（`move.c:731-739`，9 行）：
```c
if (!(data_types & BIT(bp.v->data_type)) ||
    (!bp.v->level && bp.v->btree_id == BTREE_ID_stripes)) {
    bch2_btree_iter_advance(&bp_iter);
    continue;
}
u32 bucket_len = bp.v->bucket_len;
ret = bch2_move_extent_pred(ctxt, bucket_in_flight, NULL, pred, arg, &iter, bp.v->level, k);
```
- 权衡：phys 路径逐 backpointer `resolve`（`719 bch2_backpointer_get_key`），顺带修复悬空 backpointer，防 copygc 活锁（注释 `706-717`）；代价是每次疏散都付解析开销，且尾部审计（`763-766`）只在 `!ret` 才跑，取消时不审计。

**可学**：新策略只加谓词+选扫描入口；管线、限流、统计、错误吞掉继续策略全部复用。

---

## 三、碎片选桶：排序加预留

按碎片度排序选最差桶；自留预留防自饿死；在途去重；独立线程。

### 3.1 `bch2_bucket_is_movable`（`copygc.c:89`，准入四否决）

- 签名：`static int bch2_bucket_is_movable(trans, b, time)`，`b` 出参回填 `generation/sectors`。
- 参数：`time` 为 LRU 时间戳上限，`lru_idx==0 || >time` 判 LRU 竞态。
- 返回：1 可搬；0 跳过（附带 `bch_err_throw(bucket_not_moveable_*)` 供 trace 归因）。
- 调用链：`try_add_copygc_bucket:193` 唯一调用。
- 片段（`copygc.c:109-119`，10 行，条件压缩示意）：
```c
if (bch2_bucket_is_open(c, b->k.bucket.inode, b->k.bucket.offset)) {
    bch_err_throw(c, bucket_not_moveable_bucket_open);
    return 0;
}
if (bch2_bucket_bitmap_test(&ca->bucket_backpointer_mismatch, b->k.bucket.offset)) {
    bch_err_throw(c, bucket_not_moveable_bp_mismatch);
    return 0;
}
```
- 权衡：`rw+online`、非 open 桶、无 backpointer 缺失、LRU 未竞态四关，任一不过即弃；宁可漏搬不搬错，backpointer 缺失直接拒，避免疏散一半发现数据找不到。

### 3.2 `try_add_copygc_bucket`（`copygc.c:187`，去重+入批）

- 签名：`static int try_add_copygc_bucket(trans, buckets_in_flight, bucket, lru_time)`。
- 参数：`bucket` 为 `u64_to_bucket` 解码的 LRU 位置；`lru_time` 透传给 movable 校验。
- 返回：1 入批；0 跳过（不可搬/在途重复）；`<0` 错误（ENOMEM/rhashtable）。
- 调用链：`copygc_dev_get_bucket:286`、`bch2_copygc_get_stripe_buckets:386`。
- 片段（`copygc.c:197-216`，10 行）：
```c
if (bucket_in_flight(buckets_in_flight, b.k))
    return 0;
struct move_bucket *b_i = kmalloc(sizeof(*b_i), GFP_KERNEL);
if (!b_i)
    return -ENOMEM;
*b_i = b;
ret = darray_push(&buckets_in_flight->to_evacuate, b_i);
```
- 权衡：`rhashtable_lookup_fast` 判在途重复，防同桶并发疏散双写；`kmalloc+darray+rhash` 三步非原子，失败需手工 `kfree`，以代码复杂度换无锁查询。

### 3.3 `copygc_dev_get_bucket / bch2_copygc_get_buckets`（`copygc.c:276 / :312`）

- 签名：`static int copygc_dev_get_bucket(ctxt, buckets_in_flight, d)`；`static int bch2_copygc_get_buckets(ctxt, buckets_in_flight, devs)`。
- 参数：`d->pos` 为 per-device 碎片 LRU 续扫游标；`devs` 为已按需排序的设备表。
- 返回：1 入批一个；0 该设备 LRU 耗尽（置 `done=true:294`）；`<0` 错误。
- 调用链：`bch2_copygc:495-497` → `get_buckets` 轮询各设备 → `dev_get_bucket` → `for_each_btree_key_max(LRU)` → `try_add`。
- 片段（`copygc.c:330-345`，10 行，轮询核心）：
```c
darray_for_each(*devs, i) {
    if (!i->done && !copygc_dev_still_needed(ctxt->trans->c, i))
        i->done = true;
    if (i->done) { done++; continue; }
    int ret = copygc_dev_get_bucket(ctxt, buckets_in_flight, i);
    if (ret < 0) return ret;
    if (copygc_batch_full(buckets_in_flight)) return 0;
```
- 权衡：多设备 round-robin（一设备一桶/轮），防单盘垄断批次；每轮重判 `still_needed`，在途完成可提前摘设备，批次不做无用功。

### 3.4 `copygc_batch_full:179 / move_bucket_in_flight_add:77 / move_buckets_wait:147 / bucket_in_flight:173`

- 签名：`static bool copygc_batch_full(list)`；`static void move_bucket_in_flight_add(list, b)`；`static void move_buckets_wait(ctxt, list, flush)`。
- 参数：`flush` 为 true 则阻塞等 `count归零` 再释放，否则只收已完成。
- 返回：`batch_full` 以 `max(16, nr/4)` 为阈；`wait` 无返回，维护 `nr/sectors` 计数。
- 调用链：`bch2_copygc:486 wait(false)` 开场收尾 → 选桶 → `evacuate_bucket` 发射（`b->count` 被 `__bch2_move_extent` 持有）→ 下轮 `wait` 回收。
- 片段（`copygc.c:179-183`，5 行）：
```c
static bool copygc_batch_full(struct buckets_in_flight *buckets_in_flight)
{
    size_t nr_to_get = max_t(size_t, 16U, buckets_in_flight->nr / 4);
    return buckets_in_flight->to_evacuate.nr >= nr_to_get;
}
```
- 权衡：批大小随在途规模自适应（保底 16），在途越多批越大，吞吐与延迟自平衡；`wait(false)` 非阻塞回收让选桶与 IO 重叠，但 `nr/sectors` 非原子需调用者串行。

**可学**：选桶排序（碎片 LRU 头部最空者优先）+ 在途去重（rhashtable）+ 自适应批；清运自留预留见 6.2。

---

## 四、疏散：谓词杀指针 + 物理搬迁

读写转只读转逐出由分配层状态机负责；搬迁层只做“把某设备/某桶的数据搬走”（杀指针式搬迁）；轮询归零提示删盘由上层判断。

### 4.1 `evacuate_pred`（`move.c:807`，整盘疏散）

- 签名：`static int evacuate_pred(trans, _arg:evacuate_arg{dev}, btree, k, io_opts, data_opts)`。
- 参数：遍历每个 ptr，`ptr->dev==arg->dev` 则置 `ptrs_kill` 对应位。
- 返回：`ptrs_kill!=0` 即搬。
- 调用链：`bch2_evacuate_data:827` → `__bch2_move_data_phys(~0 data_types, copygc=false)`。
- 片段（`move.c:817-824`，8 行）：
```c
unsigned ptr_bit = 1;
bkey_for_each_ptr(bch2_bkey_ptrs_c(k), ptr) {
    if (ptr->dev == arg->dev)
        data_opts->ptrs_kill |= ptr_bit;
    ptr_bit <<= 1;
}
return data_opts->ptrs_kill != 0;
```
- 权衡：只标记杀指针不指定目标，目标由分配器按当前策略另选，疏散与布局解耦；`~0` 全数据类型全搬，简单彻底但 IO 最大。

### 4.2 `bch2_evacuate_data`（`move.c:827`）

- 签名：`int bch2_evacuate_data(ctxt, dev, start, end)`。
- 参数：物理扇区区间 `[start,end)`；调用方拼 `bp_walk{BP_WALK_DEV}`。
- 返回：透传 `__bch2_move_data_phys`。
- 调用链：EC 修复（`ec/create.c:2104` 逐 block 疏散旧条带）、设备摘除/用户触发疏散。
- 片段（`move.c:832-840`，9 行）：
```c
struct bp_walk w = {
    .type = BP_WALK_DEV,
    .dev = { .dev = dev },
    .sector_start = start,
    .sector_end = end,
};
return __bch2_move_data_phys(ctxt, NULL, &w, ~0, false,
                 evacuate_pred, &arg);
```
- 权衡：`bucket_in_flight=NULL`（整盘级不定桶 pin），轻量；EC 孤儿另走 `EC_ORPHAN` 通道，不混用 dev 匹配。

### 4.3 `evacuate_ec_orphan_pred / bch2_evacuate_ec_orphan`（`move.c:856 / :882`）

- 签名：`static int evacuate_ec_orphan_pred(trans, _arg{ec_idx,ec_block}, ...)`；`int bch2_evacuate_ec_orphan(ctxt, ec_idx, ec_block, start, end)`。
- 参数：`ptr->dev==BCH_SB_MEMBER_INVALID` 且 `has_ec && ec.idx/block` 匹配才杀（注释 `848-855`）。
- 返回：同上。
- 调用链：`ec/create.c:2112`（设备已删、指针 dev 为哨兵时）与正常 `evacuate_data` 并列分支。
- 片段（`move.c:870-876`，7 行）：
```c
bkey_for_each_ptr_decode(k.k, ptrs, p, entry) {
    if (p.ptr.dev == BCH_SB_MEMBER_INVALID &&
        p.has_ec &&
        p.ec.idx == arg->ec_idx &&
        p.ec.block == arg->ec_block)
        data_opts->ptrs_kill |= ptr_bit;
```
- 权衡：不能按 dev 匹配（所有删盘 extent 都是同一哨兵），必须按 `(stripe idx, block)` 精确匹配；走 `stripe_backpointers` 树（`bp_btree=BTREE_ID_stripe_backpointers:639`），与正常 dev 树隔离。

### 4.4 `evacuate_bucket_pred / bch2_evacuate_bucket`（`move.c:902 / :929`，copygc 单桶疏散）

- 签名：`static int evacuate_bucket_pred(trans, _arg{bucket,generation,sectors,data_opts}, ...)`；`int bch2_evacuate_bucket(ctxt, bucket_in_flight, bucket, gen, data_opts)`。
- 参数：`bucket:bpos{inode=dev,offset=bucket_nr}`；`gen<0` 表通配；命中条件 `dev对 && generation对 && !cached`，并累 `sectors+=compressed_size:921`。
- 返回：`bch2_copygc:510` 逐桶调用，trace 上报 `arg.sectors/bucket_size` 疏散比。
- 调用链：`bch2_copygc:510` → 本函数 → `__bch2_move_data_phys(copygc=true)`（开 backpointer 缺失审计）。
- 片段（`move.c:916-924`，9 行）：
```c
bkey_for_each_ptr_decode(k.k, bch2_bkey_ptrs_c(k), p, entry) {
    if (p.ptr.dev == arg->bucket.inode &&
        (arg->generation < 0 || arg->generation == p.ptr.generation) &&
        !p.ptr.cached) {
        data_opts->ptrs_kill |= BIT(i);
        arg->sectors += p.crc.compressed_size;
    }
    i++;
}
```
- 权衡：generation 精确匹配防 ABA（桶已回收重用则不误杀新数据）；跳过 `cached` 指针（缓存副本由回收另行处理）；`copygc=true` 打开缺失审计，以额外开销换 copygc 不活锁。

**可学**：疏散分“判谁走”（谓词杀指针）与“怎么走”（phys 搬迁）两层；归零才算完由上层轮询，搬迁层只保证“命中即搬走”。

---

## 五、EC 整搬：不打碎条带

条带整条搬迁优先，碎条带不重写活数据；复用判一致；读到即折叠由 EC 读路径负责，搬迁层负责把旧块腾空。

### 5.1 `bch2_copygc_get_stripe_buckets`（`copygc.c:352`）

- 签名：`static int bch2_copygc_get_stripe_buckets(ctxt, buckets_in_flight)`。
- 参数：扫 `BTREE_ID_lru: BCH_LRU_STRIPE_FRAGMENTATION`，逐条带查 `BTREE_ID_stripes`。
- 返回：0；`batch_full` 即停。
- 调用链：`bch2_copygc:495` 二选一（EC 碎 vs 桶碎）→ 本函数 → `try_add_copygc_bucket(PTR_BUCKET_POS:387)` 把条带成员桶逐个入批。
- 片段（`copygc.c:376-387`，10 行，压缩）：
```c
unsigned nr_data = s->nr_blocks - s->nr_redundant;
for (unsigned i = 0; i < nr_data; i++) {
    if (!stripe_blockcount_get(s, i))
        continue;
    const struct bch_extent_ptr *ptr = s->ptrs + i;
    CLASS(bch2_dev_bkey_tryget, ca)(trans->c, s_k, ptr->dev);
    ret2 = try_add_copygc_bucket(trans, buckets_in_flight,
                     PTR_BUCKET_POS(ca, ptr), U64_MAX);
```
- 权衡：只收非空 data 块所在桶（空块跳过），`U64_MAX` 时间表“EC 桶免 LRU 时间校验”（`is_movable` 内 `lru_idx>time` 永假）；`stripe_lru_pos!=lru_time` 写缓冲竞态直接跳过（`373-374`），宁漏不錯。

### 5.2 `should_do_ec_copygc`（`copygc.c:402`，碎度对决）

- 签名：`static bool should_do_ec_copygc(trans, devs)`。
- 参数：比较最碎条带 vs 各需 copygc 设备 LRU 头（最空桶）。
- 返回：`stripe_frag_ratio && stripe*2 < bucket` 则 true（注释 `466`：偏向普通桶 copygc）。
- 调用链：`bch2_copygc:495` 每次批前决策。
- 片段（`copygc.c:437-467`，核心 6 行）：
```c
stripe_frag_ratio = div_u64(blocks_nonempty * (1ULL << 31), nr_data);
break;
// ...
return stripe_frag_ratio && stripe_frag_ratio * 2 < bucket_frag_ratio;
```
- 权衡：`blocks_nonempty/nr_data` 归一化到 2^31 可直接与桶碎度比；`*2` 偏置让 EC 整搬只在“明显更碎”才跑，因 EC 搬迁扇出大；只看首个（最碎）条带 O(1) 决策，不全局排序。

### 5.3 `may_reuse_stripe`（`fs/data/ec/create.c:1448`，整条复用判据）

- 签名：`static bool may_reuse_stripe(c, new, old)`。
- 参数：`new` 待建条带（含目标 dev 集/冗余/算法），`old` 现存条带。
- 返回：三元（label/算法/冗余）任一不同即 false；活块+1 超新条带 data 位即 false；可分配 dev 不足 parity 即 false。
- 调用链：`get_old_stripe` → `may_reuse_stripe && tryget(handle)` → `init_new_stripe_from_old` 继承旧块，否则整条重写。
- 片段（`create.c:1452-1454`，3 行）：
```c
if (old->disk_label != new->new_stripe.key.v.disk_label ||
    old->algorithm != new->new_stripe.key.v.algorithm ||
    old->nr_redundant != new->new_stripe.key.v.nr_redundant)
    return false;
```
- 权衡：三元一致才复用，保证条带不变式（同 label/算法/冗余）；`live_data+1` 预留至少一新块位，防复用后无处落新写；坏/疏散中 dev 从可分配集剔除，复用不继承坏盘。

### 5.4 EC 旧块腾空（`fs/data/ec/create.c:2104` 周边）

- 签名：复用失败路径：`bch2_evacuate_data(ctxt, ptr->dev, off, end)` 或 `bch2_evacuate_ec_orphan(ctxt, idx, block, off, end)`。
- 参数：`blocks_used` 为旧条带非空 data 块排序后取前 `need_evacuate` 个。
- 返回：腾空后返回 `stripe_needs_block_evacuate` 重试，让新条带下次复用。
- 调用链：EC 分配 → 需腾块 → 搬迁层疏散 → 重试分配。
- 片段（`create.c:2110-2115`，6 行）：
```c
if (ptr->dev != BCH_SB_MEMBER_INVALID)
    try(bch2_evacuate_data(ctxt, ptr->dev, ptr->offset, end));
else
    try(bch2_evacuate_ec_orphan(ctxt, s.k->p.offset, blocks_used[i],
                    ptr->offset, end));
```
- 权衡：搬迁与 EC 分配闭环（搬完重试），不原地改条带；正常/孤儿双通道与第四节谓词复用，无第三套代码。

**可学**：大单元整体搬（条带复用优先）；复用判一致（三元+容量+dev 集）；腾空走通用疏散谓词。

---

## 六、协同边界：串行化与判据同源

与清运（copygc 预留）、EC、reconcile 硬边界串行；reconcile 驱搬；判据纯函数防互等。

### 6.1 `bch2_copygc_dev_wait_amount`（`copygc.c:583`，纯判据）

- 签名：`s64 bch2_copygc_dev_wait_amount(ca)`，调用需持 `mark_lock` 读（注释 `571-572`）。
- 参数：读 `dev_usage_full + dev_leaving(reconcile 待搬离量)`。
- 返回：`>0` 尚不需（值为距触发的 IO 时钟扇区数）；`<=0` 需 copygc（绝对值为超配额深度，作设备间排序键）。
- 调用链：`copygc_dev_list:252` 建表排序；`copygc_dev_still_needed:309` 复判；分配器阻塞路径调 `can_make_progress`（同源，见 6.2）。
- 片段（`copygc.c:603-607`，5 行）：
```c
s64 free = usage.buckets[BCH_DATA_free] * ca->mi.bucket_size + leaving;
s64 wait = free * 5 - ca->mi.nbuckets * ca->mi.bucket_size;
if (wait > 0)
    return wait;
```
- 权衡：空闲≥20% 直接免谈（`free*5-total>0`）；`leaving` 视作 free，reconcile 能解决的不劳 copygc；阈下配额=`(free_stripe水位桶+预留)/2`（`609-611`），随空闲平滑收缩，非一刀切。

### 6.2 `bch2_copygc_can_make_progress`（`copygc.c:560`，分配器同源判据）

- 签名：`bool bch2_copygc_can_make_progress(ca)` → `wait_amount(ca)<=0`。
- 参数/返回：布尔；注释 `554-559` 点明必须与 copygc 建表同准则，否则分配器“等不来的 copygc”或“该等不等”。
- 调用链：分配器阻塞路径 + `copygc_dev_still_needed:309`。
- 片段（`copygc.c:560-563`，4 行）：
```c
bool bch2_copygc_can_make_progress(struct bch_dev *ca)
{
    return bch2_copygc_dev_wait_amount(ca) <= 0;
}
```
- 权衡：一行同源消除两处判据漂移；代价是判据改动需同步评估分配与回收两侧（注释即契约）。

### 6.3 `bch2_copygc`（`copygc.c:471`，单批编排+水位）

- 签名：`static int bch2_copygc(ctxt, buckets_in_flight, devs, did_work*)`。
- 参数：`data_opts={type=copygc, commit_flags=WATERMARK_copygc}`（`478-481`）；`did_work` 出参（`sectors_seen!=0:541`）。
- 返回：0；`ENOENT/kthread_cancelled` 吞掉；其余 `bch_err_msg`。
- 调用链：`bch2_copygc_thread:747` 每轮调用 → `evacuate_bucket:510` 逐桶发射。
- 片段（`copygc.c:478-486`，9 行）：
```c
struct data_update_opts data_opts = {
    .type = BCH_DATA_UPDATE_copygc,
    .commit_flags = (unsigned) BCH_WATERMARK_copygc,
};
u64 sectors_seen = atomic64_read(&ctxt->stats->sectors_seen);
u64 sectors_moved = atomic64_read(&ctxt->stats->sectors_moved);
int ret = 0;
move_buckets_wait(ctxt, buckets_in_flight, false);
```
- 权衡：`WATERMARK_copygc` 让 copygc 提交可用预留水位（`move.c:387-388` 提权 hipri），普通写不可碰，防自饿死；`did_work=sectors_seen!=0` 识破空转疏散（注释 `529-540`：230k 次/s 空转案例），空转则 IO 时钟退避，不忙旋。

### 6.4 `bch2_copygc_thread`（`copygc.c:664`，独立线程+三睡眠）

- 签名：`static int bch2_copygc_thread(arg=c)`。
- 参数：无；`buckets.table=rhashtable` 去重，`devs=darray`。
- 返回：线程退出码。
- 调用链：`bch2_copygc_start:789 kthread_create` → 本函数循环 → `copygc_dev_list → bch2_copygc → running_wq wake_up:751`。
- 片段（`copygc.c:722-741`，10 行，无事睡眠）：
```c
if (!devs.nr &&
    kick == READ_ONCE(c->copygc.kick_count)) {
    c->copygc.wait_at = last;
    c->copygc.wait = last + wait;
    move_buckets_wait(&ctxt, &buckets, true);
    set_current_state(TASK_INTERRUPTIBLE);
    if (kick == READ_ONCE(c->copygc.kick_count))
        bch2_kthread_io_clock_wait_once(clock, last + wait,
                MAX_SCHEDULE_TIMEOUT);
```
- 权衡：无事按 IO 时钟睡到 `wait`（非 wallclock，随写入推进），分配器 `kick` 计数防丢唤醒（双检）；`running` 标志+`running_wq` 让 `bch2_move_ratelimit:467-472 wait_on_copygc` 者可等 copygc 结束，搬迁互不踩；`copygc_enabled` 关时彻底睡（`705-709`）。

### 6.5 `bch2_move_ratelimit`（`move.c:461`，前台保护）

- 签名：`int bch2_move_ratelimit(ctxt)`。
- 参数：`ctxt->rate` 令牌桶（可空）；`wait_on_copygc` 开关。
- 返回：0 可继续；`erofs/kthread_cancelled` 上抛。
- 调用链：`move_data_btree:546`、`__move_data_phys:675` 每 key 前调用。
- 片段（`move.c:498-502`，5 行）：
```c
move_ctxt_wait_event(ctxt,
    atomic_read(&ctxt->write_sectors) < c->opts.move_bytes_in_flight >> 9 &&
    atomic_read(&ctxt->read_sectors) < c->opts.move_bytes_in_flight >> 9 &&
    atomic_read(&ctxt->write_ios) < c->opts.move_ios_in_flight &&
    atomic_read(&ctxt->read_ios) < c->opts.move_ios_in_flight);
```
- 权衡：字节数+IOPS 双限，且等待宏内先 `do_pending_writes` 再睡（`move.h:77-90`），睡中推进写，不死等；注释 `494-496` 自承应按设备分限（SSD/HDD 同限偏保守），留优化口。

### 6.6 修复旁路：`scrub_pred:962 / bch2_data_job:1201 / bch2_scrub_journal:991`

- 签名：`static int scrub_pred(trans, _arg:ioctl_data, ...)`；`int bch2_data_job(c, stats, op)`；`int bch2_scrub_journal(c, rewind_seq*)`。
- 参数：`scrub_pred` 对 `migrate.dev` 无校验和指针直接跳过（`976-977`），有校验和则 `type=scrub + hard_require_read_device` 强制从该盘读验。
- 返回：`data_job` 仅 `BCH_DATA_OP_scrub` 走 phys 全盘扫，其余 `-EINVAL`。
- 调用链：`data_job:1220 move_data_phys(scrub_pred)`；journal scrub 自建 ctxt 对 journal 各副本 `move_extent(type=scrub_no_repair:1067)` 只读验不修，错超两连好区停（`1124`）。
- 片段（`move.c:982-985`，4 行）：
```c
data_opts->type = BCH_DATA_UPDATE_scrub;
data_opts->read_dev = arg->migrate.dev;
data_opts->read_flags = BCH_READ_hard_require_read_device;
return true;
```
- 权衡：scrub 复用同一 phys 引擎只换谓词；journal 路径“验修分离”（`scrub` 只记错盘，`do_repairs:1172` 另起 ctxt 重写），mount 不被修阻塞。

**可学**：搬迁与分配用同一判据（`can_make_progress/wait_amount` 同源）；水位预留边界串行（copygc 水位）；判据纯函数（无 IO，只读 usage+leaving）防互等。

---

## 七、设计启示

1. 再平衡定位：`moving_context` 四计数器+`IDLE` 优先级+双限流，前台无感优先于搬得快。
2. 策略解耦：新策略只加 `move_pred_fn`（`move.h:92`）+选 `btree/phys` 入口，`move_extent_pred:418` 统一做选项校正与 trace。
3. 排序选桶：碎片 LRU 头部+`round-robin` 多盘+`max(16,nr/4)` 自适应批（`copygc.c:179,312`）。
4. 自留预留：`WATERMARK_copygc`（`copygc.c:479`）+ `wait_amount` 20% 门限与半配额（`:583`），普通写碰不到预留。
5. 两层疏散：谓词杀指针（`evacuate_pred:807/ec_orphan:856/bucket:902`）+ phys 搬迁（`:615`）；generation 防 ABA，cached 跳过，孤儿走 stripe 反指树。
6. 整体搬迁：EC 复用判三元一致（`ec/create.c:1448`），`*2` 偏置让普通桶优先（`copygc.c:467`），腾空闭环重试。
7. 判据纯函数：`wait_amount/can_make_progress` 同源，分配器与回收永不互等；`did_work=sectors_seen` 识破空转，IO 时钟退避。

---

## 复核途径

```bash
grep -n "bch2_move_extent_pred\|__bch2_move_extent\|bch2_move_data_btree\|__bch2_move_data_phys" fs/data/move.c
grep -n "evacuate_pred\|bch2_evacuate_data\|bch2_evacuate_ec_orphan\|evacuate_bucket_pred\|bch2_evacuate_bucket\|scrub_pred" fs/data/move.c
grep -n "bch2_bucket_is_movable\|try_add_copygc_bucket\|bch2_copygc_get_buckets\|bch2_copygc_get_stripe_buckets\|should_do_ec_copygc\|bch2_copygc_can_make_progress\|bch2_copygc_dev_wait_amount\|bch2_copygc_thread" fs/data/copygc.c
grep -n "may_reuse_stripe" fs/data/ec/create.c
grep -n "move_pred_fn\|struct moving_context" fs/data/move.h
```
