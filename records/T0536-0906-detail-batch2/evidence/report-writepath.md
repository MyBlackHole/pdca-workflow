# bcachefs 写路径全链路专题学习报告（T0525·代码级精讲版）

> 事实源：`bcachefs-tools` 源码（行号函数名均经 `rg`/`Read` 核实，禁编造）。
> 精读：`fs/vfs/pagecache.c`（961 行）、`fs/vfs/buffered.c`（1175 行）、
> `fs/vfs/direct.c`（629 行）、`fs/data/write.c`（2855 行）。
> 七节结构保留；每节逐函数精讲（签名/参数/返回/调用链/≤10 行代码片段/权衡）。
> 约定：`c` = `struct bch_fs`，`inode` = `struct bch_inode_info`，扇区一律 512B。

---

## 一、全景：四段写链路

```
bch2_write_iter (buffered.c:1121) ── IOCB_DIRECT? ──否──▶ bch2_buffered_write (1045)
        │                                                     │  __bch2_buffered_write (876)
        │                                                     │   ├─ bch2_filemap_get_contig_folios_d (pagecache.c:23)
        │                                                     │   ├─ bch2_folio_set (pagecache.c:189)
        │                                                     │   ├─ bch2_folio_reservation_get_partial (pagecache.c:561)
        │                                                     │   └─ bch2_set_folio_dirty (pagecache.c:596)
        │                                                     └─▶ 脏页 → bch2_writepages (693) → __bch2_writepage (561)
        │                                                                                         └─▶ bch2_write (write.c:2716)
        └─是──▶ bch2_direct_write (direct.c:540) ──▶ bch2_dio_write_loop (391)
                                                                      └─▶ bch2_write (write.c:2716)

bch2_write (write.c:2716)
 ├─ 小尾巴 → bch2_write_data_inline (2642) → __bch2_write_index (1340)
 ├─ nocow 优先 → bch2_nocow_write (2285)（失败回落 COW）
 └─ COW → __bch2_write (2480)
           ├─ bch2_alloc_sectors_req（开桶分配）→ bch2_write_extent (1892)
           │     ├─ bch2_write_prep_encoded_data (1744) → bch2_write_op_decode (1683)/bch2_write_rechecksum (1649)
           │     └─ init_append_extent (1557) 组装 extent key
           ├─ bch2_submit_wbio_replicas (1193) 落盘 → bch2_write_endio (1514)
           └─ bch2_write_index (1457, worker) → __bch2_write_index (1340)
                 → bch2_write_index_default (1092) → bch2_extent_update (1026)
                   → bch2_sum_sector_overwrites (862) 精确记账 + btree 提交
```

**可学**：写链路分段，每段可独立降级（对齐失败→缓冲、nocow→COW、足额→降级写+reconcile）。

---

## 二、VFS 入口：预留先行（`fs/vfs/pagecache.c`）

本层核心不变量：**先预留磁盘/配额，才敢把扇区置脏**；`bch_folio` 以 512B 扇区粒度记录
`state × nr_replicas × replicas_reserved`，状态机 `unallocated→reserved→dirty→allocated`
经 `folio_sector_{dirty,undirty,reserve}`（pagecache.c:95/108/121）单向推进。

### `bch2_filemap_get_contig_folios_d` — pagecache.c:23

- 签名：`int bch2_filemap_get_contig_folios_d(struct address_space *mapping, loff_t start, u64 end, fgf_t fgp_flags, gfp_t gfp, folios *fs)`
- 参数：`mapping/start/end` 目标区间；`fgp_flags/gfp` 取页标志；`fs` 输出 darray。
- 返回：有页返回 0；空且 `FGP_CREAT` 返回 `-ENOMEM`，否则透传 `__filemap_get_folio` 错误。
- 调用链：`__bch2_buffered_write`（buffered.c:896）→ 本函数 → `__filemap_get_folio`。
- 片段：
```c
f = __filemap_get_folio(mapping, pos >> PAGE_SHIFT, fgp_flags, gfp);
if (IS_ERR(f))
    break;
BUG_ON(fs->nr && folio_pos(f) != pos);
pos = folio_end_pos(f);
darray_push(fs, f);
```
- 权衡：1MB 后摘掉 `FGP_CREAT`（L33-34），封顶单次批量内存占用；`BUG_ON` 强制连续，
  用崩溃换不变量，简化后续 `f_pos/f_offset` 算术。

### `bch2_write_invalidate_inode_pages_range` — pagecache.c:57

- 签名：`int bch2_write_invalidate_inode_pages_range(struct address_space *mapping, loff_t start, loff_t end)`
- 参数：DIO 范围；要求调用方已持 `pagecache_block`。
- 返回：0 或 `filemap_write_and_wait_range`/`invalidate_inode_pages2_range` 错误。
- 调用链：`bch2_direct_write`（direct.c:608）、`bch2_dio_write_loop`（direct.c:429）→ 本函数。
- 片段：
```c
do {
    if (!mapping->nrpages)
        return 0;
    ret = filemap_write_and_wait_range(mapping, start, end);
    if (ret)
        break;
    ret = invalidate_inode_pages2_range(mapping,
            start >> PAGE_SHIFT, end >> PAGE_SHIFT);
} while (ret == -EBUSY);
```
- 权衡：刷盘→失效配对防 DIO/缓冲读写撕裂；`-EBUSY` 自旋可被持续 redirty 者饿死
  （注释 L62-65 自认），靠 `mkwrite` 侧让步缓解而非根治。

### `__bch2_folio_create` / `bch2_folio_create` — pagecache.c:135/148

- 签名：`struct bch_folio *__bch2_folio_create(struct folio *folio, gfp_t gfp)`；
  `struct bch_folio *bch2_folio_create(struct folio *folio, gfp_t gfp)`（要求 folio 已锁）。
- 参数/返回：依附 `bch_folio + folio_sectors 个 bch_folio_sector` 私有结构；`NULL` = OOM。
- 调用链：`bch2_folio_set`、`bch2_read_single_folio`、`readpages_iter_init` → 本函数。
- 片段：
```c
struct bch_folio *s = kzalloc(sizeof(*s) +
                sizeof(struct bch_folio_sector) *
                folio_sectors(folio), gfp);
spin_lock_init(&s->lock);
folio_attach_private(folio, s);
```
- 权衡：`kzalloc` 按 folio 大小变长分配，大 folio 内存成本高，但换来逐扇区记账精度；
  已存在则复用（`?:`），避免重复分配。

