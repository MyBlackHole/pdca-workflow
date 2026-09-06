# bcachefs EC 纠删专题学习报告（T0516）：代码级精讲

> 精读 `fs/data/ec/create.c`（2222 行，含 `DOC_LATEX` 3–46）、`io.c`（645 行）、`create.h`（216 行）、`trigger.c`（584 行）。
> 行号/签名均经 `Read`/`grep -n` 核实，10 行内片段原文摘录。事实源为现源码（`git log` 顶部为 `9281beaa2 ec: refuse an oversized target group…`）。
> 原报告八节结构保留；与现源码不符处以【纠偏】注明。

---

## 一、全景：后台整桶编码路线

设计原语（`create.c:3-46 DOC_LATEX`）：前台多副本写 → reconcile 攒桶 → 后台取数桶集 → 分配 parity 桶 → RS 算 parity → 写 parity → btree 原子改 extent 指针（删多余副本，加 parity 指针加重建读标志）。

### 1.1 `ec_stripe_head` 分配入口 — `bch2_ec_stripe_head_get`（`create.c:1919-2040`）

- 签名：`struct ec_stripe_head *bch2_ec_stripe_head_get(struct btree_trans *trans, struct alloc_request *req, unsigned algo)`
- 参数：`trans`（持事务锁上下文）；`req`（`target/ec_replicas/ec_max_data_blocks/watermark/cl`）；`algo`（RS 算法号）。
- 返回：`h`（按 `disk_label+algo+redundancy+watermark` 复用的头）；`NULL`（无需 EC/设备不足回退副本）；`ERR_PTR`（需上层重试/报错）。
- 调用链：`sector allocator → bch2_ec_stripe_head_get → __bch2_ec_stripe_head_get(1861) → ec_new_stripe_alloc(1006) → stripe_alloc_or_reuse(1687) → bch2_ec_stripe_buf_init(io.c:144)`；满块后 `bch2_ec_stripe_head_put(1850) → ec_stripe_new_set_pending(1775)`。
- 片段（`create.c:1943-1946`）：
```c
unsigned active = min_t(unsigned, h->nr_active_devs, BCH_BKEY_PTRS_MAX);
unsigned nr_data = min_t(unsigned, active - h->redundancy,
                         req->ec_max_data_blocks ?: ~0U);
```
- 权衡：按四元组复用头避免每写分配；`nr_data` 取 `active-redundancy`、`ec_max_data_blocks`、故障域上限三者最小，宽条带省空间但放大“整条锁死”与重建 IO。

### 1.2 头查找与设备刷新 — `__bch2_ec_stripe_head_get`（`create.c:1861-1917`）+ `ec_stripe_head_devs_update`（`1799-1827`）

- 签名：`static struct ec_stripe_head *__bch2_ec_stripe_head_get(trans, disk_label, algo, redundancy, watermark)`；`static void ec_stripe_head_devs_update(c, h)`。
- 参数/返回：`redundancy==0` 直接 `NULL`（纯副本）；`insufficient_devs` 时解头锁返 `NULL`；`rw_devs_change_count` 变化才重算 `devs/blocksize`。
- 片段（`create.c:1810,1819-1820`）：
```c
h->insufficient_devs = h->nr_active_devs < h->redundancy + 2;
h->insufficient_devs |= nr_domains < h->redundancy + 2;
```
- 权衡：`redundancy+2` 下限（单数据块+parity 不如副本，直接拒绝）；设备数与故障域数双条件，后者是硬约束（见 `__new_stripe_alloc_buckets:1077-1082`）。

### 1.3 可建性预判 — `bch2_can_form_ec_stripe`（`create.c:874-900`）

- 签名：`bool bch2_can_form_ec_stripe(c, target, redundancy)`；返回 `dev_mask_nr>=redundancy+2 && nr_domains>=redundancy+2`。
- 调用链：`reconcile → can_form →（false 则不排队，避免空转重写 extent）`。注释明示：只建模设备数会让分配器拒绝，浪费一次 extent 重写。
- 权衡：用便宜的 mask/域计数预判代替真实分配；`TARGET_GROUP>U8_MAX` 直接 false（`888-889`，对应 `9281beaa2` 修复折叠到 label 0 的误判）。

### 1.4 设备集计算 — `bch2_disk_label_ec_devs`（`828-848`）/ `pick_blocksize`（`803-825`）/ `bch2_disk_label_ec_rw_member_devs`（`909-926`）

