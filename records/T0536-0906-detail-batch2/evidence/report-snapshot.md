# bcachefs 快照专题学习报告（T0519）：代码级精讲

> 精读 `fs/snapshots/` 四文件共 5785 行（`delete.c:1644`、`snapshot.c:1279`、`subvolume.c:1013`、`check_snapshots.c:1849`）。
> 事实源为源码，行号函数名均经 Grep/Read 核实。九节结构保留，每节逐函数精讲（签名/参数/返回/调用链/≤10行片段/权衡）。

---

## 一、全景：快照即分支树

快照不是拷贝，是分支树节点：`snapshots` btree 存节点（parent/children[2]/subvol/tree/depth/skip[3]/state），
`subvolumes` 叶节点指向快照 id，写时按祖先可见性过滤。删除即剪枝，校验即验树。
核心矛盾：删枝不能丢活数据，查祖先必须快。

### 1.1 `bch2_snapshot_node_create`（`snapshot.c:1084`）

- 签名：`int bch2_snapshot_node_create(struct btree_trans *trans, u32 parent, u32 *new_snapids, u32 *snapshot_subvols, unsigned nr_snapids)`
- 参数：`parent==0` 表建新树（此时 `nr_snapids==1`）；`parent!=0` 表在父下分裂（此时 `nr_snapids==2`，见函数内两个 `BUG_ON`）。
- 返回：0 成功，否则 `ENOSPC_snapshot_create` / `EINVAL_snapshot_parent_already_has_children` 等。
- 调用链：`bch2_subvolume_create(subvolume.c:882)` → `bch2_snapshot_node_create` → `create_children(:1034)`/`create_tree(:1068)` → `create_snapids(:988)` → `bch2_mark_snapshot(:788)`。
- 片段（`:1089-1097`）：
```c
BUG_ON((parent == 0) != (nr_snapids == 1));
BUG_ON((parent != 0) != (nr_snapids == 2));
return parent
    ? bch2_snapshot_node_create_children(trans, parent, ...)
    : bch2_snapshot_node_create_tree(trans, ...);
```
- 权衡：快照分裂恒为“父变内节点 + 两个新叶”（`create_children:1058-1060` 把父的 `children[0..1]` 填满并清 `subvol`），
  故健康树中单孩子内节点只可能是删除残留——这正是 `redundant_interior` 可识别的前提。用一次分裂写两个叶换取“分支语义原子”。

### 1.2 `create_snapids`（`snapshot.c:988`）

- 签名：`static int create_snapids(trans, parent, tree, new_snapids, snapshot_subvols, nr_snapids)`。
- 参数/返回：从迭代器尾部倒扫空槽分配 id（id 递减、父 id恒小于子，见 `snapshot.c:705,721` 校验）；失败返 `ENOSPC_snapshot_create`。
- 调用链：被上两个 create_* 调用；内调 `bch2_snapshot_skiplist_get` 预填 `skip[]` 并 `bubble_sort` 归一化。
- 片段（`:1016-1025`）：
```c
for (unsigned j = 0; j < ARRAY_SIZE(n->v.skip); j++)
    n->v.skip[j] = cpu_to_le32(bch2_snapshot_skiplist_get(c, parent));
bubble_sort(n->v.skip, ARRAY_SIZE(n->v.skip), cmp_le32);
try(bch2_mark_snapshot(trans, bkey_i_to_s_c(&n->k_i)));
```
- 权衡：新建即拍 skiplist 快照并同步内存表（`mark_snapshot`），写放大换读加速；`skip[]` 必须排序归一化，否则 `snapshot.c:728` 校验报 `skiplist_not_normalized`。

### 1.3 `bch2_snapshot_state_set`（`snapshot.c:594`）+ `bch2_subvolume_state_set`（`subvolume.c:471`）

- 签名：`void bch2_snapshot_state_set(struct bch_snapshot *s, enum bch_snapshot_state n)`；子卷侧同形。
- 参数/返回：无返回，原子双写“新 state 码字 + 旧 flag 位”（快照侧 `SET_BCH_SNAPSHOT_*_OBSOLETE`，子卷侧 `:481` 置 `UNLINKED_OBSOLETE = (n != live)`）。
- 调用链：所有状态变迁（`set_deleted/delete/undelete/check修复`）必经此函数。
- 片段（`subvolume.c:481`）：`SET_BCH_SUBVOLUME_UNLINKED_OBSOLETE(s, n != SUBVOLUME_STATE_live);`
- 权衡：双写兼容旧内核（旧内核只认 flag），代价是引入“state/flag 不一致”一类损坏，`check_snapshot_state(:1215)` 专设 `stale_tombstone` 分支收敛它。
  状态码字间距 ≥14（`:1140` 注释），≤2bit 可定为 bitflip 自愈，>6bit 则 fail-stop——把“可纠错编码”思想用在状态字段上。

### 1.4 `bch2_snapshot_validate`（`snapshot.c:690`）/ `bch2_subvolume_validate`（`subvolume.c:413`）