### `bch2_folio_set` — pagecache.c:189

- 签名：`int bch2_folio_set(struct bch_fs *c, struct bch_inode_info *inode, struct folio **fs, unsigned nr_folios)`
- 参数：刚取到的连续 folios；返回 0/`-ENOMEM`/事务错误。
- 调用链：`bch2_write_begin`（buffered.c:784）、`__bch2_buffered_write`（925）、
  `bch2_page_mkwrite`（759）→ 本函数 → `for_each_btree_key_in_subvolume_max` 查 extents。
- 片段：
```c
unsigned nr_ptrs = bch2_bkey_durability_safe(c, k).nr_overwritable;
unsigned state = bkey_to_sector_state(c, k);
if (!bch2_folio(folio)->uptodate)
    __bch2_folio_set(folio, folio_offset, folio_len, nr_ptrs, state);
```
- 权衡：两级快路——`ei_reserved_*` 区间命中免查 btree（L202-214），超限/杂交才走事务；
  读后还预取后 16 个同态 extent 续接 `ei_reserved_*`（L257-280），摊薄下次开销。
  代价：`ei_reserved_*` 需 `ei_reserved_lock` 下发布一致，注释明示"先攒局部再一次发布"。

### `sectors_to_reserve` — pagecache.c:400

- 签名：`static inline unsigned sectors_to_reserve(struct bch_folio_sector *s, unsigned nr_replicas)`
- 返回：`max(0, nr_replicas - s->nr_replicas - s->replicas_reserved)`。
- 调用链：被三个预留路径（408/450/511）共用，是"差额预留"唯一口径。
- 片段：
```c
return max(0, (int) nr_replicas -
       s->nr_replicas -
       s->replicas_reserved);
```
- 权衡：只补差额，已有副本/已预留不重复占 debit，避免覆盖写反复吃掉空间。

### `bch2_get_folio_disk_reservation` — pagecache.c:408

- 签名：`int bch2_get_folio_disk_reservation(struct bch_fs *c, struct bch_inode_info *inode, struct folio *folio, bool check_enospc)`
- 参数：整 folio 补预留；`check_enospc=false` 传 `BCH_DISK_RESERVATION_NOFAIL`。
- 返回：0 或 `-ENOSPC` 等。
- 调用链：`__bch2_writepage`（buffered.c:605）回写前调用。
- 片段：
```c
for (i = 0; i < sectors; i++)
    disk_res_sectors += sectors_to_reserve(&s->s[i], nr_replicas);
ret = bch2_disk_reservation_get(c, &disk_res,
                disk_res_sectors, 1,
                !check_enospc ? BCH_DISK_RESERVATION_NOFAIL : 0);
```
- 权衡：回写路径用 NOFAIL（脏页必须能落盘，ENOSPC 留给写时 admission），
  把压力前移到 `write_begin`，回写永不因空间失败。

### `__bch2_folio_reservation_get` / `get` / `get_partial` / `get_nofail` — pagecache.c:450/552/561/511

- 签名：`static ssize_t __bch2_folio_reservation_get(c, inode, folio, res, offset, len, partial)`；
  `get` 包 `partial=false` 返回 int；`get_partial` 包 `partial=true` 返回实际可预留字节；
  `get_nofail` 用 `BCH_DISK_RESERVATION_NOFAIL` 且配额 `add(..., false)`。
- 参数：`offset/len` 按 `block_bytes` 上下取整到扇区；`res` 累积 `disk.sectors/quota`。
- 返回：`get` 返回 0/负错；`get_partial` 返回可写长度或负错（0 长直接 `ENOSPC_disk_reservation`）。
- 调用链：`bch2_write_begin`→`get`；`__bch2_buffered_write`→`get_partial`；
  `bch2_vfs_dirty_folio`/`bch2_page_mkwrite`→`get_nofail`/`get`。
- 片段（部分预留对齐裁剪）：
```c
unsigned reserved_offset = round_down(i << 9, block_bytes(c));
reserved = clamp(reserved_offset, offset, offset + len) - offset;
if (!reserved)
    return bch_err_throw(c, ENOSPC_disk_reservation);
```
- 权衡：`partial` 允许短预留短写（大批量缓冲写不因尾部 ENOSPC 全军覆没）；
  裁剪点强制块对齐，避免下游 `bch2_write` 因 `misaligned write` 自杀（write.c:2742）。

### `bch2_set_folio_dirty` / `bch2_set_folio_undirty` — pagecache.c:596/570

- 签名：`bool bch2_set_folio_dirty(c, inode, folio, res, offset, len)`；
  `void bch2_set_folio_undirty(c, inode, folio, offset, len)`。
- 参数：`res` 为已获预留（dirty 负责把 `res->disk.sectors` 过户到 `s->replicas_reserved`）；
  范围按块取整。
- 返回：dirty 返回 `filemap_dirty_folio` 是否新脏（已脏返回 false）；undirty 无返回，
  归还 `replicas_reserved` 并 `i_sectors_acct` 减账。
- 调用链：`bch2_write_end`（851）、`__bch2_buffered_write`（1018）、`bch2_page_mkwrite`（768）。
- 片段（过户+染色）：
```c
s->s[i].replicas_reserved += sectors;
res->disk.sectors -= sectors;
dirty_sectors += s->s[i].state == SECTOR_unallocated;
bch2_folio_sector_set(folio, s, i, folio_sector_dirty(s->s[i].state));
```
- 权衡：预留与脏化原子配对（持 `s->lock`），`writepage` 出错竞态按
  `min(sectors, res->disk.sectors)` 钳位（L637），宁可少记不透支。

### `bch2_vfs_dirty_folio` — pagecache.c:654

- 签名：`bool bch2_vfs_dirty_folio(struct address_space *mapping, struct folio *folio)`
- 参数：mm 回调，无长度信息；返回是否新脏。
- 调用链：`address_space_operations.dirty_folio` → 本函数 → `get_nofail` + `set_folio_dirty`。
- 片段：
```c
if (folio_pos(folio) >= file_size)
    return false;
bch2_folio_reservation_init(c, inode, &res);
BUG_ON(bch2_folio_reservation_get_nofail(c, inode, folio, &res, 0, dirty_bytes));
```
- 权衡：mm 侧脏页（如 PTE 回写）无预留上下文，只能 NOFAIL 补票；超 `i_size` 直接拒，
  注释承认这是"mm 疯人院"的防御。

### `bch2_page_fault` / `bch2_page_mkwrite` — pagecache.c:679/718

