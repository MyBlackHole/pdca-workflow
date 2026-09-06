# bcachefs superblock 管理专题学习报告（T0529）·代码级精讲版

> 事实源：`/home/black/Documents/bcachefs-tools/fs/sb/io.c`（1832 行）、`errors.c`（424 行）、`members.c`（1014 行）、`downgrade.c`（539 行），辅引 `fs/sb/clean.c`、`fs/sb/io.h`、`fs/bcachefs_format.h`。
> 所有函数名与行号均经 `grep -n` / `Read` 核实。八节结构与原报告一一对应，每节逐函数精讲：签名 / 参数 / 返回 / 调用链 / ≤10 行代码片段 / 权衡。

符号约定：`bch2_sb_field_resize(x, name, u64s)` 为 `fs/sb/io.h:47` 宏，展开为 `bch2_sb_field_resize_id`（`io.c:387`）；`bch2_sb_field_get` 为 `io.h:42` 宏，展开为 `bch2_sb_field_get_id`（`io.c:256`）。`BCH_SB_SECTOR=8`、`BCH_SB_LAYOUT_SECTOR=7` 见 `fs/bcachefs_format.h:1147,1160`；布局 `sb_offset[61]` 见同文件 `:1157`。

---

## 一、全景：超块即真相源头

超块是挂载的第一信任锚：三副本防撕裂（`io.c:32-95` DOC 注释明示威胁模型：断电撕裂写 > 介质错误/比特腐烂 > bootloader 共存与大物理块 RMW > 整盘丢失），序号 `seq` 仲裁最新，全拷贝选优读。核心矛盾：单点损坏不能丢真相，并发写入不能撕裂。

真相源头 = 多副本 + 序号仲裁 + 校验，缺一不可：无副本则单点即丢；无序号则副本分歧无法定序；无校验则撕裂写入会被当成真相。

### 1.1 `validate_sb_layout`（`io.c:435`）——布局守门员

- 签名：`static int validate_sb_layout(struct bch_sb_layout *layout, struct printbuf *out)`
- 参数：`layout` 待验布局（512 字节，`BUILD_BUG_ON(sizeof…!=512)`，`io.c:441`）；`out` 错误文本。
- 返回：0 有效；负 `BCH_ERR_invalid_sb_layout*`。
- 调用链：`read_layout_sector（io.c:877）→ validate`；`read_super_and_backups（io.c:1060/1064）→ validate`；`bch2_sb_validate（io.c:627）→ validate`。三路共用同一守门函数。
- 代码片段（`io.c:471-483`，重叠检查）：
```c
prev_offset = le64_to_cpu(layout->sb_offset[0]);
for (i = 1; i < layout->nr_superblocks; i++) {
    offset = le64_to_cpu(layout->sb_offset[i]);
    if (offset < prev_offset + max_sectors) { /* 重叠即拒 */
        prt_printf(out, "Invalid superblock layout: superblocks overlap\n" ...);
        return -BCH_ERR_invalid_sb_layout_superblocks_overlap;
    }
    prev_offset = offset;
}
```
- 权衡：布局体故意极简（magic + 偏移表，无校验和，独占 512B 扇区，见 `io.c:50-56` 注释），把“能找到”放在“能验对”之前；重叠/数量/类型检查全是纯内存比较，零 IO 成本。代价是布局扇区本身坏了只能走第二逃生阀（定点 `opts.sb` 或末端备份）。

### 1.2 `bch2_sb_compatible`（`io.c:488`）——版本准入

- 签名：`static int bch2_sb_compatible(struct bch_sb *sb, struct printbuf *out)`
- 参数/返回：验 `version` / `version_min` 双字段；不兼容返回 `-BCH_ERR_invalid_sb_version`。
- 调用链：`read_one_super（io.c:842）` 逐槽快筛 → `bch2_sb_validate（io.c:529）` 全量复验。读路径验两次：第一次在 checksum 之前（fail-fast，坏版本不浪费校验），第二次在顶层统一报错。
- 片段（`io.c:515-521`）：
```c
if (version_min > version) {
    prt_str(out, "Bad minimum version ");
    ...
    return -BCH_ERR_invalid_sb_version;
}
```
- 权衡：`min>max` 这种不可能状态直接拒挂，宁可误拒不冒险挂载；`no_version_check` 选项留调试后门但默认关闭。

### 1.3 `bch2_sb_validate`（`io.c:526`）——总装配线

- 签名：`int bch2_sb_validate(struct bch_sb *sb, struct bch_opts *opts, u64 read_offset, enum bch_validate_flags flags, struct printbuf *out)`
- 参数：`read_offset` 防“读 A 盘得 B 盘超块”（`io.c:567-572` 比对 `sb->offset`，写校验 `BCH_VALIDATE_write` 时跳过）；`flags` 区分读写两态。
- 返回：0 / 各类 `BCH_ERR_invalid_sb_*`。
- 调用链：读：`read_super_and_backups（io.c:1083）`；写：`__bch2_write_super（io.c:1297）` 逐盘预验，不合格 `bch2_fs_inconsistent` 后直接 `return 0`（拒绝发出 IO，见 3.4）。
- 装配顺序（`io.c:529-668`）：compatible → incompat feature 位 → UUID 非零 → offset → nr_devices 上限 `BCH_SB_MEMBERS_MAX` → dev_idx → time_precision → 版本钳位修复 → layout → 通用段边界 → **members 优先校验（`io.c:643-653`，注释 `members must be validated first`）** → 其余各段分发 → 写态追加 `member.seq == sb.seq`（`io.c:662`）。
- 权衡：members 先行是因为后续段（如 disk_groups 引用的 group id、dev_has_data）语义依赖成员表；写态才查 seq 一致是因为读态允许历史副本（seq 落后是正常的仲裁输入，不是错误）。

