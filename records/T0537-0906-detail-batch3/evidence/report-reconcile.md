# bcachefs reconcile 编排专题学习报告（T0528 代码级精讲版）

> 基于 T0493 A 向深挖 10 条（九阶段/双沿/分型/闭环/扇出/路由/旁路/
> 唤醒/单线程/边界）。事实源为源码 `fs/data/reconcile/` 下
> `work.c`（2055 行）、`trigger.c`（1092 行）、`format.h`（210 行）、
> `trigger.h`（189 行）、`work.h`（94 行）、`types.h`（41 行）。
> 行号函数名均经 Read/Grep 核实。代码片段一律 ≤10 行。

---

## 一、全景：九阶段流水线

流水线本体是 `work.c:1387 reconcile_phases[]`（8 项，scan×1 + hipri×3 + normal×3 + pending×2，
习惯称“九阶段”含终端哨兵）。驱动链：`bch2_reconcile_thread(:1840)` → `do_reconcile(:1726)` →
`do_reconcile_phase(:1705)` → `do_reconcile_phase_iter(:1631)` / `do_reconcile_phase_phys(:1693)` →
三 handler（`:1577/:1605/:1613`）。取料统一经 `next_reconcile_entry(:339)`。

### 1.1 `reconcile_phases[]`（work.c:1387，静态表，无签名）

- 参数/返回：无；8 元 `{type, priority, btree, start, end}` 数组。
- 调用链：`reconcile_phase_start` 读表置位；`do_reconcile` for 循环遍历；`do_reconcile_phase` 按 `type` 分发。
- 片段（1389-1409，取前 4 项示意）：
```c
{ RECONCILE_PHASE_scan,  RECONCILE_WORK_hipri, BTREE_ID_reconcile_scan, POS_MIN, POS(0, U64_MAX), },
{ RECONCILE_PHASE_btree, RECONCILE_WORK_hipri, BTREE_ID_reconcile_scan, POS(RECONCILE_WORK_hipri, 0), POS(RECONCILE_WORK_hipri, U64_MAX) },
{ RECONCILE_PHASE_phys,  RECONCILE_WORK_hipri, BTREE_ID_reconcile_hipri_phys, POS_MIN, SPOS_MAX },
{ RECONCILE_PHASE_normal,RECONCILE_WORK_hipri, BTREE_ID_reconcile_hipri,      POS_MIN, SPOS_MAX },
```
- 权衡：顺序写死 hipri→normal→pending，btree 内节点先行（注释 1394-1396 “indexed separately…require backpointers”），
降级恢复优先；代价是 normal 大任务会被 hipri 反复插队，靠 kick 中断而非优先级队列解决。

### 1.2 `reconcile_phase_start`（work.c:1531）`static void (struct bch_fs *c)`

- 参数：`c` 文件系统；返回 void；调用链：`do_reconcile:1787` 每阶段入口调用。
- 片段（1533-1548）：
```c
struct reconcile_phase p = reconcile_phases[r->phase];
r->work_pos = BBPOS(p.btree, p.start);
switch (p.type) {
case RECONCILE_PHASE_normal: bch2_progress_init(&r->progress, NULL, c, BIT_ULL(reconcile_work_btree[p.priority]), 0); break;
case RECONCILE_PHASE_phys:   bch2_progress_init(&r->progress, NULL, c, BIT_ULL(reconcile_work_phys_btree[p.priority]), 0); break;
```
- 权衡：每阶段重置 `work_pos` + 仅 normal/phys 重建 progress，scan/btree 走 `scan_stats`；
状态机极简但 `r->phase/work_pos` 被状态展示并发读，需 `READ_ONCE+barrier`（见 6.5）。

### 1.3 `reconcile_phase_is_pending`（work.c:1551）`static bool (unsigned i)`

- 参数：阶段下标；返回是否 pending 段；调用链：`do_reconcile:1795` 门控。
- 片段（1553-1557）：
```c
return (p.btree == BTREE_ID_reconcile_scan &&
        p.start.inode == RECONCILE_WORK_pending) ||
        p.btree == BTREE_ID_reconcile_pending;
```
- 权衡：用 btree+inode 双条件判 pending，比加 flag 更抗表漂移；但表增阶段需同步改此函数，耦合点隐蔽。

### 1.4 `do_reconcile_phase`（work.c:1705）`static int (struct reconcile_pass *p, u32 kick)`

- 参数：`p` 跨阶段上下文束，`kick` 本轮快照；返回 0=阶段走完/中断，err=真失败；调用链：`do_reconcile:1799`。
- 片段（1710-1720）：
```c
bch2_btree_write_buffer_flush_sync(trans);
switch (reconcile_phases[r->phase].type) {
case RECONCILE_PHASE_scan:   return do_reconcile_phase_iter(p, kick, do_reconcile_scan_key);
case RECONCILE_PHASE_btree:  return do_reconcile_phase_iter(p, kick, do_reconcile_btree_key);
case RECONCILE_PHASE_phys:   return do_reconcile_phase_phys(p);
case RECONCILE_PHASE_normal: return do_reconcile_phase_iter(p, kick, do_reconcile_extent_key);
```
- 权衡：入口先 `write_buffer_flush_sync` 保“所见即最新”，phys 独立 one-shot（工人线程内自循环），
其余三类复用同一迭代器；flush 代价换正确性，注释 1688-1692 已明示。

### 1.5 `do_reconcile_phase_iter`（work.c:1631）`static int (struct reconcile_pass *p, u32 kick, reconcile_key_handler handler)`

- 参数：上下文束 + 中断快照 + 单键 handler；返回 0/err；调用链：上节三分支。
- 片段（1640-1648，循环头）：
```c
while (!bch2_move_ratelimit(ctxt) && !test_bit(BCH_FS_going_ro, &c->flags) &&
       bch2_reconcile_enabled(c) && kick == r->kick) {
        bch2_trans_begin(trans);
        struct bkey_s_c k = next_reconcile_entry(trans, p->work, &r->work_pos,
                                                 reconcile_phases[r->phase].end);
```
- 片段（1659-1682，善后，节选 10 行内核心）：
```c
if (bch2_err_matches(ret, BCH_ERR_data_update_fail_need_copygc)) {
        bch2_trans_unlock_long(trans); bch2_copygc_wakeup(c);
        wait_event(c->copygc.running_wq, c->copygc.run_count != *p->copygc_run_count || kthread_should_stop());
        *p->copygc_run_count = c->copygc.run_count; ret = 0; continue; }
if (bch2_err_matches(ret, BCH_ERR_transaction_restart)) { ret = 0; continue; }
if (ret) break;
do_retry_stripes(ctxt, p->stripe_retry);
```
- 权衡：四条件中断（限流/只读/禁用/kick 变）保证“干净走完全部才退”；copygc 联动用 run_count 等待而非忙转；
restart 吞掉继续，scan 段的 restart 则 panic（见 2.5）——内外两层不同策略是刻意为之。

### 1.6 `do_reconcile`（work.c:1726）`static int (struct moving_context *ctxt)`

