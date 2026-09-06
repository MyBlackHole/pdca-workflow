# btree 搜索读路径专题学习报告（T0524 代码级精讲版）

> 精读 `fs/btree/iter.c`（遍历预取）、`bset.c`（辅助树）、`read.c`（校验）；
> 6 个搜索相关本体节点为辅。事实源为源码，行号函数名经 Grep/Read 核实。
> 六节结构保留，每节逐函数精讲：签名 / 参数 / 返回 / 调用链 / ≤10 行代码片段 / 权衡。

---

## 一、全景：三级搜索

搜索分三级：树遍历定位叶（traverse）、节点内 bset 查找（search）、
读合并（overlay/journal）。每级独立优化，互不假设。

### 1.1 `bch2_btree_path_traverse`（`fs/btree/locking.h:163`）

- 签名：`static inline int bch2_btree_path_traverse(struct btree_trans *trans, btree_path_idx_t path, enum btree_iter_update_trigger_flags flags)`
- 参数：`trans` 事务；`path` 路径下标；`flags` 触发器标志。
- 返回：`int`，0 表路径已是最新，`<0` 表需 restart/错误。
- 调用链：`bch2_btree_iter_traverse（iter.c:2266）/ __bch2_btree_iter_peek（iter.c:2541）/ peek_slot（iter.c:3200）→ 本函数 → bch2_btree_path_traverse_one（iter.c:1403）`。
- 代码片段（`locking.h:169-171`）：
```c
return !trans->paths[path].nodes_locked
    ? bch2_btree_path_traverse_one(trans, path, flags)
    : 0;
```
- 权衡：已加锁路径零开销短路，避免重复下钻；代价是调用方必须先保证 `should_be_locked` 语义，否则静默跳过会读到过期节点（由 `traverse_one:1427` 的 `should_be_locked → restart` 兜底）。

### 1.2 `bch2_btree_path_traverse_one`（`fs/btree/iter.c:1403`）

- 签名：`int bch2_btree_path_traverse_one(struct btree_trans *trans, btree_path_idx_t path_idx, enum btree_iter_update_trigger_flags flags)`
- 参数：同上，`flags` 透传给 `btree_path_down` 的更新触发器。
- 返回：0 成功；1 表该层无节点（btree 到头）；`<0` 错误/restart。
- 调用链：`traverse → traverse_one → btree_path_up_until_good_node（:1442）→ 循环 btree_path_down / btree_path_lock_root（:1454-1457）`。
- 代码片段（`iter.c:1442-1457`）：
```c
path->level = btree_path_up_until_good_node(trans, path, 0);
unsigned max_level = path->level;
while (path->level > depth_want) {
    ret = btree_path_node(path, path->level)
        ? btree_path_down(trans, path, flags)
        : btree_path_lock_root(trans, path, depth_want);
```
- 权衡：先向上找可信锚点再逐层下钻，天然容忍并发分裂/合并导致的指针失效；代价是每次 traverse 都可能走完整 `relock + up + down`，故热路径依赖 `locking.h:169` 的短路和下节预取摊销。

### 1.3 `bch2_btree_node_iter_init`（`fs/btree/bset.c:1474`）——节点内搜索总入口

- 签名：`void bch2_btree_node_iter_init(struct bch_fs *c, struct btree *b, struct btree_node_iter *iter, struct bpos *search)`
- 参数：`c` fs；`b` 已锁定的 btree 节点；`iter` 输出的多 bset 归并迭代器；`search` 搜索键。
- 返回：无（结果写入 `iter->data[]` 并排序）。
- 调用链：`traverse 下钻每层 __btree_path_level_init（iter.c:781）→ 本函数 → __bch2_bset_search（bset.c:1503）+ bch2_bset_search_linear（:1511）→ iter_sort（:1520）`。
- 代码片段（`bset.c:1502-1505`）：
```c
for (i = 0; i < b->nsets; i++) {
    k[i] = __bch2_bset_search(b, b->set + i, search, &p.k);
    prefetch_four_cachelines(k[i]);
}
```
- 权衡：两阶段（粗定位 cacheline → 细线性扫描）把变长键的二分退化为定长辅助树查找 + 短线性扫描；代价是构造 `iter->data` 需对 `MAX_BSETS` 个 bset 各查一次，小节点上不如直接线性（由 `BSET_NO_AUX_TREE` 分支兜底）。

### 1.4 `bch2_btree_and_journal_iter_peek`（`fs/btree/journal_overlay.c:612`）——读合并

- 签名：`struct bkey_s_c bch2_btree_and_journal_iter_peek(struct bch_fs *c, struct btree_and_journal_iter *iter)`
- 参数：`c` fs；`iter` 内含 btree 侧 + journal 侧双迭代器及 `prefetch/fail_if_too_many_whiteouts` 标志。
- 返回：`struct bkey_s_c`，归并后较小者（journal 优先当 `bpos_le(journal, btree)`）。
- 调用链：`__bch2_btree_iter_peek:2582 btree_trans_peek_journal → 本函数 → bch2_journal_iter_peek_btree / bch2_journal_iter_peek（:628-635）`。
- 代码片段（`journal_overlay.c:637-639`）：
```c
ret = journal_k.k &&
    (!btree_k.k || bpos_le(journal_k.k->p, btree_k.k->p))
    ? journal_k
```
- 权衡：读时归并保证“journal 覆盖 btree”的可见性而不必先刷盘；代价是每次 peek 都要推进两个迭代器并比较，故 `prefetch:617-618` 只在 `iter->prefetch && journal.level` 时触发下节的批量预取。