- 签名：`int bch2_snapshot_validate(c, k, from)`；子卷侧同形。
- 参数：`from->from==BKEY_VALIDATE_commit` 才做提交期强校验（写者当场抓现行，读旧键不严判，见 `:748-754` 注释）。
- 返回：`bkey_fsck_err_on` 累积错误码。
- 片段（`:705-712`）：
```c
bkey_fsck_err_on(id && id <= k.k->p.offset, c, snapshot_parent_bad, ...);
bkey_fsck_err_on(le32_to_cpu(s.v->children[0]) < le32_to_cpu(s.v->children[1]), ...);
```
- 权衡：序约束（父 id > 子 id、children 降序归一化）把“拓扑良构”编译成可机检不变量；
  提交期才查 `subvol 只能在 live/will_delete 叶`（`:774-780`），避免旧盘误杀。`normalize_snapshot_child_pointers(delete.c:436)` 是其写侧搭档。

**可学**：快照语义选分支树而非增量链，删除/校验都是树操作；不变量（id 序、归一化、状态码距）先行，修复才有依据。

---

## 二、祖先判定三级加速

读热路径（写时可见性判断）爬父链太慢：skiplist 跳跃 + 位图 O(1)，恢复期降级慢路，DEBUG 下三路对账不一致直接 panic。

### 2.1 `__bch2_snapshot_is_ancestor_early`（`snapshot.c:343`）+ `bch2_snapshot_is_ancestor_early`（`:352`）

- 签名：`static bool __..._early(table, id, ancestor)`；公开版加 `guard(rcu)` 取表。
- 参数/返回：`id/ancestor` 为快照号；`id==ancestor` 返回 true。利用“子 id 恒小于祖先 id”（`while (id && id < ancestor)` 爬父）。
- 调用链：恢复期快路（`__bch2_snapshot_is_ancestor:521`）、`snapshot_parent_child_consistent` 的 skiplist 修复判据（`check_snapshots.c` 经 `check_snapshot:1442`）。
- 片段（`:345-349`）：
```c
while (id && id < ancestor) {
    const struct snapshot_t *s = __snapshot_t(t, id);
    id = s ? s->parent : 0;
}
return id == ancestor;
```
- 权衡：O(深度) 慢路但零依赖（表坏/恢复期可用）；`id<ancestor` 剪枝使非祖先快速失败。

### 2.2 `get_ancestor_below`（`snapshot.c:404`）+ `test_ancestor_bitmap`（`:419`）

- 签名：`static inline u32 get_ancestor_below(t, id, ancestor)`；`static bool test_ancestor_bitmap(t, id, ancestor)`。
- 参数/返回：前者从 `skip[2..0]` 选“仍 ≤ancestor 的最高跳点”，否则退父；后者查 `is_ancestor` 位图第 `ancestor-id-1` 位。
- 调用链：仅 `__bch2_snapshot_is_ancestor(:524-528)` 快路。
- 片段（`:410-416` + `:425`）：
```c
if (s->skip[2] <= ancestor) return s->skip[2];
if (s->skip[1] <= ancestor) return s->skip[1];
...
return test_bit(ancestor - id - 1, s->is_ancestor);
```
- 权衡：skiplist 处理远祖（步长随机，`skiplist_get` 取 `nth_parent(random_below(depth))`），位图覆盖近 `IS_ANCESTOR_BITMAP` 个祖先；
  跳点是概率结构，错了只走慢路——正确性不依赖它，对了才快。

### 2.3 `__bch2_snapshot_is_ancestor`（`snapshot.c:511`）

- 签名：`bool __bch2_snapshot_is_ancestor(trans, id, ancestor)`。
- 参数/返回：同上，返回快路结论；恢复期（`recovery_pass_will_run(check_snapshots)`）直接走 `_early` 慢路。
- 片段（`:520-529`）：
```c
if (unlikely(recovery_pass_will_run(c, BCH_RECOVERY_PASS_check_snapshots)))
    return __bch2_snapshot_is_ancestor_early(t, id, ancestor);
if (likely(ancestor >= IS_ANCESTOR_BITMAP))
    while (id && id < ancestor - IS_ANCESTOR_BITMAP)
        id = get_ancestor_below(t, id, ancestor);
ret = id && id < ancestor ? test_ancestor_bitmap(t, id, ancestor) : id == ancestor;
```
- 权衡：RCU 读表无锁；恢复期自降级——表可能正被拓扑修复改写，位图不可信时不用它。DEBUG 编译再调 `is_ancestor_debug` 对账。

### 2.4 `bch2_snapshot_is_ancestor_debug`（`snapshot.c:482`）+ 三路 trace（`:429/:447/:462`）

- 签名：`void bch2_snapshot_is_ancestor_debug(trans, id, ancestor, fastpath_ret)`，仅 `CONFIG_BCACHEFS_DEBUG` 生效（`:532`）。
- 参数/返回：对比 fastpath vs slowpath（内存表爬链），不等则另读 btree 真值并 `panic`。
- 调用链：`__bch2_snapshot_is_ancestor:533` 尾部。
- 片段（`:494-508`）：`if (fastpath_ret == slowpath_ret) return; ... panic("%s", buf.buf);`
- 权衡：生产零开销（`__cold/noinline` 移出热路径），测试/调试把“加速结构与真值漂移”变成必崩——快路错立即可见。