- 参数：move 上下文；返回 0/err；调用链：`bch2_reconcile_thread:1861` 循环调用。
- 片段（1786-1816，外层 for，节选）：
```c
for (r->phase = 0; r->phase < ARRAY_SIZE(reconcile_phases); r->phase++) {
        reconcile_phase_start(c);
        if (reconcile_phase_is_pending(r->phase) && bkey_deleted(&pending_cookie.k)) goto out;
        ret = do_reconcile_phase(&pass, kick);
        if (ret) goto out;
        work.nr = 0;
        if (kick != r->kick || test_bit(BCH_FS_going_ro, &c->flags) || bch2_move_ratelimit(ctxt)) break;
        bch2_moving_ctxt_flush_all(ctxt);
}
if (r->phase == ARRAY_SIZE(reconcile_phases)) break;
```
- 片段（1819-1833，pending-cookie 收尾 + 无活等待）：
```c
if (!ret && !bkey_deleted(&pending_cookie.k))
        try(bch2_clear_reconcile_needs_scan(trans, pending_cookie.k.p, pending_cookie.v.cookie));
bch2_move_stats_exit(&r->work_stats, c);
if (!ret && !kthread_should_stop() && !atomic64_read(&r->work_stats.sectors_seen) &&
    !sectors_scanned && kick == r->kick) { ... reconcile_wait(c, kick); }
```
- 权衡：pending 段 `break 而非 continue`（注释 1789-1794 “they're all at the end”）等价收尾；
无 cookie 跳 pending（`goto out`）；每段后排空 move IO 防跨段堆积；双零（work_seen+scanned）+kick 未变才睡，防空转与丢唤醒。

### 1.7 `reconcile_pass`（work.c:1563，struct）+ 三 handler（:1577/:1605/:1613）

- `reconcile_pass` 束：`ctxt/snapshot_io_opts/work/last_flushed/stripe_retry/pending_cookie/sectors_scanned/copygc_run_count`，
注释 1559-1562 “Threaded…without a long parameter list”。
- `do_reconcile_scan_key(:1577)`：缓存 pending-cookie（见 4.3），调 `do_reconcile_scan`，restart→panic（1670-1603 区，非 DEBUG 走 `panic+last_restarted_ip`）。
- `do_reconcile_btree_key(:1605)`：`do_reconcile_btree(ctxt,…,r->work_pos,bkey_s_c_to_backpointer(k))` 一行透传。
- `do_reconcile_extent_key(:1613)`：`lockrestart_do(trans, do_reconcile_extent(…))` 包自动重试。
- 权衡：函数指针表驱动消灭 switch 重复；scan-key 独享 panic 级 restart 断言（扫描路径不应在持锁下重启），
extent-key 走常规 lockrestart，严格程度按路径区分。

### 1.8 `next_reconcile_entry`（work.c:339）`static struct bkey_s_c (trans, buf, work_pos, end)`

- 参数：事务/1024 项 darray 缓冲/游标/终点；返回下个 work key（null=耗尽，err=失败）；调用链：phase_iter 与 phys 线程。
- 片段（362-385，批量预取头，节选）：
```c
if (unlikely(!buf->nr)) {
        /* Avoid contention with write buffer flush: buffer up work entries in a darray */
        int ret = for_each_btree_key_max(trans, iter, work_pos->btree, work_pos->pos, end,
                           flags, k, ({
                        bch2_progress_update_iter(trans, &trans->c->reconcile.progress, &iter);
                        if (k.k->type != KEY_TYPE_set) continue;
```
- 片段（392-401，逆序栈化 + 弹出）：
```c
unsigned l = 0, r = buf->nr - 1;
while (l < r) { swap(buf->data[l], buf->data[r]); l++; --r; }
}
return bkey_i_to_s_c(&darray_pop(buf));
```
- 权衡：1024 批量（`RECONCILE_WORK_BUF_NR:336`）摊薄 btree 迭代开销，注释明示避 write-buffer-flush 争用；
逆序后 LIFO 弹出还原正序；`reconcile_scan` 段走单键直通分支（349-360 不缓冲，因 cookie 需逐个比对删除）。

**可学**：后台重整固定流水线加四中断条件（限流/只读/禁用/kick），禁无序抢跑；跨段排空 IO。

---

## 二、选项双沿打标

选项变更是两沿 bracketing：pre 注册在途 + bump，post 再 bump + 唤醒（`work.c:163-180` 大注释为纲）。
删除侧 cookie 比对防误删（`:309`）。触发侧见 trigger.c 第七节。

### 2.1 `bch2_set_reconcile_needs_scan_trans`（work.c:133）`int (trans, s)`

- 参数：事务 + `struct reconcile_scan`；返回 trans_update 结果；调用链：`…_scan/…_pre/…_post` 三者复用。
- 片段（135-150）：
```c
CLASS(btree_iter, iter)(trans, BTREE_ID_reconcile_scan, POS(0, reconcile_scan_encode(s)), BTREE_ITER_intent);
struct bkey_s_c k = bkey_try(bch2_btree_iter_peek_slot(&iter));
u64 v = k.k->type == KEY_TYPE_cookie ? le64_to_cpu(bkey_s_c_to_cookie(k).v->cookie) : 0;
struct bkey_i_cookie *cookie = errptr_try(bch2_trans_kmalloc(trans, sizeof(*cookie)));
bkey_cookie_init(&cookie->k_i); cookie->k.p = iter.pos; cookie->v.cookie = cpu_to_le64(v + 1);
return bch2_trans_update(trans, &iter, &cookie->k_i, 0);
```
- 权衡：读-改-写同一槽位 cookie+1，无则从 0 起；`no_enospc` 提交（调用方指定）保选项传播不因空间失败而丢。

### 2.2 `bch2_set_reconcile_needs_scan`（work.c:153）`int (c, s, wakeup)`

- 参数：fs/扫描描述/是否唤醒；返回 0；调用链：`bch2_set_fs_needs_reconcile(:295)`、pending-wakeup（work.h:76）。
- 片段（155-160）：
```c
CLASS(btree_trans, trans)(c);
try(commit_do(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc,
              bch2_set_reconcile_needs_scan_trans(trans, s)));
if (wakeup) bch2_reconcile_wakeup(c);
return 0;
```
- 权衡：同步提交 + 可选唤醒二合一；单边 bump 用于非选项路径（如 pending 队列通知）。

### 2.3 `bch2_set_reconcile_needs_scan_pre`（work.c:267）/ `…_post`（:285）

- 签名：`int (c, s, scope*)` / `int (c, s)`；返回提交结果；调用链：`bch2_opt_hook_pre/post_set`（opts.c）。
- pre 片段（270-277）：
```c
u64 cookie = reconcile_scan_encode(s);
try(reconcile_scan_in_flight_get(c, cookie));
opt_change_scope_push(scope, cookie);
CLASS(btree_trans, trans)(c);
return commit_do(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc,
                 bch2_set_reconcile_needs_scan_trans(trans, s));
```
- post 片段（287-292）：
```c
CLASS(btree_trans, trans)(c);
int ret = commit_do(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc,
                    bch2_set_reconcile_needs_scan_trans(trans, s));
bch2_reconcile_wakeup(c);
return ret;
```
- 权衡：pre 先注册在途再 bump（顺序不可换，否则扫描线程可能在注册前删 cookie）；post 只 bump+唤醒，
注销由 scope 析构完成（下一节），“erroring-out 也不 strand”（注释 264-266）。

