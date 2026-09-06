# bcachefs 配额记账专题学习报告（T0531 代码级精讲）

> 事实源：`fs/fs/quota.c`（859 行）、`fs/alloc/accounting.c`（1455 行），
> 胶水层 `fs/vfs/io.h`、`fs/vfs/io.c`、`fs/vfs/fs.c`，类型层 `fs/fs/quota_types.h`、`fs/fs/quota.h`、`fs/alloc/accounting.h`、`fs/alloc/accounting_format.h`。
> 行号函数名均经 Grep/Read 核实。八节结构保留，每节逐函数精讲。

---

## 一、全景：收费与记账分离

配额管“向谁收费”（VFS 层内存 `bch_memquota`），记账管“用了多少”（分配层磁盘 `accounting` btree + 内存 percpu 快照）。两者经预留/落账联动，核心矛盾：超卖 vs 误杀。

### 1.1 `enabled_qtypes` — `fs/fs/quota.h:29`

签名：`static inline unsigned enabled_qtypes(struct bch_fs *c)`；参数：`c`；返回：usr/grp/prj 位掩码。

```c
return ((c->opts.usrquota << QTYP_USR)|
        (c->opts.grpquota << QTYP_GRP)|
        (c->opts.prjquota << QTYP_PRJ));
```

调用链：`bch2_quota_acct:286` / `bch2_quota_transfer:343` / `bch2_fs_quota_transfer(fs.c:204)` 入口过滤。
权衡：位掩码一次算出，未启用类型零成本跳过；代价是调用方须每次重算，无缓存。

### 1.2 `bch_qid` — `fs/fs/quota.h:20`

签名：`static inline struct bch_qid bch_qid(struct bch_inode_unpacked *u)`；返回三元组 uid/gid/project（`bi_project-1` 归一）。

调用链：`bch2_fs_quota_read_inode(quota.c:516)` 重建 → `bch2_quota_acct`。
权衡：project 为 0 表无归属，避免 0 号工程被误收费；但要求解包器保证字段语义。

### 1.3 `bch2_accounting_is_mem` — `fs/alloc/accounting.h:162`

签名：`static inline bool bch2_accounting_is_mem(struct disk_accounting_pos *acc)`；逻辑：`type < TYPE_NR && type != inum`。

调用链：`bch2_accounting_mem_add_inlined:197` / `accounting_read_key:806` / `bch2_accounting_read:1212` 分流。
权衡：`inum` 刻意排除在内存表外（仅磁盘碎片分析用），省内存；误用内存读会得零（`bch2_accounting_mem_read_locked:275` 有 EBUG_ON）。

### 1.4 提交钩子 `bch2_accounting_trans_commit_hook` — `fs/alloc/accounting.h:305`

签名：`(trans, a, commit_flags) -> int`；做两事：按 `journal_res.seq/offset` 赋 `bversion`，再调 `bch2_accounting_mem_add_inlined(...,BCH_ACCOUNTING_normal)`。

```c
a->k.bversion = journal_pos_to_bversion(&trans->journal_res, (u64 *)a - base);
return ... ? bch2_accounting_mem_add_inlined(...) : 0;
```

调用链：`btree/commit.c:934-939` 遍历 `trans->accounting` 子缓冲逐项应用。
权衡：版本号即 journal 位置，全序可比，支撑回放去重；`skip_accounting_apply` 标志给 GC 修复留旁路。

**可学**：收费记账分离，预留联动；内存/磁盘双轨以版本缝合。

---

## 二、预留联动：先占后扣

写前先 `PREALLOC` 预留，落账时 `quota_res` 抵扣，无预留则 `WARN` 直收；截断/释放走负数返还。

### 2.1 `bch2_quota_reservation_add` — `fs/vfs/io.h:92`

签名：`(c, inode, res, sectors, check_enospc) -> int`；`check_enospc=true` 用 `KEY_TYPE_QUOTA_PREALLOC` 检查，false 用 `NOCHECK`。

```c
guard(mutex)(&inode->ei_quota_lock);
ret = bch2_quota_acct(c, inode->ei_qid, Q_SPC, sectors,
          check_enospc ? KEY_TYPE_QUOTA_PREALLOC : KEY_TYPE_QUOTA_NOCHECK);
inode->ei_quota_reserved += sectors; res->sectors += sectors;
```