**可学**：分级搜索，每级可独立替换；级间只用 `bkey_s_c + search_key` 契约耦合。

---

## 二、遍历：定位加预取

`traverse` 设位加逐层下钻；预取按层级定量：启动后叶层 2 个、恢复期 16 个，高层不预取；journal 归并版另起迭代器；根数组逐项 CPU 预取。

### 2.1 `btree_path_prefetch`（`fs/btree/iter.c:995`）

- 签名：`static int btree_path_prefetch(struct btree_trans *trans, struct btree_path *path)`
- 参数：`trans`；`path` 当前已锁定到 `path->level` 的路径。
- 返回：0（预取失败只影响性能不报错，`try()` 内错误向上传 restart）。
- 调用链：`traverse 下钻命中 interior 层 → 本函数 → bch2_btree_node_iter_advance + peek（:1010-1011）→ bch2_btree_node_prefetch（cache.c:1525）（:1016）`。
- 代码片段（`iter.c:1000-1002`）：
```c
unsigned nr = test_bit(BCH_FS_started, &c->flags)
    ? (path->level > 1 ? 0 :  2)
    : (path->level > 1 ? 1 : 16);
```
- 片段 2（`iter.c:1007-1017`）：
```c
while (nr--) {
    BUG_ON(!btree_node_locked(path, path->level));
    bch2_btree_node_iter_advance(&node_iter, l->b);
    struct bkey_packed *k = bch2_btree_node_iter_peek(&node_iter, l->b);
    if (!k) break;
    bch2_bkey_buf_unpack(&tmp, l->b, k);
    try(bch2_btree_node_prefetch(trans, path, tmp.k, ...));
}
```
- 权衡：高层（`level>1`）正常运行时 `nr=0` 不预取——扇出大、命中率低、预取即污染缓存；恢复期（`!started`）叶父层一次 16 个，用启动延迟换缺页风暴摊销。`noinline __cold` 标明非热路径，不膨胀 traverse 的 I-cache。

### 2.2 `btree_path_prefetch_j`（`fs/btree/iter.c:1023`）

- 签名：`static int btree_path_prefetch_j(struct btree_trans *trans, struct btree_path *path, struct btree_and_journal_iter *jiter)`
- 参数：多出 `jiter`——已定位到当前键的 btree+journal 归并迭代器。
- 返回：`int`，`bch2_btree_node_prefetch` 的错误码（`ret` 累积）。
- 调用链：`journal 模式 traverse → 本函数 → bch2_btree_and_journal_iter_advance + peek（:1043-1044）→ prefetch（:1049）`。
- 代码片段（`iter.c:1039-1051`）：
```c
while (nr-- && !ret) {
    if (!bch2_btree_node_relock(trans, path, path->level))
        break;
    bch2_btree_and_journal_iter_advance(jiter);
    k = bch2_btree_and_journal_iter_peek(c, jiter);
    if (!k.k) break;
    bch2_bkey_buf_reassemble(&tmp, k);
    ret = bch2_btree_node_prefetch(trans, path, tmp.k, ...);
}
```
- 权衡：与 2.1 共用 `nr` 定量表（:1028-1030），但每次迭代先 `relock` 再推进——journal 归并迭代器无节点锁保护，锁丢即停（`break`），宁可少预取也不读野指针；结束时 `if (!was_locked) unlock（:1053-1054）` 恢复进入时的锁状态，对调用方透明。

### 2.3 `bch2_btree_node_prefetch`（`fs/btree/cache.c:1525`）

- 签名：`int bch2_btree_node_prefetch(struct btree_trans *trans, struct btree_path *path, const struct bkey_i *k, enum btree_id btree_id, unsigned level)`
- 参数：`k` 子节点指针键；`btree_id/level` 期望位置；`path` 可为 NULL（journal 路径传 NULL）。
- 返回：恒 0（已缓存或发起异步 fill 后即返，`errptr_try` 失败也吞掉）。
- 调用链：`2.1/2.2/journal_overlay.c:608 → 本函数 → btree_cache_find（:1536, 命中即返）→ bch2_btree_node_fill（:1540, SIX_LOCK_read, 不等待）→ unlock_read（:1543）`。
- 代码片段（`cache.c:1536-1544`）：
```c
struct btree *b = btree_cache_find(bc, k);
if (b) return 0;
b = errptr_try(bch2_btree_node_fill(trans, path, k, btree_id,
                    level, SIX_LOCK_read, false));
if (b) six_unlock_read(&b->c.lock);
return 0;
```
- 权衡：纯 hint 语义——从不阻塞、不报错，调用方无需处理返回值分支；`BUG_ON(path && !locked(:1533))` 把“预取时父锁必须持有”变成契约，防止预取了已被回收的指针。fill 用读锁且立即释放，靠缓存留住节点给真正的 traverse 命中。

### 2.4 `btree_and_journal_iter_prefetch`（`fs/btree/journal_overlay.c:586`）