### 2.4 在途表：`reconcile_scan_in_flight(:196)` / `…_get(:202)` / `…_put(:230)` / `scope_push(:246)` / `scope_exit(:252)`

- 签名：lookup `bool(c, cookie)`（无锁 RCU）；get/put `int/void(c, cookie)`（mutex+refcount）；
`opt_change_scope_push(scope, cookie)`；`bch2_opt_change_scope_exit(scope)` 循环 put。
- get 片段（208-227，节选）：
```c
guard(mutex)(&r->scans_in_flight_lock);
struct reconcile_scan_in_flight *e = rhashtable_lookup_fast(&r->scans_in_flight, &cookie, ...);
if (e) { e->ref++; return 0; }
e = kzalloc(sizeof(*e), GFP_KERNEL);
```
- put 片段（238-243）：
```c
BUG_ON(!e);
if (!--e->ref) {
        BUG_ON(rhashtable_remove_fast(&r->scans_in_flight, &e->hash, ...));
        kfree_rcu(e, rcu); }
```
- 权衡：读路径（删 cookie 前检查）用 `rhashtable_lookup_fast` 无锁快路，写路径 mutex+refcount 支持多 opt 并发同 cookie；
`kfree_rcu` 保并发读不 UAF；析构 `WARN_ON_ONCE(1)`（:2021-2025）兜底泄漏显式告警。

### 2.5 `bch2_clear_reconcile_needs_scan`（work.c:309）`static int (trans, pos, cookie)`

- 参数：事务/cookie 槽位/扫描起始读到的值；返回 0；调用链：`do_reconcile_scan:1323` 与 `do_reconcile:1820`（pending 收尾）。
- 片段（314-324）：
```c
CLASS(btree_iter, iter)(trans, BTREE_ID_reconcile_scan, pos, BTREE_ITER_intent);
struct bkey_s_c k = bch2_btree_iter_peek_slot(&iter);
bkey_err(k) ?: ({
        v = k.k->type == KEY_TYPE_cookie ? le64_to_cpu(bkey_s_c_to_cookie(k).v->cookie) : 0;
        v == cookie ? bch2_btree_delete_at(trans, &iter, 0) : 0; });
```
- 片段（1300-1301，前置拒删，属 `do_reconcile_scan`）：
```c
if (reconcile_scan_in_flight(c, cookie_pos.offset))
        return 0;
```
- 权衡：值相等才删（CAS 语义），扫描期间的新 bump（值已变）不会被误删；在途注册直接跳过整轮扫描（注释 1293-1299
“would refuse to delete…so don't burn a full pass”），省整轮 IO，这是双沿设计 load-bearing 点（注释 178-179）。

**可学**：选项传播双沿打标 + cookie 比对删 + 在途注册拒删/拒扫，禁全量重扫与误删。

---

## 三、扫描分型

分型定义 `work.h:10 RECONCILE_SCAN_TYPES()`：fs/metadata/pending/stripes/device/inum。
编码 `format.h:203-207`：fs=0, metadata=1, pending=2, stripes=3, device=32+dev, inum=真实 inum（≥`BCACHEFS_ROOT_INO`）。

### 3.1 `reconcile_scan_encode`（work.c:73）`static u64 (struct reconcile_scan s)`

- 参数：类型+dev/inum 联合；返回 cookie u64；调用链：打标/查表/删 cookie 全路径。
- 片段（84-87）：
```c
case RECONCILE_SCAN_device: return RECONCILE_SCAN_COOKIE_device + s.dev;
case RECONCILE_SCAN_inum:   return s.inum;
default: BUG();
```
- 权衡：device/inum 复用 offset 自然分区（device ≥32 小整数区，inum 大整数区），decode 按阈值反推，
零额外存储；代价是 inum 必须 ≥ROOT_INO 才无歧义，由 `reconcile_scan_decode:95` 保证。

### 3.2 `reconcile_scan_decode`（work.c:93）`static struct reconcile_scan (c, v)`

- 参数：fs + cookie；返回扫描描述；未知值 `bch_err` 后回退 fs 全扫（111-112）；调用链：`do_reconcile_scan:1306`、状态展示。
- 片段（95-103）：
```c
if (v >= BCACHEFS_ROOT_INO) return (struct reconcile_scan){ .type = RECONCILE_SCAN_inum, .inum = v, };
if (v >= RECONCILE_SCAN_COOKIE_device)
        return (struct reconcile_scan){ .type = RECONCILE_SCAN_device, .dev = v - RECONCILE_SCAN_COOKIE_device, };
if (v == RECONCILE_SCAN_COOKIE_pending) return (struct reconcile_scan){ .type = RECONCILE_SCAN_pending };
```
- 权衡：阈值链顺序即优先级（先 inum 后 device），未知 cookie 宁可多扫（回退 fs）不漏扫，可用性优先。

### 3.3 `do_reconcile_scan`（work.c:1284）`static int (ctxt, snapshot_io_opts, cookie_pos, cookie, sectors_scanned*, last_flushed)`

- 参数：上下文束 + cookie 槽位/值 + 累计器；返回 0/err；调用链：`do_reconcile_scan_key`。
- 片段（1306-1323，分发+收尾）：
```c
struct reconcile_scan s = reconcile_scan_decode(c, cookie_pos.offset);
if (s.type == RECONCILE_SCAN_fs)            try(do_reconcile_scan_fs(ctxt, s, snapshot_io_opts, false));
else if (s.type == RECONCILE_SCAN_metadata) try(do_reconcile_scan_fs(ctxt, s, snapshot_io_opts, true));
else if (s.type == RECONCILE_SCAN_device)   try(do_reconcile_scan_bps(ctxt, s, last_flushed));
else if (s.type == RECONCILE_SCAN_stripes)  try(do_reconcile_scan_stripes(ctxt));
else if (s.type == RECONCILE_SCAN_inum) { r->scan_start = BBPOS(BTREE_ID_extents, POS(s.inum, 0)); ...
try(bch2_clear_reconcile_needs_scan(trans, cookie_pos, cookie));
```
- 片段（1325-1331，防睡空转）：
```c
*sectors_scanned += atomic64_read(&r->scan_stats.sectors_seen);
*sectors_scanned += 1;   /* Ensure entries we created are seen…so we don't end stuck in reconcile_wait() */
```
- 权衡：pending 类型无扫描动作（仅 cookie 收集，见 4.3），其余四型分流；`+1` 保“扫描必产生活动计数”，
解 `do_reconcile:1825-1829` 双零才睡的死锁角。

### 3.4 `do_reconcile_scan_fs`（work.c:1198）+ `do_reconcile_scan_btree`（:1152）