- 签名：`vm_fault_t bch2_page_fault(struct vm_fault *vmf)` / `vm_fault_t bch2_page_mkwrite(struct vm_fault *vmf)`。
- 参数/返回：标准 fault 回调；返回 `VM_FAULT_LOCKED/SIGBUS/NOPAGE`。
- 调用链：mmap 读缺页 → `filemap_fault`（加 `pagecache_add` 保护）；写缺页 → `folio_set` +
  `reservation_get` + `set_folio_dirty` + `folio_wait_stable`。
- 片段（死锁排序 + 写缺页提交）：
```c
if (fdm > mapping) {           /* page_fault：全局地址序取锁，拿不到就 SIGBUS 重试 */
```
```c
if (bch2_folio_set(c, inode, &folio, 1) ?:
    bch2_folio_reservation_get(c, inode, folio, &res, offset, len)) {
    folio_unlock(folio);
    ret = VM_FAULT_SIGBUS;
```
- 权衡：`page_fault` 用 mapping 指针地址定序，跨 mapping（fault-disable 映射）反序时
  主动放锁返回 SIGBUS 让用户态重试，以活锁换无死锁；`mkwrite` 持
  `pagecache_add` 期间做预留，防止与 DIO `invalidate` 互锁（L740-746 注释）。

### `bch2_mark_pagecache_reserved` / `bch2_mark_pagecache_unallocated` — pagecache.c:341/300

- 签名：`int bch2_mark_pagecache_reserved(inode, u64 *start, u64 end, bool nonblocking)`；
  `void bch2_mark_pagecache_unallocated(inode, u64 start, u64 end)`。
- 参数：`start` 输入输出（推进到已处理处）；`nonblocking` 用 `folio_trylock`，拿不到返回 `-EAGAIN`。
- 调用链：fallocate 预留/打洞路径 → 本函数（`folio_sector_reserve` 单向染色）。
- 片段：
```c
i_sectors_delta -= s->s[j].state == SECTOR_dirty;
bch2_folio_sector_set(folio, s, j,
    folio_sector_reserve(s->s[j].state));
```
- 权衡：只改状态不碰 `nr_replicas`，脏页计数 via `i_sectors_acct` 一次性结算；
  nonblocking 版宁可 `-EAGAIN` 也不阻塞，调用方可退避重试。

**可学**：写前先预留、差额预留、免读快路（见下节 `write_begin`）是必备三件套。

---

## 三、缓冲写：聚合节流（`fs/vfs/buffered.c`）

### `bch2_write_begin` — buffered.c:723

- 签名：`int bch2_write_begin([file|iocb], mapping, loff_t pos, unsigned len, struct folio **foliop, void **fsdata)`
  （6.17+ 首参由 `file*` 改为 `const kiocb*`，条件编译兼容）。
- 参数：`pos/len` 写区间；输出锁定的 folio + `bch2_folio_reservation*`（`fsdata`）。
- 返回：0 或 `bch2_err_class` 归一化负错。
- 调用链：VFS `address_space_operations.write_begin` → 本函数 → `bch2_folio_set` +
  `bch2_folio_reservation_get`；读缺角 → `bch2_read_single_folio`（349）。
- 片段（两条免读快路 + 预留失败重读）：
```c
/* If we're writing entire folio, don't need to read it in first: */
if (!offset && len == folio_size(folio))
    goto out;
if (!offset && pos + len >= inode->v.i_size) {
    folio_zero_segment(folio, len, folio_size(folio));
```
```c
ret = bch2_folio_reservation_get(c, inode, folio, res, offset, len);
if (ret) {
    if (!folio_test_uptodate(folio)) {
        goto readpage;   /* 没读盘前不知是否真需预留，先读再算一次 */
```
- 权衡：整页覆写/尾部追加直接置零免读，是顺序写带宽的关键；预留失败时若页未 uptodate
  先读后重算——读后可能发现全是已分配扇区从而免预留，用一次读换 ENOSPC 误杀率下降。

### `bch2_write_end` — buffered.c:815

- 签名：`int bch2_write_end([file|iocb], mapping, pos, len, copied, folio, fsdata)`，返回 `copied`。
- 调用链：VFS → 本函数 → `bch2_set_folio_dirty`；`fsdata` 预留在此 `put+kfree`。
- 片段（短拷重做 + i_size 扩展）：
```c
if (unlikely(copied < len && !folio_test_uptodate(folio))) {
    folio_zero_range(folio, 0, folio_size(folio));
    flush_dcache_folio(folio);
    copied = 0;   /* 逼用户态重做，避免半页脏数据 */
```
```c
scoped_guard(spinlock, &inode->v.i_lock)
    if (pos + copied > inode->v.i_size)
        i_size_write(&inode->v, pos + copied);
```
- 权衡：`copied<len` 且页未 uptodate 时宁可丢弃本次拷贝（返回 0）也不落半页，
  正确性优先于一次系统调用的进度。

### `__bch2_buffered_write` — buffered.c:876

- 签名：`static int __bch2_buffered_write(c, inode, mapping, iter, loff_t pos, unsigned len)`，
  返回实际拷贝字节或负错。
- 调用链：`bch2_buffered_write` → 本函数；内部串起取页→读头尾→`folio_set`→逐页
  `get_partial`→`copy_folio_from_iter_atomic`→`set_folio_dirty`。
- 片段（头尾页按需读 + 部分预留截断）：
```c
f = darray_first(fs);
if (pos != folio_pos(f) && !folio_test_uptodate(f)) {
    ret = bch2_read_single_folio(f, mapping);
```
```c
f_reserved = bch2_folio_reservation_get_partial(c, inode, f, &res, f_offset, f_len);
if (unlikely(f_reserved != f_len)) { ... folios_trunc(&fs, fi); end = ...; break; }
```
```c
f_copied = copy_folio_from_iter_atomic(f, f_offset, f_len, iter);
```
- 权衡：中间页跳过读（必被全覆盖），只读头尾——批量写的读放大最小化；
  预留不足时 `folios_trunc` 截断本次批量而非整体失败；`copy_..._atomic` 不
  睡眠，拷不动就截断返回， fault 处理交上层循环。

### `bch2_buffered_write` — buffered.c:1045

- 签名：`static ssize_t bch2_buffered_write(struct kiocb *iocb, struct iov_iter *iter)`。
- 调用链：`bch2_write_iter` → 本函数 → `__bch2_buffered_write`；每次成功后
  `balance_dirty_pages_ratelimited`。