- 签名：`static void btree_and_journal_iter_prefetch(struct btree_and_journal_iter *_iter)`（值拷贝 `iter = *_iter` 后推进副本，不动原迭代器）。
- 参数：仅迭代器快照；`nr` 按 `journal.level` 查同一张定量表（`level>1 ? 0 : 2 / 1 : 16`，`:591-593`）。
- 返回：无。
- 调用链：`bch2_btree_and_journal_iter_peek:617（prefetch && journal.level）→ 本函数 → advance + peek（:602-603）→ bch2_btree_node_prefetch（:608，path=NULL）`。
- 代码片段（`journal_overlay.c:595-608`）：
```c
iter.prefetch = false;
iter.fail_if_too_many_whiteouts = true;
while (nr--) {
    bch2_btree_and_journal_iter_advance(&iter);
    struct bkey_s_c k = bch2_btree_and_journal_iter_peek(c, &iter);
    if (!k.k) break;
    bch2_bkey_buf_reassemble(&tmp, k);
    bch2_btree_node_prefetch(iter.trans, NULL, tmp.k, ...);
}
```
- 权衡：副本推进实现“偷看未来 N 个键并预取”而不污染当前读位置；`prefetch=false` 防递归（peek 里再调 prefetch），`fail_if_too_many_whiteouts=true` 让预取在 whiteout 链过长（>20，见 `:625`）时早停——预取路径不值得为删除链烧 CPU。

### 2.5 `__bch2_trans_get` 根预取（`fs/btree/iter.c:3949`，循环体 `:3969-3970`）

- 签名：`struct btree_trans *__bch2_trans_get(struct bch_fs *c, unsigned fn_idx)`
- 参数：`c` fs；`fn_idx` 事务类型下标（统计/内存预算用）。
- 返回：初始化好的 `trans`（含 srcu 锁、mem 预算、path 表）。
- 调用链：任意 btree 事务入口 → 本函数 → `prefetch(roots_b[])` → 后续首次 `traverse → lock_root` 命中 L1。
- 代码片段（`iter.c:3969-3970`）：
```c
for (unsigned i = 0; i < sizeof(c->btree.cache.roots_b); i += 64)
    prefetch((const char *) c->btree.cache.roots_b + i);
```
- 权衡：注释（:3962-3967）明说冷线 miss 占 `lock_root` 约 3-7% cycles，用 trans setup 期间的内存级并行掩盖它；步长 64B 逐缓存行全覆盖 roots 数组——数组小（常驻），预取成本固定且可预测。

### 2.6 `__btree_path_level_init` / `bch2_btree_path_level_init`（`fs/btree/iter.c:775/791`）

- 签名：`void bch2_btree_path_level_init(struct btree_trans *trans, struct btree_path *path, unsigned level, struct btree *b)`
- 参数：`path/level/b`——把该层绑定到节点 `b` 并记录 `lock_seq`。
- 返回：无。
- 调用链：`traverse 每下钻一层 / trans_node_add（:858）→ 本函数 → bch2_btree_node_iter_init（:781）→ interior 层顺手 peek 跳过 whiteout（:787-788）`。
- 代码片段（`iter.c:799-802`）：
```c
path->l[level].lock_seq = six_lock_seq(&b->c.lock);
WRITE_ONCE(path->l[level].b, b);
__btree_path_level_init(trans, path, level);
```
- 权衡：`lock_seq` 快照 + `WRITE_ONCE` 发布指针，让 deadlock 检测器可无锁读；interior 层初始化即 `peek` 跳 whiteout，保证上层迭代器恒指有效子指针，代价是每次 split/replace 都要重建该层迭代器（`bch2_trans_node_add` 循环）。

**可学**：预取量按阶段调；高层不预取（扇出大命中低）；hint 式预取永不阻塞调用方。

---

## 三、节点内：Eytzinger 加浮点压缩

bset 内二分改堆式布局，子相邻可预取；`BSET_CACHELINE=256B` 配一 4 字节浮点索引，失败回退真键；RO 建树，RW 扁平懒更新。

### 3.1 数据结构：`struct bkey_float`（`fs/btree/bset.c:407`）+ `BSET_CACHELINE`（`fs/btree/bset.h:191`）

- 定义：`struct bkey_float { u8 exponent; u8 key_offset; u16 mantissa; }`（4B）；`#define BSET_CACHELINE 256`；`#define BKEY_MANTISSA_BITS 16（bset.c:412）`。
- 调用链：`__build_ro_aux_tree（:836）→ make_bfloat（:882）填充 f[]；bset_search_tree（:1266）读取 f[] 比较`。
- 代码片段（`bset.c:407-411`）：
```c
struct bkey_float {
    u8      exponent;
    u8      key_offset;
    u16     mantissa;
};
```
- 权衡：4B 定长节点 = L1 友好 + 一次 prefetch 带多个树节点（见 3.5 的 `n<<4` 预取）；`bset.h:132-135` 算过账：每 128B 数据配 4B 索引约 3% 内存开销（现 `BSET_CACHELINE=256` 则约 1.5%）。注释（`bset.h:176-188`）说明 256B 是有意大于硬件 64B 行：树上少碰一行，换线性尾扫多碰一行，而尾扫常提前结束，期望更优。

