# bcachefs journal 崩溃恢复专题学习报告（T0515）·代码级精讲版

> 精读 `fs/journal/`（7 文件共 7144 行：types.h 509 / journal.c 1570 / reclaim.c 1451 / read.c 1357 / write.c 1160 / validate.c 787 / seq_blacklist.c 310，`wc -l` 核实）。
> 方法：全部函数名与行号经 `grep -n` + `Read` 核实，代码片段均截自实测行且 ≤10 行，不编造。八节结构保留原报告，每节逐函数精讲：签名/参数/返回/调用链/片段/权衡。

---

## 一、全景：journal 是什么

journal 是 bcachefs 崩溃一致性中枢：所有 btree 更新先记日志再落盘；崩溃后按 seq 重放。核心矛盾三元组：**保序**（乱序重放即 corrupt）、**空间**（日志盘满即卡死写入）、**回收**（刷 pin 需耗日志空间，超前回收即死锁）。三套机制分别对应 `write.c` / `reclaim.c:space_available` / `reclaim.c:flush_pins`，正交建模。

### 1.1 `struct journal_buf`（`types.h:37-76`）

- 签名：`struct journal_buf { struct closure io; struct journal *j; struct jset *data; ... }`
- 参数/字段：`data/buf_size/sectors/disk_sectors/u64s_reserved` 为容量四元组；`key/cas/devs_written/failed` 为落盘位置与容错；`last_seq` 为本条目覆盖下界；`flush_picked/flush/separate_flush/need_flush_to_write_buffer/write_started/write_allocated/write_done/empty/has_overwrites` 为 8 个一位状态机；`wait` 为 flush 等待队列（哨兵复用 `list.first`）。
- 返回：无（类型定义）。生命周期：`__journal_entry_open_one:505` 内联 push 到 `in_flight` FIFO 并 `memset(buf,0,offsetof(...,wait))`，`journal_write_done:353-359` 回收 `data` 到 `free_buf`，`in_flight.front++:428` 释放槽位。
- 调用链：`open_one→do_writes_locked→bch2_journal_write→write_submit→write_done`。
- 片段（`types.h:62-75`）：
```c
bool flush_picked:1;
bool flush:1;
bool separate_flush:1;
bool write_started:1;
bool write_allocated:1;
bool write_done:1;
bool empty:1;
```
- 权衡：一位域省内存但调试需 `bufs_to_text:202`；`wait` 头复用哨兵（`JOURNAL_BUF_NOT_IN_FLIGHT/NOFLUSH/FLUSH_NO_WAIT`）省一个字段，代价是 `journal_buf_wait:1031` 必须手写 cmpxchg 附加逻辑，标准 `llist_add` 会穿透哨兵 corrupt 链表。

### 1.2 `struct journal_ringbuf`（`types.h:90-93`）

- 签名：`struct journal_ringbuf { struct journal_buf *buf; struct jset *data; }`
- 参数：`ring[4]`，索引 `seq & JOURNAL_STATE_BUF_MASK`（`JOURNAL_STATE_BUF_BITS=2`，`types.h:20-22`）。
- 返回：快路径缓存，避免 `in_flight` FIFO 间接寻址。
- 调用链：`__journal_entry_open_one:554-555` 发布 → `journal_res_get_fast:492` 读取 `journal_res_buf(j,res)->data`。
- 片段（`types.h:84-88` 注释）：
```c
* A ring slot is overwritten in journal_entry_open() when a new seq is
* assigned to that state index. Stale entries are never dereferenced
```
- 权衡：信任预留持有者（reservation pins buf），非预留查找一律走 `in_flight`，用“信任边界”换无锁快路径；`JOURNAL_SEQ_MAX=(1ULL<<56)-1:18` 留 8 位给 btree write buffer 偷用。

### 1.3 `enum journal_pin_type + struct journal_entry_pin_list`（`types.h:100-121`）

- 签名：`JOURNAL_PIN_TYPE_btree3..btree0,key_cache,other,NR`；`struct journal_entry_pin_list { spinlock_t lock; atomic_t count; list_head unflushed[NR]; list_head flushed; bool unreplayed; devs; bytes; }`
- 参数：`pin` 为 `FIFO_U64_IDX`，`front/back` 即 seq 窗口；`count` 为引用计数，零才可推进 `last_seq`。
- 返回：`journal_seq_pin(j,seq)` 即 `fifo_entry(&j->pin,seq)`。
- 调用链：`pin_set:687→pin_set_locked:594→maybe_update_last_seq→update_last_seq:437`。
- 片段（`types.h:110-115`）：
```c
struct list_head unflushed[JOURNAL_PIN_TYPE_NR];
struct list_head flushed;
bool unreplayed;
```
- 权衡：按类型分 6 链表支持有序回刷（btree0 最先，老根最先落盘）；`unreplayed` 标志实现“超前即停”（`journal_get_next_pin:783` 见即 `break`），宁可停滞不死锁。

### 1.4 `struct journal_res + union journal_res_state`（`types.h:134-174`）

- 签名：`struct journal_res { bool ref,has_overwrites; u16 u64s; u32 offset; u64 seq; }`；`union journal_res_state { atomic64_t counter; u64 v; struct { u64 cur_entry_offset:22,idx:2,buf0-3_count:10; }; }`
- 参数：`cur_entry_offset` 单位 u64s，哨兵 `OFFSET_MAX:195 / BLOCKED:197 / CLOSED:198 / ERROR:199`；`idx` 为当前 buf 槽；`bufN_count` 各 10 位（`COUNT_MAX=1023:177`）。
- 返回：`journal_state_inc/_buf_put/count` 单移位索引，无 switch。
- 调用链：`journal_res_get_fast:450→atomic64_try_cmpxchg→journal_state_inc`。
- 片段（`types.h:158-164`）：
```c
u64 cur_entry_offset:22,
idx:2,
buf0_count:10,
buf1_count:10,
```
- 权衡：64 位单字 CAS 同时推进 offset+refcount，大端反转字段序保证位布局一致；代价是单条目上限 `2^22 u64s≈32MB` 且被 `ENTRY_SIZE_MAX=4MB:189` 进一步收紧。

### 1.5 `struct journal_space + enum journal_space_from`（`types.h:201-213`）