- 签名：`unsigned bch2_disk_label_ec_devs(c, disk_label, devs*, blocksize)` 返回选定 blocksize；`pick_blocksize` 取众数（平票取小）；`rw_member_devs` 只看配置态 `rw` 不看在线态。
- 片段（`create.c:844-846`）：
```c
for_each_member_device_rcu(c, ca, devs)
        if (ca->mi.bucket_size != blocksize)
```
- 权衡：统一 bucket_size 才能整桶对齐编 parity；`can_widen` 用 RW-member 视图（`trigger.c:341-354` 同理），瞬时掉线不触发全盘重写。

**可学**：路线选择决定复杂度。后台整桶编码把写洞/RMW/部分写一次性消灭，代价是多副本→EC 窗口期的空间放大。

---

## 二、无写洞的数学保证

DOC 原文（`create.c:29-30`）：“parity 一次算定于不可变数据 + extent 更新是原子 btree 操作 → 无写洞”。

### 2.1 提交核心 — `__ec_stripe_create`（`create.c:563-657`）【纠偏：原报告写 602-649，实为 563-657；校验/提交/落盘全在此】

- 签名：`static int __ec_stripe_create(struct ec_stripe_new *s)`；返回 0/`s->err`/校验写错/`stripe_create_device_removing`。
- 调用链：`ec_stripe_create(696) ← stripe_get_iorefs(676) 持写 ref；内部 → zero_out_rest(528) → validate old(606) → generate_ec/generate_checksums → block_io(write) → ec_stripe_key_update(169)+logged_op_start → stripe_update_extents(464) → logged_op_finish`。
- 片段（`create.c:643-649`）：
```c
try(bch2_trans_commit_do(c, &s->res, NULL,
                         BCH_TRANS_COMMIT_no_check_rw|
                         BCH_TRANS_COMMIT_no_enospc,
        ec_stripe_key_update(trans, &s->new_stripe.key) ?:
        __bch2_logged_op_start(trans, &op.k_i)));
int ret = stripe_update_extents(c, s);
```
- 权衡：先提交 stripe 键 + logged_op（崩溃可 `bch2_resume_logged_op_stripe_update:484` 重放），再逐 extent 改指针（每 extent 独立 commit，`stripe_update_extent:364`），原子性由“数据不动 + 单键提交 + 可重放日志”合成，而非大事务。

### 2.2 防设备拆除复活 — `stripe_has_removing_dev`（`552-561`）+ `stripe_get/put_iorefs`（`676-691/659-665`）

- 签名：`static bool stripe_has_removing_dev(c, v)`（RCU 扫 `ca->removing`）；`static int stripe_get_iorefs(c, s, cas[])`（逐盘 `bch2_dev_get_ioref(WRITE)`，失败回滚已持 ref 返 `stripe_create_device_offline`）。
- 片段（`create.c:592-593`）：`if (stripe_has_removing_dev(c, v)) return ...device_removing;`
- 权衡：提交前验 `removing` + 创建期全盘写 ref，防“拆除 walk 已过、seal 后复活旧盘指针”；只验新键指针（注释 `583-590`），迁出盘的 create 仍放行。

### 2.3 指针级原子改写 — `stripe_update_extent`（`230-374`）

- 签名：`static int stripe_update_extent(trans, old_stripe, new_stripe, old_block, new_block, new_blocknr, bp, stats, res, last_flushed)`；返回 0（四类跳过也返 0 并计 stats：`bp_to_deleted/no_match/cached/done`）。
- 关键分支：`bp.v->level!=0` 报 `erasure_coding_found_btree_node`（`242-256`，EC 桶混入 btree 节点属不一致）；`!has_device/mismatch→no_match`；`has_ec&&同新条→0`；陈旧 stripe_ptr 用 `ret_log_fsck_err` 摘除（`301-304`）；`cached` 跳过；正常路径重组 bkey、换 dev/offset/gen、插 `stripe_ptr{block,redundancy,idx}`（`322-347`）、`drop_extra_durability` 降到 `data_replicas`（`357`）、单 key commit（`362-366`）。
- 权衡：逐 extent 小事务 + 详细 fail stats + trace，可重试可观测；`bkey_drop_stripe_ptr(207-228)` 按 `(idx,block)` 精确摘（注释 `213-220`：同条双块 extent 按 idx 粗删会误伤兄弟块）。