**可学**：真相源头必须多副本加序号仲裁再加分层校验（布局→版本→段边界→成员→各段），缺一不可；校验顺序按依赖拓扑排。

---

## 二、三副本与选优读

布局三副本（主 + 紧随 + 盘尾，`io.c:36-38`），读主扇区取内嵌布局，失败读独立布局扇区 7；轮询全槽取最高序号，平局后扫者胜；定点调试支持（`opts.sb`）。

### 2.1 `read_one_super`（`io.c:821`）——单槽读取+五道关

- 签名：`static int read_one_super(struct bch_sb_handle *sb, u64 offset, struct printbuf *err)`
- 参数：`sb` 句柄（含 `bio`/`bdev`/`buffer_size` 复用缓冲）；`offset` 扇区号。
- 返回：0 且 `sb->seq` 置位；否则负 errcode。
- 调用链：`read_backup_supers（io.c:932/962）`、`read_super_and_backups（io.c:1047/1057）`。
- 五道关（按 `io.c:823-873` 顺序）：① `submit_bio_wait` 同步读 → ② magic（`BCACHE_MAGIC`/`BCHFS_MAGIC` 二选一，兼容旧魔数）→ ③ `bch2_sb_compatible` 快筛 → ④ `vstruct_bytes` vs `512<<min(MAX, sb_max_size_bits)` 防超大 → 缓冲不够则 `bch2_sb_realloc` 后 `continue` 重读 → ⑤ csum 类型合法（拒绝加密型/越界型）→ `csum_vstruct` 比对， mismatch 报 `-BCH_ERR_invalid_sb_csum`。
- 片段（`io.c:853-856`，动态扩缓冲重读）：
```c
if (bytes > sb->buffer_size) {
    try(bch2_sb_realloc(sb, le32_to_cpu(sb->sb->u64s)));
    continue;
}
```
- 权衡：`while(true)` 重读环只为“超块比预期大”一种情况服务，避免调用方处理半包；`XXX: verify MACs`（`io.c:865`）明示加密超块暂不验 MAC，留缺口但不阻塞。

### 2.2 `read_layout_sector`（`io.c:877`）——扇区 7 逃生阀

- 签名：`static int read_layout_sector(struct bch_sb_handle *sb, struct bch_sb_layout *layout, struct printbuf *err)`
- 要点：复用 `sb->sb` 缓冲做 512B 对齐 IO（`io.c:883-887` 注释明示 layout 自身不对齐），`memcpy` 出来再 `validate_sb_layout`。只在主超块不可读时调用（`io.c:1064`）。
- 权衡：复用缓冲省一次分配，但要求调用时 `sb->sb` 已 `bch2_sb_realloc(sb,0)`（`io.c:1034`）；注释（`io.c:42-48`）承认布局丢失后只能靠第二已知偏移或全盘扫描，扇区 7 是成本与可发现性的折中。

### 2.3 `read_backup_supers`（`io.c:915`）——最高序号仲裁

- 签名：`static int read_backup_supers(struct bch_sb_handle *sb, struct bch_sb_layout *layout, bool primary_valid, u64 *best_offset, struct printbuf *err)`
- 参数：`primary_valid` 区分主槽是否已是候选（失败传 false 且 `best_seq=0`）；`best_offset` 回传胜者偏移。
- 规则（`io.c:948`）：`if (sb->seq >= best_seq)` —— **大于等于即更新，后扫者平局胜**；循环结束若胜者不是最后读槽则重读一次（`io.c:961-962`），保证返回时 `sb->sb` 即权威拷贝。
- 片段（`io.c:928-951`）：
```c
for (unsigned i = 1; i < layout->nr_superblocks; i++) {
    u64 offset = le64_to_cpu(layout->sb_offset[i]);
    struct printbuf slot_err = PRINTBUF;
    int ret = read_one_super(sb, offset, &slot_err);
    last_read = offset;             /* 成功失败都记，供末尾重读判断 */
    if (ret) { prt_printf(err, "  sb @ %llu: %s\n", offset, slot_err.buf); ... continue; }
    ...
    if (sb->seq >= best_seq) { best_seq = sb->seq; *best_offset = offset; }
}
```
- 权衡：每槽独立 `slot_err`，失败只记日志不中断（注释 `io.c:905-913` 列三种防御场景：主槽撕裂 / 槽间 seq 偏斜 / 备份比特腐烂）；代价是挂载时最坏读遍全表，但超块表通常 ≤3 项，可接受。常见全等 seq 时零重读（注释 `io.c:912-913`）。

### 2.4 `read_super_and_backups`（`io.c:967`）+ `__bch2_read_super` / `bch2_read_super`（`io.c:1088/1105`）+ 静默版（`io.c:1136`）