- 签名：`struct journal_space { unsigned next_entry,total; }`；`enum { discarded, clean_ondisk, clean, total, nr }`
- 参数：单位 512B sector；`space[4]` 四游标并存。
- 返回：`next_entry` 喂硬限制 `cur_entry_sectors`，`total` 喂软水位。
- 调用链：`space_available:277→__journal_space_available:219→journal_dev_space_available:126`。
- 权衡：显式四游标避免“已丢弃/已落盘/内存干净/总量”混用；`next_entry` 永不钳制（钳到 0 会饿死推进型写入导致自死锁，`reclaim.c:158-164` 长注释）。

### 1.6 `struct journal`（`types.h:247-428`）+ `struct journal_device`（`types.h:434-467`）

- 签名：快路径头 64B 对齐（`reservations+watermark`），`seq/atomic64`，`seq_ondisk/flushed_seq_ondisk/last_seq/last_seq_ondisk/err_seq` 五序号，`pin/in_flight` 双 FIFO，`reclaim_lock/reclaim_thread`，`space[4]`。
- 参数：`cur_entry_u64s/cur_entry_sectors/entry_u64s_reserved/buf_size_want` 控制条目尺寸；`discard_idx/dirty_idx_ondisk/dirty_idx/cur_idx` 为设备端四指针（`discard<=ondisk<=dirty<=cur`）。
- 调用链：全图中心，所有路径 `container_of(j,bch_fs,journal)` 反查。
- 片段（`types.h:308-310`）：
```c
* FIFO of in-flight journal bufs, one entry per seq in
* (seq_ondisk, cur_seq]. fifo.front = seq_ondisk + 1, fifo.back =
```
- 权衡：`in_flight` 内联存储 + `front==seq_ondisk+1` 不变量实现 O(1) seq→buf；要求 open 预留 2 空槽留哨兵（`journal.c:455`），否则 `flush_seq_async` 前向 walk 回绕到活条目。

### 1.7 `struct journal_start_info`（`types.h:502-507`）

- 签名：`{ u64 last_seq,replay_end,cur_seq; bool clean; }`
- 参数：三区制：`[last_seq..replay_end]` 重放，`[replay_end+1..cur_seq-1]` 拉黑，`[cur_seq..]` 新写（`types.h:480-498` 长注释，`read.c:1172-1187` 复述）。
- 调用链：`bch2_journal_read:1134` 产出 → `bch2_fs_recovery` + `journal_start` 消费。
- 权衡：`cur_seq` 必须大于盘上最大 seq（含 noflush/撕裂），永不复用序号是保序根基。

**可学**：把“保序/空间/回收”三矛盾显式建模为三套机制，而非一锅烩；哨兵复用与单字 CAS 是典型空间换原子性。

---

## 二、写入路径：预留→组装→校验→分配→提交

### 2.1 `journal_res_get_fast`（`journal.h:450-494`，内联快路径）

- 签名：`static inline int journal_res_get_fast(struct journal *j, struct journal_res *res, unsigned flags)`
- 参数：`j` 日志，`res` 需预填 `u64s`，`flags` 低位为 watermark（`BCH_WATERMARK_MASK`），高位 `NONBLOCK/CHECK`。
- 返回：1 成功（已 CAS 扣额并填 `ref/offset/seq`），0 需慢路径，`CHECK` 模式只试探不扣额。
- 调用链：`bch2_journal_res_get:506→fast` 失败 → `res_get_slowpath:947→__journal_res_get:820`。
- 片段（`journal.h:466-474`）：
```c
if (new.cur_entry_offset + res->u64s > j->cur_entry_u64s)
return 0;
if ((flags & BCH_WATERMARK_MASK) < j->watermark)
return 0;
new.cur_entry_offset += res->u64s;
```
- 权衡：无锁 `atomic64_try_cmpxchg` 自旋 + `smp_rmb` 保证先读计数后读 `cur_entry_u64s`；`seq` 回算 `seq-(seq-idx)&MASK:491` 容忍 idx 回绕；溢出（10 位 refcount 满）直接回 0 等慢路径开新条目。

### 2.2 `__journal_res_get`（`journal.c:820-935`）+ `bch2_journal_res_get_slowpath`（`journal.c:947-981`）

- 签名：`static int __journal_res_get(struct journal *j, struct journal_res *res, unsigned flags)`；`int bch2_journal_res_get_slowpath(..., struct btree_trans *trans)`
- 参数：`flags` 含 watermark；`trans` 用于可休眠等待（`trans_wait_event_timeout`）。
- 返回：0 成功，`-BCH_ERR_journal_{full,pin_full,max_in_flight,max_open,blocked,buf_enomem}` 等需重试/等待，`journal_retry_open` 内部重试。
- 调用链：`fast失败→error/blocked/watermark检查→pin_resize_lock+lock→prealloc→fast复判→cycle_locked(must_open)→stuck检查→满时就地reclaim:924-931`；slowpath 包一层 `async_wait` 超时（`max(2×最慢盘延迟,10s):962`）+ 调试转储。
- 片段（`journal.c:924-931`）：
```c
if ((ret == -BCH_ERR_journal_full ||
ret == -BCH_ERR_journal_pin_full) &&
!(flags & JOURNAL_RES_GET_NONBLOCK)) {
if (journal_low_on_space(j) &&
mutex_trylock(&j->reclaim_lock)) {
```
- 权衡：快路径复判避免无谓 cycle；冻结时 workitem 不跑故满时**就地同步回收**（`trylock` 防死锁）；slowpath 等待按**全部在线盘（含非日志盘）**最慢者计时，因 flush preflush 会刷全部读写成员（`947-962` 注释）。

### 2.3 `__journal_entry_close_one`（`journal.c:295-403`）

- 签名：`static void __journal_entry_close_one(struct journal *j, unsigned closed_val, bool trace)`
- 参数：`closed_val` 仅 `CLOSED_VAL/ERROR_VAL`（`BUG_ON` 断言），`trace` 打点。
- 返回：void；副作用：固化 `data->u64s`，设 `last_seq`，算 `sectors`，调 `buf_put+space_available` 或 ERO 分支。
- 调用链：`cycle_locked:665→close_one→__bch2_journal_buf_put→space_available→do_writes_locked`；`halt_locked:689` 以 `ERROR_VAL` 调用。
- 片段（`journal.c:383-385`）：
```c
buf->last_seq = j->last_seq;
buf->data->last_seq = cpu_to_le64(buf->last_seq);
BUG_ON(buf->last_seq > le64_to_cpu(buf->data->seq));
```
- 权衡：`last_seq` 必须在关旧开新**之间**快照（`364-382` 长注释：pin 替换语义要求只能写“包含新 pin 保护内容”的条目）；超额直接 `emergency_read_only:358`；ERO 路径**故意泄漏 pin ref**（`394-402`）保推进不保优雅——错误值不调 `buf_put`，只递减 state count。