**可学**：“不可变 + 原子切换 + 可重放意图日志”优于“可变 + 兜底日志”。

---

## 三、Stripe 生命期与复用

DOC（`32-37`）：成条后桶整体锁定至全死/迁走；copygc 整条疏散。

### 3.1 复用判定 — `may_reuse_stripe`（`1448-1472`）+ `get_old_stripe`（`1474-1540`）

- 签名：`static bool may_reuse_stripe(c, new, old)`；`static int get_old_stripe(trans, new, idx)`（1=可复用并已 `reassemble` 旧键，0=跳过，err=需重启/提交）。
- 判定：`disk_label/algorithm/nr_redundant` 三者必须等（`1451-1454`）；`blockcount!=0` 的活块（含 moving）计 `live_data`，`live_data+1<=新nr_data`（留一新块位，`1468`）；坏/疏散盘不占 `devs_may_alloc`，剩余可分配盘 `>nr_parity`（`1471`）。
- 片段（`create.c:1535-1538`）：
```c
bool ret = may_reuse_stripe(c, new, old.v) &&
        bch2_stripe_handle_tryget(c, &new->old_stripe_handle, idx);
if (ret) bkey_reassemble(&new->old_stripe.key.k_i, k);
```
- 权衡：标签算法冗余一致才复用是正确性门；`can_widen` 过高只降不升（`1527-1532`），升格交 `reconcile_scan_stripes`，与在线抖动解耦。
- 【纠偏】原报告“读到即折叠/halving”：现源码无 `halving`/折叠符号（`grep halving` 零命中）。对等机制是 `init_new_stripe_from_old(1542)` 的位图锚定（下节）。

### 3.2 旧条锚定 — `init_new_stripe_from_old`（`1542-1580`）+ `stripe_reuse`（`1582-1601`）

- 签名：`static void init_new_stripe_from_old(c, s, repair)`；先放掉初分配桶（防与旧块同盘冲突，`1554-1557`），再按 `blockcount` 锚活块：健康盘→`blocks_gotten`，坏/疏散盘→`blocks_moving`，统标 `blocks_allocated`，填 `old_block_map`。
- 调用链：`stripe_reuse` 扫 `BTREE_ID_lru/LRU_STRIPE_FRAGMENTATION`（`1588-1591`）→ `get_old_stripe` 逐条试 → 命中即 `init_...`。
- 权衡：只补新块 + 只移 parity/坏块槽，好块零拷贝；`BUG_ON(old_blocks_nr+!repair>new_nr_data)`（`1575`）保证复用不超宽。

### 3.3 分配 — `__new_stripe_alloc_buckets`（`1064-1176`）/ `new_stripe_alloc_buckets`（`1320-1446`，含 shrink）/ `stripe_reallocate_outliers`（`1189-1295`）/ `stripe_idx_alloc`（`1603-1641`）

- `__new_…`：先 parity（`BCH_DATA_parity`）后 data（`BCH_DATA_user`），逐块调 `bch2_bucket_alloc_set_trans` 并以 `stripe_blocks_centroid(1042)`（设备分位均值，异构盘可比）为 `target_frac`；`failure_domains_required=true`（`1082`）硬排斥同域盘；已得块对应盘清出 `devs_may_alloc`。
- `new_…`：失败且 `may_shrink` 时，若 `stripe_will_not_allocate(1308)`（watermark==copygc 或 copygc 在剩余盘上跑不动，`1297-1306`）则收缩：`need=moving+parity+(有moving?0:1)+(无旧条?1:0)`，够数则下移 parity 槽改 `nr_blocks/nr_redundant`（`1389-1411`），不够返 `stripe_insufficient_devices` 回退副本；单数据块条带被注释明判定为不如副本（`1365-1368`）。
- `reallocate_outliers`：全分配后按“相对其余块 MAD”找 `dist>2*mad` 且超一桶分位的离群新块，`alloc_nowait` 重试，减半距离才换（`1281`），否则保留——只优化不制造失败。
- `stripe_idx_alloc`：线性扫 `stripes` 空槽（`POS(0,1)..U32_MAX`，`hint` 游标），`handle_tryget` 占位 + `mem_alloc`，满返 `ENOSPC_stripe_create`。
- 权衡：质心共位降跨区寻道；shrink 保进度；outlier 纯 best-effort。