### 2.5 `bch2_mark_snapshot`（`snapshot.c:788`）+ `bch2_snapshot_table_rebuild`（`:1109`）

- 签名：`static int bch2_mark_snapshot(trans, new)`；rebuild 逆序全表重 mark。
- 参数/返回：将 btree 写入同步到内存 `snapshot_table`（parent/children/depth/skip + 重算 `is_ancestor` 位图，`:818-833`）；`will_delete` 时以 ephemeral 方式调度 `delete_dead_snapshots`（`:848-851`，原子触发上下文中不碰 `sb_lock`，失败忽略以免整体 RO）。
- 调用链：`bch2_snapshot_trigger(:860)`（atomic 触发）→ mark；`bch2_snapshots_read(:1118)` 启动逆序 mark（祖先先就绪，位图依赖它）。
- 片段（`:821-823`）：
```c
while ((parent = bch2_snapshot_parent_early(c, parent)) &&
       parent - id - 1 < IS_ANCESTOR_BITMAP)
    __set_bit(parent - id - 1, is_ancestor);
```
- 权衡：写时同步内存表（读无锁），拓扑修复后置 `need_table_rebuild` 全量重算（`check_snapshots_trans:1488`），用“批量重建”对冲“逐次增量易漂移”。

### 2.6 `bch2_snapshot_redundant_interior`（`snapshot.c:373`）

- 签名：`u32 bch2_snapshot_redundant_interior(c, id)`，返回沿单活链折叠后的终端活节点，无则 0。
- 调用链：fsck 把半迁移键放在“最终会坍缩成的孩子视角”下检查，避免误报（函数头 `:358-372` 大注释）。
- 片段（`:385-397`）：数活孩子，恰 1 个则下钻，多/零则按 `id != orig` 决定返回。
- 权衡：删除是渐进坍缩，校验必须理解“中间态语义”而非只看瞬时快照。

**可学**：热路径快路加速、慢路保底、DEBUG 三路对账防快路错；加速结构可错（只影响速度），真值通道独立。

---

## 三、删除前全量预检

更新一旦排队就拒删留碎事务，故提交前把有数据/双孩子/坏节点全判完，调用者直接丢被拒节点。

### 3.1 `bch2_snapshot_accounting_totals`（`delete.c:170`）

- 签名：`int bch2_snapshot_accounting_totals(c, id, total_keys, total_sectors, btrees_with_keys, breakdown)`。
- 参数/返回：遍历全部 `btree_type_has_snapshots` 的 btree，读内存记账（`bch2_accounting_mem_read`，`:197`），`trust_keys` 门控（`:175`，`per_dev_fragmentation_lru` 升级前 key 计数不可信，只看 sectors）。
- 调用链：`check_no_data(:275)`、`snapshot_content_empty(:384)`、`check_snapshot_deleted` 系数据裁决、`edge` 修复判据。
- 片段（`:196-209`）：
```c
u64 v[3] = {};
bch2_accounting_mem_read(c, disk_accounting_pos_to_bpos(&acc), v, ARRAY_SIZE(v));
u64 nr_keys = trust_keys ? v[0] : 0;
```
- 权衡：纯内存读、无事务、无刷盘（`:190-194` 注释），判据实时且便宜；代价是升级前 key 计数为零，dirent/xattr-only 残留不可见——`snapshot_content_empty:372` 注释明示此盲区。

### 3.2 `bch2_snapshot_node_check_deletable`（`delete.c:462`）

- 签名：`static int bch2_snapshot_node_check_deletable(trans, id, delete_interior)`。
- 参数/返回：先 `check_no_data`，再查“已 deleted / 有双孩子 / subvol 指针坏 / 运行时删内节点”四拒因；0 可删，错误码为拒因。
- 调用链：`delete_dead_snapshots_locked(:1419)` 逐叶提交前、`delete_dead_interior_snapshots(:1567)` depth 重写前（先拒后写，见 `:1558-1567` 注释）。
- 片段（`:481-487`）：
```c
if (s.v.children[1]) {
    ...prt "deleting node with two children" ...;
    return bch_err_throw(c, EINVAL_snapshot_delete_has_two_children);
}
```
- 权衡：判定与执行分离的原因在函数头 `:443-460` 写透：`get_mut` 一旦调用即排队更新，拒晚了就留碎事务；
  更糟的是 interior 删除先提交了孩子的 depth/skip 重写，拒晚了树就描述了一场没发生的删除（skip 指到 parent 之上，下次写校验即 RO）。

### 3.3 `bch2_snapshot_node_set_no_keys`（`delete.c:420`）

- 签名：`static int bch2_snapshot_node_set_no_keys(trans, id)`。
- 参数/返回：先 `check_no_data(id,"set_no_keys")` 再置 `SNAPSHOT_STATE_no_keys`（`:432`）。
- 调用链：`delete_dead_snapshots_locked:1424` 内节点清空阶段。
- 权衡：注释 `:422` 点题——预检必须在 `get_mut` 排队前。`no_keys` 是“运行时删不掉内节点”的停车态：键已迁空、节点留树保祖先可达，下次挂载再由 interior 路径摘除。