### 2.4 `__journal_entry_open_one`（`journal.c:410-598`）

- 签名：`static int __journal_entry_open_one(struct journal *j)`
- 参数：无（持 `pin_resize_lock+j->lock`）。
- 返回：0 成功，`journal_{blocked,pin_full,max_in_flight,max_open,buf_enomem,full,shutdown}` 等。
- 调用链：`cycle_locked:672→open_one→ring发布→reservations cmpxchg→wake→write_work定时`。
- 片段（`journal.c:495-496`）：
```c
u64 seq = atomic64_inc_return(&j->seq);
journal_pin_list_init(fifo_push_ref(&j->pin), 1);
```
- 权衡：六重门禁按序检查（blocked→cur_error→journal_error→pin满→in_flight留2槽→ring槽空→SEQ溢出→黑名单→free_buf→尺寸）；`in_flight` 留 2 槽保证 `NOT_IN_FLIGHT` 哨兵永存；黑名单 seq 直接 ERO（`468-474`）；`clean→dirty` 首条目打 `FLUSH_NO_WAIT:543-545`（强制 flush 写但 flushers 不等，避免脏标记超前）。

### 2.5 `bch2_journal_write_prep`（`write.c:656-769`）

- 签名：`static int bch2_journal_write_prep(struct journal *j, struct journal_buf *w)`
- 参数：`w` 待写 buf（持 `buf_lock` 调用，见 `bch2_journal_write:830`）。
- 返回：0 成功，否则 fatal（write buffer flush 失败/超额）。
- 调用链：`bch2_journal_write:833→prep→write_alloc→checksum→do_writes_locked`。
- 片段（`write.c:738-741`）：
```c
if (empty) {
scoped_guard(spinlock, &c->journal.lock)
w->empty = true;
}
```
- 权衡：三事合一——压实空预留（`689-694` 跳过 `u64s==0`）、btree 根查漏补缺（`745`）、时间戳+super 条目尾缀（`747-752`，受 `entry_u64s_reserved` 上限 `WARN_ON:755` 约束）；`write_buffer_keys→btree_keys` 类型改写（`724`）避免恢复歧义；`empty` 判定以“有无 btree_keys”为准（`696-697`）。

### 2.6 `bch2_journal_write_checksum`（`write.c:771-812`）

- 签名：`static int bch2_journal_write_checksum(struct journal *j, struct journal_buf *w)`
- 参数：`w->data` 已压实 jset。
- 返回：0 成功，加密/校验失败返回错误。
- 调用链：`prep` 后 → `bch2_journal_write:855`。
- 片段（`write.c:785-793`）：
```c
if (bch2_csum_type_is_encryption(JSET_CSUM_TYPE(jset)))
validate_before_checksum = true;
if (le32_to_cpu(jset->version) < bcachefs_metadata_version_current)
validate_before_checksum = true;
```
- 权衡：加密/旧版本**先验后算**（防加密放大坏键），否则先算后验；尾部按 sector 补零（`810`）保证设备原子语义；`magic/version/endian/csum_type/has_overwrites` 五字段在此一次固化（`778-783`）。

### 2.7 `journal_write_alloc`（`write.c:135-180`）+ `__journal_write_alloc`（`write.c:60-133`）

- 签名：`static int journal_write_alloc(struct journal *j, struct journal_buf *w, unsigned *replicas)`；内层按 failure domain 逐盘挑选。
- 参数：`replicas` 出参（累加 `durability`），目标 `metadata_target ?: foreground_target`，份数 `metadata_replicas`。
- 返回：0 成功，`-BCH_ERR_insufficient_journal_devices`（零副本）。
- 调用链：`bch2_journal_write:845→alloc→（can_discard 时先 do_discards:849）→checksum`。
- 片段（`write.c:154-158`）：
```c
if (!advance_done) {
journal_advance_devs_to_next_bucket(j, &devs, sectors, w->data->seq);
advance_done = true;
goto retry_alloc;
}
```
- 权衡：三级重试（当前桶→翻桶→全盘）；`cas[]` 暂存 `bch_dev*` 避免 alloc→submit 间隙 `dev_remove` 清表后重查（`types.h:43-49` 注释）；`stripe+wp_domain_keys` 跨故障域分散；`BUG_ON(>REPLICAS_MAX:167)`。

### 2.8 `__should_flush/should_flush`（`write.c:991-1077`）+ `bch2_journal_do_writes_locked`（`write.c:1079-1154`）

- 签名：`static int __should_flush(j,w,seq)`；`static int should_flush(j,w,seq)`；`void bch2_journal_do_writes_locked(j)`（需持 `j->lock`）。
- 参数：`w` 候选条目，`seq` 其序号。
- 返回：`__should_flush` 1 flush/0 noflush；`should_flush` 叠加 `try_noflush` 失败则强制 1；`do_writes_locked` void（条件不足静默返回）。
- 调用链：`do_writes_locked:1093→should_flush→{need_flush_write/must_not_flush/may_skip_flush+flush_would_free_space/降级级联/定时}`。
- 片段（`write.c:1097-1102`）：
```c
if (!flush) {
SET_JSET_NO_FLUSH(w->data, true);
w->data->last_seq = 0;
w->last_seq = 0;
j->nr_noflush_writes++;
```
- 权衡：降级级联（`1035-1061`）把等待者拼到下一条、一次越过全部唤醒是最大亮点——noflush 条目永不单独唤醒，由后继 flush 的 `flushed_seq_ondisk` 越过式覆盖；flush 写串行化（`flushes_outstanding>1` 时 `1109` 推迟 + `1147` 要求 `seq_ondisk+1==seq` 保序）；`flush_delay` 定时器在 `1126-1130` 按开/关条目分别 arm/cancel。

### 2.9 `journal_write_submit/preflush/done`（`write.c:547/619/261`，`done_flush:502`）