### 3.2 `make_bfloat`（`fs/btree/bset.c:727`）

- 签名：`static __always_inline void make_bfloat(struct btree *b, struct bset_tree *t, unsigned j, struct bkey_packed *min_key, struct bkey_packed *max_key)`
- 参数：`j` eytzinger 下标；`min/max_key` 该子树键范围边界（2 的幂处用边界代替缺失邻居，`:734-739`）。
- 返回：无（写入 `bkey_float(b,t,j)`）。
- 调用链：`__build_ro_aux_tree:881 eytzinger1_for_each → 本函数 → bch2_bkey_greatest_differing_bit（:764）求 l/r 首异位 → exponent/mantissa`。
- 代码片段（`bset.c:764-766`）：
```c
high_bit = max(bch2_bkey_greatest_differing_bit(b, l, r),
           min_t(unsigned, BKEY_MANTISSA_BITS, b->nr_key_bits) - 1);
exponent = high_bit - (BKEY_MANTISSA_BITS - 1);
```
- 片段 2（`:789-796` 回退与钳位）：
```c
 * legal for the bfloat to compare larger than the original key, but not smaller:
 */
if (exponent < 0)
    mantissa |= ~(~0U << -exponent);
f->mantissa = mantissa;
```
- 权衡：只存“区分当前区间 `[l,r)` 所必需的高位 + 区分 `m/p` 所必需的低位”（`bset.c:52-72` DOC），160 位键常压到 16 位；构造失败（空键/`nr_key_bits=0`）置 `BFLOAT_FAILED_UNPACKED（:750）`，查询回退真键。只允许偏大不允许偏小——偏大最多多走一步线性扫描，偏小会漏键。

### 3.3 `bset_search_tree`（`fs/btree/bset.c:1266`）——RO 快路径

- 签名：`static struct bkey_packed *bset_search_tree(const struct btree *b, const struct bset_tree *t, const struct bpos *search, const struct bkey_packed *packed_search)`
- 参数：`search` 未压缩位点；`packed_search` lossy 打包后的搜索键（与 bfloat 同坐标系可比）。
- 返回：首个 `>= search` 的候选键所在 cacheline 内某键（调用方再线性精调）。
- 调用链：`__bch2_bset_search:1343 → 本函数 → bkey_mantissa（:1282）比较 / tree_to_bkey + bkey_cmp_p_or_unp 回退（:1290-1291）`。
- 代码片段（`bset.c:1275-1286`）：
```c
do {
    if (likely(n << 4 < t->size))
        prefetch(&base->f[n << 4]);
    f = &base->f[n];
    if (likely(f->exponent < BFLOAT_FAILED)) {
        unsigned l = f->mantissa;
        unsigned r = bkey_mantissa(packed_search, f);
        if (likely(l != r) || !bkey_mantissa_bits_dropped(b, f)) {
            n = n * 2 + (l < r);
            continue;
        }
    }
```
- 权衡：堆式布局使 `n` 的子节点 `2n/2n+1` 在内存相邻，`n<<4`（提前 4 层、16 个节点）预取正好覆盖一条缓存行内的未来路径——这是放弃普通二分的核心收益；`__flatten` 强制内联展开，指令级并行掩盖访存延迟。`exponent==BFLOAT_FAILED` 或精度丢失时回退真键比较，保证正确性不依赖压缩成功率（`bset.h:119-125`：失败 <1% 即可赢）。

### 3.4 `bset_search_write_set`（`fs/btree/bset.c:1216`）——RW 慢路径

- 签名：`static struct bkey_packed *bset_search_write_set(const struct btree *b, struct bset_tree *t, struct bpos *search)`
- 参数：`t` 当前可写 bset 的扁平 `rw_aux_tree`（`{u16 offset; struct bpos k}` 数组）。
- 返回：首个 `>= search` 的 cacheline 首键。
- 调用链：`__bch2_bset_search:1341（BSET_RW_AUX_TREE 分支）→ 本函数 → rw_aux_to_bkey（:1231）`。
- 代码片段（`bset.c:1220-1231`）：
```c
unsigned l = 0, r = t->size;
while (l + 1 != r) {
    unsigned m = (l + r) >> 1;
    if (bpos_lt(rw_aux_tree(b, t)[m].k, *search))
        l = m;
    else r = m;
}
return rw_aux_to_bkey(b, t, l);
```
- 权衡：在写 bset 上维护完整 eytzinger 树太贵（每次插入重建），退化为“每 L1 行记一个 `(offset, bpos)`”的扁平二分 + 懒更新（`__bch2_bset_fix_lookup_table:1061` 插入时只移位/递增 offset，整行溢出才重找行首 `rw_aux_tree_insert_entry:1029`）；读性能让位于写性能，因为写 bset 通常最小、最热。

### 3.5 `__bch2_bset_search` 分发 + `prefetch_four_cachelines`（`fs/btree/bset.c:1316/1234`）

