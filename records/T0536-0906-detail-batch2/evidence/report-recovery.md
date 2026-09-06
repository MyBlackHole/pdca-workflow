# bcachefs recovery 全流程专题学习报告（T0526）：代码级精讲

> 事实源：`fs/init/passes.c`（880 行）、`fs/init/error.c`（996 行）、`fs/init/damage.c`（385 行），
> 辅以 `fs/init/passes_format.h`、`passes.h`、`error.h`、`damage.h`、`damage_format.h`、`error_types.h`、`sb/errors_format.h`。
> 所有函数名、签名、行号均经 Read/Grep 核实。行号指上述文件内行。
> 八节结构沿用原报告，每节逐函数精讲：签名 / 参数 / 返回 / 调用链 / ≤10 行代码片段 / 权衡。

---

## 一、全景：pass 编排中枢

恢复 = pass 集合的有序执行：稳定编号隔离磁盘格式，按需调度，在线可延迟，昂贵限流，进度可观测。核心矛盾：修彻底 vs 挂载快。

### 1.1 `recovery_pass` 表与名字表（`passes.c:261-277,37-42`）

- 签名：`static const struct recovery_pass recovery_passes[]`；元素 `{ int (*fn)(struct bch_fs *); const char *name; unsigned when; u64 depends; }`（`passes.c:261-266`）。
- 参数/返回：无（静态表）。由 `BCH_RECOVERY_PASSES()` 宏（`passes_format.h:24-240`）逐行展开 `x(_fn,_id,_when,_depends,...)` 生成。
- 调用链：`BCH_RECOVERY_PASSES()` → `recovery_passes[i].fn/when/depends` → 被 `bch2_recovery_passes_match / pass_dependents / bch2_run_recovery_pass` 消费；名字表 `bch2_recovery_passes[]`（`passes.c:37-42`）同宏展开，供日志/打印用。
- 代码片段（`passes.c:268-277`，10 行内）：
```c
static const struct recovery_pass recovery_passes[] = {
#define x(_fn, _id, _when, _depends, ...)	{	\
	.fn		= bch2_##_fn,			\
	.name		= #_fn,				\
	.when		= _when,			\
	.depends	= _depends,			\
},
	BCH_RECOVERY_PASSES()
```
- 权衡：表驱动优于 switch：新增 pass 只改宏一行（含 stable id、`when`、`depends`、文档字符串），编排逻辑零改动；代价是宏魔法降低可读性，需配合 `passes_format.h:21-23` 注释理解。

### 1.2 `bch2_recovery_passes_match`（`passes.c:279-287`）

- 签名：`u64 bch2_recovery_passes_match(unsigned flags)`。
- 参数：`flags` 为 `PASS_*` 位掩码（`passes_format.h:5-12`：`SILENT/FSCK/UNCLEAN/ALWAYS/ONLINE/ALLOC/NODEFER`）。
- 返回：`u64` 位图，置位表示该 pass 的 `when & flags != 0`。
- 调用链：`bch2_fsck_recovery_passes` → 本函数；`bch2_run_recovery_passes_startup`（4 处取 `PASS_ALWAYS/PASS_UNCLEAN/PASS_FSCK`）→ 本函数；`recovery_pass_should_defer`、`bch2_async_recovery_passes_work`（过滤 `PASS_ONLINE`）→ 本函数。
- 代码片段（`passes.c:279-287`）：
```c
u64 bch2_recovery_passes_match(unsigned flags)
{
	u64 ret = 0;
	for (unsigned i = 0; i < ARRAY_SIZE(recovery_passes); i++)
		if (recovery_passes[i].when & flags)
			ret |= BIT_ULL(i);
	return ret;
}
```
- 权衡：O(N) 线性扫描，N=pass 数（约 50），启动路径调用数次可忽略；换来调用方语义清晰（“要哪类 pass”）。

### 1.3 `bch2_fsck_recovery_passes`（`passes.c:289-292`）

- 签名：`u64 bch2_fsck_recovery_passes(void)`。
- 参数/返回：无参，返回 `PASS_FSCK` 类 pass 位图。
- 调用链：fsck 工具侧 → 本函数 → `bch2_recovery_passes_match(PASS_FSCK)`。
- 代码片段（`passes.c:289-292`）：
```c
u64 bch2_fsck_recovery_passes(void)
{
	return bch2_recovery_passes_match(PASS_FSCK);
}
```
- 权衡：薄封装，把“fsck 要跑什么”收敛到一处，避免各处硬编码 `PASS_FSCK`。

### 1.4 `bch2_recovery_pass_empty`（`passes.c:240-243`）

- 签名：`static int bch2_recovery_pass_empty(struct bch_fs *c)`。
- 参数：`c` 文件系统实例；返回 `0`。
- 调用链：`recovery_passes[BCH_RECOVERY_PASS_recovery_pass_empty].fn` → 本函数；`bch2_run_recovery_pass` 调度执行。
- 代码片段（`passes.c:239-243`）：
```c
/* Fake recovery pass, so that scan_for_btree_nodes isn't 0: */
static int bch2_recovery_pass_empty(struct bch_fs *c)
{
	return 0;
}
```
- 权衡：占位 pass 让 `scan_for_btree_nodes` 不为索引 0（0 常被当“无 pass”哨兵，见 `r->current_pass = 0` 空闲标记 `passes.c:721`）；代价是一个无意义表项，需注释（已有）防止误删。

### 1.5 `bch2_lookup_root_inode`（`passes.c:249-259`）

- 签名：`static int bch2_lookup_root_inode(struct bch_fs *c)`。
- 参数：`c`；返回 `0` 成功或错误码。
- 调用链：`recovery_passes[lookup_root_inode].fn`（`PASS_ALWAYS|PASS_SILENT`，`passes_format.h:238-240`）→ 本函数 → `bch2_subvolume_get` + `bch2_inode_find_by_inum_trans`（`lockrestart_do` 包裹）。
- 代码片段（`passes.c:249-259`）：
```c
static int bch2_lookup_root_inode(struct bch_fs *c)
{
	subvol_inum inum = BCACHEFS_ROOT_SUBVOL_INUM;
	struct bch_inode_unpacked inode_u;
	struct bch_subvolume subvol;
	CLASS(btree_trans, trans)(c);
	return lockrestart_do(trans,
		bch2_subvolume_get(trans, inum.subvol, true, &subvol) ?:
		bch2_inode_find_by_inum_trans(trans, inum, &inode_u));
}
```
- 权衡：在仍可 rewind 的 recovery 窗口内验证 root 可读（注释 `passes.c:245-248`），失败可倒带修；若放到 rw 后才发现则只能停机。代价是一次额外 btree 读。

### 1.6 `bch2_run_recovery_pass`（`passes.c:570-610`）

- 签名：`static int bch2_run_recovery_pass(struct bch_fs *c, enum bch_recovery_pass pass)`。
- 参数：`c`、`pass` 内存枚举索引；返回 `0` 成功或错误码（含 `restart_recovery` 倒带信号）。
- 调用链：`bch2_run_recovery_passes` 主循环 → 本函数 → `p->fn(c)`（各 `bch2_check_*`）→ 成功则 `bch2_sb_recovery_pass_complete`；失败则记 `passes_failing` + 内存限流条目。
- 代码片段（`passes.c:579-585`，核心分发）：
```c
	s64 start_time = ktime_get_real_seconds();
	int ret = p->fn(c);
	if (ret) {
		if (!bch2_err_matches(ret, BCH_ERR_restart_recovery)) {
			s64 end_time = ktime_get_real_seconds();
			bch_err(c, "%s(): error %s", p->name, bch2_err_str(ret));
```
- 代码片段（成功收尾，`passes.c:604-607`）：
```c
	r->passes_failing = 0;
	if (!test_bit(BCH_FS_error, &c->flags))
		bch2_sb_recovery_pass_complete(c, pass, start_time);
```
- 权衡：成功清零全量 `passes_failing`（任一 pass 成功即解除所有失败限流，给依赖修复后立即重试机会）；仅 `BCH_FS_error` 未置位才落盘 `complete`（脏状态下不宣称修好）。失败限流条目见第五节。

### 1.7 `bch2_run_recovery_passes`（`passes.c:620-727`）

- 签名：`int bch2_run_recovery_passes(struct bch_fs *c, u64 orig_passes_to_run, bool failfast)`。
- 参数：`c`；`orig_passes_to_run` 本轮待跑位图；`failfast` 启动路径为 true（遇错即停），后台路径为 false。返回首个持续错误码。
- 调用链：`bch2_run_recovery_passes_startup`（`scoped_guard(mutex,&r->run_lock)` 内，`passes.c:817-818`）→ 本函数 → `bch2_run_recovery_pass` + `bch2_journal_flush`；`bch2_async_recovery_passes_work` → 本函数。
- 代码片段（主循环取 pass，`passes.c:680-688`）：
```c
	while (r->current_passes) {
		scheduled |= r->current_passes;
		unsigned pass = __ffs64(r->current_passes);
		r->current_pass			= pass;
		r->current_passes		&= ~BIT_ULL(pass);
		r->scheduled_passes_ephemeral	&= ~BIT_ULL(pass);
		r->passes_attempted		|= BIT_ULL(pass);
```
- 代码片段（rewind 恢复，`passes.c:697-704`）：
```c
		if (r->rewound_to) {
			r->rewound_from	= max(r->rewound_from, pass);
			/* Restore current_passes up to and including rewound_to */
			r->current_passes |= scheduled & (~0ULL << r->rewound_to);
			r->rewound_to = 0;
```
- 权衡：`__ffs64` 从低位（即枚举顺序 = 运行顺序）取 pass，保证拓扑序；`scheduled` 累积 ephemeral 调度，rewind 时不丢 trigger 半路加的 pass（注释 `passes.c:670-676`）；`passes_attempted` 本轮清零、轮内只增（注释 `passes.c:663-668`），是防回绕不变量的 epoch 基础。`failfast` 区分挂载（快速失败）与后台（尽量多修）。