### 3.4 删除与 GC 协作 — `ec_stripe_delete`（`110-136`）/ `bch2_ec_stripe_delete_work`（`142-158`）/ `bch2_trigger_stripe:367-370`

- 空条（`lru_pos==EMPTY`）且未 open 才删；`is_open` 下删非空直接 `fs_inconsistent`；删动作走 `workqueue` 扫 `lru/FRAGMENTATION`，`trigger` 内空条转 `bch2_btree_delete`（须经 `trans_update` 走 write-buffer flush，注释 `360-366`）。
- 权衡：删除是异步 GC，`open` 哈希是删/复用的互斥锁（见第五节）。

**可学**：大单元整体生命周期；复用必判一致性；GC 与分配器共享同一 open 视图。

---

## 四、引用计数与状态机（原“三态”条）

【纠偏：原报告称 `open/filling/in_flight` 显式三态 + `8ca5d6212` 富 dump。现 `create.h:34-73` 无三态枚举，只有 `allocated/mem_allocated/old_mem_allocated/pending` 四 bool + `seq/err`；`grep filling|in_flight` 零命中（仅 `in flight:` 打印头）。状态机由“四 bool + 双引用 + open 哈希”承担，下文按现源码精讲；富 dump 实为 `bch2_new_stripe(s)_to_text(1711-1766)`，commit 哈希无法在离线树核实】

### 4.1 双引用 — `ec_stripe_new_get/put`（`create.h:169-198`）+ `ec_stripe_new`（`create.h:34-73`）

- `ref[STRIPE_REF_io]`：累积写持有，归零时赋 `seq=atomic64_inc_return(stripe_new_seq)`、唤醒 `stripe_new_wait`、投递 `bch2_ec_stripe_create_start(775)`（workqueue 异步 `ec_stripe_create`）。
- `ref[STRIPE_REF_stripe]`：条带持有，归零时 `bch2_ec_stripe_new_free(544)`（摘 new-buckets 哈希、放双 handle、`kfree`）。
- 初始各 1（`1022-1023`）；`ec_stripe_new_set_pending(1775)` 把头脱钩、挂 `stripe_new_list`、放 io ref；`ec_stripe_create(762)` 尾放 stripe ref。
- 片段（`create.h:191-193`）：`s->seq = atomic64_inc_return(&c->ec.stripe_new_seq); wake_up(...); bch2_ec_stripe_create_start(c, s);`
- 权衡：IO 与条带生命周期解耦，`seq` 即 commit-ready 标记（`init.c:245` 同述），`flush_outstanding` 可等 seq 而不持大锁。

### 4.2 Open 哈希互斥 — `bch2_stripe_is_open/handle_tryget/handle_put`（`trigger.c:550-583`）+ `bch2_stripe_new_buckets_add/del`（`514-537`）

- 签名：`bool bch2_stripe_handle_tryget(c, handle, idx)`（`BUG_ON(!idx)`，持 `stripes_new_lock` 查重，成功插哈希）；`void bch2_stripe_handle_put`（摘哈希清零）；`bool bch2_stripe_is_open` 供删路径查询。
- 调用链：`stripe_idx_alloc/get_old_stripe/bch2_stripe_repair:2124` 占位 → `bch2_trigger_stripe:367` 空条见 open 则跳删 → `get_old_stripe:1485` 持 intent 锁直至 open 防删 competitive。
- 权衡：小哈希 + 自旋锁做存在性栅栏，比持 btree 锁轻；`buckets` 哈希防 rebalance 与新建条带竞用同桶。

### 4.3 可观测 — `bch2_new_stripe_to_text`（`1711-1734`）

- 打印 `idx/blocks(data+parity)/allocated/ref_io/ref_stripe/watermark/blocks[]/closure余数/old余数`，`bch2_new_stripes_to_text` 另打印 `stripe_buf_bytes/limit` 与各 head/`in flight` 链。
- 权衡：异步对象“为何不完成”必须一屏可答：ref 不归零看 IO，closure 余数看块 IO，pending/allocated 看分配。

**可学**：状态机不必枚举三态，但必须显式（四 bool + 双 ref + open 哈希缺一不可）；富 dump 是可观测刚需。

---

## 五、先算后写与二次校验（原“先验后算”条，措辞纠偏）

【纠偏：现 `__ec_stripe_create:602-613` 顺序是**先验旧条（validate old）→ 换入旧数据（swap）→ 生成 parity+校验 → 只写动过数据块 + parity → 同步后验写错**；“验算分离”成立，但“先验后算”易误读为先验新条，实为先验**旧**条再算新 parity】