- 流程（`io.c:1045-1067`）：`opts.sb` 定点则单读无回退（恢复/调试）；否则先读主扇区 8 → 成功用**内嵌 layout**（常见路径，省一次 IO）→ `read_backup_supers(...,true,…)`；失败则记 `primary_err` → 读扇区 7 → `read_backup_supers(...,false,…)`。随后块大小检查（`io.c:1069`；userspace 下 direct_io 自动降级 buffered 并 `-EINTR` 重试，`io.c:1072-1075`）→ `have_layout=true` → `bch2_sb_validate(...,0,…)`。
- `__bch2_read_super` 的 `while(true)` 只处理 `-EINTR`（buffered 回退），其余错误 `bch2_free_super`；`bch2_read_super` 统一打印 `error reading superblock: %s`，备份成功则 `KERN_NOTICE successful read from backup`（`io.c:1126-1129`）。
- 权衡：内嵌布局优先 = 为常见情况省一次同步 IO；`bch2_read_super_silent`（`io.c:1136`）专供 `mount.bcachefs` 探测，避免刷屏。

**可学**：读全拷贝仲裁，不读单副本；逐槽错误隔离，胜者回填保证返回即权威。

---

## 三、写前校验与读回

持 `sb_lock` 递增序号并同步成员 `seq`；逐盘 `BCH_VALIDATE_write` 预验，拒写条件明确；先全盘读回（`read_back_super`）记分，写后按槽位顺序逐个提交；变小（静默丢弃）告警、变大（外部篡改）必错。

### 3.1 `write_super_endio`（`io.c:1148`）——统一收尾

- 签名：`static void write_super_endio(struct bio *bio)`
- 行为：`bch2_account_io_success_fail` 计账；失败则 `ca->sb_write_error = __bch2_err_throw(...)`（`io.c:1155`），成功不写（调用方先清零，见 3.4）。读写回读**共用同一 endio**（`read_back_super io.c:1170` 与 `write_one_super io.c:1197` 均挂此函数），以 `sb_write_error` 单字段汇合。
- 权衡：一函数两用，调用方靠“调用前清零 + `closure_sync` 后读字段”区分阶段，省状态机但要求严格配对清零（`io.c:1328/1369` 两处清零即证据）。

### 3.2 `read_back_super`（`io.c:1161`）——写前记分

- 签名：`static void read_back_super(struct bch_fs *c, struct bch_dev *ca)`
- 行为：读各盘**槽 0**（`sb->layout.sb_offset[0]`，`io.c:1169`）进 `ca->sb_read_scratch`（`BCH_SB_READ_SCRATCH_BUF_SIZE` 定长清零后读，`io.c:1166`），异步提交到 `c->sb_write` closure。
- 权衡：只读槽 0 而非全槽——目的是检测“静默丢弃 / 外部篡改”（见 3.4），不是仲裁；定长 scratch 避免与变长超块缓冲纠缠。

### 3.3 `write_one_super`（`io.c:1179`）——逐槽签名发射

- 签名：`static void write_one_super(struct bch_fs *c, struct bch_dev *ca, unsigned idx)`
- 行为：`sb->offset = sb->layout.sb_offset[idx]`（`io.c:1184`，先改偏移再算校验——offset 本身在校验范围内，防错位）；`SET_BCH_SB_CSUM_TYPE` 按 `metadata_checksum` 选项选型 → `csum_vstruct` → `REQ_SYNC|REQ_IDLE|REQ_META|REQ_FUA`（`io.c:1195`，注释引 `blk-wbt.c`：双 SYNC+IDLE 才免于被限流）→ `closure_bio_submit`。
- 权衡：每槽独立 checksum（offset 不同则 csum 不同），槽间不可互拷；FUA+SYNC 保证落盘顺序，但多盘多槽串行批提交（见 3.4 外层 `do…while(wrote)` 按槽号横向推进），延迟换可靠性。

### 3.4 `__bch2_write_super`（`io.c:1228`）——写主流程（本文件最长函数，约 240 行）

- 签名：`static int __bch2_write_super(struct bch_fs *c)`；要求持 `sb_lock`（`io.c:1242 lockdep_assert`）；出口包装 `bch2_write_super（io.c:1469）` 负责写后 `bch2_sb_update` 回填 CPU 侧。
- 参数/返回：无参外式（全状态在 `c`）；0 含“跳过/降级成功”，负 errcode 仅致命路径。
- 七阶段调用链：
  1. 门禁（`io.c:1234`）：`!BCH_FS_may_upgrade_downgrade → return 0`，初始化完成前不写半成品（`io.c:1311` `!INITIALIZED → return 0` 双保险）。
  2. 脏/净标记（`io.c:1246-1249`）：有 journal 字段 → `bch2_fs_mark_dirty`（`clean.c:261` 清 CLEAN 位）；否则 `bch2_fs_mark_clean`（`clean.c:267` 打包 clean 段，见第四节）。
  3. 快照在线盘 + 序号推进（`io.c:1258-1274`）：`for_each_online_member` 持 `BCH_DEV_READ_REF_write_super` 引用防掉盘；魔数统一 `BCHFS_MAGIC`；`seq+1`；**逐在线盘成员 `seq = sb.seq`**；`write_time` 打点；error/topology  sticky 位。
  4. CPU→盘回填（`io.c:1283-1291`）：counters / members / v1 兼容拷贝 / errors / downgrade / extent_type，全部落盘后再 `bch2_sb_from_fs` 分发到各盘私有 `disk_sb`。
  5. 写前预验（`io.c:1293-1302`）：逐盘 `bch2_sb_validate(...,BCH_VALIDATE_write,…)`，失败 `bch2_fs_inconsistent` 并 `return 0`——**不一致时拒绝发出任何 IO**，比写坏强。
  6. 版本与开关检查（`io.c:1304-1312`）：`nochanges` / 未初始化直接返回；`version > current` 走 `bch2_fs_fatal_error` + `sb_not_downgraded`（升级未降级不准写）。
  7. 读回记分→判定（`io.c:1330-1363`）→逐槽写（`io.c:1365-1399`）→记账（`io.c:1401-1403` 各盘 `disk_sb.seq`）→ quorum 判定（`io.c:1405-1408` `bch2_can_read_fs_with_devs`）→ 分级报错（`io.c:1410-1466`）。