- 片段（先 fault 用户页 + 零进展降级）：
```c
if (unlikely(fault_in_iov_iter_readable(iter, bytes))) {
    bytes = min_t(unsigned long, iov_iter_count(iter),
              PAGE_SIZE - offset);
```
```c
if (unlikely(ret == 0)) {
    bytes = min_t(unsigned long, PAGE_SIZE - offset,
              iov_iter_single_seg_count(iter));
    goto again;
```
- 权衡：先把用户页 fault 进来，避免 `copy_atomic` 持页锁睡死（同页自拷死锁，
  L1064-1073 注释）；零进展时退到单段单页重试，用小步推进换不活锁。

### `bch2_write_iter` — buffered.c:1121

- 签名：`ssize_t bch2_write_iter(struct kiocb *iocb, struct iov_iter *from)`，VFS `file_operations.write_iter`。
- 调用链：VFS → 按 `IOCB_DIRECT` 分流 DIO/缓冲；缓冲侧 `inode_lock` +
  `snapshots.create_lock` → `generic_write_checks` → `bch2_buffered_write` →
  `generic_write_sync`。
- 片段：
```c
if (iocb->ki_flags & IOCB_DIRECT) {
    ret = bch2_direct_write(iocb, from);
    goto out;
}
inode_lock(&inode->v);
percpu_down_read(&c->snapshots.create_lock);
```
- 权衡：缓冲写串行化快照创建，保证快照不抓到"脏页已提交一半"的中间态；
  DIO 侧免此锁（btree 提交本身对快照原子，L1136-1137 注释），读多写少不互伤。
  代价：缓冲写并发度被 inode 锁限制，大文件多线程写同一 inode 串行。

### `__bch2_writepage` — buffered.c:561

- 签名：`static int __bch2_writepage(struct folio *folio, struct writeback_control *wbc, void *data)`。
- 参数：`data` 为 `bch_writepage_state`（攒批 bio + `tmp` 快照 + opts）。
- 调用链：`bch2_writepages` 的 `writeback_iter` → 本函数 → `bch2_writepage_io_alloc` 攒批 →
  `bch2_writepage_do_io`（`closure_call(bch2_write)`）。
- 片段（i_size 裁剪 + 预留快照 +  contiguous 续接）：
```c
ret = bch2_get_folio_disk_reservation(c, inode, folio, false);
BUG_ON(ret);
scoped_guard(spinlock, &s->lock) {
    memcpy(w->tmp, s->s, sizeof(struct bch_folio_sector) * f_sectors);
```
```c
if (w->io &&
    (w->io->op.res.nr_replicas != nr_replicas_this_write ||
     bch_io_full(w->io, sectors << 9) ||
     bio_end_sector(&w->io->op.wbio.bio) != sector))
    bch2_writepage_do_io(w);
```
- 权衡：跨 `i_size` 的页先清尾再 `set_undirty`（L593-596），mmap 语义正确；
  脏扇区取 `min(nr_replicas)`（L616-620）统一本批副本数，不同副本需求绝不混批；
  非连续扇区立即提交旧批，保证一个 `writepage_io` 的 bio 物理连续。

### `bch2_writepages` / `bch2_writepage_io_alloc` / `bch2_writepage_do_io` / `bch2_writepage_io_done` — buffered.c:693/498/486/424

- 签名：`int bch2_writepages(mapping, wbc)`；`alloc(c, wbc, w, inode, sector, nr_replicas)`；
  `do_io(w)` 发射；`io_done(op)` 收尾。
- 调用链：mm 回写 → `bch2_writepages` → `throttle_writes` + `writeback_iter`/`__bch2_writepage`。
- 片段（节流 + 结算）：
```c
while (throttle_writes(c, w->opts.data_replicas, &cl),
       (folio = writeback_iter(mapping, wbc, folio, &ret)))
    ret = __bch2_writepage(folio, wbc, w);
```
```c
bio_for_each_folio_all(fi, bio) {
    if (atomic_dec_and_test(&s->write_count))
        folio_end_writeback(fi.folio);
```
- 权衡：`throttle_writes` 看 open-bucket 余量与 journal 水位（见下），背压写回而非
  OOM；`io_done` 出错把整批扇区 `nr_replicas=0`（L439-444）并 `EI_INODE_ERROR`，
  下次读必走降级/修复，不静默。

### `can_write_now` / `throttle_writes` / `bch_io_full` — buffered.c:528/546/417

- 签名：`static bool can_write_now(c, replicas_want, cl)`；`static void throttle_writes(c, replicas_want, cl)`；
  `static inline bool bch_io_full(io, len)`。
- 片段：
```c
if (unlikely(c->allocator.open_buckets_nr_free <= reserved)) {
    closure_wait(&c->allocator.open_buckets_wait, cl);
    return false;
}
if (BCH_WATERMARK_normal < c->journal.watermark && !bch2_journal_error(&c->journal)) {
    closure_wait(&c->journal.async_wait, cl);
```
```c
return bio_full(bio, len) ||
    (bio->bi_iter.bi_size + len > BIO_MAX_VECS * PAGE_SIZE);
```
- 权衡：双水位（开桶/journal）联动写回，journal 拥塞时主动停写，防止 checkpoint
  追不上；单批上限 `BIO_MAX_VECS*PAGE_SIZE` 是迁就 `bch2_write_extent` bounce 路径
  的上限（L409-416 注释），宁可多批不大包。

**可学**：聚合节流（攒连续批）+ 背压（水位停写）+ 刷盘失效配对，三者缺一不可。

---

## 四、直通写：对齐快检（`fs/vfs/direct.c`）

### `bch2_direct_write` — direct.c:540

- 签名：`ssize_t bch2_direct_write(struct kiocb *req, struct iov_iter *iter)`。
- 参数：`req->ki_pos` + `iter->count` 必须同时块对齐；返回写入字节或负错（异步 `-EIOCBQUEUED`）。
- 调用链：`bch2_write_iter`（IOCB_DIRECT）→ 本函数 → `bch2_write_invalidate_inode_pages_range` →
  `bch2_dio_write_loop` → `bch2_dio_write_done`。