调用链：`vfs/pagecache.c:504,541` / `vfs/direct.c:469` / `vfs/io.c:735,895` 写路径入口。
权衡：`ei_quota_lock` 串行化同一 inode 预留，避免并发超发；快照 inode 直接返回 0（100 行），不向快照收费。

### 2.2 `__bch2_quota_reservation_put` / `bch2_quota_reservation_put` — `fs/vfs/io.h:70,82`

签名：`(c, inode, res)`；以 `PREALLOC` 模式做负数 `bch2_quota_acct(..., -sectors)`，清 `ei_quota_reserved`。

调用链：写失败/释放路径与 `bch2_i_sectors_acct` 配对。
权衡：负数路径走 `check_limit` 的减量分支（清警告），不触发限额拒绝；`BUG_ON(res->sectors > ei_quota_reserved)` 防 double-put。

### 2.3 `bch2_i_sectors_acct` 落账 — `fs/vfs/io.c:160-173`

签名要点：`(c, inode, quota_res, sectors)`；`sectors>0` 且有预留则双减（`quota_res->sectors` 与 `ei_quota_reserved`），否则 `bch2_quota_acct(..., Q_SPC, sectors, KEY_TYPE_QUOTA_WARN)`。

调用链：`__bch2_i_sectors_acct` 被页缓存/direct 落账调用。
权衡：有预留直扣不二次检查（预留时已审），无预留走 WARN 兜底收费并告警；快照跳过，防止双收。

**可学**：预留落账联动，缺一超卖；负数返还必须走同一把锁。

---

## 三、三档收费：免检预留警告

`enum quota_acct_mode`（`fs/fs/quota_types.h:11`）：`PREALLOC=0` 创建预检、`WARN=1` 落账驱逐、`NOCHECK=2` 重建回滚。

### 3.1 `bch2_quota_check_limit` — `fs/fs/quota.c:226`

签名：`(c, qtype, mq, msgs, counter, v, mode) -> int`；`n = qc->v + v`；`BUG_ON((s64)n < 0)` 防下溢。

```c
if (mode == KEY_TYPE_QUOTA_NOCHECK) return 0;
if (v <= 0) { /* 清 HARDWARN/SOFTWARN，warning_issued=0 */ return 0; }
```

调用链：仅被 `bch2_quota_acct:305` 与 `bch2_quota_transfer:358,364` 调用。
权衡：NOCHECK 最先返回，重建/回滚零开销；`BUG_ON` 把记账 bug 转为显式崩溃而非静默负数。

### 3.2 减量分支 `quota.c:243-257`

`n < hardlimit` 清 `HARDWARN` 发 `HARDBELOW`；`n < softlimit` 清 `SOFTWARN` 发 `SOFTBELOW`，最后 `warning_issued=0`。

权衡：回落通知让 userspace 解除告警；直接清零而非逐位清，简化但丢失跨计数器历史（可接受，因 v<=0 即视为恢复）。

### 3.3 `prepare_msg / prepare_warning / flush_warnings` — `quota.c:191,203,215`

签名：`prepare_msg(qtype,counter,msgs,msg_type)` 查 `quota_nl[msg][counter]` 表（169 行）映射 netlink 码；`prepare_warning` 以 `warning_issued & (1<<msg)` 去重；`flush_warnings(qid,sb,msgs)` 在锁外逐条 `quota_send_warning`。

权衡：锁内只攒消息、锁外才发送，避免持 `q->lock` 进 netlink；`BUG_ON(nr >= ARRAY_SIZE)` 界 `QTYP_NR*Q_COUNTERS`。

**可学**：收费分档、场景对号；锁内攒告警、锁外发送。

---

## 四、超限强制：硬软限时

硬限非特权直拒；软限首次置 timer 警告，超时仍超才拒；特权（CAP_SYS_RESOURCE）豁免硬限。

### 4.1 `ignore_hardlimit` — `fs/fs/quota.c:146`

```c
static bool ignore_hardlimit(struct bch_memquota_type *q) {
    if (capable(CAP_SYS_RESOURCE)) return true;
    return false;
}
```

`#if 0` 保留旧 root_squash 分支。权衡：简单即安全，特权不被配额误杀；代价是特权进程可撑爆（由管理员负责）。