**可学**：判定与执行分离，拒删必须在副作用前；注释把“为什么不能后移”写成定理，供后来者不敢乱改顺序。

---

## 四、带数据拒删加精准调度

删时发现残留不直接删，按记账掩码调度对应内容修复；运行时不可倒带则靠持久需求下次修。

### 4.1 `bch2_snapshot_node_check_no_data`（`delete.c:267`）

- 签名：`static int bch2_snapshot_node_check_no_data(trans, id, op)`，`op` 仅用于日志（set_no_keys/leaf delete/interior delete）。
- 参数/返回：记账零则 0；非零则调度修复后返 `EINVAL_snapshot_delete_with_data`（`:331`）。
- 调用链：`set_no_keys`、`check_deletable`、`locked:1411/1415` 三处“出口许可证”。
- 片段（`:316-331`）：
```c
ret = bch2_run_explicit_recovery_pass(c, &msg, BCH_RECOVERY_PASS_check_allocations, 0);
ret = schedule_content_passes(c, &msg, btrees_with_keys) ?: ret;
...
if (bch2_err_matches(ret, BCH_ERR_cannot_rewind_recovery))
    ret = 0;
return ret ?: bch_err_throw(c, EINVAL_snapshot_delete_with_data);
```
- 权衡：删读耦合——删前读账，残留转修复而非硬删；`cannot_rewind` 时把调度到的 pass 需求先持久化（注释 `:322-327`），本次返 0 让运行时直接过、下次挂载再修。

### 4.2 `schedule_content_passes`（`delete.c:244`）

- 签名：`static int schedule_content_passes(c, msg, btrees)`，`btrees` 为记账掩码。
- 参数/返回：按位调度 `check_extents/check_inodes/check_dirents/check_xattrs`（`:253-259` switch），`ret` 累积。
- 调用链：仅上函数。注释 `:240` 点出因果：这些 pass 的 `key_has_snapshot` 修复正是“让下次删除找得到 stranded 键”的前提。
- 权衡：精准调度（只修有账的 btree）而非全量 fsck；曾只调度 `check_inodes` 导致 dirent 残留永远拒删的 bug 即是此掩码要修的（注释 `:309-314`）。

### 4.3 `snapshot_content_empty` / `dying_snapshots_content_btrees`（`delete.c:378/406`）

- 签名：前者查单节点（排除 inodes，`:387`），后者汇总全部 dying 节点得 `bad_btrees` 掩码。
- 调用链：`delete_dead_snapshot_keys_v2:1036/1064` 的“删 inode 索引前”检查点。
- 权衡：v2 用 inode 做索引加速（见第五节），删 inode 即毁索引，故先让记账（不走索引）独立验一遍——双通道互验。

### 4.4 `snapshot_delete_refused`（`delete.c:1440`）

- 签名：`static bool snapshot_delete_refused(ret)`，`with_data/bad_topology` 两种拒因返 true。
- 调用链：`__bch2_delete_dead_snapshots:1462`、`bch2_delete_dead_interior_snapshots:1604` 把拒绝吞成 0。
- 片段（`:1430-1438` 注释）：“拒绝 = 先修后重试，不是失败；恢复 pass 首错即掉挂载，故拒绝止于此。”
- 权衡：拒绝不进错误通道，避免“修得了的小病把文件系统变 RO”。

**可学**：删读耦合（删前读账，残留转修复而非硬删）；拒绝是控制流，不是错误。

---

## 五、v2 索引范围删

有内容必有同快照 inode，先扫 inode 按号删各树区间，再扫自身；残留回退全表扫，仍残拉分配修复。

### 5.1 `delete_dead_snapshot_keys_v2`（`delete.c:978`）

- 签名：`static int delete_dead_snapshot_keys_v2(trans)`。
- 参数/返回：无参（读 `c->snapshots.delete`  dying 集合），0 或修复性错误。
- 调用链：`delete_dead_snapshots_locked:1397`（特性门：老版本走 v2？注意 `:1396` 三元写反直觉——`!request(v2) ? v2 : v1`，即未请求 v2 特性才用 v2 路径，实为兼容旧盘语义）。
- 核心逻辑三段：
  1. 扫 inodes，遇 dying 快照号则对该 `inum` 的 extents/dirents/xattrs/damage 做区间删（`:1009-1023`）；
  2. `dying_snapshots_content_btrees` 复验，残留则 `bad_btrees` 掩码回退 v1 重扫（`:1038-1064`）；
  3. 仍残留则跑 `check_allocations` 自证计数，拒删（`:1067-1085`）。
- 片段（`:1010-1013`）：
```c
struct bpos start = POS(k.k->p.offset, 0);
struct bpos end   = POS(k.k->p.offset, U64_MAX);
try(delete_dead_snapshot_keys_range(trans, &res.r, BTREE_ID_extents, start, end));
```
- 权衡：不变量“内容键 ⇒ 同快照 inode 存在”（`:994-997` 注释，damage 键另由 `check_damage` 保证）把全表扫降为“按 inode 号区间删”；索引（inode）与内容互为对方的查找路径，故删内容时绝不能先删 inode（`:1027-1032` 注释）。