- 签名：均为 `CLOSURE_CALLBACK`（`submit/preflush/done`）；`journal_write_endio:524` 为 bio 回调。
- 参数：`closure_type(w,journal_buf,io)` 自举。
- 返回：closure 链式 `continue_at`。
- 调用链：`bch2_journal_write→(separate_flush? preflush:619→submit:547)→done_flush:502→done:261→cycle+do_writes`。
- 片段（`write.c:580-584`）：
```c
blk_opf_t opf = REQ_OP_WRITE|REQ_SYNC|REQ_IDLE|REQ_META;
if (flush)
opf |= REQ_FUA;
if (flush && !w->separate_flush)
```
- 权衡：多盘 `REQ_FUA` + 单盘 `PREFLUSH` 合并优化；`separate_flush`（多读写成员时 `870-871` 置位）先对**全部读写成员**发空 PREFLUSH 再写数据——慢盘 pacing 根源，也是 slowpath 计时取全盘的原因；`done:367` 按 `last_uncompleted_write_seq:251` 保序推进 `seq_ondisk/flushed_seq_ondisk`，`write_done` 二态语义（`225-250` 长注释）防并发回调提前 mark-clean。

**可学**：提交分预留/组装/校验/分配/提交五段，每段失败语义明确；错误路径保推进（泄漏 pin）而非保优雅；noflush 降级级联是“一次越过全部唤醒”的典范。

---

## 三、空间记账：三视角加短板仲裁

### 3.1 `journal_space_from`（`reclaim.c:35-48`）+ `bch2_journal_dev_buckets_available`（`reclaim.c:50-68`）

- 签名：`static unsigned journal_space_from(ja,from)`；`unsigned bch2_journal_dev_buckets_available(j,ja,from)`
- 参数：`from∈{discarded:discard_idx, clean_ondisk:dirty_idx_ondisk, clean:dirty_idx}`。
- 返回：可用桶数（环形减法 `(from-cur-1+nr)%nr`），`dirty_ondisk==dirty` 时扣 1（最后一桶需新 last_seq 才能腾出）。
- 调用链：`space_available:308-314` 先前移双脏指针 → `__journal_space_available` 逐盘调用。
- 片段（`reclaim.c:57-58`）：
```c
unsigned available = (journal_space_from(ja, from) -
ja->cur_idx - 1 + ja->nr) % ja->nr;
```
- 权衡：游标语义显式到“指针名即视角”；最后一桶保留规则是防“写了也腾不出”的活锁。

### 3.2 `journal_dev_space_available`（`reclaim.c:126-217`）

- 签名：`static struct journal_space journal_dev_space_available(j,ca,from)`
- 参数：`ca` 单盘，`from` 视角。
- 返回：`{next_entry,total}`（sector）。
- 调用链：`__journal_space_available:235` 逐盘调用 → Top-K 仲裁。
- 片段（`reclaim.c:182-186`）：
```c
fifo_for_each_entry_ptr(buf, &j->in_flight, seq) {
unsigned unwritten = buf->sectors;
if (!unwritten)
continue;
```
- 权衡：在途扣减（未分配条目预扣，不足借整桶对齐 `193-203`，尾部碎片借一桶 `206-209`）；RAM/4 非对称钳制（`166-173/211-215`）：`total` 钳常量、`clean` 随 `dirty_entry_bytes` 收缩——只钳 `total` 不钳 `next_entry`，防推进型写入饿死（长注释 `133-164` 必读）。

### 3.3 `__journal_space_available`（`reclaim.c:219-275`）

- 签名：`static struct journal_space __journal_space_available(j,nr_devs_want,from)`
- 参数：`nr_devs_want=min(在线数,metadata_replicas):347`。
- 返回：Top-K 中最小者的 `{total,next_entry}`；盘数不足回 `{0,0}`。
- 调用链：`space_available:350` 对四视角各调一次。
- 片段（`reclaim.c:244-248`）：
```c
unsigned nr_kept = min(nr_devs, nr_devs_want);
for (pos = 0; pos < nr_kept; pos++)
if (space.total > dev_space[pos].total)
break;
```
- 权衡：Top-K 插入排序（K≤`BCH_REPLICAS_MAX`，小数组 memmove 可接受）而非全局最小——异构盘阵中“第 K 大的最小值”才是短板；`next_entry` 再与最小桶尺寸取 min（`273`）防块不对齐。

### 3.4 `bch2_journal_space_available`（`reclaim.c:277-373`）

- 签名：`void bch2_journal_space_available(struct journal *j)`（需持 `j->lock`）
- 参数：无（读 `last_seq/last_seq_ondisk` 双指针）。
- 返回：void；副作用：刷新 `space[4]`、`can_discard`、`cur_entry_sectors/error`、`may_skip_flush`，调 `set_watermark`。
- 调用链：`close_one:396 / write:877 / update_last_seq:453 / discard:405` 之后必调；是全图“记账中枢”。
- 片段（`reclaim.c:308-314`）：
```c
while (ja->dirty_idx != ja->cur_idx &&
ja->bucket_seq[ja->dirty_idx] < j->last_seq)
ja->dirty_idx = (ja->dirty_idx + 1) % ja->nr;
```
- 权衡：双指针推进（内存脏指针跟 `last_seq`，落盘脏指针跟 `last_seq_ondisk`）+ 丢弃排队（`321-325`）；免刷三条件（`356-360`：ondisk 视角 next<total 且内存-落盘差距≤total/8 且 ondisk 占优超半）是“脏水位低时省一次 flush”的精细优化；无盘时 `cur_entry_error=insufficient_journal_devices:343` 直接卡预留。

**可学**：多视角记账必须显式定义游标；钳制非对称（保推进的不钳）；异构成员取短板用 Top-K 而非最小值；在途预扣防超卖。

---

## 四、回收水位机：四条件加节拍线程

### 4.1 `bch2_journal_set_watermark`（`reclaim.c:70-123`）

- 签名：`void bch2_journal_set_watermark(struct journal *j)`
- 参数：无（读 `space[clean/total]`、`pin` FIFO、`write_buffer`、`open_buckets`）。
- 返回：void；副作用：置 `med/low_on_{space,pin,wb,open_buckets}` 四标志 + `watermark∈{reclaim,stripe}`。
- 调用链：`space_available:364` 尾调；`watermark` 反压 `res_get_fast:471`。
- 片段（`reclaim.c:93-95`）：
```c
unsigned watermark = low_on_space || low_on_pin || low_on_wb || low_on_open_buckets
? BCH_WATERMARK_reclaim
: BCH_WATERMARK_stripe;
```
- 权衡：四条件**或语义**（任一紧张即 reclaim 水位，低优先级写等待）；`med_on_space(clean*4≤total*3:74)` 提前踢回收线程；水位**降低**时 `journal_wake:119-120` 唤醒等待者，升高时不唤醒（自然收敛）；`low_on_open_buckets`（`90-91`）是 fsck 修复耗桶防 wedges 的专项节流，reclaim 路径自身 `no_journal_res` 豁免。