### 1.8 `bch2_run_recovery_passes_startup`（`passes.c:767-842`）

- 签名：`int bch2_run_recovery_passes_startup(struct bch_fs *c, enum bch_recovery_pass from)`。
- 参数：`c`；`from` 起始 pass（`passes &= ~(BIT_ULL(from)-1)` 支持从中断点续跑）。返回 `0` 或 `try()` 错误。
- 调用链：挂载 recovery 入口 → 本函数 → 组装 `passes`（ALWAYS + UNCLEAN + FSCK + opts + sb 持久请求）→ defer 在线 pass → `bch2_run_recovery_passes(passes,true)` → 清 `BCH_FS_in_recovery` → 踢异步 runner。
- 代码片段（组装，`passes.c:781-788`）：
```c
	u64 passes =
		bch2_recovery_passes_match(PASS_ALWAYS) |
		(!c->sb.clean ? bch2_recovery_passes_match(PASS_UNCLEAN) : 0) |
		(c->opts.fsck ? bch2_recovery_passes_match(PASS_FSCK) : 0) |
		c->opts.recovery_passes |
		(!c->opts.recovery_passes_skip_scheduled
		 ? c->sb.recovery_passes_required
		 : 0);
```
- 代码片段（defer，`passes.c:806-815`）：
```c
	u64 defer = 0;
	if (!c->opts.fsck)
		for (unsigned i = 0; i < BCH_RECOVERY_PASS_NR; i++)
			if ((passes & BIT_ULL(i)) &&
			    !(c->opts.recovery_passes & BIT_ULL(i)) &&
			    !(recovery_passes[i].when & PASS_NODEFER) &&
			    recovery_pass_should_defer(i, passes)) {
				defer |= BIT_ULL(i);
				passes &= ~BIT_ULL(i);
			}
```
- 权衡：显式请求的 pass（`opts.recovery_passes`）永不 defer、`check_snapshots` 带 `PASS_NODEFER` 永不 defer（快照体系是后续一切的前提）；`skip_scheduled` 只跳过执行不清除 sb 请求（注释 `passes.c:773-780`），检查型工具不污染修复状态。挂载快 vs 修彻底的矛盾在此收敛。

### 1.9 `bch2_async_recovery_passes_work` / `bch2_run_async_recovery_passes`（`passes.c:729-765`）

- 签名：`static void bch2_async_recovery_passes_work(struct work_struct *work)`；`void bch2_run_async_recovery_passes(struct bch_fs *c)`。
- 参数：work 反查 `c`（`container_of`）；返回 void。
- 调用链：`__bch2_run_explicit_recovery_pass`（在线 pass 调度时，`passes.c:494-496`）/ `startup` 尾（`passes.c:838-839`）→ `bch2_run_async_recovery_passes` → `queue_work(system_long_wq)` → `work` → `bch2_run_recovery_passes(... & PASS_ONLINE, false)`。
- 代码片段（过滤，`passes.c:734-740`）：
```c
	if (mutex_trylock(&r->run_lock)) {
		bch2_run_recovery_passes(c,
			(c->sb.recovery_passes_required |
			 r->scheduled_passes_ephemeral) &
			~r->passes_ratelimiting &
			bch2_recovery_passes_match(PASS_ONLINE),
			false);
```
- 代码片段（守卫，`passes.c:755-762`）：
```c
	if (c->opts.nochanges)
		return;
	if (!enumerated_ref_tryget(&c->writes, BCH_WRITE_REF_async_recovery_passes))
		return;
	if (queue_work(system_long_wq, &c->recovery.work))
		return;
```
- 权衡：`trylock` + `tryget` + `queue_work` 三重“拿不到就放弃”（调用方已把需求记入 sb/ephemeral，下次再跑），后台线程永不阻塞前台；`nochanges` 直接不调度（注释 `passes.c:749-754`：fake-rw 会收回，后台写无处可去）；`~passes_ratelimiting` 把正被限流的 pass 排除在后台轮外。

### 1.10 `bch2_recovery_pass_status_to_text` / `bch2_fs_recovery_passes_init`（`passes.c:844-880`）

- 签名：`__cold void bch2_recovery_pass_status_to_text(struct printbuf *out, struct bch_fs *c)`；`void bch2_fs_recovery_passes_init(struct bch_fs *c)`。
- 参数/返回：前者打印 Scheduled(sb)/Scheduled(ephemeral)/Completed/Failing/Currently running/Next/Rewound from；后者初始化 `recovery.lock/run_lock/work`。
- 调用链：debugfs/sysfs 状态查询 → 前者；fs 分配初始化 → 后者。
- 代码片段（`passes.c:874-880`）：
```c
void bch2_fs_recovery_passes_init(struct bch_fs *c)
{
	spin_lock_init(&c->recovery.lock);
	mutex_init(&c->recovery.run_lock);
	INIT_WORK(&c->recovery.work, bch2_async_recovery_passes_work);
}
```
- 权衡：`__cold` 标记状态打印为冷路径，不污染热路径 icache；`rewound_from` 仅在 `in_recovery` 且非零时打印，避免空字段噪音。

**可学**：恢复必须编排化：pass 表独立声明（fn/when/depends），编排层统一处理顺序/倒带/限流/可观测，新增修复能力只加表项。

---

## 二、稳定编号映射

内存枚举可随意增删重排，磁盘只存 stable id，双向表重映射。`passes_format.h:20-23` 明示第二字段为持久标识、永不可变。

### 2.1 `passes_to_stable_map` / `passes_from_stable_map`（`passes.c:44-54`）

- 签名：`static const u8 passes_to_stable_map[]`；`static const u8 passes_from_stable_map[]`。
- 参数/返回：编译期由 `BCH_RECOVERY_PASSES()` 生成的双向数组：前者以内存索引取 stable id，后者以 stable id 取内存索引。
- 调用链：所有 to/from stable 转换的唯一数据源。
- 代码片段（`passes.c:44-54`）：
```c
static const u8 passes_to_stable_map[] = {
#define x(n, id, ...)	[BCH_RECOVERY_PASS_##n] = BCH_RECOVERY_PASS_STABLE_##n,
	BCH_RECOVERY_PASSES()
#undef x
};
static const u8 passes_from_stable_map[] = {
#define x(n, id, ...)	[BCH_RECOVERY_PASS_STABLE_##n] = BCH_RECOVERY_PASS_##n,
	BCH_RECOVERY_PASSES()
#undef x
};
```
- 权衡：`u8` 数组 O(1) 查表，内存可忽略；stable id 须 <256（当前最大 49，见 `check_damage 49`，`passes_format.h:181`），若超 255 需换位宽——这是用一字节换简洁的隐含约束。

### 2.2 `bch2_recovery_pass_to_stable`（`passes.c:56-59`）

- 签名：`static enum bch_recovery_pass_stable bch2_recovery_pass_to_stable(enum bch_recovery_pass pass)`。
- 参数：内存枚举；返回 stable 枚举。
- 调用链：`bch2_sb_recovery_pass_entry`、`bch2_sb_recovery_pass_complete`、`__bch2_run_explicit_recovery_pass`（`__test_and_set_bit_le64` 置 sb 位）→ 本函数。
- 代码片段（`passes.c:56-59`）：
```c
static enum bch_recovery_pass_stable bch2_recovery_pass_to_stable(enum bch_recovery_pass pass)
{
	return passes_to_stable_map[pass];
}
```
- 权衡：static 内联级小函数，调用点不直接碰数组，便于加边界断言而不改全树。

### 2.3 `bch2_recovery_passes_to_stable`（`passes.c:61-68`）

- 签名：`u64 bch2_recovery_passes_to_stable(u64 v)`。
- 参数：内存位图；返回 stable 位图（逐位翻译）。
- 调用链：sb 写入路径（superblock 编解码）→ 本函数。
- 代码片段（`passes.c:61-68`）：
```c
u64 bch2_recovery_passes_to_stable(u64 v)
{
	u64 ret = 0;
	for (unsigned i = 0; i < ARRAY_SIZE(passes_to_stable_map); i++)
		if (v & BIT_ULL(i))
			ret |= BIT_ULL(passes_to_stable_map[i]);
	return ret;
}
```
- 权衡：O(N) 逐位翻译只走 sb 编解码冷路径；位图而非数组传递，与 `recovery_passes_required` 的 `__le64` 位图存储（`passes.c:157-158`）同构。