- 读比分级（`io.c:1340-1362`）：`scratch.seq < disk_sb.seq` = **变小：静默丢弃**，`errors==continue/fix_safe` 仅日志，否则 `emergency_read_only`；`scratch.seq > disk_sb.seq` = **变大：外部篡改**，无条件 `emergency_read_only` + `erofs_sb_err`。不对称处理的理由：丢弃是存储栈常见毛病可容忍，变大意味着有第二个写者，继续写必脑裂。
- 逐槽写循环：`do { 按槽号 sb 横向扫全盘发射; closure_sync; 记 failures } while(wrote)`——同一轮次所有盘的同一槽一起写，失败记 `(offset, err)` 二元组（`sb_offset_err io.c:1209` + `write_sb_dev io.c:1215` darray，`write_sb_dev_put io.c:1220` 释放引用）。
- quorum：`!nr_wrote || !can_read_with(written)` 即 fatal → emergency RO；非 fatal（写少了但还能挂载）→ ratelimit 警告后仍 `return 0`（`io.c:1461-1466` 注释明示“调用方要的东西已落盘，消息是 warning 不是 failure”）。
- 片段（`io.c:1297-1301`，写前预验拒写）：
```c
int ret = bch2_sb_validate(i->ca->disk_sb.sb, &opts, 0, BCH_VALIDATE_write, &err);
if (ret) {
    bch2_fs_inconsistent(c, "sb invalid before write: %s", err.buf);
    return 0;
}
```
- 权衡：写前读回多一轮全盘同步读，用延迟换“丢弃/篡改”可区分；`degraded==very` 时加 `BCH_FORCE_IF_LOST`（`io.c:1239`）放宽 quorum，极端降级可写但挂载语义同步放宽。

**可学**：写后读回比对要做在写前（记分）而非写后（覆写证据）；丢弃与篡改必须区分报错等级；quorum 失败转 emergency RO 而非继续。

---

## 四、clean 段加速

关机打包树根、用量、时钟；下次比对不一致丢弃走日志。加速结构纯加速，校验失败回退全量。

> clean 段本体在 `fs/sb/clean.c`；写触发点在 `__bch2_write_super（io.c:1246-1249）`。行号：`bch2_sb_clean_validate clean.c:205`、`bch2_sb_clean_to_text clean.c:230`、`bch2_fs_mark_dirty clean.c:261`、`bch2_fs_mark_clean clean.c:267`。

### 4.1 `bch2_fs_mark_dirty`（`clean.c:261`）/ `bch2_fs_mark_clean`（`clean.c:267`）

- 签名：`void bch2_fs_mark_dirty(struct bch_fs *c)` / `void bch2_fs_mark_clean(struct bch_fs *c)`
- 调用链：`__bch2_write_super（io.c:1246）` 有 journal 字段即 dirty；否则 clean。`mark_clean` 内：已 CLEAN 直接返回（`clean.c:274` 幂等）；置 CLEAN 位 + `compat alloc_info/alloc_metadata`（`clean.c:279-280`）；`u64s = sizeof(*sb_clean)/8 + journal.entry_u64s_reserved` 后 `bch2_sb_field_resize(&c->disk_sb, clean, u64s)`，失败仅 `bch_err` 不致命（`clean.c:284-288`）。
- 片段（`clean.c:261-265`，dirty 极简）：
```c
void bch2_fs_mark_dirty(struct bch_fs *c)
{
    SET_BCH_SB_CLEAN(c->disk_sb.sb, false);
    c->disk_sb.sb->features[0] |= cpu_to_le64(BCH_SB_FEATURES_ALWAYS);
}
```
- 权衡：dirty 路径零分配（只清位），保证 journal 路径写超块永不因 clean 段 ENOSPC 失败；clean 路径允许 resize 失败降级（下次走日志回放即可），加速失败不影响正确性。

### 4.2 `bch2_sb_clean_validate`（`clean.c:205`）+ `bch2_verify_superblock_clean`（`clean.c:88`）

- 签名：`static int bch2_sb_clean_validate(struct bch_sb *sb, struct bch_sb_field *f, enum bch_validate_flags flags, struct printbuf *err)`；校验仅两条：段长 ≥ `sizeof(*clean)`；逐 `jset_entry` 不越界（`clean.c:216-225`）。深校验（usage/时钟/btree 根比对）在 `bch2_verify_superblock_clean（clean.c:88）`，不一致即丢弃 clean 段走 journal 回放。
- 权衡：挂载时浅验（防越界崩溃）+ 深验（防用错加速数据），两层分离使非法输入先被挡在内存安全线外。