### 5.1 旧条先验与换入 — `__ec_stripe_create:602-613` 调 `bch2_stripe_buf_validate_msg`（`io.c:393-423`）

- 片段（`create.c:606-610`）：
```c
try(bch2_stripe_buf_validate_msg(c, &s->old_stripe, true));
for (unsigned i = 0; i < s->old_blocks_nr; i++)
        swap(s->new_stripe.data[i], s->old_stripe.data[s->old_block_map[i]]);
```
- `validate_msg(is_open=true)`：`closure_sync` 后全块验 csum（`io.c:363`），失败走 `bch2_ec_do_recov` 重构；`is_open` 下 `ptr_stale` 计 fsck（`383-384`，pin 住的条不可能 stale，见则不一致）；`stale_race`（未 pin 的陈旧读竞态，`306-312`）降为 `stripe_reconstruct_stale_race`（`388-389`）供上层转 `data_read_ptr_stale_race`。
- 权衡：复用旧块前必须先证明旧条可读，否则污染新 parity；`is_open=true` 收紧 stale 判定（读路径用 false，见七）。

### 5.2 生成与定向写 — `bch2_ec_generate_ec`（`io.c:271-277`）/ `bch2_ec_generate_checksums`（`213-227`）/ `bch2_ec_block_io[_range]`（`io.c:451-521`）

- `generate_ec`：`raid_gen(nr_data, nr_redundant, bytes, data)`；`np==1→raid5_recov` 异或，`np==2→raid6_gen_syndrome`，`np>2 BUG`（`io.c:67-74`，即最多 RAID6 双 parity）。
- `generate_checksums`：按 `csum_granularity_bits`（初值 `ilog2(encoded_extent_max>>9)`，`ec_stripe_key_init:979`，超 `BKEY_VAL_U64s_MAX` 则放粗，`996-1001`）逐块逐段 `crc32c` 入键。
- 写：仅 `blocks_moving` 数据块（`621-623`）+ 全部 parity（`626-627`），`closure_sync` 后验 `PRE_RECOV` 失败数（写错直接记 `err[]`，`ec_block_endio:441-444`），非零返 `ec_block_write`（`630-633`）。
- 片段（`create.c:595-600`）：新数据块尾零填充（`zero_out_rest_of_ec_bucket:528` 按 `bucket_size-sectors_free` memset + 单块 range 写）。
- 权衡：好块零重写（降写放大）；零填保证 parity 确定性；校验粒度可放粗以塞下大条带键。

### 5.3 内存配额 — `bch2_ec_stripe_buf_init`（`io.c:144-190`）

- `offset/size` 按 csum 粒度对齐（`154-156`）；配额 `totalram*ec_stripe_buf_limit/100`，超限 `closure_wait(stripe_buf_wait)` 返 `stripe_buf_mem_blocked`（`163-169`，create 侧 `req->cl` 挂等待）；`exit(115)` 先 `closure_sync` 防 UAF，再扣 `stripe_buf_bytes` 唤醒等待者。
- 权衡：内存背压进分配器等待链，而非 OOM。

**可学**：复用旧数据必先验；失败路径短路（`s->err` 在 `__ec_stripe_create:569` 首查），不污染好数据。

---

## 六、修复：单坏即判级 + 先疏散后重建

【纠偏：原报告写 `bch2_stripe_repair:2044-2112`＋`do_retry_stripes` 压延队列。现源码 `bch2_stripe_repair` 为 `2052-2222`；`grep do_retry_stripes` 零命中——重试/排空由 `stripe_needs_block_evacuate` 错误码交外层 `moving_context` 驱动，无名曰 `do_retry` 的队列函数】

### 6.1 降级判定 — `stripe_degraded`（`2044-2050`）

- 签名：`static bool stripe_degraded(c, s)`；任一 `ptrs[i].dev` 经 `bch2_dev_bad_or_evacuating` 即 true（阈值确为 1，原报告此点正确）。
- 调用链：`bch2_stripe_repair:2068` 首判，非降级记 `stripe_repair_race` trace 返 0——并发后来者无害化（原报告此点正确，行号现为 `2069-2071`）。
- 另：`BUG_ON(!intent_locked)`（`2065`）与 `get_old_stripe` 同纪律，防与 trigger 删空条竞态。