- 片段（门槛三连 + 扩展锁策略）：
```c
if (!enumerated_ref_tryget(&c->writes, BCH_WRITE_REF_dio_write))
    return -EROFS;
if (unlikely((req->ki_pos|iter->count) & (block_bytes(c) - 1))) {
    ret = bch_err_throw(c, EINVAL_unaligned_io);
```
```c
extending = req->ki_pos + iter->count > inode->v.i_size;
if (!extending) {
    inode_unlock(&inode->v);   /* 非扩展立即放锁，扩展全程持锁保 i_size */
```
- 权衡：未对齐直接 `-EINVAL` 不降级（与缓冲写分工明确）；`writes` 引用计数做 RO 门禁；
  非扩展写放掉 inode 锁换并发，扩展写持锁保 `i_size`，读写锁粒度的经典折中。

### `bch2_dio_write_loop` — direct.c:391

- 签名：`static __always_inline long bch2_dio_write_loop(struct dio_write *dio)`，
  同步返回字节数，异步返回 `-EIOCBQUEUED`。
- 参数：`dio` 捆绑 req/mapping/inode/iter/op/quota_res/written/sync/flush/loop/mm。
- 调用链：`bch2_direct_write` / `bch2_dio_write_continue`（worker）→ 本函数 →
  `bch2_bio_iov_iter_get_pages` → `bch2_write_op_init` → `bch2_quota_reservation_add` +
  `bch2_disk_reservation_get` → `closure_call(bch2_write)`。
- 片段（FDM 防死锁 + 块尾裁剪 + 预留失败快检）：
```c
ret = bch2_bio_iov_iter_get_pages(bio, &dio->iter, 0);
dropped_locks = bch2_fdm_dropped_locks(c);
fdm_clear(&c->fdm_table);
if (dropped_locks && ret)
    ret = 0;
```
```c
unaligned = bio->bi_iter.bi_size & (block_bytes(c) - 1);
bio->bi_iter.bi_size -= unaligned;
iov_iter_revert(&dio->iter, unaligned);
```
```c
ret = bch2_disk_reservation_get(c, &dio->op.res, bio_sectors(bio),
                dio->op.opts.data_replicas, 0);
if (unlikely(ret) &&
    !bch2_dio_write_check_allocated(dio))
    goto err;
```
- 权衡：`FDM`（fault-disable mapping）期间 mmap fault 会主动丢锁，loop 检测到
  `dropped_locks` 就重做 `invalidate` 再试，以一次重刷换不死锁；块尾非对齐字节
  退回 iter 而非报错，容忍 `get_pages` 多拿；磁盘预留失败先查"已足额分配"
  （`bch2_check_range_allocated` 逐 extent 验 `durability.total`），覆盖写不额外占空间。

### `bch2_check_range_allocated` / `bch2_dio_write_check_allocated` — direct.c:241/277

- 签名：`static bool bch2_check_range_allocated(c, inum, offset, size, nr_replicas, compressed)`；
  `static noinline bool bch2_dio_write_check_allocated(struct dio_write *dio)`（noinline 压栈帧）。
- 返回：全区间快照一致、副本数达标、无"压缩混杂"（非压缩写遇压缩扇区判 false）即 true。
- 片段：
```c
if (k.k->p.snapshot != snapshot ||
    nr_replicas > bch2_bkey_durability_safe(c, k).total ||
    (!compressed && bch2_bkey_durability_safe(c, k).sectors_compressed))
    return false;
```
- 权衡：transaction_restart 自旋重试，读一致性优先；`total`（非 overwritable）口径，
   degraded 副本也算数——复用旧空间比新分配便宜，但把耐久债留给 reconcile。

### `bch2_dio_write_copy_iov` — direct.c:298

- 签名：`static noinline int bch2_dio_write_copy_iov(struct dio_write *dio)`，
  返回 0/-1/-ENOMEM。
- 片段：
```c
if (iter_is_ubuf(&dio->iter))
    return 0;
if (!iter_is_iovec(&dio->iter))
    return -1;
if (dio->iter.nr_segs > ARRAY_SIZE(dio->inline_vecs)) {
    dio->iov = iov = kmalloc_array(dio->iter.nr_segs, sizeof(*iov), GFP_KERNEL);
```
- 权衡：异步 DIO 的 iov 可能在调用者栈上，必须内联/堆拷贝续命；`ubuf` 单段免拷，
  非 iovec（如 kvec/bvec）直接放弃异步转同步——覆盖全部 iter 类型不如守住常用路。

### `bch2_dio_write_end` / `bch2_dio_write_done` / `bch2_dio_write_sync_done` — direct.c:356/327/384

- 签名：`static __always_inline void bch2_dio_write_end(struct dio_write *dio)`（每片结算）；
  `static __always_inline long bch2_dio_write_done(struct dio_write *dio)`（总值班）；
  `sync_done` 为同步版 `end_io` 回调（仅置旗）。
- 片段（双阶段结算）：
```c
req->ki_pos += (u64) dio->op.written << 9;
dio->written  += dio->op.written;
if (dio->extending) { guard(spinlock)(&inode->v.i_lock);
    if (req->ki_pos > inode->v.i_size) i_size_write(&inode->v, req->ki_pos); }
if (dio->op.i_sectors_delta || dio->quota_res.sectors) {
    guard(mutex)(&inode->ei_quota_lock);
    __bch2_i_sectors_acct(c, inode, &dio->quota_res, dio->op.i_sectors_delta);
```
```c
long ret = dio->op.error ?: ((long) dio->written << 9);
bio_put(&dio->op.wbio.bio);
enumerated_ref_put(&c->writes, BCH_WRITE_REF_dio_write);
inode_dio_end(&inode->v);
```
- 权衡：`end` 只做记账+放页（可跑多次），`done` 做引用/计数/complete（只跑一次），
  职责分离使 async continue（`bch2_dio_write_continue` direct.c:515，`kthread_use_mm` 切
  回用户 mm + `bio_reset` 复用 bio）循环简洁；扩展 i_size 在 `i_lock` 下条件前推，
  不回退（短写不缩文件）。

### `bch2_dio_write_loop_async` / `bch2_dio_write_continue` — direct.c:528/515

- 签名：`static void bch2_dio_write_loop_async(struct bch_write_op *op)`（`end_io` 回调）；
  `static noinline __cold void bch2_dio_write_continue(struct dio_write *dio)`。
- 片段：
```c
bch2_dio_write_end(dio);
if (likely(!dio->iter.count) || dio->op.error)
    bch2_dio_write_done(dio);
else
    bch2_dio_write_continue(dio);   /* bio_reset 复用 bio，mm 切回后继续 loop */
```
- 权衡：中断/完成上下文只做轻结算，重循环踢到 worker 并复用 bio，减少分配；
  `mm` 指针续命用户地址空间，代价是生命周期管理复杂度。