- 签名：`static struct bkey_packed *__bch2_bset_search(struct btree *b, struct bset_tree *t, struct bpos *search, const struct bkey_packed *lossy_packed_search)`；`static inline void prefetch_four_cachelines(void *p)`。
- 参数/返回：按 `bset_aux_tree_type(t)` 三选一：`NO → btree_bkey_first（:1339）；RW → 3.4；RO → 3.3`。
- 调用链：`bch2_btree_node_iter_init:1503 → 本函数 → init 紧接着 prefetch_four_cachelines(k[i])（:1504）`。
- 代码片段（`bset.c:1337-1344`）：
```c
switch (bset_aux_tree_type(t)) {
case BSET_NO_AUX_TREE: return btree_bkey_first(b, t);
case BSET_RW_AUX_TREE: return bset_search_write_set(b, t, search);
case BSET_RO_AUX_TREE: return bset_search_tree(b, t, search, lossy_packed_search);
default: BUG();
}
```
- 片段 2（`:1236-1242` x86 版）：
```c
asm("prefetcht0 (-127 + 64 * 0)(%0);"
    "prefetcht0 (-127 + 64 * 1)(%0);"
    "prefetcht0 (-127 + 64 * 3)(%0);" : : "r" (p + 127));
```
- 权衡：粗定位结果一出来立刻预取其后 4 行（256B = 一整个 `BSET_CACHELINE`），与紧随的 `bch2_bset_search_linear` 线性尾扫形成“生产-消费”流水线；x86 用单条 asm 一次发 4 个 `prefetcht0`，省 3 次调用开销。`__always_inline __flatten` 让三路分发在编译期摊薄，分支预测器只记“RO”热路。

### 3.6 `bch2_bset_search_linear`（`fs/btree/bset.c:1350`）+ 构造对 `__build_ro/rw_aux_tree`（`:836/:817`）、`bch2_bset_build_aux_tree`（`:903`）

- 签名：`bch2_bset_search_linear(struct btree *b, struct bset_tree *t, struct bpos *search, struct bkey_packed *packed_search, const struct bkey_packed *lossy_packed_search, struct bkey_packed *m)`；构造：`void bch2_bset_build_aux_tree(struct btree *b, struct bset_tree *t, bool writeable)`。
- 参数/返回：`m` 粗定位起点，线性走到首个 `>=`；构造按 `writeable` 二选一，`size<2` 退化为 `BSET_NO_AUX_TREE（:845-849）`。
- 调用链：`init:1511 线性精调；build ← read_done:882（读盘重建）/ sort.c:439（排序后重建）`。
- 代码片段（`bset.c:1357-1361`）：
```c
if (lossy_packed_search)
    while (m != btree_bkey_last(b, t) &&
           bkey_iter_cmp_p_or_unp(b, m, lossy_packed_search, search) < 0)
        m = bkey_p_next(m);
```
- 片段 2（`:903-919`）：
```c
void bch2_bset_build_aux_tree(struct btree *b, struct bset_tree *t, bool writeable)
{
    if (writeable ? bset_has_rw_aux_tree(t) : bset_has_ro_aux_tree(t))
        return;
    bset_alloc_tree(b, t);
    if (!__bset_tree_capacity(b, t)) return;
    if (writeable) __build_rw_aux_tree(b, t);
    else __build_ro_aux_tree(b, t);
```
- 权衡：线性段上限为 `BSET_CACHELINE` 字节，可预测、可预取；构造是“中等昂贵”（`bset.h:137`）但只发生在 bset 落盘/重排后，读放大换写时零维护。`size<2` 直接放弃建树——小 bset 线性更快，省内存也省分支。

**可学**：节点内搜索是独立优化域；压缩索引必有回退；读写 bset 用不同索引结构。

---

## 四、peek 语义家族

peek 不推进、max 加止、prev 反向、slot 合成空洞、root 直读；快照过滤缓存写位；journal 叠加归并读。

### 4.1 `__bch2_btree_iter_peek`（`fs/btree/iter.c:2541`）——全家底座

- 签名：`static struct bkey_s_c __bch2_btree_iter_peek(struct btree_iter *iter, struct bpos *search_key, const struct bpos *end)`
- 参数：`search_key` 可推进的游标（whiteout/跨叶时前移）；`end` 叶内终止水位。
- 返回：首个可见键；`bkey_s_c_null` 表到头；`bkey_s_c_err(ret)` 表 restart/错误。
- 调用链：`peek_max:2783 循环驱动 → 本函数内 set_pos + traverse（:2552-2556）→ level_peek_all（:2576）→ key_cache / journal / trans_updates 三层叠加（:2578-2587）→ whiteout 跳键（:2590-2602）/ 跨叶推进（:2606-2609）`。
- 代码片段（`iter.c:2589-2602`）：
```c
if (likely(k.k)) {
    if (!bkey_deleted(k.k)) break;
    *search_key = !bpos_eq(*search_key, k.k->p)
        ? k.k->p
        : bpos_successor(k.k->p);
```
- 权衡：叠加顺序（btree → key_cache → journal → trans_updates）即优先级倒序，后者覆盖前者，保证“事务内写入立即可见”；whiteout 不直接跳过而是把 `search_key` 先对齐到 whiteout 自身（deleted 键排在同位 live 键之前），防止漏掉同位的 btree whiteout 后的真键。循环收敛性靠 `search_key` 严格单调递增保证。

### 4.2 `bch2_btree_iter_peek_max`（`fs/btree/iter.c:2758`）+ `peek`（`fs/btree/iter.h:534`）