### 4.2 `bch2_journal_dev_do_discards`（`reclaim.c:383-411`）+ `bch2_journal_do_discards`（`reclaim.c:424-430`）

- 签名：`static void bch2_journal_dev_do_discards(ja)`；`void bch2_journal_do_discards(j)`
- 参数：`ja` 单盘设备日志。
- 返回：void；循环 `discard_idx++` + `space_available` 重算。
- 调用链：`space_available:325 queue_work(discard)→discard_work:417→dev_do_discards`；`bch2_journal_write:849` 分配失败时同步直调。
- 片段（`reclaim.c:394-401`）：
```c
while (should_discard_bucket(j, ja)) {
if (!c->opts.nochanges &&
bch2_discard_opt_enabled(c, ca) &&
bdev_max_discard_sectors(ca->disk_sb.bdev))
blkdev_issue_discard(ca->disk_sb.bdev,
```
- 权衡：`should_discard_bucket:24` 要求可用桶 `<max(4,nr/2)` 且 `discard!=dirty_ondisk`；持 `discard_lock` 串行 + `ioref` 防删盘；`nochanges` 测试模式跳过真 discard 只前移指针。

### 4.3 `journal_seq_to_flush`（`reclaim.c:895-922`）

- 签名：`static u64 journal_seq_to_flush(struct journal *j)`
- 参数：无。
- 返回：需刷到的 seq（max（各盘半满对应桶 seq，`cur_seq-pin.size/2`））。
- 调用链：`__reclaim:974` 每轮首调。
- 片段（`reclaim.c:910-915`）：
```c
nr_buckets = ja->nr / 2;
bucket_to_flush = (ja->cur_idx + nr_buckets) % ja->nr;
seq_to_flush = max(seq_to_flush,
ja->bucket_seq[bucket_to_flush]);
```
- 权衡：“日志至多半满 + pin 至多半满”双半满目标，温和而稳定；`pin.size>>1:921` 把 FIFO 压力也折成 seq 目标，一次 `flush_pins` 双达标。

### 4.4 `__bch2_journal_reclaim`（`reclaim.c:945-1023`）+ `bch2_journal_reclaim_thread`（`reclaim.c:1030-1083`）

- 签名：`static int __reclaim(j,bool direct,bool kicked)`；`static int reclaim_thread(void *arg)`；`int bch2_journal_reclaim(j)` 即 `__reclaim(j,true,true):1027`。
- 参数：`direct` 同步/后台，`kicked` 是否被踢醒。
- 返回：0 或 journal error。
- 调用链：`thread→reclaim_lock→__reclaim→seq_to_flush→flush_pins(~0,0,min_nr,min_key_cache)`；`res_get:929` 就地直调。
- 片段（`reclaim.c:1006-1008`）：
```c
nr_flushed = journal_flush_pins(j, seq_to_flush,
~0, 0,
min_nr, min_key_cache);
```
- 权衡：最小量三来源取 max 语义叠加——超时（`reclaim_delay` 未刷则 ≥1:`981-983`）、`med_on_space` 则 ≥1:`985-986`、btree 脏过半则 ≥1:`991-992`，key_cache 另计 `min(need,128):994`；`memalloc_flags(NOIO):961` 防回收锁内触内存回收死锁；线程节拍睡（`next_reclaim=last_flushed+delay:1055`，空队 `schedule():1073` 无限睡，踢醒/超时唤醒），`set_freezable:1038` 配合冻结——冻结时就地干（见 2.2）。

**可学**：水位多条件或语义；后台线程节拍睡加踢醒；冻结时就地干而不等线程；回收锁内禁内存回收。

---

## 五、Pin 钉住：引用保持阻止推进

### 5.1 `bch2_journal_pin_set`（`reclaim.c:687-740`）+ `bch2_journal_pin_set_locked`（`reclaim.c:594-623`）

- 签名：`void bch2_journal_pin_set(j,u64 new_seq,pin,flush_fn)`；内联 `pin_set_locked(j,old_l,new_l,pin,seq,flush_fn)->bool reclaim`
- 参数：`new_seq` 目标 seq，`pin` 嵌入调用者对象（如 `btree.writes[].journal`），`flush_fn` 必非空（debugfs 标识）。
- 返回：void（bool 版回是否需 `maybe_update_last_seq`）。
- 调用链：btree 节点变脏时调用 → `pin_set_locked:原子inc新链表count+list_add(unflushed[type])`。
- 片段（`reclaim.c:610-620`）：
```c
atomic_inc(&new_l->count);
pin->seq = seq;
pin->flush = flush_fn;
enum journal_pin_type type = journal_pin_type(pin, flush_fn);
list_add(&pin->list, &new_l->unflushed[type]);
```
- 权衡：双链表加锁序防死锁（小 seq 先锁：`712-718`）；`WARN_ON(越界:700)` 防 FIFO resize UAF；`new_seq==last_seq` 时 `journal_wake:733`（满时立即尝试 flush_fn）；与容量记账正交——pin 阻止 `last_seq` 推进，space 阻止新预留。

### 5.2 `bch2_journal_pin_copy`（`reclaim.c:630-685`）

- 签名：`void bch2_journal_pin_copy(j,dst,src,flush_fn)`
- 参数： interior 更新 pin 转移（reparent/will_free_node）多 pin 合一取 min。
- 返回：void。
- 调用链：btree 分裂/重父时调用。
- 片段（`reclaim.c:664-667`）：
```c
bool keep = dst_seq && dst_seq <= src_seq;
bool reclaim = false, race = src_seq != src->seq || dst_seq != dst->seq;
if (!race && !keep)
```
- 权衡：Keep-oldest（dst 更老则不动，防释放义务）；seq 双读 + race 重试（无锁读→加锁复验标准模式）。

### 5.3 `journal_get_next_pin`（`reclaim.c:763-805`）