**可学**：加速结构纯加速，校验失败回退全量；加速写入允许失败，正确路径永不依赖它。

---

## 五、成员全周期

槽位哨兵（`BCH_SB_MEMBER_INVALID` 永不分配），删除双态（deleted-UUID → 清零），变长 `member_bytes` 升级，合法校验（`validate_member`），分诊恢复，双轨引用（`disk_sb`/`ca->mi`），切换时序，扫描联动（btree bitmap），移除流水线，添加四阶段。本节函数均在 `members.c`。

### 5.1 读/写双轨：`bch2_sb_member_get`（`:93`）/ `bch2_sb_members_to_cpu`（`:512`）/ `bch2_sb_members_from_cpu`（`:495`）

- 签名：`struct bch_member bch2_sb_member_get(struct bch_sb *sb, int i)`（按值返回，v2 优先回退 v1，`:94-99`）；`void bch2_sb_members_to_cpu(struct bch_fs *c)`（盘→CPU）；`void bch2_sb_members_from_cpu(struct bch_fs *c)`（CPU→盘）。
- 调用链：`bch2_sb_update（io.c:743）→ to_cpu`（每次读/写超块后刷新）；`__bch2_write_super（io.c:1284）→ from_cpu`（落盘前回填）。`from_cpu` 仅回填 `errors[]` 原子计数（`:500-505` 持 rcu 遍历），其余字段以盘侧为准——错误计数是唯一 CPU 侧单调源。
- 片段（`:93-100`）：
```c
struct bch_member bch2_sb_member_get(struct bch_sb *sb, int i)
{
    struct bch_sb_field_members_v2 *mi2 = bch2_sb_field_get(sb, members_v2);
    if (mi2)
        return bch2_members_v2_get(mi2, i);
    struct bch_sb_field_members_v1 *mi1 = bch2_sb_field_get(sb, members_v1);
    return bch2_members_v1_get(mi1, i);
}
```
- 权衡：按值返回杜绝调用方持盘侧指针跨锁修改；`to_cpu` 内 failure-domain 字符串 intern 成小 id（`:530-553`），盘上存串、内存存 id，比较变整数比较，ENOMEM 时留 unset 保安全。

### 5.2 变长升级：`sb_members_v2_resize_entries`（`:102`）/ `bch2_sb_members_v2_init`（`:125`）/ `bch2_sb_members_cpy_v2_v1`（`:148`）

- 行为：`v2_init` 无 v2 段时按 v1 宽度建段再调 `resize_entries` 自后向前 `memmove` 扩到 `sizeof(struct bch_member)`（`:114-119` 逆序防重叠覆盖）；`cpy_v2_v1` 在 `version_incompat > extent_flags` 时删 v1 段（`:153-156`，老内核已读不懂，留着无用），否则截断回填 v1 前缀（`:166-167` 只拷 `BCH_MEMBER_V1_BYTES`）。
- 权衡：逆序 memmove + 尾部清零保证扩宽不残留垃圾；v1 影子段是给老内核的只读兼容，写侧永远以 v2 为准。

### 5.3 合法校验：`validate_member`（`:172`）+ `bch2_sb_members_v2_validate`（`:471`）/ v1 版（`:398`）

- 签名：`static int validate_member(struct printbuf *err, struct bch_member m, struct bch_sb *sb, int i)`（按值传，纯函数）。
- 五条红线（`:179-217`）：`nbuckets ≤ MAX`；`nbuckets-first_bucket ≥ MIN_NR`；`bucket_size ≥ block_size`；`bucket_size ≥ btree_node_size`；`btree_bitmap_shift < MAX`；另 `freespace_initialized && no_alloc_info` 互斥。
- 段级（`:471-488`）：先算 `mi_bytes` 防段过小，再逐项 `try(validate_member…)`。`bch2_sb_validate` 保证 members 最先被验（`io.c:647-653`）。
- 权衡：几何关系（bucket vs block vs btree node）全在挂载时静态拒掉，不留给分配器运行时崩；按值校验无锁可重入。

### 5.4 槽位分配：`bch2_sb_member_find_slot`（`:852`）/ `bch2_sb_member_alloc`（`:891`）/ `bch2_sb_members_clean_deleted`（`:913`）

- 签名：`static int bch2_sb_member_find_slot(struct bch_fs *c)` / `int bch2_sb_member_alloc(struct bch_fs *c)` / `void bch2_sb_members_clean_deleted(struct bch_fs *c)`
- 行为：`nr_devices < MAX 且 ≠ INVALID` 直接追加（`:859-861`）；否则扫 `BCH_SB_MEMBERS_MAX` 跳过哨兵 `INVALID`（`:865`），复用全零槽并挑 `last_mount` 最老者（`:875-879`，复用“最久未挂载”减少误复活）；全满则数 deleted-UUID 提示跑 fsck（`:884-886`）——**deleted-UUID 槽不自动复用**，必须 fsck 显式清理（`clean_deleted` 将其清零，`:921-923`）。
- 片段（`:863-880`）：
```c
for (unsigned dev_idx = 0; dev_idx < BCH_SB_MEMBERS_MAX; dev_idx++) {
    if (dev_idx == BCH_SB_MEMBER_INVALID)
        continue;   /* 哨兵永不分配 */
    ...
    if (!bch2_is_zero(&m.uuid, sizeof(m.uuid)))
        continue;
    u64 last_mount = le64_to_cpu(m.last_mount);
    if (best < 0 || last_mount < best_last_mount) { best = dev_idx; ... }
}
```
- 权衡：删除双态（deleted-UUID vs 零槽）把“待 fsck 确认”与“可复用”显式区分，防误删盘复活；`alloc` 内 `EBUG_ON(INVALID)`（`:897`）把哨兵当不变量断言。