- 签名：`struct bkey_s_c bch2_btree_iter_peek_max(struct btree_iter *iter, const struct bpos *end)`；`peek(iter) = peek_max(iter, &SPOS_MAX)`。
- 参数：`end` 上界（含 snapshot/extent 语义的三种比较，`:2821-2823`）。
- 返回：`[pos, end]` 内首键；越界/到头返回 null 并把 `iter->pos` 设为 `*end（:2853）`。
- 调用链：`用户 → peek_max → __bch2_btree_iter_peek（:2783）→ snapshot 过滤器 btree_iter_filter_snapshots（:2793）→ 落点 set_pos + relock update_path（:2826-2838）`。
- 代码片段（`iter.c:2813-2816`）：
```c
if (!(iter->flags & BTREE_ITER_is_extents))
    iter->pos = k.k->p;
else
    iter->pos = bkey_max(iter->pos, bkey_start_pos(k.k));
```
- 权衡：peek 不推进、只同步 `iter->pos` 到返回键（extent 取 `max` 防回退），调用方用 `advance/next（:2865-2869）` 显式步进——“看”与“走”分离使重试语义简单（restart 后重 peek 即得同一键）。代价是连续扫描必须 peek+advance 交替， случаев用 `next_slot` 合并。

### 4.3 `bch2_btree_iter_peek_prev_min`（`fs/btree/iter.c:2994`）+ `peek_prev`（`fs/btree/iter.h:541`）

- 签名：`struct bkey_s_c bch2_btree_iter_peek_prev_min(struct btree_iter *iter, struct bpos end)`；`peek_prev = peek_prev_min(iter, POS_MIN)`。
- 参数：`end` 下界；`iter->pos` 为上界。
- 返回：`[end, pos]` 内末键。
- 调用链：`extent/snapshot 模式先经 peek_slot 试探（:3009，同函数内）→ __bch2_btree_iter_peek_prev 循环（:3035）→ snapshot 候选 saved_path 回填（:3049-3054）`。
- 代码片段（`iter.c:3009-3016`）：
```c
struct bkey_s_c k = bch2_btree_iter_peek_slot(iter);
if (bkey_err(k)) return k;
if (!bkey_deleted(k.k) &&
    (!(iter->flags & BTREE_ITER_is_extents) ||
     bkey_lt(bkey_start_pos(k.k), iter->pos)))
    return k;
```
- 权衡：extent 反向不能直接倒查（`bkey_start_pos` 非单调），先正向 `peek_slot` 定位覆盖当前 `pos` 的 extent，快路命中即返；注释（`:2946-2956`）坦承反向路径的 `path->pos` 与上层节点可能不一致（只靠 debug 的 `bch2_btree_iter_verify` 兜底），是已知技术债——反向读正确但路径缓存弱于正向。

### 4.4 `bch2_btree_iter_peek_slot`（`fs/btree/iter.c:3166`）——精确位置语义

- 签名：`struct bkey_s_c bch2_btree_iter_peek_slot(struct btree_iter *iter)`
- 参数：仅 `iter`（`iter->pos` 即槽位）。
- 返回：该槽位的键或按 extent/whiteout 规则合成的空洞（deleted/whiteout 转 `KEY_TYPE_deleted`，`:3248/:3287`）。
- 调用链：`set_pos + traverse（:3196-3204）→ bch2_btree_path_peek_slot（:3226）→ key_cache（:3228）→ journal（:3232）→ trans_updates（:3240）；extent+snapshot 分支改走 peek_max 循环（:3262）`。
- 代码片段（`iter.c:3216-3226`）：
```c
 * Consult sources in the same order as bch2_btree_iter_peek_max():
 * btree, then key cache, then journal, then the transaction's own
 * updates - each overlaying the last, so an in-transaction update wins.
 */
k = bch2_btree_path_peek_slot(btree_iter_path(trans, iter), &iter->k);
```
- 权衡：注释点出关键顺序依赖——key_cache 必须在 trans_updates 之前 peek，否则同事务内二次更新同一缓存键会跳过 cache 建 `key_cache_path`，在 `bch2_trans_update_get_key_cache` 处活锁。extent 分支用 `iter2` 拷贝 + `nofilter_whiteouts` 循环跳 whiteout（`:3258-3272`），用一次额外 traverse 换统一的正向语义。

### 4.5 `bch2_btree_iter_peek_node`（`fs/btree/iter.c:2286`）+ `advance/rewind`（`:2317/:2331`）+ `traverse`（`:2266`）

- 签名：`struct btree *bch2_btree_iter_peek_node(struct btree_iter *iter)`；`bool advance/rewind(struct btree_iter *iter)`；`int bch2_btree_iter_traverse(struct btree_iter *iter)`。
- 参数/返回：`peek_node` 返回叶节点指针（错则 `ERR_PTR`）；`advance` 把 `pos` 移到 `bkey_successor(pos)（:2325）`；`traverse` 做 `set_pos + traverse（:2273-2278）`。
- 调用链：`peek_node → traverse（:2293）→ 取 path_l->b（:2296）→ pos 回绕到 min_key（:2302）`。
- 代码片段（`iter.c:2301-2306`）：
```c
bkey_init(&iter->k);
iter->k.p = iter->pos = b->data->min_key;
iter->path = bch2_btree_path_set_pos(trans, iter->path, &b->key.k.p, ...);
```
- 权衡：`peek_node` 是整节点扫描/调试的专用入口，一次定位后调用方在节点内自驱，避免逐键 traverse 的锁开销；`advance` 对 extent 不动 `pos`（extent 可横跨，由 peek 侧推进），正反两种步进语义不对称是为 extent 覆盖语义服务的。