- 签名：`int (ctxt, s, snapshot_io_opts, metadata)` / `int (ctxt, s, snapshot_io_opts, btree, level, start, end)`。
- fs 片段（1210-1221）：
```c
for (enum btree_id btree = 0; btree < btree_id_nr_alive(c); btree++) {
        if (!bch2_btree_id_root(c, btree)->b) continue;
        bool scan_leaves = !metadata && (btree == BTREE_ID_extents || btree == BTREE_ID_reflink);
        for (unsigned level = !scan_leaves; level < BTREE_MAX_DEPTH; level++)
                try(do_reconcile_scan_btree(ctxt, s, snapshot_io_opts, btree, level, POS_MIN, SPOS_MAX));
}
```
- btree 片段（1185-1194，中断+间接链）：
```c
(kthread_should_stop() || !bch2_reconcile_enabled(c)) ? 1 :
bch2_bkey_get_io_opts(trans, snapshot_io_opts, k, &opts) ?:
update_reconcile_opts_scan(trans, snapshot_io_opts, &opts, &iter, level, k, s) ?:
(start.inode && k.k->type == KEY_TYPE_reflink_p && REFLINK_P_MAY_UPDATE_OPTIONS(...)
 ? do_reconcile_scan_indirect(ctxt, s, &res.r, bkey_s_c_to_reflink_p(k), snapshot_io_opts, &opts) : 0) ?:
bch2_trans_commit(trans, &res.r, NULL, BCH_TRANS_COMMIT_no_enospc);
```
- 权衡：metadata 仅内节点（level 从 1 起，叶由 btree 指针覆盖），fs 全树叶+枝；`scan_leaves` 谓词把 reflink/extents 叶扫
与其余树区分；reflink_p 间接 extent 顺带展开（下一节），一次遍历双覆盖。

### 3.5 `do_reconcile_scan_bps`（work.c:1099）+ `do_reconcile_scan_bp`（:1068）

- 签名：`int (ctxt, s, last_flushed)` / `int (trans, s, bp, last_flushed)`；device 反向扫描（backpointer 有序）。
- 片段（1107-1119）：
```c
r->scan_start = BBPOS(BTREE_ID_backpointers, POS(s.dev, 0));
r->scan_end   = BBPOS(BTREE_ID_backpointers, POS(s.dev, U64_MAX));
return backpointer_scan_for_each(trans, iter, BTREE_ID_backpointers, POS(s.dev, 0), POS(s.dev, U64_MAX),
                          last_flushed, NULL, bp, ({
        ctxt->stats->pos = BBPOS(BTREE_ID_backpointers, iter.pos);
        ...
```
- bp 片段（1078-1079 + 1085-1096，节选）：
```c
if (BACKPOINTER_ERASURE_CODED(bp.v)) return 0;   /* EC extent handled at stripe level */
struct bkey_s_c k = bkey_try(bch2_backpointer_get_key(trans, bp, &iter, BTREE_ITER_intent, last_flushed));
if (!k.k) return 0;
return update_reconcile_opts_scan(trans, NULL, &opts, &iter, bp.v->level, k, s);
```
- 权衡：device 扫描走 backpointer（物理有序，利于 HDD 顺序化）；EC 编码 extent 跳过（stripe 层统一处理），
职责不重叠；注意此处 `snapshot_io_opts=NULL`（device 路径不缓存快照 opts，换简单换内存）。

### 3.6 `do_reconcile_scan_stripes`（work.c:1256）+ `reconcile_scan_stripe_can_widen_one`（:1226）

- 签名：`int (ctxt)` / `int (trans, iter, k, cache*)`；stripes 只刷 `can_widen` 标志，不做数据搬移。
- 片段（1242-1253）：
```c
u8 new_can_widen = stripe_widen_value(
        stripe_widen_target_nr_data(nr_devs, cur->nr_redundant, c->opts.ec_max_data_blocks),
        cur->nr_blocks - cur->nr_redundant);
if (cur->can_widen == new_can_widen) return 0;
struct bkey_i_stripe *update = errptr_try(bch2_bkey_make_mut_typed(trans, iter, &k, 0, stripe));
update->v.can_widen = new_can_widen;
```
- 权衡：`widen_cache` 批量查目标宽度，相等早退零写放大；stripes 扫描独立成型，避免与 extent 数据路径互锁。

### 3.7 `do_reconcile_scan_indirect`（work.c:1122）+ `update_reconcile_opts_scan`（:1039）

- 签名：`int (ctxt, s, res, p, snapshot_io_opts, opts)` / `int (trans, snapshot_io_opts, opts, iter, level, k, s)`。
- indirect 片段（1131-1145，节选）：
```c
u64 idx = REFLINK_P_IDX(p.v) - le32_to_cpu(p.v->front_pad);
u64 end = REFLINK_P_IDX(p.v) + p.k->size + le32_to_cpu(p.v->back_pad);
try(for_each_btree_key_commit(trans, iter, BTREE_ID_reflink, POS(0, idx),
                              BTREE_ITER_intent|BTREE_ITER_not_extents, k, res, NULL, ...));
```
- update 片段（1056-1058）：
```c
return bch2_update_reconcile_opts(trans, snapshot_io_opts, opts, iter, level, k,
                                  SET_NEEDS_RECONCILE_opt_change);
```
- 权衡：reflink_p 按 front/back_pad 外扩区间全覆盖间接区；统一以 `opt_change` 上下文打标（触发侧宽容新 need_rb，
见 7.4），扫描与前台写权限分离；`restart_count` 压制（1147-1148）防误报重启。

**可学**：扫描按类型分流（全树/内节点/device 反向/inum 单区间/stripes 刷旗），各走各路，EC 与间接各有专道。

---

## 四、pending 闭环

仅“缺设备空间类”错误转 pending（`check_reconcile_pending_err:706`）；执行前 `can_do` 预检；
旋转介质摘链转 phys 重排（`__do_reconcile_extent:867-877`）。

### 4.1 `check_reconcile_pending_err`（work.c:706）`static int (trans, opts, data_opts, k, err)`

- 参数：原 move 错误码；返回原 err / 1（已转 pending）/ restart；调用链：`__do_reconcile_extent:882` 主路径 +
`do_reconcile_extent` pending 段预检 `:861`。
- 片段（713-716，错误过滤器）：
```c
if (!bch2_err_matches(err, BCH_ERR_data_update_fail_no_rw_devs) &&
    !bch2_err_matches(err, BCH_ERR_insufficient_devices) &&
    !bch2_err_matches(err, ENOSPC))
        return err;
```
- 权衡：白名单仅三类空间/设备错误可转 pending，其余（EROFS/snapshot/freelist_empty 等）走各自策略，
防“什么都 pending”导致 pending 队列膨胀；转 pending 前打 `reconcile_set_pending` trace（含 `can_do` 诊断，720-729）。

### 4.2 `bch2_extent_reconcile_pending_mod`（work.c:662）`int (trans, iter, level, k, set)`

- 参数：事务/迭代器/层级/键/置位；返回 0/err；调用链：`__do_reconcile_extent` 两处 + EC 无 stripe 路径（见 7.6）。
- 叶片段（676-686）：
```c
unsigned buf_u64s = level ? BKEY_BTREE_PTR_U64s_MAX : BKEY_EXTENT_U64s_MAX;
struct bkey_i *n = errptr_try(bch2_trans_kmalloc(trans, buf_u64s * sizeof(u64)));
bkey_reassemble(n, k);
if (!level) { bkey_reconcile_pending_mod(c, n, set);
        CLASS(disk_reservation, res)(c);
        return bch2_trans_update_buf(trans, iter, n, buf_u64s, 0) ?:
               bch2_trans_commit(trans, &res.r, NULL, BCH_TRANS_COMMIT_no_enospc); }
```
- 枝片段（688-702，节选）：`btree_node_iter` 取节点 → 一致性 panic 校验 → `bch2_btree_node_update_key`。
- 前置（671-672）：`(rb_work_id(r) == RECONCILE_WORK_pending) == set` 早退，幂等。
- 权衡：叶走 `trans_update`，枝走 `node_update_key`（btree 内节点不能增量改副本，见 423-453 注释）；
无 work 时（`!r||!r->need_rb`）直接 0，不建空 pending；切换 tracking btree 由 trigger 自动搬运（7.2）。