### 5.5 扫描联动：btree bitmap（`__bch2_dev_btree_bitmap_marked :617` / `__bch2_dev_btree_bitmap_mark :639` / `mark_locked :684` / `mark :700` / `bch2_btree_bitmap_gc :726`）

- 行为：成员表存 64 位 `btree_allocated_bitmap` + `shift`（每 bit 覆盖 `1<<shift` 扇区）；`mark` 按 `end` 动态放大粒度（`:647 ilog2(roundup(end))-(shift+6)`），旧位右移折叠（`:653-658`），GC 位同步折叠；`gc :726` 全 btree 重扫后整体替换并 `bch2_write_super`（`:767`）。
- 权衡：精度换空间（64bit 覆盖全盘，盘越大粒度越粗）；`mark` 路径可触发 `write_sb`，调用方批量合并一次落盘（`mark_locked` 回传 `bool *write_sb`，`:684`）。

### 5.6 硬件指纹：`bch2_dev_mi_field_read`（`:950`）/ `upgrades_locked`（`:959`）/ `upgrades`（`:978`）/ `bch2_fs_mi_field_upgrades`（`:997`）

- 行为：读内核 `name/model/serial/rotational`，`dev_mi_update_str`（`:931`）做 pad 后比对，仅变化才置 `write_sb`；`ROTATIONAL` 只在未初始化时写一次（`:971-975`）。
- 权衡：指纹变化走超块持久化，`memcpy_and_pad` 消除尾部垃圾导致的误写；批量版 `fs_mi_field_upgrades` 全盘扫完只写一次超块。

**可学**：成员变更全流水线加回滚（分配→指纹→bitmap→错误计数→删除双态），槽位哨兵与 deleted 双态缺一不可。

---

## 六、错误持久化

段严格校验；展示拷贝倒序（按时间倒序不改盘序）；饱和钳位（`+` 后缀）；128 位时间戳（first/last 双轨 v2）；解压双轨（sb 计数 + key 定责）；写回折叠（v2 写时删 legacy，读时归并）。

### 6.1 唯一性护栏：`bch2_sb_errs_check_unique`（`errors.c:26`）+ `static_assert`（`:38`）

- 行为：`switch(0){case -1: … case n:…}` 使重复 id 变成 duplicate-case 编译错（`:28-34` 注释自述）；`0 BCH_SB_ERRS()` 求和 = `MAX*(MAX+1)/2` 则 ids 恰为 `0..MAX` 稠密（`:38-40`，和最小值论证： distinct 非负整数和最小当且仅当取全集）。
- 片段（`:37-41`）：
```c
#define x(t, n, ...) + (n)
static_assert((0ULL BCH_SB_ERRS()) ==
          (unsigned long long) BCH_FSCK_ERR_MAX * (BCH_FSCK_ERR_MAX + 1) / 2,
          "sb error ids are not dense: gap, duplicate, or id > MAX");
```
- 权衡：把“持久化枚举稠密”变成编译期不变量，on-disk id 永不漂移；代价是新增错误类型必须串改宏表，但这正是想要的摩擦。

### 6.2 段校验：`bch2_sb_errors_validate`（`:62`）/ `bch2_sb_errors_v2_validate`（`:151`）

- 签名：`static int bch2_sb_errors_validate(struct bch_sb *sb, struct bch_sb_field *f, enum bch_validate_flags flags, struct printbuf *err)`（v1）；v2 同形（`:151`）。
- 规则：v1：`NR==0` 拒（`:69-74`，零计数条目无意义）；id 非严格递增拒（`:76-81`）。v2 加 `FIRST ≤ LAST`（`:165-171`）。错误码统一 `-BCH_ERR_invalid_sb_errors`。
- 权衡：严格递增是归并读（6.5）的前置不变量，写时保证、读时信任，归并可做线性 merge 而非哈希。

### 6.3 展示：`bch2_sb_errors_to_text`（`:97`）/ `v2_to_text`（`:195`）/ `bch2_fs_errors_to_text`（`:230`）+ `bch2_prt_error_nr`（`:144`）

- 行为：拷贝到局部 darray 按 `last_error_time` 倒序（`error_entry_cmp :87` 返回 `-cmp_int(last…)`，v2 版 `:184` 比 `LAST`），**排序只动拷贝**，盘序（id 升序）不动；饱和计数 `≥ BCH_SB_ERROR_ENTRY_V2_NR_MAX` 后缀 `+`（`:146-149`），明示“地板非精确值”（`:143` 注释）。
- 片段（`:108-113`）：
```c
CLASS(darray_bch_sb_field_error_entry, sorted)();
for (struct bch_sb_field_error_entry *i = e->entries; i < e->entries + nr; i++)
    darray_push(&sorted, *i);
darray_sort(sorted, error_entry_cmp);
```
- 权衡：展示层排序与存储层分离，读放大换写入简单；`+` 标记把饱和语义显式化，避免运维误读精确值。