### 2.4 `bch2_recovery_pass_from_stable` / `bch2_recovery_passes_from_stable`（`passes.c:70-84`）

- 签名：`static enum bch_recovery_pass bch2_recovery_pass_from_stable(enum bch_recovery_pass_stable pass)`；`u64 bch2_recovery_passes_from_stable(u64 v)`。
- 参数/返回：stable→内存的单值/位图反向翻译；越界 stable 返回 0（即 `recovery_pass_empty` 占位），见下。
- 调用链：sb 读取路径、`bch2_sb_recovery_passes_to_text`（`passes.c:114` 按 stable 下标反查名字）→ 本函数。
- 代码片段（`passes.c:70-75`）：
```c
static enum bch_recovery_pass bch2_recovery_pass_from_stable(enum bch_recovery_pass_stable pass)
{
	return pass < ARRAY_SIZE(passes_from_stable_map)
		? passes_from_stable_map[pass]
		: 0;
}
```
- 权衡：未知 stable id 映射到 0（即 `recovery_pass_empty` 占位），而非报错：旧盘遇到新内核删掉的 pass 时表现为“无操作”，前向兼容；代价是拼写错误的 stable id 也被静默吞掉，需靠 `validate` 补位（但当前 `validate` 直接 `return 0`，见 2.5）。

### 2.5 `bch2_sb_recovery_passes_validate`（`passes.c:86-90`）

- 签名：`static int bch2_sb_recovery_passes_validate(struct bch_sb *sb, struct bch_sb_field *f, enum bch_validate_flags flags, struct printbuf *err)`。
- 参数/返回：sb 字段校验钩子，当前恒返回 0。
- 调用链：sb 字段 ops 表 `bch_sb_field_ops_recovery_passes`（`passes.c:234-237`）→ 本函数。
- 代码片段（`passes.c:86-90`）：
```c
static int bch2_sb_recovery_passes_validate(struct bch_sb *sb, struct bch_sb_field *f,
					    enum bch_validate_flags flags, struct printbuf *err)
{
	return 0;
}
```
- 权衡：占位实现：recovery_passes 字段是“提示性”调度信息而非完整性关键数据，坏了最坏多跑/少跑一轮 pass；但未知 stable id 的静默映射（2.4）若配上空校验，长期是隐患——后续应加长度/越界检查。

### 2.6 `bch2_sb_recovery_passes_to_text`（`passes.c:92-126`）

- 签名：`static __cold void bch2_sb_recovery_passes_to_text(struct printbuf *out, struct bch_fs *c, struct bch_sb *sb, struct bch_sb_field *f)`。
- 参数：打印目标、fs、sb 及字段；无返回。
- 调用链：sb 显示路径 → 本函数 → `bch2_recovery_pass_from_stable(idx)` 反查名字 + `bch2_prt_datetime` + `bch2_pr_time_units`。
- 代码片段（`passes.c:108-114`）：
```c
	for (struct recovery_pass_entry *i = r->start; i < r->start + nr; i++) {
		if (!i->last_run)
			continue;
		unsigned idx = i - r->start;
		prt_printf(out, "%s\t", bch2_recovery_passes[bch2_recovery_pass_from_stable(idx)]);
```
- 权衡：跳过 `last_run == 0` 的从未运行项，`show-super` 输出只含有效行；`__cold` 避免污染热路径。

### 2.7 `bch2_sb_recovery_pass_entry`（`passes.c:128-149`）

- 签名：`static struct recovery_pass_entry *bch2_sb_recovery_pass_entry(struct bch_fs *c, enum bch_recovery_pass pass)`。
- 参数：`c`（要求持有 `sb_lock`，`lockdep_assert_held`）、内存 pass；返回指向 sb 内 `recovery_pass_entry` 的指针（必要时自动扩容字段），失败返回 NULL。
- 调用链：`bch2_sb_recovery_pass_complete`、`bch2_recovery_pass_set_no_ratelimit` → 本函数 → `bch2_sb_field_get/resize`。
- 代码片段（`passes.c:138-148`）：
```c
	if (stable >= recovery_passes_nr_entries(r)) {
		unsigned u64s = struct_size(r, start, stable + 1) / sizeof(u64);
		r = bch2_sb_field_resize(&c->disk_sb, recovery_passes, u64s);
		if (!r) {
			bch_err(c, "error creating recovery_passes sb section");
			return NULL;
		}
	}
	return r->start + stable;
```
- 权衡：按 stable 下标稀疏数组 + 按需扩容：新 pass 的 `last_run` 天然为 0（“没跑过”），老盘挂新内核无需迁移；`resize` 失败返回 NULL 由调用方容忍（完不成时间戳记录不影响修复本身）。

**可学**：内存演进与磁盘稳定解耦：枚举顺序随便改，stable id 永冻；双向表 + 稀疏数组 + 越界归零三件套是低成本兼容范式。

---

## 三、在线延迟与防回绕

可后台跑的 pass 不倒带；已 rw 的不可倒带直接拒；同轮已尝试的不重排，防死循环。

### 3.1 `pass_dependents`（`passes.c:294-311`）

- 签名：`static u64 pass_dependents(enum bch_recovery_pass pass)`。
- 参数：目标 pass；返回其传递闭包依赖者位图（含自身）。
- 调用链：`recovery_pass_should_defer` → 本函数。
- 代码片段（`passes.c:295-310`）：
```c
static u64 pass_dependents(enum bch_recovery_pass pass)
{
	u64 passes = BIT_ULL(pass);
	bool found;
	do {
		found = false;
		for (unsigned i = 0; i < BCH_RECOVERY_PASS_NR; i++)
			if (!(passes & BIT_ULL(i)) &&
			    (passes & recovery_passes[i].depends)) {
				passes |= BIT_ULL(i);
				found = true;
			}
	} while (found);
	return passes;
}
```
- 权衡：不动点迭代求闭包，N 小（~50）且只在 startup 调度时跑，开销可忽略；正确性关键：defer 判定必须看“自己+所有后代”是否全可在线，只看自己会切断依赖链。

### 3.2 `recovery_pass_should_defer`（`passes.c:313-320`）

- 签名：`static bool recovery_pass_should_defer(enum bch_recovery_pass pass, u64 passes)`。
- 参数：候选 pass、本轮待跑集合；返回 true 表示可推迟到后台。
- 调用链：`startup` 的 defer 循环、`__bch2_run_explicit_recovery_pass` 的 `run_now` 判定 → 本函数。
- 代码片段（`passes.c:314-320`）：
```c
static bool recovery_pass_should_defer(enum bch_recovery_pass pass,
				       u64 passes)
{
	passes &= pass_dependents(pass);
	passes |= BIT_ULL(pass);
	return passes == (passes & bch2_recovery_passes_match(PASS_ONLINE));
}
```
- 权衡：一行语义：“我及我的待跑后代全是 ONLINE 类”才可 defer；`check_snapshots` 纵使 ONLINE 也因 `PASS_NODEFER` 被 startup 显式排除（`passes.c:811`），因它是后续 fsck 的地基。

### 3.3 `recovery_pass_needs_rewind`（`passes.c:322-329`）

- 签名：`static bool recovery_pass_needs_rewind(struct bch_fs *c, enum bch_recovery_pass pass)`。
- 参数：`c`、目标 pass；返回是否需要倒带（目标在当前指针之前且本轮未尝试过）。
- 调用链：`recovery_pass_needs_set`、`__bch2_run_explicit_recovery_pass`（`rewind` 变量）→ 本函数。
- 代码片段（`passes.c:322-329`）：
```c
static bool recovery_pass_needs_rewind(struct bch_fs *c,
				       enum bch_recovery_pass pass)
{
	struct bch_fs_recovery *r = &c->recovery;
	return  test_bit(BCH_FS_running_recovery_passes, &c->flags) &&
		r->current_pass > pass &&
		!(r->passes_attempted & BIT_ULL(pass));
}
```
- 权衡：三条件缺一不可：非运行期无“倒带”概念；`current_pass > pass` 保证只向后倒；`!passes_attempted` 是防回绕不变量——同轮跑过的 pass 永不倒回（注释 `passes.c:440-452` 解释：若按 `passes_complete` 门控，失败 pass 永不 complete 会在 `errors=continue` 下无限倒带）。

### 3.4 `recovery_pass_needs_set`（`passes.c:331-375`）