### 4.3 pending-cookie 收集：`do_reconcile_scan_key`（work.c:1577）+ `do_reconcile` 收尾（:1819-1821）

- 片段（1582-1587）：
```c
if (reconcile_scan_decode(c, k.k->p.offset).type == RECONCILE_SCAN_pending)
        bkey_reassemble(&p->pending_cookie->k_i, k);
int ret = do_reconcile_scan(p->ctxt, p->snapshot_io_opts, k.k->p,
                            le64_to_cpu(bkey_s_c_to_cookie(k).v->cookie),
                            p->sectors_scanned, p->last_flushed);
```
- 收尾（1819-1821）：`if (!ret && !bkey_deleted(&pending_cookie.k)) try(bch2_clear_reconcile_needs_scan(…))`。
- 权衡：pending 扫描不做数据动作，只“记住 cookie 槽位”，全轮干净才删；`reconcile_phase_is_pending+goto out`
保无 cookie 时跳过两 pending 段（1.6），有 cookie 才跑 `reconcile_pending` 逻辑树。

### 4.4 执行侧 pending 预检与旋转摘链（`__do_reconcile_extent` work.c:826，859-877）

- 片段（859-877）：
```c
if (work.btree == BTREE_ID_reconcile_pending) {
        int ret = bch2_can_do_data_update(trans, opts, data_opts, k, NULL);
        ret = check_reconcile_pending_err(trans, opts, data_opts, k, ret);
        if (ret > 0) return 0;
        if (ret) return ret;
        if (extent_has_rotational(c, k)) {
                /* pending list is logical order…want device LBA order: take off list, pick up in phys */
                return bch2_extent_reconcile_pending_mod(trans, iter, level, k, false);
        }
}
```
- 权衡：pending 段先 dry-run（`can_do`），仍不可做则留队（ret>0→0）；旋转介质主动摘链，
转由 phys 阶段按 LBA 重排，逻辑序与物理序解耦，这是 4↔5 的交接点。

### 4.5 `bch2_reconcile_pending_wakeup`（work.h:76）+ `bch2_reconcile_scan_pending_to_text`（work.c:1952）

- wakeup：`bch2_set_reconcile_needs_scan(c, {.type=RECONCILE_SCAN_pending}, true)` 一行，设备 add/resize/label 变时调用。
- to_text 片段（1962-1967）：`BTREE_ID_reconcile_scan/POS_MIN` peek，`prt_printf(out, "%u\n", iter.pos.inode == 0)`。
- 权衡：pending 重试不轮询，靠事件唤醒（配置变才看）；状态页只报“有无 pending 扫描”，轻量可观测。

**可学**：满目标转待定闭环而非丢弃；白名单错误 + 预检 + 事件唤醒，禁 pending 膨胀与忙轮询。

---

## 五、物理扇出与路由

物理路：backpointer 天然有序 → 旋转盘每盘一线程（`do_reconcile_phys:1510`）→ `do_reconcile_phys_thread:1453`
强制本盘读（`read_dev`）→ 跳过在途（`bch2_data_update_in_flight`）。路由：`rb_work_id(trigger.h:36)` 三态 +
`data_to_rb/rb_to_data` 映射硬约束。

### 5.1 `do_reconcile_phys`（work.c:1510）`static int (c, reconcile_phase)`

- 参数：fs + 阶段下标；返回 0/err；调用链：`do_reconcile_phase_phys:1700`（已先 `trans_unlock_long`）。
- 片段（1515-1528）：
```c
for_each_member_device(c, ca)
        if (ca->mi.rotational && bch2_dev_is_online(ca))
                try(darray_push(&thrs, ((reconcile_phys_thr){ .c = c, .dev = ca->dev_idx, .reconcile_phase = reconcile_phase, })));
darray_for_each(thrs, i)
        closure_call(&i->cl, do_reconcile_phys_thread, system_unbound_wq, &cl);
closure_sync_unbounded(&cl);
```
- 权衡：仅旋转盘扇出（SSD 走逻辑序 normal 段），在线才入组；`closure_sync_unbounded`  barrier 语义，
全工人才算阶段完成；SSD 不扇出省线程 churn。

### 5.2 `do_reconcile_phys_thread`（work.c:1453，CLOSURE_CALLBACK）

- 上下文：`reconcile_phys_thr{c, dev, phase, cl, stats}`（:1430-1437）；每线程独立 `moving_context` + 1024 缓冲 + stripe_retry。
- 片段（1481-1501，游标与消费）：
```c
struct bbpos work_pos = BBPOS(reconcile_phases[thr->reconcile_phase].btree, POS(thr->dev, 0));
while (!bch2_move_ratelimit(&ctxt)) {
        if (!bch2_reconcile_enabled(c) || test_bit(BCH_FS_going_ro, &c->flags)) break;
        bch2_trans_begin(trans);
        struct bkey_s_c k = next_reconcile_entry(trans, &work, &work_pos, POS(thr->dev, U64_MAX));
        if (bkey_err(k) || !k.k || k.k->p.inode != thr->dev) break;
        int ret = lockrestart_do(trans, do_reconcile_extent_phys(&ctxt, &snapshot_io_opts,
                                                 BBPOS(work_pos.btree, k.k->p), &last_flushed, &stripe_retry));
```
- 析构注记（1441-1452 大注释）：`closure_return` 后 `__cleanup` 才跑，父可先释 darray，
故 `moving_ctxt` 手动 init/exit，不用 CLASS——Rust Drop 序类比已写明。
- 权衡：按 dev 分片（`POS(dev,0)→POS(dev,U64_MAX)`，`inode!=dev` 即停），backpointer 物理有序→顺序 IO；
线程数 = 旋转盘数，短暂派生（阶段结束即 join），非常驻池。

### 5.3 `do_reconcile_extent_phys`（work.c:946）`static int (ctxt, snapshot_io_opts, work, last_flushed*, stripe_retry*)`

- 参数：work 槽位 bpos；返回 0/err；调用链：上节工人循环。
- 片段（955-964，bp 取数 + 在途跳过）：
```c
CLASS(btree_iter, bp_iter)(trans, BTREE_ID_backpointers, work.pos, 0);
struct bkey_s_c bp_k = bkey_try(bch2_btree_iter_peek_slot(&bp_iter));
if (!bp_k.k || bp_k.k->type != KEY_TYPE_backpointer) return 0;  /* write buffer race */
struct bkey_s_c_backpointer bp = bkey_s_c_to_backpointer(bp_k);
struct bbpos pos = BBPOS(bp.v->btree_id, bp.v->pos);
if (bch2_data_update_in_flight(c, &pos, BCH_DATA_UPDATE_reconcile)) return 0;
```
- 片段（986-992，强制本盘读）：
```c
struct data_update_opts data_opts = { .read_dev = work.pos.inode,
                                      .read_flags = BCH_READ_soft_require_read_device, };
```
- 权衡：三重防护（bp 类型校验/在途跳过/intent 锁防 stripe 删除赛，注释 916-918）；
`soft_require` 偏好本盘而非硬绑，盘瞬断可降级；stripe 目标加 intent（969-970）。