### 5.2 `delete_dead_snapshot_keys_v1{_btree}`（`delete.c:921/941`）

- 签名：`v1_btree(trans, btree)` 逐 btree 全表 `for_each_btree_key_commit`；`v1` 按序扫（inodes 最后，`:954-957` 注释称 fsck 依赖此顺序）。
- 调用链：v2 回退（`:1058-1060` 按 `bad_btrees` 掩码只扫有账的树）、新盘路径（`:1398`）。
- 权衡：v1 不依赖“内容⇒inode”不变量，是 v2 的无假设回退；慢但稳。两档设计 = 快路 + 无假设回退。

### 5.3 `delete_dead_snapshots_process_key`（`delete.c:901`）

- 签名：`static int delete_dead_snapshots_process_key(trans, iter, k)`。
- 参数/返回：先 `bch2_check_key_has_snapshot` 修/判（返 1 表已处理，顺手提交），再 `snapshot_id_dying` 查 Eytzinger 表命中才调 `bch2_delete_dead_snapshot_key`。
- 片段（`:908-918`）：
```c
int ret = bch2_check_key_has_snapshot(trans, iter, k);
if (ret < 0) return ret;
if (ret) return bch2_trans_commit_lazy(...);
const struct snapshot_interior_delete *dying = snapshot_id_dying(d, k.k->p.snapshot);
```
- 权衡：删除与 fsck 修复合用同一 per-key 入口，运行时顺手修、修不好转交 pass。

### 5.4 `__bch2_check_key_has_snapshot`（`check_snapshots.c:1709`）

- 签名：`int __bch2_check_key_has_snapshot(trans, iter, k)`，`iter==NULL`（promote 路径）直接返 1 不修（`:1719`）。
- 参数/返回：快照态非 deleted/empty 返 0；deleted 键按“有无活后代”二分：无则删（`:1817`），有则迁（`:1827` 调 `bch2_delete_dead_snapshot_key` + `check_key_has_inode_in_snapshot:1685` 把 inode 一并搬下，避免下次再 strand）。
- 调用链：删除扫描与各内容 pass 共用。
- 门禁（`:1784-1788`）：snapshots/subvolumes 两树非 clean（`bch2_btree_is_clean`）则不信内存表，先调度 pass 回来再说——“表脏则 key 不动”，防误删活数据。
- 权衡：迁移时保留“inode 伴随”不变量（函数头 `:1676-1682` 大注释），否则修好一次、下次删除又 strand。

**可学**：批量删除索引快路加全表回退两档；不变量（内容⇒inode）是快路的合法性来源，记账是独立于索引的第二 double-check。

---

## 六、dying 下迁与落盘序

有活孩子搬键到活槽，损伤双存归并；无活叶直接删；迁移、熔断、逐叶提交、置空四段落盘。

### 6.1 `bch2_delete_dead_snapshot_key`（`delete.c:862`）

- 签名：`int bch2_delete_dead_snapshot_key(trans, iter, k, live_child)`。
- 参数：`live_child==0` 表叶删；非零表把键搬到后代同位（`dst.snapshot=live_child`）。
- 返回：底层 `bch2_btree_delete_at` 结果。
- 片段（`:870-882`）：
```c
struct bpos dst = k.k->p;
dst.snapshot = live_child;
...peek_slot(&dst_iter)...
if (bkey_deleted(dst_k.k)) {
    struct bkey_i *new = errptr_try(bch2_bkey_make_mut_noupdate(trans, k));
    new->k.p = dst;
    try(bch2_trans_update(trans, &dst_iter, new, BTREE_UPDATE_internal_snapshot_node));
}
```
- 权衡：只在目标空槽才搬（后代已有键 = 已覆写，不搬）；damage 键双存归并（`:883-895` 调 `bch2_damage_keys_merge`，注释明言“后记的计数不能丢”）；
  `BUG_ON(!bch2_snapshot_exists(:868))` 保证迁移目标活。删除与 fsck 修复共用此函数，语义统一。

### 6.2 `check_should_delete_leaf`（`delete.c:1100`）

- 签名：`static int check_should_delete_leaf(trans, s)`，返 1 表该删。
- 参数：按 `live/will_delete/no_keys/非法` 四态分支。
- 要点：`will_delete` 有 subvol 背指则必须与子卷墓碑互指（`:1133-1141` 双 `inconsistent_on`，用裸读而非 `bch2_subvolume_get`——删除路径是唯一要看墓碑的调用者，`:1124-1127` 注释）；
  无背指的 `will_delete` 叶须 `require(check_subvols)`（`:1121`，信“刚跑过的 pass”不信版本号）。
- 权衡：互指校验把“删子卷没删快照 / 删快照没删子卷”两类半截事务都拦在收集期。

### 6.3 `check_should_delete_snapshot`（`delete.c:1181`）