### 4.2 硬限分支 `quota.c:260-265`

```c
if (qc->hardlimit && qc->hardlimit < n && !ignore_hardlimit(q)) {
    prepare_warning(qc, qtype, counter, msgs, HARDWARN);
    return -EDQUOT;
}
```

权衡：`hardlimit==0` 表不限，避免零配置误杀；`-EDQUOT` 与 VFS 配额语义对齐。

### 4.3 软限分支 `quota.c:267-277`

首次超限：`timer = now + q->limits[counter].timelimit` 并发 `SOFTWARN`；`now >= timer && !ignore_hardlimit` 则发 `SOFTLONGWARN` 并 `-EDQUOT`。

调用链上游 `timelimit` 来自 `bch2_sb_quota_read:475`（默认 7 天，`bch2_sb_get_or_create_quota:455`）。
权衡：软限给宽限，硬限不含糊；timer 存内存（`memquota_counter.timer:quota_types.h:21`），重启丢失则重计时，偏宽松但简单。

**可学**：软限状态机（未超→警告计时→超时拒），减量即复位。

---

## 五、两阶段提交与迁移

按类型序加锁，先全检查后累加；属主迁移过滤相同项，失败不迁回（调用方持有旧 qid，无分歧）。

### 5.1 `bch2_quota_acct` — `fs/fs/quota.c:282`

签名：`(c, qid, counter, v, mode) -> int`；流程：`genradix_ptr_alloc` 取三类表项 → `mutex_lock_nested(&q->lock,i)` 按序加锁 → 逐类 `check_limit`，任一失败 `goto err` → 全过才 `mq[i]->c[counter].v += v` → 解锁 → `flush_warnings`。

```c
for_each_set_qtype(c, i, q, qtypes) {
    ret = bch2_quota_check_limit(c, i, mq[i], &msgs, counter, v, mode);
    if (ret) goto err;
}
for_each_set_qtype(c, i, q, qtypes) mq[i]->c[counter].v += v;
```

权衡：两阶段保证 usr/grp/prj 原子一致；`lock_nested(i)` 固定序防死锁；`for_each_set_qtype`（139 行）用 `__ffs` 跳过未启用类型。

### 5.2 `__bch2_quota_transfer` — `quota.c:321`

```c
BUG_ON(v > src_q->c[counter].v);
BUG_ON(v + dst_q->c[counter].v < v);
src_q->c[counter].v -= v; dst_q->c[counter].v += v;
```

权衡：纯内存搬运，不做检查（检查由调用方前置），溢出/透支直接 BUG。

### 5.3 `bch2_quota_transfer` — `quota.c:332`

签名：`(c, qtypes, dst, src, space, mode)`；对 dst 做 `Q_SPC+space` 与 `Q_INO+1` 双检查（注意传的是 `dst->v + delta` 风格增量，358/364 行），全过才搬 `Q_SPC/space` + `Q_INO/1`。

权衡：chown 场景一次审空间+inode，防止只审一项的漏洞；失败直接返回，源端未动，无需回滚。

### 5.4 `bch2_fs_quota_transfer` 包装 — `fs/vfs/fs.c:198`

签名：`(c, inode, new_qid, qtypes, mode)`；先 `qtypes &= enabled` 再过滤 `new==old` 的类型（206 行），为零直接回；持 `ei_quota_lock` 调核心 `bch2_quota_transfer(..., i_blocks+ei_quota_reserved)`，成功才更新 `ei_qid`。

调用链：`fs.c:1454` chown/setattr；创建 `fs.c:761` 用 `Q_INO+1/PREALLOC`，失败回滚 `783` 用 `-1/WARN`。
权衡：把“已落账 + 已预留”一并迁移，避免预留悬空；`ei_qid` 延迟更新保证失败无分歧。

**可学**：全检查后累加；迁移按差集过滤、成功才换属主。

---

## 六、启动重建与工具分离

先恢复限额（sb→内存），再扫 quotas 表恢复 hard/soft，最后扫 inodes 主卷全免检累加；启停删查职责分离。

### 6.1 `__bch2_quota_set` — `quota.c:385`

签名：`(c, k, qdq) -> int`；`k.p.inode` 为 qtype，过滤未启用；`guard(mutex)` 后 `genradix_ptr_alloc`，回填 `hardlimit/softlimit`（le64→cpu），可选回填 timer/warns。