- 签名：`static bool recovery_pass_needs_set(struct bch_fs *c, enum bch_recovery_pass pass, enum bch_run_recovery_pass_flags *flags)`。
- 参数：`c`、pass、可被改写的 flags（`scan_for_btree_nodes` 强制加 `nopersistent`；ratelimit 不需要时可清除）；返回是否需要调度。
- 调用链：`__bch2_run_explicit_recovery_pass`、`bch2_run_explicit_recovery_pass` 快捷路径 → 本函数。
- 代码片段（`passes.c:341-350`，两个短路）：
```c
	if (pass == BCH_RECOVERY_PASS_scan_for_btree_nodes)
		*flags |= RUN_RECOVERY_PASS_nopersistent;
	if ((*flags & RUN_RECOVERY_PASS_skip_if_complete) &&
	    (r->passes_complete & BIT_ULL(pass)))
		return false;
	if ((*flags & RUN_RECOVERY_PASS_ratelimit) &&
	    !bch2_recovery_pass_want_ratelimit_locked(c, pass, 100))
		*flags &= ~RUN_RECOVERY_PASS_ratelimit;
```
- 代码片段（持久/临时状态二选一，`passes.c:361-368`）：
```c
	bool in_recovery = test_bit(BCH_FS_in_recovery, &c->flags);
	bool persistent = !in_recovery || !(*flags & RUN_RECOVERY_PASS_nopersistent);
	u64 already_running = persistent
		? c->sb.recovery_passes_required
		: r->current_passes;
	if (!(already_running & BIT_ULL(pass)))
		return true;
```
- 权衡：`scan_for_btree_nodes` 永不持久化（注释 `passes.c:337-340`：它是 `check_topology` 的按需子程序）；`skip_if_complete` 给“清理类 pass”（修了也未必治本的）用，避免每次遇到损伤就重新武装 sb 导致每挂必 fsck；`persistent` 按是否在 recovery 内二选一，避免用错状态源。

### 3.5 `__bch2_run_explicit_recovery_pass` 倒带/在线分支（`passes.c:380-500`）

- 签名：`int __bch2_run_explicit_recovery_pass(struct bch_fs *c, struct printbuf *out, enum bch_recovery_pass pass, enum bch_run_recovery_pass_flags flags, bool *write_sb)`（`passes.c:380-384`）。
- 参数：`c`、`out` 日志缓冲、`pass`、`flags`（`passes.h:17-35` 四位）、`write_sb` 输出是否需写超块；返回 0 或 `cannot_rewind_recovery/restart_recovery`。
- 调用链：`bch2_run_explicit_recovery_pass`（持 `sb_lock` 版）、`bch2_require_recovery_pass`、`__bch2_topology_error`（`error.c:108`）→ 本函数。
- 代码片段（rw 后拒倒带，`passes.c:425-430`）：
```c
	if (pass < BCH_RECOVERY_PASS_set_may_go_rw &&
	    test_bit(BCH_FS_may_go_rw, &c->flags)) {
		prt_printf(out, "need recovery pass %s (%u), but already rw\n",
			   bch2_recovery_passes[pass], pass);
		return bch_err_throw(c, cannot_rewind_recovery);
	}
```
- 代码片段（run_now 不变量，`passes.c:453-455`）：
```c
	bool run_now = rewind ||
		(!recovery_pass_should_defer(pass, r->current_passes) &&
		 !(r->passes_attempted & BIT_ULL(pass)));
```
- 代码片段（ephemeral 永不倒带，`passes.c:464-465`）：
```c
	if (running && !ratelimit && run_now &&
	    !(rewind && (flags & RUN_RECOVERY_PASS_ephemeral))) {
```
- 权衡：`set_may_go_rw` 是单向门：之前 pass 管的是只读期结构，rw 后 journal/replay 语义已变，倒回去会 corrupt，因此直接报错下次修；`run_now` 同样受 `passes_attempted` 门控（注释 `passes.c:440-452` 的 `check_key_has_snapshot` 循环案例）；ephemeral 调度来自 btree trigger 原子上下文，不能 restart recovery，只能记 `scheduled_passes_ephemeral` 等异步 runner（注释 `passes.c:457-463`）。

**可学**：延迟判定用依赖闭包而非单点属性；重跑门控用“已尝试”而非“已完成”，失败态才不会转圈。

---

## 四、sb_write 去重

持久化请求去重（原子测设），临时路径自证不碰盘。

### 4.1 `__bch2_run_explicit_recovery_pass` 持久化分支（`passes.c:407-413`）

- 签名：见 3.5；本节聚焦 `write_sb` 去重语义。
- 参数/返回：`write_sb` 为调用方持有的“需写超块”累积位。
- 调用链：`bch2_run_explicit_recovery_pass`（`passes.c:527-531` 持锁调本函数后按 `write_sb` 决定 `bch2_write_super`）。
- 代码片段（`passes.c:407-413`）：
```c
	if (flags & (RUN_RECOVERY_PASS_nopersistent|RUN_RECOVERY_PASS_ephemeral)) {
		r->scheduled_passes_ephemeral |= BIT_ULL(pass);
	} else {
		struct bch_sb_field_ext *ext = bch2_sb_field_get(c->disk_sb.sb, ext);
		*write_sb |= !__test_and_set_bit_le64(bch2_recovery_pass_to_stable(pass),
						     ext->recovery_passes_required);
	}
```
- 权衡：`__test_and_set_bit_le64` 原子“测设”：位已置则 `write_sb` 不再置位，避免同一 pass 被反复发现损伤时每次都写 sb（mount 风暴下省 N-1 次写）；`ext->recovery_passes_required` 用 stable 位（跨版本可读），内存位图用 `current_passes`，两者不可混用。

### 4.2 `bch2_run_explicit_recovery_pass`（`passes.c:502-533`）

- 签名：`int bch2_run_explicit_recovery_pass(struct bch_fs *c, struct printbuf *out, enum bch_recovery_pass pass, enum bch_run_recovery_pass_flags flags)`。
- 参数：无锁入口（内部按需取 `sb_lock`）；ephemeral 路径断言不写 sb。
- 调用链：各 check 路径发现损伤 → 本函数 → `recovery_pass_needs_set` 快捷返回 → `__bch2_run_explicit_recovery_pass`。
- 代码片段（ephemeral 免锁，`passes.c:520-525`）：
```c
	if (flags & RUN_RECOVERY_PASS_ephemeral) {
		bool write_sb = false;
		int ret = __bch2_run_explicit_recovery_pass(c, out, pass, flags, &write_sb);
		WARN_ON(write_sb);
		return ret;
	}
```
- 代码片段（持久路径持锁写，`passes.c:527-532`）：
```c
	guard(mutex_noio)(&c->sb_lock);
	bool write_sb = false;
	int ret = __bch2_run_explicit_recovery_pass(c, out, pass, flags, &write_sb);
	if (write_sb)
		bch2_write_super(c);
```
- 权衡：三档锁策略：`ratelimit` 查询需 `sb_lock`（读 sb 时间戳）故走持锁版；ephemeral 只碰 `r->lock` 下内存状态，可在持 btree 锁的 trigger 上下文调用；`WARN_ON(write_sb)` 自证“临时路径永不碰盘”，一旦有人误加持久化分支立刻现形。`mutex_noio`（而非普通 mutex）避免回收期 IO 死锁。

### 4.3 `bch2_require_recovery_pass`（`passes.c:540-568`）

- 签名：`int bch2_require_recovery_pass(struct bch_fs *c, struct printbuf *out, enum bch_recovery_pass pass)`。
- 参数：`c/out/pass`；返回 0（已跑过）、`restart_recovery`（已武装倒带）、`recovery_pass_will_run`（已调度稍后跑）。
- 调用链：必须依赖某 pass 结果的代码 → 本函数 → `__bch2_run_explicit_recovery_pass`。
- 代码片段（`passes.c:544-551`）：
```c
	if (test_bit(BCH_FS_running_recovery_passes, &c->flags) &&
	    c->recovery.passes_complete & BIT_ULL(pass))
		return 0;
	guard(mutex_noio)(&c->sb_lock);
	if (bch2_recovery_pass_want_ratelimit_locked(c, pass, 100))
		return 0;
```
- 代码片段（`passes.c:562-564`）：
```c
	int ret = __bch2_run_explicit_recovery_pass(c, out, pass, flags, &write_sb) ?:
		bch_err_throw(c, recovery_pass_will_run);
```
- 权衡：限流中的 pass 视为“近期跑过”直接返回 0（注释 `passes.c:535-539`），避免 require 语义与限流打架；`restart_recovery` 只允许来自真正武装的 rewind（注释 `passes.c:555-561`），否则循环看到无 `rewound_to` 的 restart 会失败——错误码与状态机严格配对。

### 4.4 `bch2_sb_recovery_pass_complete`（`passes.c:151-173`）

- 签名：`static void bch2_sb_recovery_pass_complete(struct bch_fs *c, enum bch_recovery_pass pass, s64 start_time)`。
- 参数：`c`、pass、本轮开始秒级时间戳；无返回（内部写超块）。
- 调用链：`bch2_run_recovery_pass` 成功 → 本函数 → 清 `recovery_passes_required` stable 位 + 写 `last_run/last_runtime` + `bch2_write_super`。
- 代码片段（`passes.c:155-162`）：
```c
	guard(mutex_noio)(&c->sb_lock);
	struct bch_sb_field_ext *ext = bch2_sb_field_get(c->disk_sb.sb, ext);
	__clear_bit_le64(bch2_recovery_pass_to_stable(pass),
			 ext->recovery_passes_required);
	struct bch_fs_recovery *r = &c->recovery;
	if (!r->current_passes)
		memset(ext->errors_silent, 0, sizeof(ext->errors_silent));
```
- 权衡：清位 + 时间戳 + 写盘三合一，保证“宣称修好”与“限流基准更新”原子可见；`current_passes` 为空（整轮结束）才清 `errors_silent`：静默错误只在完整无错轮后解除，避免半轮修好就放噪音。