- 签名：`static int check_should_delete_snapshot(trans, k)`，收集期唯一写者（`:1210` 注释：读无需锁）。
- 参数/返回：自底向上分类：两活孩子→留；零活→`delete_leaves`；单活→`delete_interior{ id, live_child }`（`:1253-1273`）。
- 关键细节：
  - 升序扫 + “子 id 恒小于父”（`:1169`），故孩子先于父母分类，死子树自底累积、拆时同序（`:1172-1176`）；
  - `live_child` 沿链解析到终端（`:1218-1220` 查三表），键一次搬到位；
  - `live_child` 非法（自指/不在表/非后代）则调度 `check_snapshots` 并以 `bad_topology` 熔断（`:1233-1245`）；
  - 收集幂等（`nodup/has_id`，`:1199-1204`）防 per-key-commit 重放 double-add。
- 权衡：收集即定序，迁移目标一次算对；拓扑坏先修树不删键。

### 6.4 `delete_dead_snapshots_locked`（`delete.c:1350`）四段落盘

1. 收集（`:1364` 全表扫 `check_should_delete_snapshot`）；空则返 0。
2. 建 Eytzinger 索引 + 记日志 + 打印每节点记账（`:1376-1394`，注释 `:1373` 称 1-based Eytzinger 缓存友好）。
3. 迁移（v1/v2，`:1396`）。
4. 熔断复验 + 逐节点提交：叶 `check_no_data→check_deletable→node_delete` 各自独立 commit（`:1417-1420`），内节点 `set_no_keys`（`:1422-1424`）。
- 注释 `:1401-1407` 点题：复验不能前移——验的是“迁过去的键真过去了”；且拒一半停全部，否则已删节点描述了不存在的树形。
- 权衡：多小事务换崩溃可续（childless `no_keys` 由下次收集顺手回收，见 `check_should_delete_leaf:1146` 注释）；熔断（`bad_topology/with_data`）停全删保一致。

### 6.5 `bch2_snapshot_node_delete`（`delete.c:526`）

- 签名：`int bch2_snapshot_node_delete(trans, id)`，前置要求调用者已 `check_deletable`（`:522` 注释：此后只许硬错不许拒绝）。
- 参数/返回：摘链（父 child 槽指向孙、孙 parent 指祖，`:543-583`），根则改 `snapshot_tree.root` 或删树（`:585-601`）；
  旧盘（pre-`snapshot_deletion_v2`）保留指针置 `deleted` 态（`:603-613` 留修车信息），新盘直接删键。
- 权衡：删节点不动记账（`:619-624` 注释：记账是派生的，触发器随键删自然归零；此处非零是 bug，该拒的早拒了）。

### 6.6 interior 路径：`delete_dead_interior_snapshots`（`delete.c:1519`）+ `bch2_fix_child_of_deleted_snapshot`（`:1297`）+ `bch2_check_snapshot_needs_deletion`（`:1613`）

- `needs_deletion:1613`：`will_delete` 或单孩子内节点（`interior_snapshot_needs_delete:1607`）即调度 deleter；`no_keys` 计数供启动诊断。
- `delete_dead_interior:1519`：先跑 `check_snapshots` 定树（`:1532`），重收敛（`:1552`，state 可能被修），先全员 `check_deletable` 熔断（`:1565`），
  再全表重写幸存孩子 depth/skip（`:1580`，非原子、注释 `:1570-1578` 明言崩溃中间态 `depth != parent+1` 是途经态非不变量），最后逐个 `node_delete`。
- 调用链：`bch2_delete_dead_interior_snapshots:1598`（`auto_snapshot_deletion` 门控，拒绝吞零）。
- 权衡：depth/skip 是派生冗余，崩可由 check 重算——用“可重算”换“免大事务”。

**可学**：迁移与校验分阶段落盘，熔断停全删；派生字段敢分多事务写的底气是“崩后可重算”。

---

## 七、删态复活裁决

状态字段可能是谎言：先查数据再查互指，分级自愈；冗余内节点沿单活链折叠识别。

### 7.1 `check_snapshot`（`check_snapshots.c:1323`）总序

`check_state(:1338)` → 数据裁决（deleted/no_keys 有账则复活，`:1359-1382`）→ `check_deleted(:1384)`（双活孩子/活子卷互指复活，返 1 表 settled tombstone 止）→
边（parent+2 children，`:1388-1395`）→ 树指针（`:1403`）→ depth（父先子后，`:1426`）→ skip（`:1437`）→ subvol 互指（`:1471`）。
注释 `:1341-1356` 定调：数据第一，state 再可疑也先对账。

### 7.2 `check_snapshot_state`（`check_snapshots.c:1097`）

- 签名：`static int check_snapshot_state(trans, iter, k, s, u)`（`u` 为延迟物化 mut，`*u ?: make_mut` 惯用法）。
- 三级：零态→从 legacy flag 恢复（`:1115`，升级中静默、升级后 autofix）；无效码字→按汉明距分级（≤2 bitflip 自愈 / ≤6 可恢复损坏 / 更远则“被引用即 live，无引用 fail-stop”，`:1134-1197`）；
  有效但与 legacy `DELETED` 位 + `tree==0` 墓碑形矛盾→ stale_tombstone 修 deleted（`:1215-1226`，2026-07-20 现场报告回归）。