### 5.4 路由三态：`rb_work_id`（trigger.h:36）+ `rb_work_id_phys`（:47）+ 映射对（:11/:25）

- `rb_work_id` 片段（36-45）：
```c
static inline enum reconcile_work_id rb_work_id(const struct bch_extent_reconcile *r) {
        if (!r || !r->need_rb) return RECONCILE_WORK_none;
        if (r->pending) return RECONCILE_WORK_pending;
        if (r->hipri)   return RECONCILE_WORK_hipri;
        return RECONCILE_WORK_normal; }
```
- `data_to_rb_work_pos(:11)`：reflink/stripes 钳 `inode=0`，extents 抬至 `≥ROOT_INO`，reflink `inode++`
（与 stripes 抢 0 号槽冲突，+1 错开）；`rb_work_to_data_pos(:25)` 逆映射（0→stripes，<ROOT→reflink-1，否则 extents）。
- `rb_work_id_phys(:47)`：pending→none（phys 树无 pending 位，由 normal 段覆盖）。
- 权衡：pending>hipri>normal 硬优先级，空/零 work 归 none（触发器可删索引位）；
映射函数承担“命名空间隔离”（stripes/reflink/extents 三域投影到一维 work bpos），由 `bch2_extent_reconcile_validate(:22)`
三断言护栏（pending 必有 need_rb；hipri 必为 replicas 位；replicas 非 0）。

### 5.5 索引载体：`reconcile_work_btree[]` / `…_phys_btree[]`（format.h:191/198）+ `reconcile_work_mod`（trigger.c:371）

- 片段（191-201）：
```c
static const enum btree_id reconcile_work_btree[] = {
        [RECONCILE_WORK_hipri] = BTREE_ID_reconcile_hipri, [RECONCILE_WORK_normal] = BTREE_ID_reconcile_work,
        [RECONCILE_WORK_pending] = BTREE_ID_reconcile_pending, };
static const enum btree_id reconcile_work_phys_btree[] = {
        [RECONCILE_WORK_hipri] = BTREE_ID_reconcile_hipri_phys, [RECONCILE_WORK_normal] = BTREE_ID_reconcile_work_phys, };
```
- `reconcile_work_mod(:371)`：`w ? bch2_btree_bit_mod_buffered(trans, reconcile_work_btree[w], pos, set) : 0`。
- 权衡：bitset btree 存位不存值（format.h:34-37 “simple bitset”），buffered 改 amortize；
phys 独立两树（无 pending），与逻辑树双写（见 7.2 `__bch2_trigger…` 非 level 分支隐含的 phys 维护，
经 `bch2_trigger_extent_reconcile` 旁路触发，物理位与逻辑位同事务）。

**可学**：物理有序扇出（backpointer 序 + 每旋转盘一工人 + 本盘读偏好）；路由三态硬约束 + 位图索引。

---

## 六、索引唤醒与线程

叶（逻辑数据）走位图树（reconcile_work*），内节点走扫描条目 backpointer（reconcile_scan inum=1 区）；
kick 自增唤醒无丢失；欠账（hipri）直接返不睡；单主线程 + phys 短暂工人；入口刷写缓冲、跨段排空；
与 copygc/ec 交界串行化。

### 6.1 `bch2_reconcile_wakeup`（work.h:67）`static inline void (c)`

- 片段（67-74）：
```c
static inline void bch2_reconcile_wakeup(struct bch_fs *c) {
        c->reconcile.kick++;
        guard(rcu)();
        struct task_struct *p = rcu_dereference(c->reconcile.thread);
        if (p) wake_up_process(p); }
```
- 调用链：`…_scan_post`、pending-wakeup、电源 notifier（work.c:2016）、`bch2_set_reconcile_needs_scan(wakeup=true)`。
- 权衡：kick++ 与 wake 分离计数——`reconcile_wait:1375` 先 `TASK_INTERRUPTIBLE` 再比 kick，
“seen here or wakes the sleep”（1369-1373），无丢失；RCU 取线程指针，stop 路 `synchronize_rcu` 配对（1979）。

### 6.2 `reconcile_wait`（work.c:1346）`static void (c, kick)`

- 参数：fs + 入睡前 kick 快照；返回 void；调用链：`do_reconcile:1832` 双零且 kick 未变时。
- 片段（1353-1377）：
```c
if (reconcile_hipri_work_pending(c)) { cond_resched(); return; }
if (min_member_capacity == U64_MAX) min_member_capacity = 128 * 2048;
r->wait_iotime_end = now + (min_member_capacity >> 6);
if (r->running) { r->wait_iotime_start = now; r->wait_wallclock_start = ktime_get_real_ns(); r->running = false; }
set_current_state(TASK_INTERRUPTIBLE);
if (kick == READ_ONCE(r->kick)) bch2_kthread_io_clock_wait_once(clock, r->wait_iotime_end, MAX_SCHEDULE_TIMEOUT);
__set_current_state(TASK_RUNNING);
```
- 权衡：hipri 欠账（`reconcile_hipri_work_pending:1335` 读 accounting mem `v[0]||v[1]`）直接返不睡，
高优不被 io-clock 睡眠饿死；等待时长 ∝ 最小成员容量>>6，自适应大小盘；`running=false` 翻转供状态页报 waiting。

### 6.3 `bch2_reconcile_enabled`（work.c:1060）`static bool (c)`

- 片段（1060-1066）：`return !c->opts.read_only && c->opts.reconcile_enabled && !(c->opts.reconcile_on_ac_only && c->reconcile.on_battery);`
- 调用链：phase_iter 循环条件、scan/btree 中断三元、phys 工人、do_reconcile 顶层（1768-1775 `kthread_wait_freezable`）。
- 权衡：三开关与（只读/总使能/仅 AC+电池），禁用时 `flush_all + wait_freezable` 挂起而非退出，选项回切即续跑。

### 6.4 `bch2_reconcile_thread`（work.c:1840）`static int (void *arg)`

- 片段（1851-1862）：
```c
kthread_wait_freezable(c->recovery.pass_done > BCH_RECOVERY_PASS_check_snapshots || kthread_should_stop());
if (kthread_should_stop()) return 0;
struct moving_context ctxt __cleanup(bch2_moving_ctxt_exit);
bch2_moving_ctxt_init(&ctxt, c, NULL, &r->work_stats, writepoint_ptr(&c->allocator.reconcile_write_point), true);
while (!kthread_should_stop() && !do_reconcile(&ctxt)) ;
```
- 起停（:1970/:1986）：stop 取 RCU 指针→`synchronize_rcu`→`kthread_stop+put`；start `nochanges` 直接 0，
`kthread_create(bch2_reconcile_thread…)+get_task+rcu_assign+wake`。
- 权衡：单主线程（phys 工人除外），启动闸等 `check_snapshots`（`snapshot_is_ancestor` 可用性）；
`while(!stop && !do_reconcile)` —— do_reconcile 返回非 0（EROFS 除外 `bch_err_fn:1835`）即退出循环停线程，
 fail-stop 而非 fail-loop。

### 6.5 可观测与边界：`bch2_reconcile_status_to_text`（:1867）/ `init/exit`（:2040/:2027）/ copygc 联动（:1659-1666）