**可学**：持久化请求必须去重（测设返回值决定是否写盘）；临时路径用 `WARN_ON(write_sb)` 自证不碰盘，锁粒度按调用上下文分档。

---

## 五、昂贵限流

起止时间存盘，超比限流，单次放行。内存限流只管失败重试，成功重跑看持久限流。

### 5.1 `recovery_pass_entry_ratelimited`（`passes.c:209-215`）

- 签名：`static bool recovery_pass_entry_ratelimited(const struct recovery_pass_entry *e, unsigned runtime_fraction)`。
- 参数：`e`（`last_run/last_runtime/flags`，`passes_format.h:257-261`）、`runtime_fraction`（倍数，如 100）；返回是否应限流。
- 调用链：sb 持久限流（`bch2_recovery_pass_want_ratelimit_locked`）与内存失败限流（`bch2_run_recovery_passes:656`）共享本函数。
- 代码片段（`passes.c:209-215`）：
```c
static bool recovery_pass_entry_ratelimited(const struct recovery_pass_entry *e,
					    unsigned runtime_fraction)
{
	return !BCH_RECOVERY_PASS_NO_RATELIMIT(e) &&
		(u64) le32_to_cpu(e->last_runtime) * runtime_fraction >
		ktime_get_real_seconds() - le64_to_cpu(e->last_run);
}
```
- 权衡：成本模型限流：上次跑 T 秒，100×T 内不重跑——跑得越贵歇得越久，O(1) 无定时器；`NO_RATELIMIT` 位是单次放行阀（见 5.4）。

### 5.2 `bch2_recovery_pass_entry_get_locked` / `want_ratelimit_locked` / `want_ratelimit`（`passes.c:187-232`）

- 签名：`static bool bch2_recovery_pass_entry_get_locked(struct bch_fs *c, enum bch_recovery_pass pass, struct recovery_pass_entry *e)`；`static bool bch2_recovery_pass_want_ratelimit_locked(...)`；`bool bch2_recovery_pass_want_ratelimit(struct bch_fs *c, enum bch_recovery_pass pass, unsigned runtime_fraction)`。
- 参数：`c`（需持 `sb_lock` 的为 `_locked` 版）、pass、倍数；返回是否限流（无条目 = 没跑过 = 不限流）。
- 调用链：`recovery_pass_needs_set`、`bch2_require_recovery_pass` → `_locked` 版；外部查询 → 公开版（内部 `guard(mutex_noio)(&c->sb_lock)`）。
- 代码片段（`passes.c:195-200`）：
```c
	enum bch_recovery_pass_stable stable = bch2_recovery_pass_to_stable(pass);
	bool found = stable < recovery_passes_nr_entries(r);
	if (found)
		*e = r->start[stable];
	return found;
```
- 权衡：拷贝出 `e` 再判定，锁内只做 memcpy 级短临界；无条目返回 false（新 pass 首跑永不限流）， Fail-open 偏向修彻底。

### 5.3 `bch2_recovery_pass_set_no_ratelimit`（`passes.c:175-185`）

- 签名：`void bch2_recovery_pass_set_no_ratelimit(struct bch_fs *c, enum bch_recovery_pass pass)`。
- 参数：`c`、pass；无返回（幂等：已置位则不写盘）。
- 调用链：管理员/显式 fsck 路径 → 本函数 → 置 `BCH_RECOVERY_PASS_NO_RATELIMIT` + `bch2_write_super`。
- 代码片段（`passes.c:180-184`）：
```c
	struct recovery_pass_entry *e = bch2_sb_recovery_pass_entry(c, pass);
	if (e && !BCH_RECOVERY_PASS_NO_RATELIMIT(e)) {
		SET_BCH_RECOVERY_PASS_NO_RATELIMIT(e, false);
		bch2_write_super(c);
	}
```
- 权衡：注意命名陷阱：宏名为 `NO_RATELIMIT`，但 setter 传 `false`（`passes.c:169,182` 两处皆 `SET_...(e,false)`）——实际语义是“清除限流豁免/恢复限流”或位定义反转，读时以 `!BCH_..._NO_RATELIMIT(e)`（`passes.c:212`）为准，即该位存在时**不限流**。单次放行后 `complete` 会清该位（`passes.c:169`），豁免不遗留。

### 5.4 失败 pass 内存限流（`passes.c:581-597,618,650-660`）

- 签名：常量 `#define RECOVERY_PASS_FAILING_RATELIMIT 100`（`passes.c:618`）；载体 `r->passes_failing_ratelimit[pass]`（`struct recovery_pass_entry` 同构）。
- 参数/返回：失败时记录 `last_run/last_runtime`；下轮 `bch2_run_recovery_passes` 开头过滤。
- 调用链：`bch2_run_recovery_pass` 失败分支写条目 → 下次 `bch2_run_recovery_passes` 读条目过滤 → 成功时 `r->passes_failing = 0` 全清。
- 代码片段（记录，`passes.c:593-596`）：
```c
			r->passes_failing_ratelimit[pass] = (struct recovery_pass_entry) {
				.last_run	= cpu_to_le64(end_time),
				.last_runtime	= cpu_to_le32(max(0, end_time - start_time)),
			};
```
- 代码片段（过滤，`passes.c:656-658`）：
```c
			if (recovery_pass_entry_ratelimited(&r->passes_failing_ratelimit[pass],
							    RECOVERY_PASS_FAILING_RATELIMIT))
				orig_passes_to_run &= ~BIT_ULL(pass);
```
- 权衡：失败不写 sb（注释 `passes.c:586-592`：失败 pass 无资格写超块，且 `NO_RATELIMIT` 豁免的是成功重跑、不豁免失败 hammer）；显式 fsck（`BCH_FS_in_fsck`）跳过此过滤（注释 `passes.c:646-649`：用户点了名就要跑， loud fail 好过静默跳过）；任一成功全清 `passes_failing`，依赖被修好后立即重试而不必等 100×T。

**可学**：限流状态必须持久化（存 `last_run/last_runtime` 于 sb），内存限流等于没有（重启即失忆）；成功/失败用两套限流域，豁免位只管前者。

---

## 六、错误分级调度

声明式分级表 + 按掩码精准派发；运行时不可倒带的靠下次修。

### 6.1 分级声明：`BCH_SB_ERRS` + `FSCK_*`（`sb/errors_format.h:5-13`，`error.c:364-368`）

- 签名：`enum bch_fsck_flags { FSCK_CAN_FIX=BIT(0), FSCK_CAN_IGNORE=BIT(1), FSCK_AUTOFIX=BIT(2), FSCK_ERR_NO_LOG=BIT(3), FSCK_ERR_SILENT=BIT(4); }`；`fsck_flags_extra[]` 按 error id 查附加掩码。
- 参数/返回：`x(name, id, flags)` 宏每错误一行声明能力；`fsck_flags_extra[err]` 在运行时 OR 进调用方 flags。
- 调用链：`BCH_SB_ERRS()` → `fsck_flags_extra` → `bch2_fsck_err_opt` / `__bch2_fsck_err` / `__bch2_bkey_fsck_err` 开头 `flags |= fsck_flags_extra[err]`。
- 代码片段（`error.c:364-368`）：
```c
static const u8 fsck_flags_extra[] = {
#define x(t, n, flags)		[BCH_FSCK_ERR_##t] = flags,
	BCH_SB_ERRS()
#undef x
};
```
- 代码片段（`errors_format.h:5-11`）：
```c
enum bch_fsck_flags {
	FSCK_CAN_FIX		= BIT(0),
	FSCK_CAN_IGNORE		= BIT(1),
	FSCK_AUTOFIX		= BIT(2),
	FSCK_ERR_NO_LOG		= BIT(3),
	FSCK_ERR_SILENT		= BIT(4),
};
```
- 权衡：能力声明与处理逻辑分离：加新错误类型只需在 `BCH_SB_ERRS()` 加一行（含 id 与 AUTOFIX 属性，id 持久稳定）；`u8` 表 O(1)，id 上限 255 需注意（当前已用到 300+，如 `btree_node_topology_gap_between_nodes 328`，实际数组按最大 id sizing——读时以 `WARN_ON(err >= ARRAY_SIZE(...))` 守卫，见 `error.c:449,503,748`）。

### 6.2 `bch2_fsck_err_opt`（`error.c:445-486`）

- 签名：`int bch2_fsck_err_opt(struct bch_fs *c, enum bch_fsck_flags flags, enum bch_sb_error_id err)`。
- 参数：`c`、调用方 flags、错误 id；返回错误码（`fsck_fix / fsck_ignore / fsck_ask / fsck_errors_not_fixed / fsck_repair_unimplemented`，均为 `bch_err_throw` 编码）。
- 调用链：轻量决策点（不打印、不计数）→ 由各 check 路径在“只想知道 fix/ignore”时调用。
- 代码片段（fsck 内，`error.c:457-473`）：
```c
		switch (c->opts.fix_errors) {
		case FSCK_FIX_exit:
			return bch_err_throw(c, fsck_errors_not_fixed);
		case FSCK_FIX_yes:
			if (flags & FSCK_CAN_FIX)
				return bch_err_throw(c, fsck_fix);
			fallthrough;
		case FSCK_FIX_no:
			if (flags & FSCK_CAN_IGNORE)
				return bch_err_throw(c, fsck_ignore);
			return bch_err_throw(c, fsck_errors_not_fixed);
		case FSCK_FIX_ask:
			if (flags & FSCK_AUTOFIX)
				return bch_err_throw(c, fsck_fix);
			return bch_err_throw(c, fsck_ask);
```
- 权衡：`FSCK_FIX_yes` 对不可 fix 但可 ignore 的错误 fallthrough 到 `no` 分支（继续跑而非退出）；`ask` 模式下 `AUTOFIX` 直接 fix 不打扰用户——“简单且安全”的才自动，“需判断”的才问。