调用链：`bch2_fs_quota_read:538` 扫描、`bch2_set_quota:841` 在线生效。
权衡：btree 值与内存表双写（btree 持久 + 内存加速），在线 set 先提交 btree 再刷内存，崩溃一致性由重建兜底。

### 6.2 `bch2_fs_quota_read_inode` — `quota.c:483`

经 snapshot tree 查 `master_subvol`（498 行），非主卷跳过；`inode_find_by_inum` 找不到（已删快照残留）跳过；命中则双调 `bch2_quota_acct(...,NOCHECK)` 累 `bi_sectors` 与 `1`。

```c
bch2_quota_acct(c, bch_qid(&u), Q_SPC, u.bi_sectors, KEY_TYPE_QUOTA_NOCHECK);
bch2_quota_acct(c, bch_qid(&u), Q_INO, 1, KEY_TYPE_QUOTA_NOCHECK);
```

权衡：只算主卷防快照重复收费；NOCHECK 使重建不受旧限额干扰。

### 6.3 `bch2_fs_quota_read` — `quota.c:525`

三步：`sb_lock` 下 `get_or_create_quota + sb_quota_read` → 扫 `BTREE_ID_quotas` 调 `__bch2_quota_set` → 扫 `BTREE_ID_inodes`（`all_snapshots`）调上节函数。

权衡：只读扫描重建，不写 btree；sb 缺 quota 段则创建默认 7 天 timelimit，保证可挂载。

### 6.4 工具面：`enable:548 / disable:591 / remove:612 / get_state:653 / set_info:682 / get:755 / get_next:772 / set:820`

- `enable`：只读挂载拒；禁止开 acct（acct 挂载时定）；无对应 mount opt 的 ENFD 拒；成功置 sb  flag + `write_super`。
- `disable/remove`：清 flag；`remove` 要求对应 quota 已关，否则 `EINVAL`，再 `btree_delete_range(POS(type,0..U64_MAX))`。
- `set_info`：仅 `TIMER/WARNS` 可改，写 sb 后 `sb_quota_read` 回读内存。
- `get_next`：`genradix_for_each_from + memcmp ZERO_PAGE` 跳空洞，支撑 quotacheck 遍历。
- `set_quota_trans:793`：`peek_slot` 读旧值，按 `d_fieldmask` 合并 `>>9`（VFS 字节→sectors），再 `trans_update`。
  权衡：启停删查分离，删除按类型区间删；单位换算 `<<9/>>9` 集中在 `__bch2_quota_get:740` 与 set 路径，内存统一 sectors。

**可学**：重建只读扫描；工具职责分离；单位换算收口。

---

## 七、记账双轨与归并

磁盘 delta + 内存快照，提交钩子赋版本；11 类型（`accounting_format.h:105`）；启动双流归并；失配显式修复。

### 7.1 类型表 `BCH_DISK_ACCOUNTING_TYPES` — `fs/alloc/accounting_format.h:105`

`nr_inodes(0,1)` / `persistent_reserved(1,1)` / `replicas(2,1)` / `dev_data_type(3,3)` / `compression(4,3)` / `snapshot(5,3)` / `btree(6,3)` / `rebalance_work(7,1)` / `inum(8,3)` / `reconcile_work(9,2)` / `dev_leaving(10,1)`。`accounting_type_nr_counters`（`accounting.c:76`）做 EBUG 校验。

权衡：tag-union 复用 bpos 20 字节，可扩展；`dev_data_type` 三计数（buckets/sectors/fragmented）暴露碎片。

### 7.2 `bch2_disk_accounting_mod_normal` — `accounting.c:107`

签名：`(trans, k, d, nr)`；校验 `nr/TYPE`，replicas 按 dev 排序归一；在 `trans->accounting` 子缓冲内同 bpos 合并（`acc_u64s`），归零则 `memmove` 删项；否则 `subbuf_alloc + __accounting_key_init` 追加。

权衡：同事务同 key 合并，提交前消零，避免 journal 膨胀；排序归一保证 key 可比。

### 7.3 `bch2_disk_accounting_mod_gc` — `accounting.c:152`