### 6.2 活块清点与疏散前置 — `bch2_stripe_repair:2074-2113`

- 按 `blockcount` 数活数据块（`2076-2077`）；零活直接返 0（空条交 trigger 删）；`need_evacuate = live_data+redundant - dev_mask_nr`（`2085-2086`，同尺寸 `bch2_disk_label_ec_devs` 视图）。
- 缺口时取最小活块逐个 `bch2_evacuate_data`（坏盘指针有效）/`bch2_evacuate_ec_orphan`（`INVALID` 孤儿，`2099-2110`），返 `stripe_needs_block_evacuate` 让外层腾出设备后重入。
- 片段（`2085-2086`）：`unsigned need_evacuate = max(0, (int)(nr_live_data_blocks + old_s->nr_redundant) - (int) dev_mask_nr(&devs));`
- 权衡：设备不足不硬建（硬建会降冗余或同域放块，违硬约束），先疏散活块再重建。

### 6.3 重建提交 — `bch2_stripe_repair:2115-2221`

- `ec_new_stripe_alloc(nr_live_data_blocks, nr_redundant)` 窄条重建；`handle_tryget(old_idx)` 失败（有人先手）即 `kfree` 返 0（`2124-2128`，二次无害化）；`init_new_stripe_from_old(repair=true)`（`2132`，坏块进 `blocks_moving`）；`stripe_buf_init(old+new)+stripe_idx_alloc(2137-2146)`；`new_stripe_alloc_buckets(may_shrink=true)` 补新桶（`2168`）；挂 `moving_context`（`write_sectors/write_ios/cl`，`2208-2213`）后投递（`2220` 放 io ref，复用 `__ec_stripe_create` 同一提交流水）。
- 权衡：repair 与 create 共用 `__ec_stripe_create`，修好即新条带 + `can_widen` 初值（`ec_stripe_key_init:989-994`），可被加宽逻辑接管。

**可学**：阈值显式（1 坏即修）；并发修后来者无害化（双 tryget + race trace）；设备不足先疏散后重建。

---

## 七、读路径：直读优先，重构兜底

DOC（`39-45`）：先直读数据桶，失败（离线/校验错）才重构读（存活块+parity，RS 解码，映射查 stripes 树）。

### 7.1 重构读 — `bch2_ec_read_extent`（`io.c:542-645`）

- 签名：`int bch2_ec_read_extent(trans, rbio, orig_k, msg)`；前置 `trans_relock`（保 extent 锁，`550`）→ `get_stripe_key_trans(531)`（`BTREE_ITER_slots` 读键，`reassemble`，非 stripe 返 `-ENOENT`）→ `bch2_ptr_matches_stripe`（`568` 指针漂移直接 `stripe_reconstruct`）→ 越界检查（`575-581`）→ RCU 预扫 stale（`594-602`，持 btree 锁时 key 必 live，stale 即 alloc 不一致，计 `stale_dirty_ptr` + 跑 `check_allocations`，`604-611`，此处**不**分 is_open，注释 `583-592`）→ 解锁 → `buf_init(offset,size)`（仅分配所读区间，省内存）→ `bch2_stripe_buf_read(523)` 全条并发读 → `validate(false)` → 拷贝目标块（`631-632`）。
- `stale_race→data_read_ptr_stale_race`（`627-628`）交上层按“删竞态”重试，而非报错。
- 权衡：重构读是慢路但只读所需区间；锁内只做判定，IO 前必解锁。

### 7.2 校验与恢复 — `bch2_stripe_buf_validate`（`359-391`）/ `bch2_ec_do_recov`（`281-301`）/ `raid_rec`（`76-107`）

- `validate`：先全块 csum（`363`，跳过已 IO 错块，`242`），零失败速返；否则 `do_recov`：`PRE 失败数>redundant` 直接 `insufficient_blocks`（`287-288`）；仅收集**数据块**失败下标（`290-292`，parity 失败由 `raid_rec` 内部分支覆盖 `p/q` 组合，`87-103`），调 `raid_rec`（0/1/2 坏ikh：单坏按 `<nd+1` 分 raid5/regen-q，双坏分 data+data/data+p/data+q/p+q 四路），再对数据块二次验 csum（`296`，防“解对但错”），仍坏返 `stripe_read_csum_err`。
- 【纠偏：原报告“超冗余直接报（`bch2_stripe_buf_validate`）”正确，但漏了关键细节——只对数据块做 POST 二次校验（`validate_checksums(data_only=true)`），parity 不复验】
- 权衡：csum 先行（静默损坏可定位到块并记 `BCH_MEMBER_ERROR_checksum`，`260-262`），RS 只解必须解的块。