- 签名：`static struct journal_entry_pin *journal_get_next_pin(j,seq_to_flush,allowed_below,allowed_above,seq,flush_fn)`
- 参数：`allowed_*` 为类型位图，`seq` 出参定位。
- 返回：pin 或 NULL；副作用：置 `flush_in_progress`。
- 调用链：`flush_pins:849` 循环调用。
- 片段（`reclaim.c:778-784`）：
```c
* Flushing journal pins (writing btree nodes) requires
* consuming journal space: don't get ahead of journal replay to
* avoid deadlocking
*/
if (pin_list->unreplayed)
break;
```
- 权衡：遇 `unreplayed` 即停（重放前刷 pin 会耗空间又写不出，超前死锁）；`seq_to_flush` 上界 + 类型位图实现“分类型有序回刷”（`flush_done:1165` 自老类型向新类型逐类刷净才下一类）。

### 5.4 `journal_flush_pins`（`reclaim.c:808-893`）

- 签名：`static size_t journal_flush_pins(j,seq_to_flush,allowed_below,allowed_above,min_any,min_key_cache)`
- 参数：`min_any/min_key_cache` 为保底刷量。
- 返回：刷数 `nr_flushed`。
- 调用链：`__reclaim:1006 / flush_pins_or_still_flushing:1154`。
- 片段（`reclaim.c:877-879`）：
```c
/* Pin might have been dropped or rearmed: */
if (likely(!err && !j->flush_in_progress_dropped))
list_move(&pin->list, &pin_l->flushed);
```
- 权衡：`pin_resize_lock` 护全程 grab→flush→clear（`847`），防 resize 快照撕裂；按类型计时（`869-875`）；`flush_in_progress_dropped` 处理 flush 中被 drop/rearm 的 ABA；`wake_up(pin_flush_wait):884` 唤 `pin_flush:747` 等待者；遇 err 即停（`886-887`）。

### 5.5 `bch2_journal_update_last_seq`（`reclaim.c:437-456`）+ `bch2_journal_update_last_seq_ondisk`（`reclaim.c:468-503`）+ `bch2_journal_replay_pins_put`（`reclaim.c:505-525`）

- 签名：`void update_last_seq(j)`（需持 lock）；`int update_last_seq_ondisk(j,last_seq_ondisk,refs)`；`void replay_pins_put(j,seq)`。
- 参数：分别为内存推进 / 落盘推进（附 replicas 引用转移）/ 重放放行。
- 返回：void/int(0)。
- 调用链：`pin_drop:576→maybe_update:458→update_last_seq:437→space_available+reclaim_flush_wait唤醒`；`write_done:374→update_last_seq_ondisk→last_seq_ondisk/flushed_seq_ondisk推进`；`recovery→replay_pins_put:清unreplayed`。
- 片段（`reclaim.c:447-450`）：
```c
while (j->last_seq < j->pin.back &&
j->last_seq <= j->seq_ondisk &&
!atomic_read(&(pin_list = journal_seq_pin(j, j->last_seq))->count))
j->last_seq++;
```
- 权衡：`last_seq` 永不超 `seq_ondisk`（未落盘不推进）；`update_last_seq_ondisk` 把 pin 的 `devs` 引用转入 replicas darray（`486-489`，`GFP_ATOMIC` 锁内分配，失败也继续——预分配 darray 总能做部分功，`write.c:377-397` 注释）；`replay_pins_put` 逐 seq 清 `unreplayed` 并 `dec_and_test→update_last_seq`，重放与回收先后关系显式建模。

**可学**：引用保持必须显式 pin；回收与重放先后关系显式建模，超前即停优于死锁后排查；ABA 用 dropped 标志而非复杂锁。

---

## 六、崩溃恢复：三区加黑名单加逐键校验

### 6.1 `bch2_journal_read_device`（`read.c:709-848`）+ `journal_read_bucket`（`read.c:320-441`）

- 签名：`CLOSURE_CALLBACK(bch2_journal_read_device)`（ per-dev 并发）；`static int journal_read_bucket(ca,buf,jlist,bucket)`
- 参数：`jlist` 共享收集器（`lock+cl+last_seq`），`buf` 桶缓冲。
- 返回：0 成功，`jlist->ret` 汇总。
- 调用链：`bch2_journal_read:1159 closure_call(read_device)→(bsearch快路径:746→read_bucket:763 | 全量:841-845→read_bucket)→journal_entry_add:410`。
- 片段（`read.c:736-746`）：
```c
if (!c->opts.read_entire_journal && ja->nr > 32 && !jlist->full_read) {
CLASS(darray_journal_bucket_entry, order)();
ret = journal_bsearch_collect(ca, &buf, &order);
```
- 权衡：大日志（>32 桶）先只读头找 seq 再按 seq 降序全读活桶（SD 卡优化），读过 `last_seq` 即停（`777`）；读后单调性自检（`790-832`，非单调记 fsck err 不崩）；`read_bucket` 内 IO 错误不直接失败（`340-346` 注释：副本可能在别盘）。

### 6.2 `journal_entry_add`（`read.c:167-299`）——读副本仲裁

- 签名：`static int journal_entry_add(c,ca,entry_ptr,jlist,j)`
- 参数：`entry_ptr{sector,csum_good}`，`j` 本次读到的 jset。
- 返回：0（含去重返回），`OUT_OF_RANGE/ENOMEM` 等。
- 调用链：`read_bucket:410` 逐条目调用。
- 片段（`read.c:245-252`）：
```c
darray_for_each(dup->ptrs, ptr) {
if (ptr->dev == ca->dev_idx) {
if (ptr->sector == entry_ptr.sector)
return 0; /* same physical location, re-read */
```
- 权衡：仲裁四规则显式——同盘同扇区（重读去重）/同盘异扇区（`journal_entry_dup_same_device` fsck 错）/双好非全等（`replicas_data_mismatch` fsck 错）/坏者被好者替换（`274-275`：identical 或新者坏则弃新，`288-295` 好者替换坏者并继承 ptrs）；`last_seq` 前移时丢弃旧 genradix（`203-216`）控内存；`read_entire_journal` 关时 `seq<jlist->last_seq` 直接 `OUT_OF_RANGE:184`。

### 6.3 `bch2_journal_read`（`read.c:1134-1357`）——三区定界

- 签名：`int bch2_journal_read(c,info)`
- 参数：`info` 出参三序号。
- 返回：0 成功。
- 调用链：`mount recovery→read→check_for_missing→jset_validate`。
- 片段（`read.c:1194-1200`）：
```c
if (!info->cur_seq)
info->cur_seq = le64_to_cpu(i->j.seq) + 1;
if (JSET_NO_FLUSH(&i->j)) {
i->ignore_blacklisted = true;
continue;
}
```
- 权衡：逆序找最新 flush 条目定三值（`1188-1224`）：`cur_seq=最大seq+1`（含 noflush，永不复用），`replay_end=最新flush.seq`，`last_seq=其last_seq`；撕裂尾（首个坏校验 flush）标 `ignore_blacklisted:1204` 交上层拉黑；`last_seq>seq` 自愈为 `=`（`1212-1218`）；bsearch 联合缺口在此统一验（`1296-1302`：单盘 bsearch 间隙合法，多盘并集缺口才 fallback 全读 `retry_full_read:956`）。