GC 上下文直改内存（`mem_add_inlined(...,BCH_ACCOUNTING_gc)`），`need_mark_replicas` 时 `drop_locks_do(accounting_update_sb_one)` 后重试。

权衡：GC 重建走内存旁路，不污染正常 delta；superblock replicas 标记缺失显式补。

### 7.4 `bch2_accounting_mem_add_inlined` — `fs/alloc/accounting.h:183`

GC 未运行则丢 GC 更新；非 mem 类型直接回；normal 模式同步 `fs_usage_delta`（reserved/replicas/dev）与 percpu dev usage；`eytzinger0_find` 缺项则 `mem_insert` 后重试；最终 `this_cpu_add(e->v[gc][i], delta)`。

调用链：`commit.c:938` 提交路径 / `accounting.h:314` hook / `mod_gc:176`。
权衡：eytzinger 有序数组二分，读快写慢，适合“多读少增”；双槽 `v[0]/v[1]` 隔离正常与 GC 计数。

### 7.5 `bch2_accounting_accumulate` — `fs/alloc/accounting.h:33`

`min(nr)` 项相加，`bversion` 取 max。调用链：`write_buffer.c:205,713` / `journal_overlay.c:310` / `recovery.c:314` / `accumulate_newer_accounting_keys:956`。

权衡：delta 语义天然可交换，版本取 max 保全序；`accumulate_maybe_kill:48` 归零即 `maybe_kill` 回收 replicas 标记。

### 7.6 `bch2_accounting_read` 双流归并 — `accounting.c:1138`

清空内存表 → journal 按 btree 序定位 `[jk,end)` → btree/journal 同序迭代：旧版本 journal 标 `overwritten` 丢弃，同 key 累加（`accounting_read_key:823` 相邻合并），非 mem 类型跳段（`set_pos(predecessor(next))`）→ 压 gap → 排序 → 断言无重复 → `accounting_read_mem_fixups`。

权衡：btree 基值 + journal 增量一次归并，旧 delta 早丢；`with_journal` 关掉后手动走 journal，避免重复应用。

### 7.7 `bch2_gc_accounting_done` — `accounting.c:686` 与 `accounting_read_mem_fixups:1004`

两者皆比对 `dst(normal)` vs `src(gc)`，失配则 `fsck_err(accounting_mismatch)`，确认后 `commit_do(skip_accounting_apply, disk_mod(delta))` 补差；启动早期（`!may_go_rw`）还需手动 `mem_add + fs_usage`（737 行）。

`fixups` 另做：零项删除（O(N) 前向过滤，注释 1009 行点名修过 O(N*R) 旧实现）、`validate_late`（无效设备取反冲销，856/877 行）、下溢聚合限流告警并调度 `check_allocations`（1125 行）。

权衡：自愈必须显式确认（fsck_err），不静默改数；GC 双槽使“应有 vs 实有”可比。

**可学**：双轨版本化；归并累加；自愈显式。

---

## 八、设计启示

分离联动、分档收费、宽限硬限、检查后累、迁移回滚、只读重建、双轨归并。

1. 收费与记账分离，但以“预留→落账同一把锁 + 同一 qid”缝合，否则超卖。
2. 三档模式把“重建/预检/兜底”正交化，调用方对号入座，不复用布尔。
3. 锁内只做判定与累加，netlink/super 写锁外做（`flush_warnings`、`write_super`）。
4. 跨三类配额用固定序 + 两阶段（全审后加），chown 用差集过滤 + 成功才换属主。
5. 磁盘记账用 delta + 版本（journal 位即版本），内存用 eytzinger + percpu，启动双流归并，GC 双槽比对，修复走显式 fsck 确认。

---

## 复核途径

- `grep -n "bch2_quota_acct\|bch2_quota_check_limit\|bch2_quota_transfer\|bch2_fs_quota_transfer" fs/fs/quota.c fs/vfs/fs.c fs/vfs/io.h` 看收费与迁移。
- `grep -n "bch2_disk_accounting_mod_normal\|bch2_accounting_mem_add_inlined\|bch2_accounting_read\|bch2_gc_accounting_done" fs/alloc/accounting.c fs/alloc/accounting.h` 看记账双轨。
- `grep -n "BCH_DISK_ACCOUNTING_TYPES" fs/alloc/accounting_format.h` 看 11 类型。