### 6.3 `__bch2_fsck_err`（`error.c:488-723`）

全流程中枢，560 行级函数，按段精讲。签名：`int __bch2_fsck_err(struct bch_fs *c, struct btree_trans *trans, struct bpos pos, enum bch_fsck_flags flags, enum bch_sb_error_id err, const char *fmt, ...)`。参数：`c` 可为空（取 `trans->c`）；`trans` 可为空（bkey 路径传 NULL）；`pos != POS_MIN` 表示 inode 域错误，先记 damage；返回同 6.2 错误码集合。调用链：`bch2_fsck_err/inode_fsck_err/ret_fsck_err` 等宏（`error.h:92-226`）→ 本函数 → `bch2_damage_record` + `count_fsck_err_locked` + `do_fsck_ask_yn` + 置 `BCH_FS_errors_fixed / errors_not_fixed / error`。

- 分段 1——先记 damage（`error.c:515-516`）：
```c
	if (!bpos_eq(pos, POS_MIN) && !WARN_ON(!trans))
		try(bch2_damage_record(trans, pos, err));
```
权衡：上报前先记账（注释 `error.c:509-514`）：“error 即 damage，无论修不修”；静默/限流实例同样记录且幂等。完整性来自“唯一上报路径”，而非各修复点自觉调用。

- 分段 2——静默短路（`error.c:535-541`）：
```c
	if ((flags & FSCK_ERR_SILENT) ||
	    test_bit(err, c->sb.errors_silent)) {
		set_bit(BCH_FS_errors_fixed_silent, &c->flags);
		return flags & FSCK_CAN_FIX
			? bch_err_throw(c, fsck_fix)
			: bch_err_throw(c, fsck_ignore);
	}
```
权衡：静默错误不打印不计数不问，直接按能力返回；置 `errors_fixed_silent` 供最终状态区分“修过但安静”。

- 分段 3——计数去重与限流（`error.c:567-575`）：
```c
	mutex_lock(&c->errors.msgs_lock);
	bool repeat = false, print = true, suppress = false;
	bool inconsistent = false, exiting = false;
	struct fsck_err_state *s =
		count_fsck_err_locked(c, err, buf.buf, &repeat, &print, &suppress);
	if (repeat) {
		ret = s->ret;
		goto err_unlock;
	}
```
权衡：同 msg 重复上报（事务 restart 重放）直接复用上次决策 `s->ret`，不二次问用户（`count_fsck_err_locked` 注释 `error.c:402-406`）；`FSCK_ERR_RATELIMIT_NR=10`（`error.c:18`）后降噪（`count_fsck_err_locked:416-422`）。

- 分段 4——非 fsck 运行时决策（`error.c:590-616`）：`AUTOFIX+errors=continue/fix_safe` 则自愈；否则 inconsistent 关机。权衡：运行时自愈门槛极高（必须 AUTOFIX 且 errors 模式允许），不可自愈的宁可 emergency-ro（`__bch2_inconsistent_error`）等下次 fsck，不在运行时冒险。

- 分段 5——fsck 内 ask（`error.c:625-639`）：`do_fsck_ask_yn` 问用户，`Y/N` 全局记忆于 `s->fix`（`YN_ALLNO/ALLYES`）。权衡：逐类记忆避免同类错误问千遍；`trans` 先解锁再问（见七）。

- 分段 6——收尾记账（`error.c:709-716`）：
```c
	} else if (bch2_err_matches(ret, BCH_ERR_fsck_fix)) {
		set_bit(BCH_FS_errors_fixed, &c->flags);
	} else {
		set_bit(BCH_FS_errors_not_fixed, &c->flags);
		set_bit(BCH_FS_error, &c->flags);
	}
```
权衡：`fsck_fix` 不置 `BCH_FS_error`（修好了就不脏），其他一律置脏 + 未修好，供 mount 退出码与 `run_recovery_pass` 的 `complete` 门控（`passes.c:606`）使用。

### 6.4 `__bch2_bkey_fsck_err`（`error.c:732-773`）

- 签名：`int __bch2_bkey_fsck_err(struct bch_fs *c, struct bkey_s_c k, const struct bkey_validate_context *from, enum bch_sb_error_id err, const char *fmt, ...)`。
- 参数：`c`、坏 key、`from`（`from->from` 上下文/`btree/level/journal_seq`）、错误 id；返回 `fsck_fix(fsck_delete_bkey)` 或 ignore。
- 调用链：`bkey_validate` 各处 → `bkey_fsck_err_on` 宏（`error.h:264-268`）→ 本函数 → `__bch2_fsck_err(..., POS_MIN, fsck_flags, err, "%s, delete?", ...)`。
- 代码片段（`error.c:741-747`）：
```c
	unsigned fsck_flags = 0;
	if (!(from->flags & (BCH_VALIDATE_write|BCH_VALIDATE_commit))) {
		if (test_bit(err, c->sb.errors_silent))
			return bch_err_throw(c, fsck_delete_bkey);
		fsck_flags |= FSCK_AUTOFIX|FSCK_CAN_FIX;
	}
```
- 权衡：读路径（非 write/commit）的 bkey 错误一律 AUTOFIX（注释 `error.c:518-529`）：“修法固定（删 key）+ 事务 plumbing 进 validate 太丑”，用“统一删”换代码简洁；写/commit 路径走正常分级（此时有 trans 可解锁问用户）。

### 6.5 `__bch2_inconsistent_error` 系（`error.c:29-97`）与 `__bch2_topology_error`（`error.c:99-111`）

- 签名：`bool __bch2_inconsistent_error(struct bch_fs *c, struct printbuf *out)`（true=已转 RO/panic，false=continue）；`int __bch2_topology_error(struct bch_fs *c, struct printbuf *out)`。
- 参数/返回：前者按 `c->opts.errors`（continue/fix_safe/ro/panic）分派；后者 recovery 内调度 `check_topology` pass，recovery 外转 inconsistent。
- 调用链：运行时一致性断言 → `bch2_fs_inconsistent/bch2_trans_inconsistent` → `bch2_fs_trans_inconsistent`（附 `bch2_trans_updates_to_text`）→ `__bch2_inconsistent_error`；拓扑错 → `__bch2_topology_error` → `bch2_run_explicit_recovery_pass(check_topology)`。
- 代码片段（`error.c:33-39`）：
```c
	switch (c->opts.errors) {
	case BCH_ON_ERROR_continue:
		return false;
	case BCH_ON_ERROR_fix_safe:
	case BCH_ON_ERROR_ro:
		bch2_fs_emergency_read_only(c, out);
		return true;
```
- 代码片段（`error.c:99-110`）：
```c
int __bch2_topology_error(struct bch_fs *c, struct printbuf *out)
{
	prt_printf(out, "btree topology error: ");
	set_bit(BCH_FS_topology_error, &c->flags);
	if (!test_bit(BCH_FS_in_recovery, &c->flags)) {
		__bch2_inconsistent_error(c, out);
		return bch_err_throw(c, btree_need_topology_repair);
	} else {
		return bch2_run_explicit_recovery_pass(c, out, BCH_RECOVERY_PASS_check_topology, 0) ?:
			bch_err_throw(c, btree_need_topology_repair);
	}
}
```
- 权衡：拓扑内外分流：recovery 内可倒带修（调度 pass + 返回 `btree_need_topology_repair` 中断当前 pass），运行时只能 RO 下次修——“修彻底”让位于“不 corrupt”。

### 6.6 `count_fsck_err_locked` / `__bch2_count_fsck_err` / `fsck_err_get`（`error.c:300-443`）

- 签名：`static struct fsck_err_state *count_fsck_err_locked(struct bch_fs *c, enum bch_sb_error_id id, const char *msg, bool *repeat, bool *print, bool *suppress)`；`bool __bch2_count_fsck_err(struct bch_fs *c, enum bch_sb_error_id id, struct printbuf *msg)`。
- 参数/返回：前者需持 `msgs_lock`，更新 `nr/last_msg` 并输出三态；后者是锁包装 + `bch2_sb_error_count`（sb 计数器）。
- 调用链：`__bch2_fsck_err` → `count_fsck_err_locked` → `fsck_err_get`（darray 线性找，无则 kzalloc 新建）。
- 代码片段（限流，`error.c:416-424`）：
```c
		if (c->opts.ratelimit_errors &&
		    s->nr >= FSCK_ERR_RATELIMIT_NR) {
			if (s->nr == FSCK_ERR_RATELIMIT_NR)
				*suppress = true;
			else
				*print = false;
		}
		s->nr++;
```
- 权衡：第 11 个同类错误打印一次“Ratelimiting…”（suppress），之后静默计数（!print），`nr` 照涨供 `fsck_err_counts_to_text`（`error.c:336-347`，按 `nr` 降序排）事后复盘—— firehose 与可观测兼得。