**可学**：对齐门槛前置、快检复用旧空间、FDM+mm 续命两处死锁防护，是 DIO 吞吐的关键。

---

## 五、数据组装：覆盖记账（`fs/data/write.c` 前半）

### `bch2_sum_sector_overwrites` — write.c:862

- 签名：`int bch2_sum_sector_overwrites(trans, extent_iter, new, usage_increasing, i_sectors_delta, disk_sectors_delta)`。
- 参数：`new` 为待插 extent；输出逻辑扇区增量（i_sectors，是否分配态翻转）与
  物理增量（disk_sectors，按 `nr_replicas` 加权）。
- 返回：0 或遍历错误。
- 调用链：`bch2_extent_update` → 本函数（`for_each_btree_key_max_continue_norestart` 扫被覆旧键）。
- 片段：
```c
*i_sectors_delta += sectors *
    (bkey_extent_is_allocation(&new->k) -
     bkey_extent_is_allocation(old.k));
*disk_sectors_delta += sectors * new_d.nr_replicas;
*disk_sectors_delta -= new->k.p.snapshot == old.k->p.snapshot
    ? sectors * old_d.nr_overwritable : 0;
```
- 权衡：物理账只认 `nr_replicas` 不认 `total`/durability（L904-908 注释：accounting 持久化，
  durability 运行时可调，混用会追溯性欠账）；压缩旧盘只按 `nr_overwritable` 返还，
  不把"没占的空间"退回来——精确但要求调用方理解两套口径。

### `bch2_extent_update` — write.c:1026

- 签名：`int bch2_extent_update(trans, inum, iter, k, k_buf_u64s, disk_res, new_i_size, i_sectors_delta_total, check_enospc, change_cookie, flush)`。
- 参数：`disk_res` 可空（空则只查不补）；`check_enospc` 控制超额时是否硬失败；
  `flush`（dsync 时为 `&op->cl`）决定刷盘责任归属。
- 返回：0 或 btree/空间错误（`transaction_restart` 由上层循环消化）。
- 调用链：`bch2_write_index_default` → 本函数 → `bch2_extent_trim_atomic` +
  `bch2_sum_sector_overwrites` + `bch2_extent_update_i_size_sectors` +
  `bch2_bkey_set_needs_reconcile` + `bch2_trans_update` + `bch2_trans_commit_flush`。
- 片段（超额补预留 + 原子提交）：
```c
if (disk_res &&
    disk_sectors_delta > (s64) disk_res->sectors)
    try(bch2_disk_reservation_add(c, disk_res,
                disk_sectors_delta - disk_res->sectors,
                !check_enospc || !usage_increasing
                ? BCH_DISK_RESERVATION_NOFAIL : 0));
```
- 权衡：非增长覆盖（`usage_increasing=false`）永不 ENOSPC——覆写不该因空间失败；
  trim 切分后 `flush` 职责只归最后一片（L1053-1057），dsync 语义精确不重复刷。

### `bch2_write_index_default` — write.c:1092

- 签名：`static int bch2_write_index_default(struct bch_write_op *op)`，逐 key 前插，返回 0/负错。
- 调用链：`__bch2_write_index`（非 move）→ 本函数 → `bch2_extent_update` 循环。
- 片段：
```c
ret =   bch2_extent_update(trans, inum, &iter, sk.k,
                sk.k->k.u64s + 1 + BCH_REPLICAS_MAX,
                &op->res,
                op->new_i_size, &op->i_sectors_delta,
                op->flags & BCH_WRITE_check_enospc,
                op->opts.change_cookie,
                flush ? &op->cl : NULL);
if (bkey_ge(iter.pos, k->k.p))
    bch2_keylist_pop_front(&op->insert_keys);
else
    bch2_cut_front(c, iter.pos, k);
```
- 权衡：快照号现查现填（L1125），写与快照创建竞态下归属明确；部分提交用 `cut_front`
  收尾，下次接着插——大写不因单次提交量受限而丢失进度。

### `__bch2_write_index` / `bch2_write_index` — write.c:1340/1457

- 签名：`static void __bch2_write_index(struct bch_write_op *op)`；
  `static CLOSURE_CALLBACK(bch2_write_index)`（worker 入口，经 `write_point_do_index_updates` 调度）。
- 调用链：同步写 `__bch2_write` 内联调；异步写 `bch2_write_queue` 入队 →
  `bch2_write_point_do_index_updates`（write.c:1488）→ `bch2_write_index` → `__bch2_write_index`。
- 片段（IO 错降级 + 已写结算）：
```c
if (unlikely(op->io_error)) {
    ret = bch2_write_drop_io_error_ptrs(op);   /* 摘坏盘指针，零副本则报错 */
```
```c
ret = !(op->flags & BCH_WRITE_move)
    ? bch2_write_index_default(op)
    : bch2_data_update_index_update(op);
op->written += sectors_start - keylist_sectors(keys);
```
- 权衡：`PF_MEMALLOC_NOIO` 护体（L1352，回写死锁防护）；坏盘不整单失败，
  摘指针后降级写 + `NEEDS_RECONCILE` 记账（index_default L1117-1121 注释），
  可用性优先、后台补足。

### `bch2_write_data_inline` — write.c:2642

- 签名：`static void bch2_write_data_inline(struct bch_write_op *op, unsigned data_len)`。
- 调用链：`bch2_write` → 本函数（`data_len <= min(block_bytes/2, 1024)` 且开 `inline_data`）。
- 片段：
```c
id = bkey_inline_data_init(op->insert_keys.top);
id->k.p       = op->pos;
id->k.size    = sectors;
memcpy_from_bio(id->v.data, bio, iter);
```
- 权衡：文件尾小尾巴直接塞 btree key，零数据 IO、零开桶；置
  `BCH_WRITE_wrote_data_inline` 使回写完成回调清 `nr_replicas`（buffered.c:447），
  页缓存状态与"无处可读"保持一致。代价：key 膨胀，大量小文件 btree 压力上升。

### `bch2_write_prep_encoded_data` / `bch2_write_op_decode` / `bch2_write_rechecksum` — write.c:1744/1683/1649

- 签名：`prep(op, wp)` 返回 1（整 extent 原样走）/0（需重编码）/负错；
  `decode(op, bio)` 原地解密解压；`rechecksum(c, op, new_csum_type)` 切校验类型并裁剪 bio。