### 6.4 归因双轨：`bch2_blk_sts_sb_err`（`:257`）/ `bch2_decompress_sb_err`（`:271`）/ `bch2_decompress_key_type_error`（`:292`）

- 签名：`enum bch_sb_error_id bch2_blk_sts_sb_err(int err)` 等，输入为 `abs()` 后 switch（`:259`），未知兜底 `blk_sts_unknown` / `decompress_unknown`（zstd 另分 `zstd_error` 匹配，`:280-282`）。
- 双轨含义（`:286-291` 注释）：sb 计数答“坏了多少次”，`KEY_TYPE_error` key 答“坏的是哪个 extent”，同表同名保证两者可 join。
- 权衡：表驱动归因，新增解压算法只需加 `BCH_DECOMPRESS_SB_ERRS()` 表行，不动分发逻辑。

### 6.5 写回折叠与读归并：`bch2_sb_error_count`（`:307`）/ `from_cpu`（`:336`）/ `to_cpu`（`:370`）

- 签名：`void bch2_sb_error_count(struct bch_fs *c, enum bch_sb_error_id err)`（内存计数，有序插入，`:320-328` 同 id `nr++/last=`，更小 id 处 `break` 插入）；`void bch2_sb_errors_from_cpu(struct bch_fs *c)`；`int bch2_sb_errors_to_cpu(struct bch_fs *c)`。
- `from_cpu`（`:336-355`）：`resize(errors_v2, …)` 后逐项回填四元组，最后 `bch2_sb_field_delete(&c->disk_sb, errors)`（`:354`）——**写 v2 必删 legacy**，同一次超块写内原子。
- `to_cpu`（`:370-424`）：v2+legacy 双段有序归并（`:384-421` 经典双指针；同 id 则 `nr` 相加、`first=min/last=max`，legacy 单时间戳同时充 first/last，`:398-406`）。注释（`:357-369`）阐明语义：双段共存 ⇔ 中途被老内核降级写过，legacy 恰为降级后新增量，相加即无损、无 double-count，下次写回折叠进 v2。
- 片段（`:407-418`，同 id 折叠）：
```c
} else {
    u64 t = le64_to_cpu(legacy->entries[j].last_error_time);
    n = (struct bch_sb_error_entry_cpu) {
        .id   = id_v2,
        .nr   = BCH_SB_ERROR_ENTRY_V2_NR(&v2->entries[i]) +
                BCH_SB_ERROR_ENTRY_NR(&legacy->entries[j]),
        .first_error_time = min(BCH_SB_ERROR_ENTRY_V2_FIRST(&v2->entries[i]), t),
        .last_error_time  = max(BCH_SB_ERROR_ENTRY_V2_LAST(&v2->entries[i]), t),
    };
    i++; j++;
}
```
- 权衡：读写不对称（写单轨、读双轨归并）换跨版本零丢失；内存 `counts` 持 `counts_lock`（`:318/338/372` 三处同锁），与超块 IO 串行化。

**可学**：计数校验严格（零计数/乱序/时间倒置全拒）；展示不改盘序；饱和钳位并显式标记；跨版本用“写折叠+读归并”保无损。

---

## 七、升级降级表驱动

按版本声明所需 recovery passes 与静默错误；写前校验版本（`__bch2_write_super io.c:1314`）；老内核拒挂（`bch2_sb_validate` incompat 位检查）。本节函数均在 `downgrade.c`，表在 `:25-216`。

### 7.1 三张表：`UPGRADE_TABLE`（`:25`）/ `UPGRADE_TABLE_INCOMPAT`（`:146`）/ `DOWNGRADE_TABLE`（`:151`）

- 形：`x(version, recovery_passes, errors...)`，如 `x(snapshot_skiplists, BIT(check_snapshots), snapshot_bad_depth, snapshot_bad_skiplist)`（`:46-50`）；`RECOVERY_PASS_ALL_FSCK`（`:18`，`BIT(63)` 哨兵）表示“该版本跨越需全量 fsck”，在落表时展开为 `bch2_fsck_recovery_passes()`（`:302-304`）。
- 升级表示例（`:65-85` disk_accounting_v2/v3 携带一串 accounting 错误静默）；降级表（`:151-216`）为老内核准备的“降回去后要跑什么”，如 `disk_accounting_v2 → check_allocations + 9 个 usage 错误`（`:154-167`）。
- 权衡：版本演进知识全部数据化，进新版本只加表行，不碰执行引擎；`ALL_FSCK` 哨兵把“全量”推迟到执行时展开，表与 fsck pass 集合解耦。

### 7.2 落表执行：`__bch2_sb_set_upgrade`（`:288`）/ `bch2_sb_set_upgrade`（`:314`）/ `set_upgrade_incompat`（`:323`）/ `bch2_sb_set_upgrade_extra`（`:263`）

- 签名：`static void __bch2_sb_set_upgrade(struct bch_fs *c, unsigned old_version, unsigned new_version, const struct upgrade_downgrade_entry *table, size_t nr_entries)`，要求持 `sb_lock`（`:294`）。
- 行为（`:298-311`）：仅 `old < ver ≤ new` 区间条目生效；passes 经 stable 编码或进 `ext->recovery_passes_required[0]`；errors 逐个 `__set_bit_le64` 进 `ext->errors_silent`。`extra`（`:263`）处理条件型升级：跨 `bucket_stripe_sectors` 且真有 stripes（`have_stripes :255` 查 btree 根非 fake）才追加 `check_allocations` + 2 个静默错误，写超块。
- 权衡：区间语义保证重复升级幂等（已覆盖版本不再重复置位也无害）；条件型（extra）把“运行时状态相关”从静态表剥离，避免无 stripes 文件系统白跑 pass。