- 权衡：码距解码 + 形状佐证（flag 单比特不可全信，须看 tree/children 形状），宁可 fail-stop 不猜。

### 7.3 `check_snapshot_deleted`（`check_snapshots.c:1236`）

- 签名：`static int check_snapshot_deleted(trans, iter, k, s, u)`，返 1 表 settled、无需再查。
- 参数：非 live 节点若有**双活互指孩子**（`:1266-1278`，墓碑的 splice 面包屑不计——须 `points_back` 才算，`:1256-1258`）则复活（单活合法：`no_keys` 停车态本就单孩子，`:1251-1254`）；
  无孩子非 live 叶若 subvol 活且指回则复活（`:1299-1317`，墓碑读作 ENOENT 属正常删除中途，不算证据）。
- 权衡：状态不可信时以“活引用”（孩子/子卷/数据）为准；单双孩子分开处理是整节最易错点。

### 7.4 `bch2_snapshot_node_undelete`（`delete.c:650`）+ `snapshot_undelete_owns_data`（`check_snapshots.c:717`）+ `snapshot_in_tree`（`delete.c:635`）

- `undelete:650`：删的逆 splice。用保留的 parent/children 历史指针找槽：无孩子→父槽复活（`:666-715`，根特例 `:675-680`）；
  有单孩子→把孩子 parent 指回、祖父槽从 child 改指我、树根指针跟进（`:717-800`），depth/skip 按父重算。
  双孩子直接 `fsck_repair_unimplemented`（`:661-664`，从未 splice 过，无逆可 undo）；父/子已删亦 fail 不猜。
- `undelete_owns_data:717`：双孩子=结构完好仅 state 错，置 live 即完（undelete 会拒此形）；否则调 `node_undelete` 做 splice 逆。
- `snapshot_in_tree:635`：`state_compat != deleted` 即在树（`no_keys` 算在树——可挂靠，见 `:630-634` 注释）。
- 权衡：undelete 只 undo 证明发生过的 splice，不做拓扑手术；`tree==0` 老墓碑无指针可考则复活为 unlinked，由树指针检查接管。

**可学**：状态不可信时以数据为准；残留形态（冗余内节点/墓碑面包屑）可识别、可折叠。

---

## 八、子卷两阶段与校验

unlink 先记链表置态，再拿页缓存围栏，异步清后删；创建占空槽复用父快照，配额主卷收费快照旁路；校验逆扫使父先正，按序修复。

### 8.1 `bch2_subvolume_unlink`（`subvolume.c:862`）+ hook（`:844`）+ work（`:805`）

- 签名：`int bch2_subvolume_unlink(trans, subvolid)`。
- 两阶段：① 同事务挂 commit hook + 置 `unlinked` 态（`:864-870`）并调度 `check_subvols` 兜底（`:878`，防崩在“已 unlink、仍被打开”窗口）；
  ② hook（提交后）把 id 记 `snapshots.unlinked` 链表、取 write ref、投 workqueue（`:850-858`，`tryget` 失败返 EROFS 保围栏）；
  ③ work（`:805`）逐批 `evict_subvolume_inodes` 清页缓存后再 `bch2_subvolume_set_deleted(:788)`（reparent→置 deleted→快照 `will_delete`）。
- 权衡：记账（unlinked 可见性切换）与清场（evict + 删）分离；页缓存围栏防“删了树、内存还有脏页回写”；链表 + pass 兜底防崩失约。

### 8.2 `__bch2_subvolume_set_deleted`（`subvolume.c:743`）+ `bch2_subvolume_set_deleted`（`:788`）+ `bch2_subvolume_set_state_trans`（`:722`）

- `__:743`：子卷→快照→树三级裸查（快照/树缺失即 `inconsistent`，`:759/:770`），清 `master_subvol`（`:775`），同事务置子卷 deleted + 快照 `will_delete`（`:784`，`bch2_snapshot_node_set_deleted(delete.c:118)`，背指保留指墓碑供删检查）。
- `:788`：先 `commit_lazy` 冲掉 fsck 排队（`:798`，防 `trans_begin` 丢更新 WARN），再 reparent（删被删子卷的 fs 路径父子关系）再提交删。
- 权衡：子卷删与快照标删同事务——“快照 will_delete ⇔ 子卷 tombstoned”耦合恰为一比特（`check_snapshot_to_subvol:426` 注释），修亦单向（子卷定快照，反之要在 live/unlinked 间猜）。

### 8.3 `bch2_subvolume_create`（`subvolume.c:882`）

- 签名：`int bch2_subvolume_create(trans, inode, parent_subvolid, src_subvolid, new_subvolid, new_snapshotid, out, ro)`。
- 参数：`src==0` 表新卷（单节点新树），`src!=0` 表快照（父分裂双节点：`new_nodes[0]` 归新子卷、`[1]` 归源子卷，`:920-925` 改源 `snapshot` 指向新叶）。
- 要点：占子卷表空槽（`:896`，满返 `ENOSPC_subvolume_create`）；`SET_RO/SNAP` 标志、state live（`:937-939`）；配额在调用方（fs-common）按主卷收费、快照旁路（本文件外，此处只保证 `creation_parent/fs_path_parent` 双亲链 `:932-933`）。
- 权衡：创建与分裂同事务，源子卷即刻指向新叶——快照语义“旧 id 冻结、新 id 可写”一次提交生效。