**可学**：读语义按需分裂（peek/max/prev/slot/node），但共用 `set_pos → traverse → 叠加 → 过滤` 底座。

---

## 五、读节点：黑名单与校验

首 bset 黑名单即报错，非首跳过；回写最大序号保证新于日志不可见；自描述跳自身字段校验。

### 5.1 `bch2_validate_bset`（`fs/btree/read.c:268`）——头校验

- 签名：`int bch2_validate_bset(struct bch_fs *c, struct bch_dev *ca, struct btree *b, struct bset *i, unsigned offset, int write, struct bch_io_failures *failed, struct printbuf *err_msg)`
- 参数：`i` 当前 bset；`offset` 扇区偏移（0 表首 bset，带自描述头）；`write` 读/写校验强度。
- 返回：0 或 fsck 错误码（`btree_err_on` 系列，可修复项带 `FSCK_CAN_FIX`）。
- 调用链：`read_done:758 → 本函数 → 版本兼容（:279）→ seq/btree_id/level/min/max/format（:344-410）`。
- 代码片段（`read.c:339-348`）：
```c
if (b->key.k.type == KEY_TYPE_btree_ptr_v2) {
    struct bch_btree_ptr_v2 *bp = &bkey_i_to_btree_ptr_v2(&b->key)->v;
    btree_err_on(bp->seq != bn->keys.seq, 0, c, ca, b, NULL, NULL,
             bset_bad_seq,
             "incorrect sequence number (wrong btree node)");
}
```
- 权衡：首 bset（`!offset`）才验 `seq/btree_id/level/min_key/max_key/format`——后续 bset 无自描述头，验了也是错；`seq` 不匹配直接判“读错节点”（不可修复，返回错误），而版本/偏移类问题尽量 `FSCK_CAN_FIX`，分级信任、分级处置。

### 5.2 `bch2_validate_bset_keys`（`fs/btree/read.c:470`）+ 帮手 `bset_key_validate:429 / bkey_packed_valid:439 / btree_node_bkey_val_validate:416`

- 签名：`int bch2_validate_bset_keys(... struct bset *i, int write, ...)`；逐键循环 `i->start → vstruct_last(i)`。
- 参数：`write` 决定 compat 转换方向（读 `:522` / 写 `:535`）与是否跑值校验（`bset_key_validate:436` 仅 `BCH_VALIDATE_write` 才调 `btree_node_bkey_val_validate`）。
- 返回：0；坏键 `drop_this_key` 截断/跳过并标 `need_rewrite`，致命错 `goto fsck_err`。
- 调用链：`read_done:765 → 本函数 → bkey_p_next 越界（:496）→ format（:505）→ u64s（:512）→ compat（:522）→ __bkey_disassemble + bset_key_validate（:526-528）→ 有序性 btree_node_read_bkey_cmp（:540）`。
- 代码片段（`read.c:434-436`）：
```c
return __bch2_bkey_validate(c, k, from) ?:
    (!updated_range ? bch2_bkey_in_btree_node(c, b, k, from) : 0) ?:
    (from->flags & BCH_VALIDATE_write ? btree_node_bkey_val_validate(c, b, k, from->flags) : 0);
```
- 权衡：三段短路按成本排序——通用键校验最先，区间成员检查次之（`updated_range` 时跳过，容忍分裂中的瞬时越界），昂贵的值语义校验只在写路径跑；读路径相信“写时已验过”，把启动恢复速度放在首位，坏值留给后台 scrub。

### 5.3 `bch2_btree_node_read_done`（`fs/btree/read.c:595`）——组装与黑名单

- 签名：`int bch2_btree_node_read_done(struct bch_fs *c, struct bch_dev *ca, struct btree *b, struct bch_io_failures *failed, struct printbuf *err_msg)`
- 参数：`b` 已填盘数据的节点缓冲；`failed/err_msg` 错误聚合。
- 返回：0 成功；非 0 触发 `fsck_err` 清理 `fill_iter` 并更新 `BCH_TIME_btree_node_read_done`。
- 调用链：`read work/endio → 本函数 → magic（:627）→ 逐 bset csum/解密（:670-688）→ validate（:758/765）→ 黑名单（:771）→ sort归并（:826）→ aux 重建（:882）`。
- 代码片段（`read.c:771-793`，黑名单分级）：
```c
blacklisted = bch2_journal_seq_is_blacklisted(c, le64_to_cpu(i->journal_seq), true);
btree_err_on(blacklisted && first, FSCK_CAN_FIX, c, ca, b, i, NULL,
         bset_blacklisted_journal_seq,
         "first btree node btree/bset.has blacklisted journal seq (%llu)", ...);
btree_err_on(blacklisted && ptr_written, FSCK_CAN_FIX, ...);
b->written = min(b->written + sectors, btree_sectors(c));
if (blacklisted && !first) continue;
```
- 片段 2（`:799/:844` 水位与 `:882` 重建）：
```c
max_journal_seq = max(max_journal_seq, le64_to_cpu(i->journal_seq));
b->data->keys.journal_seq = cpu_to_le64(max_journal_seq);
bch2_bset_build_aux_tree(b, b->set, false);
```
- 权衡：首 bset 黑名单即报错（无可信锚点），非首黑名单 `continue` 跳过该 bset——日志回放期写入的旧 bset 允许“部分可见”；归并后把 `max_journal_seq` 回写到合并 bset 头，保证重放水位单调，后续 journal 重放不会二次应用已合并键。末尾 `sort_iter` 归并 + 单 bset 回写（`:826-844`）把多 bset 读放大一次性摊销掉。