### 6.4 `journal_validate_key`（`validate.c:53-113`）+ `bch2_journal_entry_validate`（`validate.c:639-649`）+ `jset_validate_entries`（`validate.c:662-692`）+ `bch2_jset_validate`（`validate.c:694-746`）+ `bch2_jset_validate_early`（`validate.c:748-787`）

- 签名：`static int journal_validate_key(c,jset,entry,k,from,version,big_endian)`；`int bch2_journal_entry_validate(c,jset,entry,version,big_endian,from)`；`int bch2_jset_validate(c,ca,jset,sector,flags)`；`int bch2_jset_validate_early(c,ca,jset,sector,bucket_sectors_left)`。
- 参数：`from{BKEY_VALIDATE_journal,journal_seq,journal_offset}` 定位报错；`flags` 含 WRITE（写前验）/READ。
- 返回：0 好，`JOURNAL_ENTRY_NONE/BAD`，`FSCK_DELETED_KEY`（边验边删继续），版本不兼容直接 `EINVAL` 不续验。
- 调用链：`write_checksum:792/805→jset_validate(WRITE)`；`read:1325→jset_validate(READ)`；`entry_validate→ops[type].validate` 分发表。
- 片段（`validate.c:65-72`）：
```c
if (journal_entry_err_on(!k->k.u64s,
c, version, jset, entry,
journal_entry_bkey_u64s_0,
"k->u64s 0")) {
entry->u64s = cpu_to_le16((u64 *) k - entry->_data);
```
- 权衡：容器内坏键**边验边删**（截 `u64s` + `null_range/memmove`，三种坏形 `u64s==0/越界/坏format/validate失败` 各有裁剪公式 `69-70/79-80/88-90/102-104`）而非整条目丢弃；`magic:706/759` 先行（不对即 NONE）；`last_seq>seq` 在 NO_FLUSH 时豁免（`732`）；`early` 版只验 magic+版本+桶越界并截断（`777-784`），读 bucket 头时快速过滤。

### 6.5 黑名单五件套（`seq_blacklist.c:49/113/131/151/188/275`）

- 签名：`int bch2_journal_seq_blacklist_add(c,start,end)`；`u64 next_blacklisted(c,seq)`；`u64 next_nonblacklisted(c,seq)`；`bool is_blacklisted(c,seq,dirty)`；`int blacklist_table_initialize(c)`；`bool blacklist_entries_gc(c)`。
- 参数：半开区间 `[start,end)`（`validate:230` 要求 `start<end`，`238` 要求有序不交）。
- 返回：add 0 成功；next 系列 Eytzinger 二分（`find_gt/find_le:121/140/161`）；is 命中时可选标 dirty。
- 调用链：`read:三区中间段→add`；`open_one:468→is_blacklisted` 守门；`recovery bset newer→is_blacklisted(dirty=true)`。
- 片段（`seq_blacklist.c:75-77`）：
```c
start = min(start, le64_to_cpu(e->start));
end = max(end, le64_to_cpu(e->end));
array_remove_item(bl->start, nr, i);
```
- 权衡：区间合并插入（重叠/邻接归一）+ 超级块持久化（`80-91`：resize→插序→置 feature→write_super→重建内存表）；内存 Eytzinger 布局二分查询 O(log n)；`gc:295` 仅当 `!dirty && end<oldest_seq_found_ondisk` 才删（脏的/还可能被问到的永留）；`last_blacklisted:185` 钳 `cur_seq` 下界防复用。

**可学**：恢复分三区定界；黑名单保序加永不复用；副本仲裁规则显式；容器内坏键边验边删而非整丢；读优化（bsearch）缺口必须在并集层复验。

---

## 七、生命周期：开关机状态机加单调刷盘号

### 7.1 `bch2_journal_cycle_locked`（`journal.c:655-676`）+ `bch2_journal_cycle`（`journal.c:678-683`）

- 签名：`int bch2_journal_cycle_locked(j,flags)`（需持双锁）；`void bch2_journal_cycle(j,flags)`
- 参数：`flags∈{must_close,force_close,must_open}`。
- 返回：0 或 `open_one` 错误。
- 调用链：`res_get:869 / flush_seq_async:1113 / quiesce:718 / write_done:482` 统一入口。
- 片段（`journal.c:664-672`）：
```c
if (journal_should_close(j, flags))
__journal_entry_close_one(j, JOURNAL_ENTRY_CLOSED_VAL, true);
flags &= ~(JOURNAL_CYCLE_must_close | JOURNAL_CYCLE_force_close);
if (!journal_should_open(j, flags))
return 0;
try(__journal_entry_open_one(j));
```
- 权衡：关→开循环机（`should_close:614` 非强制时需 `must_flush` 才关；`should_open:630` 略）消除旧递归；`must_open` 语义“有关必重开”，`flush_waiters` 空转时 `661` 早退。

### 7.2 `bch2_journal_halt_locked/halt`（`journal.c:685-709`）+ `journal_quiesced/quiesce/shutdown_quiesced/shutdown_quiesce`（`journal.c:711-759`）+ `bch2_journal_write_work`（`journal.c:767-772`）

- 签名：`void halt_locked(j)`；`void quiesce(j)`；`void shutdown_quiesce(j)`；`void write_work(work)`。
- 参数：无。
- 返回：void（`quiesce` 阻塞到 `seq==seq_ondisk`，`shutdown_quiesce` 到 `seq==flushed_seq_ondisk` 且 `flush_wait` 空）。
- 调用链：`halt→close(ERROR)+err_seq=cycle+wake(flush_wait,reclaim_flush_wait)`；`quiesce→cycle(must_close)直到静默`；`write_work→flush_async(NULL)`（`flush_delay` 定时器回调）。
- 片段（`journal.c:689-692`）：
```c
__journal_entry_close_one(j, JOURNAL_ENTRY_ERROR_VAL, true);
if (!j->err_seq)
j->err_seq = journal_cur_seq(j);
```
- 权衡：停机置错唤醒防驻留（`701-702` 双 wake，否则 waiter 永等）；shutdown 版多等 `flushed_seq_ondisk+replicas_put+mark_clean`（`727-740` 长注释），错态回退到 `seq_ondisk` 防永等；`write_work` 是 auto-commit 定时器唯一回调（arm 点见 `write.c:1126-1130`）。