- status 片段（1897-1908，phase 快照）：
```c
unsigned phase_idx = READ_ONCE(r->phase);
struct bpos work_pos = r->work_pos.pos; barrier();
if (phase_idx >= ARRAY_SIZE(reconcile_phases)) { prt_printf(out, "between phases\n"); }
else { struct reconcile_phase phase = reconcile_phases[phase_idx];
        if (phase.type == RECONCILE_PHASE_scan) { prt_printf(out, "scanning: ");
                struct reconcile_scan s = reconcile_scan_decode(c, work_pos.offset); ...
```
- init（2040-2046）：`mutex_init + rhashtable_init + init_done=true`；exit（2027-2033）按 flag 销毁（`free_and_destroy`）。
- copygc 联动（1659-1666）：`need_copygc → unlock_long + copygc_wakeup + wait_event(run_count 变化)`，双工协作不叠写。
- 权衡：状态页容忍“phase==N 越界瞬间”（注释 1892-1896）；线程 backtrace 经 RCU+get_task 安全取；
电源 notifier（:2010-2018）电池翻转即 kick，AC-only 策略闭环。

**可学**：唤醒无丢失（kick 计数 + 睡前重检）；单主 + 短暂工人；边界串行化（write-buffer flush、跨段 drain、copygc run_count、快照门）。

---

## 七、设计启示（触发器精讲 + 执行决策 + 可复用模式）

本节精讲写路径触发器（trigger.c）与执行决策（work.c 第四组函数），末尾收敛八条启示。

### 7.1 脏位计算：`bch2_bkey_needs_reconcile`（trigger.c:463）`static int (trans, k, opts, need_update_invalid_devs*, ret*)`

- 参数：事务/键/IO opts/补 INVALID 指针数/输出 reconcile 结构；返回 >0 需更新，0 无需，<0 err；调用链：
`bch2_bkey_set_needs_reconcile:827`、`bch2_update_reconcile_opts:936`。
- 片段（496-528，逐指针派生 need_rb，节选）：
```c
bkey_for_each_ptr_decode(k.k, ptrs, p, entry) {
        if (!poisoned && !btree && !p.ptr.cached) {
                if (p.crc.csum_type != csum_type) r.need_rb |= BIT(BCH_RECONCILE_data_checksum);
                if (p.crc.compression_type != compression_type) r.need_rb |= BIT(BCH_RECONCILE_background_compression); }
        if (!poisoned && !evacuating && !p.ptr.cached && r.background_target &&
            !bch2_dev_in_target(c, p.ptr.dev, r.background_target)) { r.need_rb |= BIT(..._target); ... }
        if (evacuating) { r.need_rb |= BIT(BCH_RECONCILE_data_replicas); r.hipri = 1; ... } }
```
- 片段（564-583，耐久度三规则 + EC 地板，节选）：
```c
if (max(durability, ec_redundancy + 1) < r.data_replicas) { r.need_rb |= BIT(..._data_replicas); r.hipri = 1; }
if (durability >= r.data_replicas + min_durability) r.need_rb |= BIT(..._data_replicas);
if (!unwritten && r.erasure_code != ec) r.need_rb |= BIT(..._erasure_code);
```
- 片段（590-604，pending 继承 + 变更判定，节选）：
```c
const struct bch_extent_reconcile *old = bch2_bkey_ptrs_reconcile_opts(c, ptrs);
if (old && !(old->need_rb & ~r.need_rb)) { r.pending = old->pending; if (r.hipri && !old->hipri) r.pending = 0; }
return (*need_update_invalid_devs || should_have_rb != !!old || (should_have_rb ? memcmp(old, &r, sizeof(r)) : ...)) && !...incompat...;
```
- 权衡：单遍同时算 need_rb/hipri/ptrs_moving/INVALID 补数，durability 一次读（含 stripe 去重，注释 552-557）；
pending 继承仅当“旧需求 ⊆ 新需求”（`!(old->need_rb & ~r.need_rb)`），升级 hipri 清 pending 防饿死；
poisoned/unwritten/incompressible 各剪枝（486-550），误标代价逐项砍。

### 7.2 索引搬运：`__bch2_trigger_extent_reconcile`（trigger.c:377）`int (trans, op, old_r, new_r)`

- 参数：事务/触发 op（含 btree/level/old/new）/新旧 reconcile；返回 0/err；调用链：
`bch2_trigger_extent_reconcile(trigger.h:115)` 快路（`rb_needs_trigger` 任一非零才进）。
- 叶片段（386-393）：`old_work != new_work` 才 `bit_mod_buffered(old,false)+bit_mod_buffered(new,true)`，
pos 经 `data_to_rb_work_pos` 换算。
- 枝片段（394-417，节选）：`bp.inode != new_work && bp.offset` 则 `reconcile_bp_del`；
`BTREE_TRIGGER_insert` 时 `get_mutable_new` 预留 `+sizeof(reconcile_bp)/8` 后 `reconcile_bp_add + set_reconcile_bp`。
- 会计片段（428-443）：size 变则 `old|new` 全量，size 不变则 `old^new` 差量，逐 bit `disk_accounting_mod2(reconcile_work)`。
- 权衡：叶走位图、枝走 backpointer，双载体同事务搬运；`get_mutable_new` 预留防触发期扩容失败；
accounting 差量/全量双模式，size 不变省一半记账 IO。

### 7.3 旁路写入：`bch2_bkey_set_needs_reconcile`（trigger.c:811）/ `bch2_extent_trigger_set_needs_reconcile`（:895）/ `bch2_update_reconcile_opts`（:917）

- set_needs（811）片段（837-852，节选）：
```c
unsigned new_need_rb = new.need_rb & ~(old ? old->need_rb : 0);
if (unlikely(new_need_rb)) try(new_needs_rb_allowed(trans, snapshot_io_opts, k.s_c, ctx, opt_change_cookie, old, &new, new_need_rb));
if (bkey_should_have_rb_opts(k.s_c, new)) { if (!old) { BUG_ON(...); old = bkey_val_end(k); k.k->u64s += ...; } *old = new; }
else if (old) extent_entry_drop(c, k, (union bch_extent_entry *) old);
```
- trigger_set（895）预留 `+1+BCH_REPLICAS_MAX`（注释 901-905），`get_mutable_new` 扩容后调 set_needs(ctx=other)。
- update（917）叶 `kmalloc+reassemble+set_needs+trans_update`，枝 `node_iter+node_update_key+throw restart_commit(:959)`。
- 权衡：仅新增位才走 `new_needs_rb_allowed` 严格校验（7.4），存量位免检省 fsck 开销；
reflink_v 无 need 也保留条目（`bkey_should_have_rb_opts:452`，间接 extent 需自带 opts，因无反向 inode）；
枝更新后强制 restart-commit，调用方重读，防半更新 btree 节点。

### 7.4 校验门：`new_needs_rb_allowed`（trigger.c:667）`static int (trans, s, k, ctx, opt_change_cookie, old, new, new_need_rb)`