- 调用链：`bch2_write_extent`（move/重编码）→ `prep` → (`decode`|`rechecksum`)。
- 片段（原样快路 + 先验后算）：
```c
if (op->crc.uncompressed_size == op->crc.live_size &&
    op->crc.uncompressed_size <= c->opts.encoded_extent_max >> 9 &&
    op->crc.compressed_size <= wp->sectors_free &&
```
```c
csum = bch2_checksum_bio(c, op->crc.csum_type, nonce, bio);
if (bch2_crc_cmp(op->crc.csum, csum) && !c->opts.no_data_io)
    goto csum_err;
```
- 权衡：整 extent 可原样走时零解压零重算（L1802 `return 1`）；压缩损坏到
  不可解时**保数据原样落盘**（L1828-1844）而非报错——读出仍是旧校验可验，
  损坏不扩散；`rechecksum` 禁止加解密跨域（L1658-1660），加密类型错配宁可保留旧校验。

**可学**：记账精确（双口径）+ journal 协同（`trans_commit_flush`）+ 降级可用优先（摘坏盘/保原样）。

---

## 六、分配落盘：开桶追踪（`fs/data/write.c` 后半）

### `bch2_write` — write.c:2716（`CLOSURE_CALLBACK` 入口）

- 签名：`CLOSURE_CALLBACK(bch2_write)` 即 `void bch2_write(struct work_struct *work)`，
  `closure_type(op, struct bch_write_op, cl)` 取回 op。
- 参数：`op` 需预填 `c/pos/new_i_size/nr_replicas/write_point/target/opts/wbio.bio`；
  `flags` 控制 sync/move/cached/check_enospc 等。
- 返回：无（结果进 `op->error/op->written`，`end_io` 回调交付）。
- 调用链：DIO loop / writepage_do_io / move 路径 → 本函数 → inline/nocow/`__bch2_write`。
- 片段（三道门 + 内联截胡）：
```c
if (unlikely(bio->bi_iter.bi_size & (c->opts.block_size - 1))) {
    op->error = bch_err_throw(c, data_write_misaligned);
```
```c
data_len = min_t(u64, bio->bi_iter.bi_size,
         op->new_i_size - (op->pos.offset << 9));
if (c->opts.inline_data &&
    data_len <= min(block_bytes(c) / 2, 1024U)) {
    bch2_write_data_inline(op, data_len);
```
- 权衡：块不对齐直接判死刑（上游本应裁好），fail-fast 定位责任层；
  `nochanges`/`writes` 双 RO 门（L2749-2758）使只读挂载零落盘。

### `__bch2_write` — write.c:2480（COW 主循环）

- 签名：`static void __bch2_write(struct bch_write_op *op)`。
- 调用链：`bch2_write` → 本函数 → `alloc_request_get`/`bch2_alloc_sectors_req` 开桶 →
  `bch2_write_extent` 编码组装 → `bch2_submit_wbio_replicas` 下发；sync 内联
  `__bch2_write_index`，async 经 `bch2_write_queue` + `continue_at(bch2_write_index)`。
- 片段（分配器背压 + 同步/异步分叉）：
```c
ret = lockrestart_do(trans, ({
    struct alloc_request *req __free(alloc_request_put) =
        alloc_request_get(trans, op->target,
                  op->opts.erasure_code && !(op->flags & BCH_WRITE_cached),
```
```c
if (op->flags & BCH_WRITE_sync) {
    closure_sync(&op->cl);
    __bch2_write_index(op);
    if (!(op->flags & BCH_WRITE_submitted))
        goto again;
    bch2_write_done(op);
} else {
    bch2_write_queue(op, wp);
    continue_at(&op->cl, bch2_write_index, NULL);
```
- 权衡：`operation_blocked` + 同步等待时转 `bch2_wait_on_allocator` 并先做
  `__bch2_write_index`（L2543-2549），已落盘部分先进 btree，不空转；
  `write_point` 按进程哈希隔离（direct.c:457/buffered.c:519），防碎片但小 IO
  有启桶摊销。

### `bch2_write_extent` — write.c:1892

- 签名：`static int bch2_write_extent(op, wp, struct bio **_dst)`，返回 `more`（src 是否还有剩余）。
- 调用链：`__bch2_write` → 本函数 → `bch2_write_bio_alloc`（bounce）→
  `bch2_bio_compress`/`bch2_encrypt_bio`/`bch2_checksum_bio` → `init_append_extent`。
- 片段（bounce 判定 + 输出封顶）：
```c
if (ec_buf ||
    op->compression_opt ||
    (op->csum_type &&
     !(op->flags & BCH_WRITE_pages_stable)) ||
    (bch2_csum_type_is_encryption(op->csum_type) &&
     !(op->flags & BCH_WRITE_pages_owned))) {
    dst = bch2_write_bio_alloc(c, wp, src, &page_alloc_failed, ec_buf);
```
```c
} while (dst->bi_iter.bi_size &&
     src->bi_iter.bi_size &&
     wp->sectors_free &&
     !bch2_keylist_realloc(&op->insert_keys, ... BKEY_EXTENT_U64s_MAX));
```
- 权衡：用户页不稳定（DIO/页缓存皆可被改）时 bounce 复制保校验稳定，
  代价一次 memcpy；直写（`dst==src`）且还有剩余时 `bio_split` 切片（L2088-2096），
  大写自动分页不超 `sectors_free`。

### `bch2_write_bio_alloc` — write.c:1581

- 签名：`static struct bio *bch2_write_bio_alloc(c, wp, src, bool *page_alloc_failed, void *buf)`。
- 片段：
```c
unsigned output_available =
    min(wp->sectors_free << 9, src->bi_iter.bi_size);
output_available = min(output_available, BIO_MAX_VECS * PAGE_SIZE);
```
```c
bch2_bio_alloc_pages(bio, c->opts.block_size,
             output_available, GFP_NOIO|__GFP_SKIP_ZERO);
unsigned required = min(output_available, c->opts.encoded_extent_max);
if (unlikely(bio->bi_iter.bi_size < required))
    __bch2_bio_alloc_pages_pool(c, bio, ...);   /* mempool 兜底 */
```
- 权衡：`__GFP_SKIP_ZERO` 跳过清零（L1635-1638 注释：直通数据无需保密清零，省 CPU）；
  超出 budge 部分先用 mempool 保证 `encoded_extent_max` 内必有页， producers 不饿死。

### `bch2_submit_wbio_replicas` — write.c:1193