### 7.3 降级段编解码：`bch2_sb_downgrade_validate`（`:391`）/ `to_text`（`:425`）/ `bch2_sb_downgrade_update`（`:461`）/ `bch2_sb_set_downgrade`（`:516`）+ `downgrade_table_extra`（`:347`）

- `validate`（`:391-423`）：容忍 2 字节对齐的尾部空条目（`:399-405` 注释：段按 8 字节对齐，末尾空洞允许并忽略）；写态（`BCH_VALIDATE_write`）才查条目越界（读态容忍未来版本多写，`:407-411`）；`major` 不匹配直接拒（`:413-419`，跨大版本降级不允许）。
- `update`（`:461-514`）：仅 `btree_running` 后重建（`:463`）；跳过异 major（`:471`）与低于 `version_incompat` 的条目（`:474`）；空条目（无 passes 无 errors）不收录（`:492-495`）；**只增不减**语义：新表更小（`le32(d->field.u64s) > sb_u64s`）则 `return 0` 不收缩（`:504-505`），防旧信息丢失；`ENOSPC` 报 `ENOSPC_sb_downgrade`（`:509`）。
- `extra`（`:347-376`）：`bucket_stripe_sectors` 且有 stripes 时追加 `check_allocations` + 错误（packed 未对齐结构体用 open-coded 置位，`:365-368` 注释明示 `recovery_passes` misaligned）。
- `set_downgrade`（`:516-539`）：遍历段内条目，仅 `new_minor < minor ≤ old_minor` 区间生效，passes 或进 `ext->recovery_passes_required`，errors 双写 CPU 位图与盘侧 `ext->errors_silent`（`:532-535`，各带界检查）。
- 片段（`:500-513`，只增不减+落盘）：
```c
struct bch_sb_field_downgrade *d = bch2_sb_field_get(c->disk_sb.sb, downgrade);
unsigned sb_u64s = DIV_ROUND_UP(sizeof(*d) + table.nr, sizeof(u64));
if (d && le32_to_cpu(d->field.u64s) > sb_u64s)
    return 0;   /* 新表更小：保留旧信息，不收缩 */
d = bch2_sb_field_resize(&c->disk_sb, downgrade, sb_u64s);
if (!d)
    return bch_err_throw(c, ENOSPC_sb_downgrade);
memcpy(d->entries, table.data, table.nr);
```
- 权衡：降级信息只增不减，用少量空间换“降级路径永不因信息丢失而错过 fsck”；读写两态校验不对称（读容忍未来、写严格），保证老版本写不出新版本读不懂的降级段。

**可学**：演进表驱动（静态表 + 区间生效 + 条件 extra）；老版本拒挂不 corrupt（incompat 位 + major 检查双保险）。

---

## 八、设计启示

1. **多副本仲裁**：`read_backup_supers（io.c:915）` 逐槽隔离错误、`>=` 平局后胜、胜者回填，三行规则解决撕裂/偏斜/腐烂三类故障。
2. **写后读回**：`read_back_super（io.c:1161）` 写前记分 + `__bch2_write_super（io.c:1340-1362）` 变小/变大分级处置，丢弃容忍、篡改必停。
3. **加速回退**：`bch2_fs_mark_clean（clean.c:267）` 可失败、`verify（clean.c:88）` 失败回 journal，正确性永不依赖加速。
4. **全流水线成员**：哨兵 `INVALID`（`members.c:863-866`）+ deleted 双态（`:913`）+ 变长升级（`:102-146`）+ 几何校验（`:172`）+ bitmap 联动（`:639-726`）。
5. **严格校验**：零计数/乱序/时间倒置全拒（`errors.c:62/151`）；枚举稠密编译期保证（`errors.c:26-40`）。
6. **钳位不绕**：饱和 `+`（`errors.c:144`）、段只增不减（`downgrade.c:504`）、quorum 不足转 RO（`io.c:1452-1458`）——上限与底线都显式。
7. **表驱动演进**：`UPGRADE/DOWNGRADE_TABLE` + 区间生效 + 条件 extra，加版本只加表行；`bch2_sb_upgrade（io.c:1513）` 跨 major 清降级段防旧语义残留。

---

## 复核途径

```bash
grep -n "read_backup_supers\|__bch2_write_super\|bch2_sb_errors_validate" fs/sb/io.c fs/sb/errors.c
# read_backup_supers io.c:915；__bch2_write_super io.c:1228；bch2_sb_errors_validate errors.c:62（static），v2 版 :151
grep -n "bch2_sb_downgrade_validate\|bch2_sb_members_v2_validate\|validate_member\|bch2_fs_mark_clean" fs/sb/downgrade.c fs/sb/members.c fs/sb/clean.c
# downgrade_validate downgrade.c:391；members_v2_validate members.c:471；validate_member members.c:172；mark_clean clean.c:267
grep -n "BCH_SB_SECTOR\|BCH_SB_LAYOUT_SECTOR" fs/bcachefs_format.h
# BCH_SB_SECTOR=8，LAYOUT_SECTOR=7
```