**可学**：分级声明式（能力随错误类型走），调度精准化（fix/ignore/ask/exit 五 outcomes × fsck 内外 × AUTOFIX 三维矩阵），运行时不可倒带的靠“转 RO + 下次修”兜底。

---

## 七、损伤账本与交互

inode 粒度独立 btree，随修复同事务提交，跨快照累积；提问先解锁加超时；写错三守卫降级。

### 7.1 `bch2_damage_record`（`damage.c:87-149`）

- 签名：`int bch2_damage_record(struct btree_trans *trans, struct bpos pos, enum bch_sb_error_id err)`。
- 参数：调用方事务、`pos`（两种 inum 约定：`pos.inode ?: pos.offset`）、错误 id；返回事务更新结果。
- 调用链：`__bch2_fsck_err`（`pos != POS_MIN` 时，`error.c:515-516`）、`bch2_damage_record_data_loss` → 本函数 → `bch2_fsck_damaged`（内存报表）+ `bch2_trans_update`（持久 damage btree）。
- 代码片段（有序插入，`damage.c:109-112`）：
```c
		while (idx < nr && BCH_SB_ERROR_ENTRY_V2_ID(&old[idx]) < err)
			idx++;
		found = idx < nr && BCH_SB_ERROR_ENTRY_V2_ID(&old[idx]) == err;
```
- 代码片段（防包装，`damage.c:122-123`）：
```c
	if (!found && bytes > BKEY_VAL_U64s_MAX * sizeof(u64))
		return 0;
```
- 代码片段（饱和计数，`damage.c:144-146`）：
```c
	/* the setter saturates; a wrapped count would be zero, which validate rejects */
	SET_BCH_SB_ERROR_ENTRY_V2_NR(e, BCH_SB_ERROR_ENTRY_V2_NR(e) + 1);
	SET_BCH_SB_ERROR_ENTRY_V2_LAST(e, now);
```
- 权衡：同事务提交（注释 `damage.c:73-86`）：repair 与记账同生共死，crash 不分离、restart 丢弃连带回滚；value 按 id 升序（validate 强约束，见 7.4）；`bkey.u64s` 为 u8，满了宁可丢新 id（内存报表仍可见）也不包装 corrupt 同事务的 repair；计数饱和而非回绕（回绕到 0 会被 validate 判坏）。

### 7.2 `bch2_damage_delete` / `bch2_damage_clear`（`damage.c:159-195`）

- 签名：`int bch2_damage_delete(struct btree_trans *trans, u64 inum, u32 snapshot)`；`int bch2_damage_clear(struct btree_trans *trans, subvol_inum inum)`。
- 参数/返回：前者删精确版本（inode 删除同事务）；后者按 subvol 视图清（filtered delete：无祖先需要则真删，否则 whiteout）。
- 调用链：inode 删除路径 → `delete`；用户“此文件我认了” → `clear`。
- 代码片段（delete，`damage.c:167-171`）：
```c
	/* whiteouts (cleared damage) die with the inode too: */
	if (k.k->type != KEY_TYPE_damage &&
	    k.k->type != KEY_TYPE_whiteout)
		return 0;
	return bch2_btree_delete_at(trans, &iter, BTREE_UPDATE_internal_snapshot_node);
```
- 代码片段（clear，`damage.c:183-194`）：
```c
	u32 snapshot;
	try(bch2_subvolume_get_snapshot(trans, inum.subvol, &snapshot));
	CLASS(btree_iter, iter)(trans, BTREE_ID_damage,
				SPOS(0, inum.inum, snapshot),
				BTREE_ITER_intent);
	struct bkey_s_c k = bkey_try(bch2_btree_iter_peek_slot(&iter));
	if (k.k->type != KEY_TYPE_damage)
		return 0;
```
- 权衡：`delete` 只杀本版本（注释 `damage.c:151-158`：祖先版本损伤归祖先，快照删除时 merge）；`clear` 用 whiteout 遮蔽继承（快照语义：祖先的伤后代默认可见，清掉只是本视图不看）；无 damage 时不排删除（`return 0` 早退），大多数干净 inode 零开销。

### 7.3 `bch2_damage_record_data_loss`（`damage.c:205-213`）

- 签名：`int bch2_damage_record_data_loss(struct btree_trans *trans, enum btree_id btree, struct bpos pos, enum bch_sb_error_id err)`。
- 参数：btree id（仅 extents 归因）、pos、错误 id；返回记账结果。
- 调用链：运行时数据丢失（掉副本、读错，`damage.c:197-204` 注释）→ 本函数 → `bch2_sb_error_count` + 条件 `bch2_damage_record`。
- 代码片段（`damage.c:205-213`）：
```c
int bch2_damage_record_data_loss(struct btree_trans *trans, enum btree_id btree,
				 struct bpos pos, enum bch_sb_error_id err)
{
	bch2_sb_error_count(trans->c, err);
	return btree == BTREE_ID_extents
		? bch2_damage_record(trans, pos, err)
		: 0;
}
```
- 权衡：非 extents（如 indirect extent）只计数不归因（注释：找 reflink 反向拥有者要倒走指针，得不偿失）——承认“计数完整、归因尽力”的边界。

### 7.4 `bch2_damage_validate` / `bch2_damage_to_text`（`damage.c:20-71`）

- 签名：`int bch2_damage_validate(struct bch_fs *c, struct bkey_s_c k, const struct bkey_validate_context *from)`；`void bch2_damage_to_text(struct printbuf *out, struct bch_fs *c, struct bkey_s_c k)`。
- 参数/返回：前者返回 0 或经 `bkey_fsck_err_on` 跳 `fsck_err` 的删除决策；后者打印每条 `id nr/first/last`。
- 调用链：bkey 验证框架 → `validate`（`damage.h:24-28` 注册进 `bkey_ops`）；debug/报错 → `to_text`。
- 代码片段（validate，`damage.c:37-42`）：
```c
		/* Strictly ascending ids: covers unsorted, dup and zero: */
		bkey_fsck_err_on(id <= prev,
				 c, damage_entries_bad,
				 "entry %u: id %u nr %llu (prev id %u)",
				 i, id, BCH_SB_ERROR_ENTRY_V2_NR(e), prev);
		prev = id;
```
- 权衡：一条 `id <= prev` 同时覆盖乱序/重复/零值三坏（零 id 是 fs 级保留，damage 条目 id 必 >0）；坏条目修法是删 key（`bkey_fsck_err` 语义），账本坏了重建而非将就。

### 7.5 `check_damage_key` / `bch2_check_damage`（`damage.c:223-251`）

- 签名：`static int check_damage_key(struct btree_trans *trans, struct btree_iter *iter, struct bkey_s_c k)`；`int bch2_check_damage(struct bch_fs *c)`。
- 参数/返回：前者逐 key 检查（孤儿 damage 删之）；后者全 btree 遍历（`for_each_btree_key_commit`）。
- 调用链：`recovery_passes[check_damage].fn`（`PASS_FSCK`，依赖 `check_inodes`，`passes_format.h:181-185`）→ `bch2_check_damage` → `check_damage_key`。
- 代码片段（`damage.c:235-239`）：
```c
	CLASS(printbuf, buf)();
	if (ret_fsck_err_on(!bkey_is_inode(inode_k.k),
			    trans, damage_key_no_inode,
			    "damage key with no inode:\n%s",
			    (bch2_bkey_val_to_text(&buf, trans->c, k), buf.buf)))
		return bch2_btree_delete_at(trans, iter, BTREE_UPDATE_internal_snapshot_node);
```
- 权衡：damage 必须有同位 inode（注释 `damage.c:215-222`：无 inode 的 damage 是“老内核无 damage btree 时代遗留 + inum 复用会张冠李戴”），孤儿直接删；`ret_fsck_err_on` 宏使“报错→删 key”一行完成。

### 7.6 `bch2_damage_keys_merge`（`damage.c:263-316`）

- 签名：`struct bkey_i *bch2_damage_keys_merge(struct btree_trans *trans, struct bpos pos, struct bkey_s_c a, struct bkey_s_c b)`。
- 参数：目标 pos、双源 key；返回归并新 key（有序并集，计数饱和加，first 取 min、last 取 max，超长截断留小 id）。
- 调用链：`delete_dead_snapshots` 折叠垂死快照节点 → 本函数。
- 代码片段（归并，`damage.c:290-304`）：
```c
		if (id_a == id_b) {
			e->v[0] = 0;
			e->v[1] = 0;
			SET_BCH_SB_ERROR_ENTRY_V2_ID(e, id_a);
			SET_BCH_SB_ERROR_ENTRY_V2_NR(e,
				BCH_SB_ERROR_ENTRY_V2_NR(ea) +
				BCH_SB_ERROR_ENTRY_V2_NR(eb));
			SET_BCH_SB_ERROR_ENTRY_V2_FIRST(e,
				min(BCH_SB_ERROR_ENTRY_V2_FIRST(ea),
				    BCH_SB_ERROR_ENTRY_V2_FIRST(eb)));
```
- 权衡：不用“copy-if-empty”（注释 `damage.c:253-262`：垂死 key 可能有子 key 建后新记的数，会丢），必须真归并；截断策略与 record 的 skip-on-full 一致（留小 id），账本满时行为可预测。