- 签名：`void bch2_submit_wbio_replicas(struct bch_write_bio *wbio, c, enum bch_data_type type, const struct bkey_i *k, bool nocow, struct bch_dev **cas)`。
- 参数：`cas` 仅 nocow 传（ioref 已取，本函数只接管）；COW 传 NULL 现场取。
- 片段（每副本 clone + 最后一副本复用原 bio）：
```c
if (ptr != last) {
    n = to_wbio(bio_alloc_clone(NULL, &wbio->bio, GFP_NOIO, &c->replica_set));
    n->parent = wbio; n->split = true; ... bio_inc_remaining(&wbio->bio);
} else {
    n = wbio; n->split = false;
}
n->bio.bi_iter.bi_sector = ptr->offset;
if (likely(n->ca)) { ... submit_bio(&n->bio); }
else { n->bio.bi_status = BLK_STS_REMOVED; bio_endio(&n->bio); }
```
- 权衡：clone 开销换各副本独立 `bi_sector`/dev/complete；掉线盘直接 `REMOVED` endio，
  错误汇总到 `op->wbio.failed` 走降级而非整单重试。

### `bch2_write_endio` — write.c:1514

- 签名：`static void bch2_write_endio(struct bio *bio)`（`bi_end_io`）。
- 片段：
```c
if (unlikely(bio->bi_status)) {
    guard(spinlock_irqsave)(&c->write_error_lock);
    bch2_dev_io_failures_mut(&op->wbio.failed, wbio->dev)->errcode =
        __bch2_err_throw(c, -blk_status_to_bch_err(bio->bi_status));
```
```c
if (wbio->bounce)
    bch2_bio_free_pages_pool(c, bio);
if (parent)
    bio_endio(&parent->bio);
else
    closure_put(cl);
```
- 权衡：错误只记表不立刻判（`io_error=true` 延后到 index 阶段统一降级）；
  bounce 页在 endio 即释，内存周转最短；父子 bio 引用计数配对，防 use-after-free。

### `bch2_nocow_write` — write.c:2285（含 `bch2_extent_is_writeable` 2111、`bkey_get_dev_iorefs` 2249）

- 签名：`static bool bch2_nocow_write(struct bch_write_op *op)`，true=已接管（成功或已提交），false=回落 COW。
- 准入：`opts.nocow && nocow_enabled`（2481）、非 move、快照一致、extent 纯净
  （`crc_is_encoded||has_ec` 即拒，2111）、副本数达标、块对齐。
- 片段（先拿 ioref 再放 btree 锁 + stale 校验）：
```c
ptrs = bch2_bkey_ptrs_c(k);
nr_cas = bkey_get_dev_iorefs(c, ptrs, cas);   /* dev 移除竞态下只走 cas[] 回滚 */
bch2_trans_unlock(trans);
bch2_bkey_nocow_lock(c, trans, ptrs, cas, BUCKET_NOCOW_LOCK_UPDATE);
```
```c
int gen = bucket_gen_get(ca, PTR_BUCKET_NR(ca, ptr));
stale = gen < 0 ? gen : gen_after(gen, ptr->generation);
```
- 权衡：原地覆写零分配零读改写，VM/DB 负载写放大最小；代价 per-bucket nocow 锁
  与 move 路径互斥，高并发同桶排队（`nocow_lock_contended` 可观测）；无校验无加密，
  坏块不自愈——把完整性责任交还应用。stale pointer 采"报错重试 vs 报不一致"二分
  （2456-2477），可恢复的走 `transaction_restart` 回 COW。

### `bch2_write_done` / `__bch2_write_done` — write.c:1302/1278；`bch2_write_queue` / `bch2_write_point_do_index_updates` — write.c:1477/1488

- 签名：`static void bch2_write_done(op)`；`CLOSURE_CALLBACK(__bch2_write_done)`；
  `void bch2_write_point_do_index_updates(struct work_struct *work)`。
- 片段：
```c
if (op->flags & BCH_WRITE_sync)
    closure_sync(&op->cl);
continue_at(&op->cl, __bch2_write_done, ...);
```
```c
if (!op->error)
    op->error = bch2_journal_error(&op->c->journal);
bch2_time_stats_update(&c->times[BCH_TIME_data_write], op->start_time);
bch2_disk_reservation_put(c, &op->res);
```
- 权衡：完工即算 `data_write` 端到端延时（可观测）；journal 错误在收尾统一污染
  `op->error`——数据落盘但 journal 坏了也算写失败，fsync 语义不撒谎；index 更新
  按 write_point 串行 worker 化，同桶 key 顺序提交，btree 合并友好。

**可学**：失败染色隔离（`bch2_open_bucket_write_error` write.c:1405，坏桶禁 EC 化）、
水位联动（journal/开桶双背压）、开桶追踪（同 write_point 顺序 index）。

---

## 七、设计启示

1. **分段降级**：对齐→DIO/缓冲、nocow→COW、足额→降级+reconcile，每段独立失败语义。
2. **预留先行**：差额预留（`sectors_to_reserve`）+ 脏化过户，ENOSPC 拦在 admission 不拦回写。
3. **免读快路**：整页覆写/尾部追加/已分配复用三条快路，读放大量化最小。
4. **聚合节流**：连续批 + `BIO_MAX_VECS` 封顶 + 双水位背压，吞吐与内存/ journal 平衡。
5. **对齐快检**：DIO 门槛前置 + 块尾裁剪 + 已分配快检，覆盖写零新空间。
6. **记账精确**：逻辑/物理双口径 + 快照感知 + 非增长覆写免 ENOSPC。
7. **染色隔离**：坏桶写错染色、坏盘摘指针、损坏压缩保原样，错误不扩散、可观测（`write_op_error` write.c:1174、`data_write` 时延）。

---

## 复核途径

- `rg -n "bch2_write_begin|bch2_write_end|__bch2_buffered_write|bch2_writepages|__bch2_writepage" fs/vfs/buffered.c` 看缓冲写（723/815/876/693/561）。
- `rg -n "bch2_direct_write|bch2_dio_write_loop|bch2_check_range_allocated" fs/vfs/direct.c` 看直通写（540/391/241）。
- `rg -n "bch2_folio_set|bch2_folio_reservation_get|bch2_set_folio_dirty|bch2_page_mkwrite" fs/vfs/pagecache.c` 看预留（189/552/596/718）。
- `rg -n "bch2_write$|__bch2_write|bch2_write_extent|bch2_extent_update|bch2_nocow_write|bch2_submit_wbio_replicas" fs/data/write.c` 看组装落盘（2716/2480/1892/1026/2285/1193）。