### 5.4 `bch2_btree_node_read`（`fs/btree/read.c:1044`）+ `__bch2_btree_root_read:1129` / `bch2_btree_root_read:1175`

- 签名：`void bch2_btree_node_read(struct btree_trans *trans, struct btree *b, bool sync)`；`int bch2_btree_root_read(struct bch_fs *c, enum btree_id id, const struct bkey_i *k, unsigned level)`。
- 参数：`sync` 同步/异步下发；root 版 `k` 为根指针、`level` 期望层高。
- 返回：node 版无（完成经 `btree_node_read_work:901`）；root 版返回错误码。
- 调用链：`traverse 缺页 → node_read → pick_read_device（:1056）→ bio 下发（sync: submit_bio_wait :1113 / async: submit_bio :1117）→ read_done:595；root_read → cannibalize_lock（:1139）→ mem_alloc（:1143）→ unlock 后同步 read（:1156-1157）→ set_root_for_read（:1167）`。
- 代码片段（`read.c:1112-1118`）：
```c
if (sync) {
    submit_bio_wait(bio);
    bch2_latency_acct(ca, rb->start_time, READ);
    btree_node_read_work(&rb->work);
} else {
    submit_bio(bio);
}
```
- 权衡：普通缺页走异步（不堵事务，`trans->srcu_io_submitted=true（:1110）` 免误报 stuck）；root 读走同步（启动/恢复关键路径，简单压倒一切，且 `cannibalize` 保证极端内存压力下仍有页可用）。无设备可选（`:1059`）直接判 lost-data + 只读降级，不静默返回空树。

**可学**：分级信任（首 bset 严、余部松；读松、写严）；可见性用水位（journal_seq max）保证。

---

## 六、设计启示

分级独立、预取分层、压缩回退、语义分裂、底座共享、分级信任。

1. **分级独立**：`traverse（locking.h:163）/ search（bset.c:1316）/ overlay（journal_overlay.c:612）` 三级只经 `bkey_s_c + search_key` 契约耦合，可独立替换（如换 BSET_CACHELINE 不动 traverse）。
2. **预取分层**：`btree_path_prefetch:1000` 定量表（2/16/0）+ `node_prefetch:1536` 缓存命中短路 + `trans_get:3970` 根预热，三层分别覆盖“未来兄弟”“已缓存”“根热线”。
3. **压缩回退**：`make_bfloat:750` 失败置 `BFLOAT_FAILED`，`search_tree:1280` 回退真键；正确性不依赖压缩成功率，性能只要求失败 <1%（`bset.h:119-125`）。
4. **语义分裂**：`peek_max:2758 / prev_min:2994 / slot:3166 / node:2286` 四语义共享 `__peek:2541` 底座，差异收敛到 `search_key` 推进方向与 `end` 比较方式。
5. **底座共享**：叠加顺序 btree → cache → journal → updates（`peek_slot:3216` 注释）是全家族不变量，改顺序即改可见性语义，需同步改四处调用点。
6. **分级信任**：`validate_bset:339` 的 seq（错即错节点）vs 版本/偏移（可修复）vs `validate_bset_keys:436` 读跳值检，是“启动速度 vs 正确性”的显式分档。

---

## 复核途径

- `sed -n 995,1057p fs/btree/iter.c` 看预取双路径（`btree_path_prefetch / _j`)。
- `sed -n 9,85p fs/btree/bset.c` 看辅助树 DOC（Eytzinger + 预取动机）。
- `sed -n 407,412p fs/btree/bset.c; grep -n BSET_CACHELINE fs/btree/bset.h` 看 4B 浮点 + 256B 粒度。
- `sed -n 1266,1347p fs/btree/bset.c` 看 `search_tree / __bset_search` 三路分发。
- `sed -n 1474,1521p fs/btree/bset.c` 看 `node_iter_init` 两阶段查找 + 4 行预取。
- `sed -n 2541,2624p fs/btree/iter.c` 看 `__peek` 底座（叠加 + whiteout 跳键）。
- `sed -n 2758,2856p fs/btree/iter.c` 看 `peek_max`（快照过滤 + 越界处理）。
- `sed -n 3166,3248p fs/btree/iter.c` 看 `peek_slot`（叠加顺序注释 + 活锁规避）。
- `sed -n 595,800p fs/btree/read.c` 看 `read_done`（csum → validate → 黑名单 → 水位）。
- `sed -n 1044,1180p fs/btree/read.c` 看 `node_read / root_read`（同步异步双路径）。