### 7.3 `__bch2_journal_flush_seq_async`（`journal.c:1066-1119`）+ `bch2_journal_flush_seq_async`（`journal.c:1148-1196`）+ `bch2_journal_flush_seq`（`journal.c:1198-1234`）

- 签名：`waitlist* __flush_seq_async(j,seq,cl)`；`int flush_seq_async(j,seq,cl)→1已刷/0已挂/-EIO永不刷`；`int flush_seq(j,seq,task_state)` 同步版。
- 参数：`seq` 目标，`cl` 调用者 closure（`BUG_ON(已waiting)`）。
- 返回：见上；`flushing_seq` 原子 max 化（`1178-1182`）。
- 调用链：`flush_seq→flush_seq_async→__flush_seq_async(前向walk挂buf.wait或flush_wait)→cycle→error复查`。
- 片段（`journal.c:1081-1084`）：
```c
for (;; seq++) {
struct journal_buf *buf = &fifo_entry(&j->in_flight, seq);
int r = journal_buf_wait(&fifo_entry(&j->in_flight, seq), cl);
```
- 权衡：前向 walk 跳 NOFLUSH（搭后继 flush 顺风车）、停 NOT_IN_FLIGHT（转 `flush_wait:1104` 并触发 cycle 开新条目 flush 空转日志——fsync 空日志也持久）；`journal_buf_wait:1031` 挂载即转 must-flush（wait 头变真指针）；错态 `err_seq` 后 seq 直接 `-EIO:1172` 防永等；同步版超时（`2×最慢盘/10s:1215`）打调试转储后继续等。

### 7.4 `bch2_journal_noflush_seq`（`journal.c:1268-1285`）+ `bch2_journal_advance_rewind_seq`（`journal.c:1291-1295`）+ `bch2_journal_add_rewind_range`（`journal.c:1297-1315`）+ `bch2_journal_entry_res_resize`（`journal.c:985-1017`）

- 签名：`bool noflush_seq(j,start,end)`；`void advance_rewind_seq(j,seq)`；`int add_rewind_range(c,from,to)`；`void entry_res_resize(j,res,new_u64s)`。
- 参数：noflush 需 `BCH_FEATURE_journal_no_flush` 门控（`1272`）且 `flushed_ondisk<start`（`1275`）。
- 返回：noflush 全设成功才 true（任一 `try_noflush` 失败即 false）；resize void（不够则 `must_close+force_close:1012`）。
- 调用链：分配器免刷区标记 → noflush；discard 安全点 → advance；特殊重写区间 → add（经 `early_journal_entries` 注入下一条）。
- 片段（`journal.c:1278-1282`）：
```c
for (u64 seq = start; seq < end; seq++) {
struct journal_buf *buf = &fifo_entry(&j->in_flight, seq);
if (!journal_buf_try_noflush(buf))
return false;
}
```
- 权衡：免刷区需特性门控 + 已落盘检查 + 逐条目 CAS，任一失败整体失败（调用者回退正常 flush）；rewind 区间记覆盖语义（`types.h:342-352`：`(to,from]` 用 overwrite 条目）；空预留 `early_journal_entries` 强制下条目非空推进（`open_one:557-561` memcpy 注入）。

**可学**：开关机显式状态机；刷盘号（`flushing_seq/flushed_seq_ondisk`）单调；错态回错防永等；定时器 arm/cancel 与开/关条目联动。

---

## 八、设计启示（可学之处汇总）

1. 三矛盾显式建模三套机制，不一锅烩（保序→seq+黑名单，空间→四游标+Top-K，回收→pin+水位机）。
2. 提交分段，每段失败语义明确；错误路径保推进（ERO 泄漏 pin、`write_done` 越过式唤醒、降级级联一次越过全部）。
3. 记账多视角加非对称钳制（只钳 `total` 不钳 `next_entry`）；短板用 Top-K（第 K 大的最小值）；在途预扣防超卖。
4. 水位多条件或（space/pin/wb/open_buckets）；冻结就地干（`trylock+direct reclaim`）；回收锁内禁内存回收（`PF_MEMALLOC_NOIO`）。
5. 引用保持显式 pin（6 分类有序回刷）；超前即停（`unreplayed→break`）；ABA 用 dropped 标志。
6. 恢复三区定界（replay/ blacklist/ new）；序号永不复用（含 noflush/撕裂）；坏键边验边删；副本仲裁四规则显式；读优化缺口并集层复验。
7. 状态机显式（cycle 关→开）；刷盘号单调（`flushing_seq` CAS max）；错态回错防永等（`err_seq`）；定时器与条目联动。
8. 哨兵复用与单字 CAS 是通用技巧，但必须配手写并发原语（`journal_buf_wait` cmpxchg 循环）与长注释载明不变量（`in_flight.front==seq_ondisk+1`、`last_seq` 快照点、`write_done` 二态）——注释即契约。

---

## 复核途径（行号均已核实）

- `wc -l fs/journal/types.h fs/journal/journal.c fs/journal/reclaim.c fs/journal/read.c fs/journal/write.c fs/journal/validate.c fs/journal/seq_blacklist.c` 看 7144 行规模。
- `grep -n "^struct journal\|^union journal_res_state\|^enum journal" fs/journal/types.h` 看中枢（37/90/100/110/134/142/201/247/434/502）。
- `sed -n 450,517p fs/journal/journal.h` 看快路径；`sed -n 295,403p fs/journal/journal.c` 看关条目；`sed -n 410,598p fs/journal/journal.c` 看开条目。
- `sed -n 656,812p fs/journal/write.c` 看组装校验；`sed -n 991,1154p fs/journal/write.c` 看降级级联与提交。
- `sed -n 70,123p fs/journal/reclaim.c` 看水位；`sed -n 219,373p fs/journal/reclaim.c` 看记账；`sed -n 945,1083p fs/journal/reclaim.c` 看回收线程。
- `sed -n 1134,1230p fs/journal/read.c` 看三区；`sed -n 167,299p fs/journal/read.c` 看仲裁；`sed -n 53,113p fs/journal/validate.c` 看边验边删；`cat fs/journal/seq_blacklist.c` 看 1-40 头注释保序论证。