### 7.3 报错节流 — `bch2_stripe_buf_validate_msg`（`393-423`）+ `stripe_buf_errs_to_text`（`343-357`）

- 零错零恢复静返；`stale_race` 原样上抛不打日志；成功重构记 `successful reconstruct`（`414`）， hard 错记 `error:`，统一 `msg.m.suppress = bch2_ratelimit(c)`（`416/419`）。
- 【纠偏：原报告“仅离线致失败静默（`88209f67b`）/成功降级写静默（`a088d5bca`）”在现源码无对应符号（`grep burst|silent` 零命中；`io.c` 仅 `ratelimit suppress` 两处 + `read.c:770` 同款）。现机制是“成功重构与硬错共用 ratelimit 抑制”，非按离线/降级分类静默；commit 哈希离线无法核实】

**可学**：快路直读、慢路重构；预期竞态（stale_race）转重试码；报错必须 ratelimit，保错误预算。

---

## 八、设计启示

1. 后台整桶：以前台空间换一致性简单性（DOC 3–30）。
2. 不可变 + 原子切换 + 意图日志：`__ec_stripe_create:643-654` 三段提交。
3. 大单元生命期：整条锁死 + copygc 整条疏散 + trigger 空删（`trigger.c:367-370`）。
4. 状态显式化：四 bool + 双 ref（`create.h:50-56,169-198`）+ open 哈希（`trigger.c:556-583`）；富 dump（`create.c:1711-1766`）。
5. 复用旧数据必先验旧条（`create.c:606`），只写动过块 + parity（`621-627`）。
6. 分配三约束：同尺寸桶、异故障域、质心共位（`1064-1176,1189-1295`）；不足则 shrink 或回退副本。
7. 阈值显式：1 坏即修（`2044-2050`）；修前先疏散（`2085-2113`）；并发无害化（`2069-2071,2124-2128`）。
8. 读分级：直读 → 重构（`io.c:542`）→ stale_race 重试；报错节流（`393-423`）。
9. 域感知 `can_widen`：RW-member 视图 + trigger 刷新（`trigger.c:341-354`）+ 复用降格（`create.c:1527`），设备增减可加宽。

---

## 复核途径（均已执行，禁编造）

- `sed -n 3,46p fs/data/ec/create.c` 通读 DOC_LATEX。
- `grep -n "may_reuse_stripe\|get_old_stripe\|__ec_stripe_create\|bch2_stripe_repair\|stripe_degraded\|ec_stripe_new_get\|ec_stripe_new_put" fs/data/ec/create.c fs/data/ec/create.h` 定位创建/复用/修复/引用。
- `grep -n "bch2_ec_do_recov\|bch2_stripe_buf_validate\|raid_rec\|bch2_ec_read_extent\|stripe_buf_mem_blocked" fs/data/ec/io.c` 定位校验/恢复/读/配额。
- `grep -n "bch2_trigger_stripe\|mark_stripe_bucket\|bch2_stripe_is_open\|bch2_stripe_handle_tryget" fs/data/ec/trigger.c` 定位触发/记账/open 互斥。
- `grep -rn "halving\|do_retry_stripes\|in_flight\|filling" fs/data/ec/` 验证原报告三处表述零命中（已纠偏）；`git log --oneline -5 -- fs/data/ec/` 确认引用 commit 哈希不在现检出顶部（已纠偏）。

## 本次纠偏清单

1. `__ec_stripe_create` 行号 `602-649`→`563-657`；`bch2_stripe_repair` 行号 `2044-2112`→`2052-2222`。
2. “open/filling/in_flight 显式三态”→ 实为四 bool + 双引用 + open 哈希，无三态枚举。
3. “`do_retry_stripes` 压延队列”→ 无此符号，重试由 `stripe_needs_block_evacuate` 交 `moving_context` 驱动。
4. “读到即折叠/halving”→ 无此符号，对等机制为 `init_new_stripe_from_old` 位图锚定。
5. “仅离线静默/降级写静默 + 四 commit 哈希”→ 现源码为 `ratelimit suppress` + `stale_race` 转重试，哈希离线不可核实。