### 8.4 `check_subvol`（`subvolume.c:46`）+ `bch2_subvolume_trigger`（`:533`）

- `check_subvol:46`：零态/坏码字三级自愈同快照（`:68-127`）；deleted 墓碑早退（`:134`，live 不变量不适用——root inode 可能已擦）；
  子卷指丢快照→调度 `reconstruct_snapshots`（`:146`）；双子卷争一快照以后背指为准（`:162-170` 先定归属再修，防后迭代者夺节点）。
- `trigger:533`：事务性维护 `subvolume_children` 位图（fs 路径父子），`bch2_subvol_has_children(:551)` 删非空子卷报 `ENOTEMPTY`。
- 权衡：子卷校验信“背指”、快照校验信“数据”，两类真相各有主；children 位图是 fs 命名空间约束，与快照拓扑正交。

### 8.5 `bch2_check_snapshots_trans`（`check_snapshots.c:1476`）+ `check_snapshot_edge`（`:841`）

- `trans:1476`：`for_each_btree_key_reverse_commit` 逆扫（id 降序 = 父先子后，depth 依赖父，`:1479` 注释）；完后按需 `table_rebuild`；`bch2_check_snapshots:1495` 全净且无错才置 snapshots 树 clean（`:1510`，`key_has_snapshot` 的“信表”门禁用它）。
- `edge:841`：删墓碑绕行（沿保留指针链上/下走到最近非 deleted，`:903-932`，超 `BTREE_MAX_DEPTH*64` 停防环，`:907`）；有账墓碑不绕反 undelete（`:884-900`，逆扫先见父、数据未裁决前不绕）；
  互补边（`:943`）、借表找边（`:962`）、丢子指针重建叶（`snapshot_resurrect_child:754`，有账重建、无账清除 `:996-1014`）；多损坏并联则上报止（`:1024-1046`，指去 `reconstruct_snapshots`）。
- 片段（`:921-922`）：`if (state != deleted) break;`——绕行链遇活即止。
- 权衡：边修复只做单损坏局部手术；depth/skip/tree 脏由后续按序检查顺带收敛；修一次提交一次（`snapshot_edge_repair_commit:727` 置 `need_table_rebuild` 重启 bila）。

### 8.6 `bch2_reconstruct_snapshots`（`check_snapshots.c:1639`）+ `check_snapshot_exists`（`:1517`）

- 逻辑：全内容树扫 key 的 snapshot 号聚类得树（`get_snapshot_trees:1605`），缺节点即 `reconstruct_snapshot_node:1620` 按单树链重建（多节点树拒修 `:1628`）；
  子卷侧丢快照亦可触发（`check_subvol:146`）。
- 权衡：终极回退——拓扑全毁时用“key 实证”重建树（名副其实的 reconstruct），平时绝不走。

**可学**：删除分记账与清场两阶段；校验顺序保证父先子后；修边只修单损坏，多损坏转重建。

---

## 九、设计启示

1. 分支树语义：快照=节点，分裂恒双叶，删除=剪枝+键下迁（`node_create:1084` / `delete_key:862`）。
2. 热路加速：skiplist+位图，恢复期自降级，DEBUG 三路对账（`is_ancestor:511` / `debug:482`）。
3. 判定执行分离：预检在 `get_mut` 排队前，拒删丢节点（`check_deletable:462` / `set_no_keys:420`）。
4. 删读耦合：删前读账，残留按掩码转修复而非硬删（`check_no_data:267` / `schedule_passes:244`）。
5. 索引快路：内容⇒inode 不变量做区间删，记账双验，回退 v1（`keys_v2:978`）。
6. 分阶段落盘：迁移→熔断→逐叶提交→置空；派生字段崩后可重算（`locked:1350` / `fix_child:1297`）。
7. 数据为准：state 可谎，账/互指/引用说了算，分级自愈（`check_state:1097` / `check_deleted:1236` / `undelete:650`）。
8. 两阶段删除：unlink 记账、evict 后清场，崩溃由 pass 兜底（`unlink:862` / `work:805`）；校验父先子后、单损坏局部修（`trans:1476` / `edge:841`）。

---

## 复核途径

- `grep -n "is_ancestor\|skiplist_get\|mark_snapshot" fs/snapshots/snapshot.c` 定位祖先三路与位图重建。
- `sed -n 482,536p fs/snapshots/snapshot.c` 看三路对账与快路主体。
- `grep -n "check_deletable\|check_no_data\|schedule_content\|accounting_totals" fs/snapshots/delete.c` 定位预检与拒删调度。
- `sed -n 978,1098p fs/snapshots/delete.c` 看 v2 区间删与回退。
- `sed -n 1350,1427p fs/snapshots/delete.c` 看四段落盘。
- `sed -n 1323,1474p fs/snapshots/check_snapshots.c` 看 check 总序；`sed -n 841,935p` 看边绕行。
- `sed -n 844,880p fs/snapshots/subvolume.c` 看 unlink 两阶段。