### 7.7 `bch2_inode_has_damage` / `bch2_damage_accumulate`（`damage.c:323-385`）

- 签名：`int bch2_inode_has_damage(struct btree_trans *trans, u64 inum, u32 snapshot)`（>0 有、0 无、<0 错）；`int bch2_damage_accumulate(struct btree_trans *trans, u64 inum, u32 snapshot, bch_sb_errors_cpu *out)`。
- 参数：inum、视图 snapshot、累积输出（保持 id 有序，支持非空合并）；返回 0 或错误。
- 调用链：readdir 过滤 → `has_damage`；用户查询某文件全部历史伤 → `accumulate`（沿 `bch2_snapshot_parent` 上溯祖先）。
- 代码片段（上溯，`damage.c:381-382`）：
```c
		snapshot = bch2_snapshot_parent(c, k.k->p.snapshot);
	} while (snapshot);
```
- 权衡：存储细节收敛于二函数之后（注释 `damage.c:318-322`）；`accumulate` 把祖先伤并入后代视图（“祖先的数据伤就是后代看到的数据伤”，注释 `damage.c:331-339`），readdir 用轻量 `has_damage`（单点查）而非全累积，热路径零浪费。

### 7.8 交互：`parse_yn_response` / `bch2_fsck_ask_yn` / `do_fsck_ask_yn`（`error.c:207-392`）

- 签名：`static enum ask_yn parse_yn_response(char *buf)`（`YN_NO/YES/ALLNO/ALLYES`，`error.c:207-212`）；`static enum ask_yn bch2_fsck_ask_yn(struct bch_fs *c, struct btree_trans *trans)`（内核/用户态双实现，`error.c:233,281`）；`static int do_fsck_ask_yn(struct bch_fs *c, struct btree_trans *trans, struct printbuf *question, const char *action)`。
- 参数/返回：解析单字符 `y/n/Y/N`；ask 返回用户选择；do 版问完后 `bch2_trans_relock`。
- 调用链：`__bch2_fsck_err` ask 分支 → `do_fsck_ask_yn` → `bch2_print(question)` → `bch2_fsck_ask_yn`。
- 代码片段（先解锁，`error.c:243-244`）：
```c
	if (trans)
		bch2_trans_unlock(trans);
```
- 代码片段（超时降级，`error.c:258-263`）：
```c
		int r = bch2_stdio_redirect_readline_timeout(stdio, &line, t);
		if (r == -ETIME) {
			bch2_trans_unlock_long(trans);
			unlock_long_at = 0;
			goto rewait;
		}
```
- 代码片段（问后重锁，`error.c:385-389`）：
```c
	int ask = bch2_fsck_ask_yn(c, trans);
	if (trans) {
		int ret = bch2_trans_relock(trans);
		if (ret)
			return ret;
	}
```
- 权衡：提问不持锁（先 `unlock`，2 秒无答再 `unlock_long` 让出更久，注释含 `stdio_filter` 防错 console 问错人 `error.c:237-241`）；问后 `relock` 失败则整个 fsck 错误返回 restart（调用方 `ret < 0 → goto err_unlock`，`error.c:629-630`），事务语义优先于用户答案。

### 7.9 内存报表：`bch2_fsck_damaged` 系（`error.c:810-949`）与写错路径（`error.c:125-205`）

- 签名：`void bch2_fsck_damaged(struct btree_trans *trans, struct bpos pos, enum bch_sb_error_id err)`；`static int damaged_path_resolve(struct btree_trans *trans, u64 inum, u32 snapshot, struct printbuf *path)`；`void bch2_fsck_damaged_paths_to_text(struct printbuf *out, struct bch_fs *c)`；`void bch2_io_error(struct bch_dev *ca, enum bch_member_error_type type)`；`void bch2_fatal_error(struct bch_fs *c, const char *func, const char *fmt, ...)`。
- 参数/返回：`damaged` 按 `(inum,snapshot)` 去重合并 error id（`FSCK_DAMAGED_PATHS_MAX=4096` 封顶，`PRINT=200`，`error.c:810-811`）；`resolve` 快照死时退到同 inum 存活快照解路径（注释 `error.c:869-874`）；`io_error` 仅计数 + 排 work。
- 调用链：`bch2_damage_record` → `bch2_fsck_damaged`；fsck 尾摘要 → `paths_to_text` → `damaged_path_resolve` → `bch2_inum_snapshot_to_path`；写错 → `bch2_io_error` → `bch2_io_error_work`（`write_error_timeout` 后降 dev-ro/fs-ro）。
- 代码片段（last 优先，`error.c:845-851`）：
```c
	/* Damage on one inode arrives in runs - check the last entry first: */
	if (c->errors.damaged_paths.nr) {
		struct fsck_damaged_path *last = &darray_last(c->errors.damaged_paths);
		if (last->inum == inum && last->snapshot == pos.snapshot) {
			fsck_damaged_path_add_err(last, err);
			return;
		}
	}
```
- 代码片段（写错三守卫，`error.c:165-167`）：
```c
		if (!READ_ONCE(ca->removing) &&
		    !test_bit(BCH_FS_stopping, &c->flags) &&
		    ca->mi.state < BCH_MEMBER_STATE_ro) {
```
- 权衡：损伤同 inode 成串到达，last-entry 优先是 O(1) 快路径；报表封顶 4096（超了置 `alloc_err` 注“list incomplete”）防 OOM，打印截 200（余下指 debugfs 全量）；写错 work 持 `ref_outer` 而非 `ca->ref`（注释 `error.c:157-166,197-201`），device removal 排空 `ca->ref` 时不死锁 `state_lock`；`removing/stopping/已 ro` 三守卫防 teardown 中途翻成员状态。

**可学**：账本独立 btree 但同事务提交（crash 一致）；提问不持锁 + 超时降级；报表有损（封顶截断）但显式声明不完整。

---

## 八、设计启示

| 原报告要点 | 代码级落点 | 权衡一句话 |
|---|---|---|
| 编排收敛 | `recovery_passes[]` 表 + `run_recovery_passes` 主循环（`passes.c:268-277,620-727`） | 新增修复只加宏行，顺序/倒带/限流由编排层统一保证 |
| 编号隔离 | 双向 `u8` 表 + stable 稀疏数组（`passes.c:44-84`，`passes_format.h:24-55`） | 内存随便重排，磁盘 id 永冻；越界归零前向兼容 |
| 延迟闭包 | `pass_dependents` 不动点 + `should_defer` 全 ONLINE 判定（`passes.c:294-320`） | 只看自己会切断依赖链，必须看后代闭包 |
| 去重自证 | `__test_and_set_bit_le64` 去重 + `WARN_ON(write_sb)`（`passes.c:407-413,520-525`） | 同一 pass 发现风暴下只写一次盘；临时路径用断言自证 |
| 持久限流 | `last_run/last_runtime` 存 sb + 失败内存限流（`passes.c:151-232,581-660`） | 成功/失败双域；豁免位只管成功重跑，不管失败 hammer |
| 分级调度 | `BCH_SB_ERRS` 声明 + `fsck_err_opt/__fsck_err` 矩阵（`error.c:364-723`） | 能力随类型走；运行时自愈门槛极高，不可修则 RO 下次修 |
| 账本同事务 | `damage_record` 与 repair 同 `trans`（`damage.c:87-149`） | crash 不分离、restart 连带滚；满了丢新不包装 |
| 提问解锁 | `unlock→问→relock` + 2s `unlock_long`（`error.c:243-263,385-389`） | 用户思考时不卡 btree；relock 失败则答案作废 |

复核途径（均已核实存在）：

- `grep -n "bch2_run_explicit_recovery_pass\|recovery_pass_should_defer\|pass_dependents" fs/init/passes.c` 看编制定位（`passes.c:294-320,380-533`）。
- `grep -n "recovery_pass_entry_ratelimited\|RECOVERY_PASS_FAILING_RATELIMIT\|NO_RATELIMIT" fs/init/passes.c` 看双域限流（`passes.c:169,182,209-232,618,650-660`）。
- `grep -n "fsck_flags_extra\|bch2_fsck_err_opt\|__bch2_fsck_err" fs/init/error.c` 看分级调度（`error.c:364-723`）。
- `grep -n "bch2_damage_record\|bch2_damage_keys_merge\|bch2_damage_accumulate" fs/init/damage.c` 看账本（`damage.c:87-149,263-385`）。
- `grep -n "BCH_RECOVERY_PASSES()\|PASS_ONLINE\|PASS_NODEFER" fs/init/passes_format.h` 看 pass 声明（`passes_format.h:5-240`）。
- `grep -n "FSCK_CAN_FIX\|FSCK_AUTOFIX" fs/sb/errors_format.h` 看错误分级声明（`errors_format.h:5-13` 及后续 `x()` 行）。