- 参数 8 元；返回 0 允许 / fsck_err；调用链：上节 set_needs。
- 片段（692-729，节选）：
```c
if (ctx == SET_NEEDS_RECONCILE_opt_change || ctx == SET_NEEDS_RECONCILE_opt_change_indirect) return 0;
if ((new_need_rb & BIT(BCH_RECONCILE_erasure_code)) && !bkey_has_ec(c, k)) new_need_rb &= ~BIT(..._erasure_code);
if (ctx == SET_NEEDS_RECONCILE_foreground) { new_need_rb &= ~(..._compression|..._target); new_need_rb &= ~BIT(..._replicas);
        if (!new_need_rb) return 0; if (opt_change_cookie != c->opt_change_cookie) return 0; }
int ret = check_reconcile_scan_cookie(trans, 0, s ? &s->fs_scan_cookie : NULL) ?:
          check_reconcile_scan_cookie(trans, k.k->p.inode, s ? &s->inum_scan_cookie : NULL);
```
- 权衡：opt_change 上下文全放行（扫描即权威）；前台写豁免 compression/target/replicas（后台归一），
EC 非 stripe 豁免（前台不直接写 EC）；`opt_change_cookie`  nonce 防“我读 opts 时你改 opts”误报；
cookie 存在性缓存于 `per_snapshot_io_opts`（`fs/inum_scan_cookie`、`dev_cookie` 位图，trigger.h:140-149），
“只缓存存在不缓存不存在”（注释 739-748），防假阴性。

### 7.5 执行决策：`reconcile_set_data_opts`（work.c:423）`static int (trans, iter, level, k, opts, data_opts*)`

- 参数：事务/迭代器/层级/键/opts/输出 move 指令；返回 >0 可做 / 0 无事 / <0 err（含 pending-mod=1 语义上游处理）；
调用链：`__do_reconcile_extent:855`。
- 片段（448-453，btree 枝硬约束）：
```c
/* we can't add/drop replicas from btree nodes incrementally, we always need to spill over to the whole fs */
if (!r->hipri && !bkey_is_btree_ptr(k.k)) data_opts->write_flags |= BCH_WRITE_only_specified_devs;
```
- 片段（567-587，EC 不可成形，节选）：
```c
if (r->erasure_code) {
        if (!bch2_can_form_ec_stripe(c, r->background_target, r->data_replicas)) {
                if (r->need_rb == BIT(BCH_RECONCILE_erasure_code))
                        return bch2_extent_reconcile_pending_mod(trans, iter, level, k, true);
                goto skip_ec; }
```
- 片段（630-648，空转判定，节选）：
```c
bool ret = (data_opts->ptrs_kill || data_opts->ptrs_kill_ec || data_opts->extra_replicas);
if (!ret) { if (r->need_rb == BIT(BCH_RECONCILE_data_replicas))
                return bch2_extent_reconcile_pending_mod(trans, iter, level, k, true);
        else { CLASS(bch_log_msg_ratelimited, msg)(c); prt_printf(&msg.m, "got extent to reconcile but nothing to do…"); } }
```
- 权衡：过副本走“工作拷贝试删 + 全键 durability 重算”（484-564 两 phase：先保 total 再保 online，offline 优先），
只提 apply 层真会执行的 drop，防 respin；`alloc_nowait`（445）宁 fail 不等分配器（注释 438-444 stale-write 论证）；
EC 组不成 → 纯 EC 转 pending、混合 EC 跳过 EC 位（`goto skip_ec:608`）；空转 replicas-only 也 pending（durability 死锁 ubiquitous case 634-642 注释）。

### 7.6 执行总装：`__do_reconcile_extent`（work.c:826）/ `do_reconcile_extent`（:907）/ `do_reconcile_btree`（:1007）/ `do_reconcile_stripe`（:739）

- `__do_reconcile_extent` 片段（848-857）：`get_io_opts → update_reconcile_opts(other) → commit_lazy → set_data_opts(≤0 早返)`，
先重推导再决策，写缓冲赛（`!r||!r->need_rb`）零代价出。
- `do_reconcile_extent`（907）片段（914-935，节选）：`rb_work_to_data_pos` 反解 → intent/快照迭代 →
stack_k 快照拷贝 → `__do…` → trace。每 work 位精确定位回数据键，stripes 键加 intent（919-920）。
- `do_reconcile_btree`（1007）经 `reconcile_bp_get_key`（trigger.c:276，双 iter：父锁转子锁 300-306，
`will_make_reachable` 跳过 313-314，失配 fsck 删 bp 334-336）；stripe（739）`needs_reconcile` 二检（748/752 write-buffer race），
`-stripe_needs_block_evacuate` 入 retry 数组（768-779），`do_retry_stripes(:808)` 待 IO 排空重放（`stripe_retry_must_wait:787` 比 io_seq）。
- 权衡：读-推导-提交-决策四步同事务前缀，`restart_count` 压制（903）防 ec-retry 误报；
btree/ stripe/ phys 三入口共享 `__do…`，变体仅取数方式不同；未覆盖错误 `WARN_ONCE` 白名单（889-895）后跳过继续，
单键坏不卡整轮。

### 7.7 数据结构速览（format.h）

- `bch_extent_reconcile(:90)`：64 位位域——`type:8/need_rb:5/pending:1/hipri:1/ptrs_moving:5` + 六 opts 快照
（`BCH_RECONCILE_OPTS:147` data_replicas/data_checksum/erasure_code/background_compression/background_target/promote_target）
+ 六 `_from_inode` 位；`reconcile_bp(:136)` 9+55 位外挂索引。
- `BCH_RECONCILE_ACCOUNTING(:161)` 8 计数器（replicas/checksum/ec/compression/target/high_priority/pending/stripes），
`rb_accounting_counters(trigger.c:180)` pending 时剔除 target/replicas 防双记。
- 权衡：每 extent 自带目标快照（前台写即带标，扫描只纠偏），`_from_inode` 区分继承与显式，
reflink 间接 extent 常驻条目换“无反查也能推导”。

### 八条可复用启示

1. 固定流水线 + 四中断（限流/只读/禁用/kick），禁抢跑；跨段排空 IO。
2. 选项双沿（pre 注册+ bump / post bump+唤醒）+ cookie-CAS 删 + 在途拒扫，禁重扫误删。
3. 扫描分型（fs/metadata/device/inum/stripes），EC/间接各有专道。
4. 白名单转 pending + can_do 预检 + 事件唤醒，禁膨胀与轮询；旋转介质逻辑摘链转物理重排。
5. 物理有序扇出（backpointer 序，每旋转盘一工人，本盘 soft 读偏好）+ 在途跳过。
6. 路由三态硬约束（pending>hipri>normal）+ 三域投影映射 + 位图/反指双载体同事务搬运。
7. 唤醒无丢失（kick 计数 + 睡前重检）+ 单主线程 + 短暂工人 + 快照/电源/copygc 门。
8. 脏位单遍派生（need/hipri/INVALID 补数/durability 一次读）+ 新增位才严格校验 + 执行前重推导防写缓冲赛。

---

## 复核途径

- `grep -n "reconcile_phases\|do_reconcile_phase\|rb_work_id\|reconcile_scan_in_flight\|bch2_clear_reconcile_needs_scan\|check_reconcile_pending_err\|do_reconcile_phys_thread\|bch2_bkey_needs_reconcile\|new_needs_rb_allowed" fs/data/reconcile/work.c fs/data/reconcile/trigger.c fs/data/reconcile/trigger.h fs/data/reconcile/format.h` 定位编排、打标、闭环、扇出、触发全链。
