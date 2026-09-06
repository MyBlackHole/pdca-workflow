# bcachefs SIX 锁专题学习报告（T0512）：代码级精讲

> 精读对象：`fs/util/six.h`（全 465 行）、`fs/util/six.c`（全 1131 行）、
> `fs/btree/locking.c`（全 1384 行）+ `fs/btree/locking.h`（544 行，含全部内联快路）。
> 事实源为源码注释与实现；下文所有行号均经 Grep/Read 核实，代码片段均 ≤10 行。

---

## 一、为什么需要第三态：读写锁的死结

设计陈述：`six.h:9-20` + `locking.c:3-37`（DOC_LATEX）。

| 项目 | 内容 |
|------|------|
| 死结 | 读不能升级为写。多线程各持读再升级 → 互等，必死锁（`six.h:13-15`，`locking.c:16-18`） |
| 树场景 | btree split：起点在叶，发现要分裂需排斥父节点防其他 split；读锁探路→升级写锁改父指针 → 与分裂兄弟叶的线程死锁（`locking.c:23-29`） |
| SIX 洞察 | split 长期要的是父节点的**排斥权**，真改内存只是指针切换一瞬。排斥权持有时长 ≫ 真修改时长（`locking.c:19-21,31-37`） |
| 解法 | 第三态 `intent`：与读兼容、与 intent/写互斥。操作起点拿 intent 占位定范围，读全程并发；逐节点短持写锁真改（`six.h:17-20`） |

调用链（自顶向下）：`btree_node_lock(trans,path,b,lvl,intent)`（`locking.h:357`）
→ 快路 `six_trylock_type`（`six.h:258`）→ 慢路 `bch2_btree_node_lock_slowpath`（`locking.c:704`）
→ `btree_node_lock_nopath`（`locking.h:308`）→ `six_lock_ip_waiter/six_lock_contended`（`six.c:739/769`）。

**可学之处**：先量化"排斥权持有时长 vs 真修改时长"错配，再决定加不加状态。

---

## 二、三态语义与数据结构：逐函数/逐字段精讲

### 2.1 `enum six_lock_type`（`six.h:133-137`）

```c
enum six_lock_type {
	SIX_LOCK_read,    /* 0，与读兼容 */
	SIX_LOCK_intent,  /* 1，与读兼容、与intent/写互斥 */
	SIX_LOCK_write,   /* 2，与一切互斥 */
};
```

- 参数/返回：无；纯类型标签，数值被多处复用（见 2.5 WAITING 位移、`locking.h:121-126` 与 SIX 一一对应）。
- 调用链：`l[]` 表（`six.c:48`）、`lock_type_conflicts`（`locking.c:426`）、`__btree_lock_want`（`locking.h:197`）都以它为下标/判据。
- 权衡：intent 编码为 1 使冲突判据可写成 `t1+t2>1`（读读和=0 不冲突，其余都>1），见第六节。

### 2.2 `struct six_lock_waiter`（`six.h:139-146`）

```c
struct six_lock_waiter {
	u64 trans_start_time; struct task_struct *task;
	enum six_lock_type lock_want; bool lock_acquired;
	u16 slot_idx;  /* 插入时设定，用于 O(1) 自摘除 */
};
```

- 签名：被嵌入 `struct btree_trans.locking_wait`（`btree/types.h:730` 附近，grep 核实引用）。
- 调用链：`btree_node_lock_nopath` 传 `&trans->locking_wait`（`locking.h:326-327`）→ `six_lock_wait_fifo_insert` 发布（`six.c:250`）→ 死锁检测 `container_of(w, btree_trans, locking_wait)` 回查（`locking.c:560`）→ 唤醒置 `lock_acquired=true`（`six.c:375/410`）。
- 权衡：`slot_idx` 让 abort 路径 O(1) 摘除（`six.c:674`），不用扫描；`trans_start_time` 既是唤醒选最老者的键，又是检测遍历游标（`six.h:121-123`）。

### 2.3 `struct six_lock_wait_slot` + 位打包（`six.h:159-165`）

```c
#define SIX_LOCK_WANT_BITS 2
#define SIX_LOCK_WANT_MASK ((1U << SIX_LOCK_WANT_BITS) - 1)
struct six_lock_wait_slot { struct six_lock_waiter *w; u64 start_time; };
```

- 语义：`start_time = trans_start_time<<2 | lock_want`（写入点 `six.c:285-286`）。注释 `six.h:148-158` 明示：同类比较免掩码（低位相等可直接比），跨类先掩码。
- 调用链：写入 `six_lock_wait_fifo_insert`（`six.c:285`）→ 读取过滤 `(slot->start_time & MASK) != lock_type`（`six.c:353/392`）→ 最老比较 `time_before64(slot->start_time, oldest->start_time)`（`six.c:396`）→ 检测冲突 `i->start_time & MASK`（`locking.c:564`）。
- 权衡：唤醒扫描免解引用每个 waiter（只碰选中的 `->task`），代价是打包/解包心智负担 + 2 位假设（类型数 ≤4）。

### 2.4 `struct six_lock_wait_fifo`（`six.h:179-184`）+ 内联 8 槽（`six.h:186`）

```c
struct six_lock_wait_fifo {
	u16 size; u16 nr; u16 next_free_hint;
	struct six_lock_wait_slot data[];
};
#define SIX_LOCK_INLINE_WAITERS 8
```

- 语义（`six.h:167-178`）：非 FIFO，"固定槽位 RCU 表"。删除写 NULL（`six.c:241`），插入找空槽（`six.c:256-265`），`nr` 为高水位、尾部全墓碑时收缩（`six.c:220-226`）。
- 初始化：`__six_lock_init` 置 `size=8, nr=0, hint=0`，`wait_fifo` 指向 `inline_fifo`（`six.c:1104-1108`）。
- 权衡：绝大多数锁竞争者 <8，零堆分配；超 8 才 `realloc` 翻倍（`six.c:320`），上限 `1<<15`（`six.c:312`）。

### 2.5 `struct six_lock`（`six.h:188-207`）

```c
struct six_lock {
	atomic_t state; u32 seq; unsigned __percpu *readers;
	unsigned intent_lock_recurse, write_lock_recurse;
	struct task_struct *owner;
	raw_spinlock_t wait_lock;
	struct six_lock_wait_fifo __rcu *wait_fifo;
	struct six_lock_wait_fifo inline_fifo;
	struct six_lock_wait_slot inline_fifo_data[8];
	struct lockdep_map dep_map; /* CONFIG_DEBUG_LOCK_ALLOC */
};
```

- `state` 位布局（`six.c:26-32`）：低 26 位读计数（`HELD_read=~(~0U<<26)`），bit26 intent，bit27 write，bit28+type WAITING 位，bit31 NOSPIN。读多时低 26 位是计数器，intent/write 是独占位。
- `readers` per-CPU（`six.h:191`）：读多场景免缓存颠簸；可分配失败回退非 per-CPU 语义（`six.c:1119-1128` 注释明示"优化而非语义"）。
- `owner`：仅 intent 有意义（`six_set_owner`，`six.c:81-93`：非 intent 直接返回；首次拿 intent 记 owner，复核 `EBUG_ON(owner!=current)`）。
- `intent_lock_recurse/write_lock_recurse`：可重入计数（`six.c:845-855` 递减短路），write 只许"一次持有+计数叠加"（`six_lock_increment` 对 write 先 `recurse++` 再 fallthrough 到 intent，`six.c:970-976`）。
- 权衡：结构变大（内联 8 槽 + per-CPU 指针）换无竞争快路零分配；recurse 把可重入交上层，原语保持最小。

### 2.6 `__six_lock_init` — 签名/参数/返回/调用链（`six.c:1098-1131`）

```c
void __six_lock_init(struct six_lock *lock, const char *name,
		     struct lock_class_key *key, enum six_lock_init_flags flags,
		     gfp_t gfp);
```

- 参数：`lock` 待初始化；`name/key` 给 lockdep；`flags` 仅 `SIX_LOCK_INIT_PCPU`（`six.h:213-215`）；`gfp` 传给 `alloc_percpu_gfp`。
- 返回：void；per-CPU 分配失败不报错（语义不变，见上）。
- 调用链：宏 `six_lock_init` 就地声明 `static key`（`six.h:226-231`）→ `__six_lock_init`；btree 封装 `bch2_btree_lock_init`（`locking.c:143-149`，key 全局单例 `bch2_btree_node_lock_key` + `lockdep_set_notrack_class`）。
- 权衡：btree 全节点共享一个 lockdep class（防状态爆炸）+ notrack（btree 自有环检测，不走通用 lockdep 排序）。

---

## 三、seq 乐观重锁：掉锁做 IO 的答案

设计陈述：`six.h:48-64` + `locking.c:64-73`。

### 3.1 `six_lock_seq`（`six.h:244-247`）

```c
static inline u32 six_lock_seq(const struct six_lock *lock)
	{ return lock->seq; }
```

- 前置：调用时应持有读/intent、不能持有写（`six.h:237` 注释）。
- 调用链：加锁后快照 `path->l[level].lock_seq = six_lock_seq(...)`（`iter.c:799`、`locking.c:799`、`key_cache.c:41`）→ 解锁做 IO → `six_relock_type` 比对。
- 权衡：一次 u32 读取，零原子开销；正确性依赖"写解锁必递增"（下）。

### 3.2 写解锁递增 seq（`six.c:857-858`，在 `six_unlock_ip:834-862` 内）

```c
	if (type == SIX_LOCK_write)
		lock->seq++;
	do_six_unlock_type(lock, type);
```

- 精确语义：**仅写解锁递增**（实现），DOC 表述"take and release 递增"（`six.h:50`）是宽松说法——`__btree_node_lock_write` 快路拿写锁不增 seq（`locking.h:394`），`bch2_btree_node_unlock_write_inlined` 还额外 `linked->l[level].lock_seq++` 预补偿（`locking.h:246-257`，保持"持有者视角 seq 连续"）。
- 调用链：`six_unlock_ip(write)` → `seq++` → `atomic_sub_return_release`（`six.c:813`）→ `six_lock_wakeup(read)`（`six.c:816`，`unlock_wakeup` 表 `six.c:65`：write 释放唤 write 等待者…注意映射是"释放某态唤醒等该态者"，read 释放唤 write 者等，见 5.1）。
- 权衡：每次写解锁一次加法，换"放锁-阻塞-重拿"可验证。

### 3.3 `six_relock_ip`（`six.c:492-505`）+ `six_relock_type`（`six.h:354-358`）

```c
bool six_relock_ip(struct six_lock *lock, enum six_lock_type type,
		   unsigned seq, unsigned long ip);
static inline bool six_relock_type(struct six_lock *lock,
				   enum six_lock_type type, unsigned seq)
	{ return six_relock_ip(lock, type, seq, _THIS_IP_); }
```

- 参数/返回：`seq` 为此前快照；先比对 `six_lock_seq(lock)!=seq`（`six.c:495`，不等直接 false，连 try 都省）→ `six_trylock_ip` → **二次比对**（`six.c:498`，关 TOCTOU：try 成功后 seq 变了说明中间有写，必须解锁重试）→ true。
- 调用链：`__bch2_btree_node_relock`（`locking.c:889-912`）：`six_relock_type(want, lock_seq)` 或（seq 匹配 + 本事务别处已持锁→`increment`，`locking.c:900-901`）→ `mark_btree_node_locked`。
- 权衡：双检一次 trylock 开销，换"通常免重走整条 btree 路径"。

### 3.4 实战范式 A：读穿透掉锁做 IO（`cache.c:1134-1150`，核实）

```c
u32 seq = six_lock_seq(&b->c.lock);
six_unlock_intent(&b->c.lock);   /* 解锁再做IO */
bch2_trans_unlock(trans);
bch2_btree_node_read(trans, b, sync);
... else if (!six_relock_type(&b->c.lock, lock_type, seq))
	b = NULL;                     /* 失败置空，上层重走 */
```

- 调用链：`bch2_btree_node_read`（发 IO）→ relock 失败 → 返回 NULL → 调用方 `bch2_trans_relock` 全路径重锁（`cache.c:1163-1164` 注释）。
- 权衡：IO 期零持锁，并发全开；失败代价是重遍历（可接受，读穿透本就慢路）。

### 3.5 实战范式 B：SRCU 短等预算（`iter.h:354-365`，核实；原报告"超限先放读侧锁"表述修正如下）

```c
static inline long bch2_trans_short_wait_budget(struct btree_trans *trans, long timeout)
{
	if (!trans || !trans->srcu_held) return timeout;
	long elapsed = jiffies - trans->srcu_lock_time;
	if (elapsed >= HZ) { bch2_trans_unlock_long(trans); return timeout; }
	return min(HZ - elapsed, timeout);
}
```

- 签名/返回：输入期望超时，返回本轮允许等多久。SRCU 已持 ≥1s（HZ）→ `bch2_trans_unlock_long` 放 SRCU（`locking.c:1278`：同时把未锁定的 cached 路径毒化 `ERR_PTR(no_btree_node_srcu_reset)`，`locking.c:1288-1290`）后全额等；否则截断到 HZ 剩余。
- 调用链：`trans_closure_sync_timeout`（`iter.h:374`，循环扣减 `remaining`）、`trans_wait_on_bit_io`（`iter.h:445`，预算耗尽转无界 `wait_on_bit_io`）。
- 权衡：SRCU 持有 stall 内存回收，长等必须放；截断等待把"长阻塞"切成"短等+重试"，代价是虚假超时一轮。注意：它放的是 **SRCU**，不是 SIX 读锁——SIX 侧的"放锁做事"由 seq/relock 承担，二者正交。

**可学之处**：任何"持锁做阻塞事"先问：能否快照 seq 后放锁？seq 把"持有"从布尔变版本，是乐观并发最小构件；SRCU 这类域锁另配预算截断。

---

## 四、升降级与转换：精细流转

### 4.1 `six_lock_downgrade`（`six.c:870-875`）

```c
void six_lock_downgrade(struct six_lock *lock)
	{ six_lock_increment(lock, SIX_LOCK_read); six_unlock_intent(lock); }
```

- 签名/返回：void，不失败。先读计数+1（`increment` 内 per-CPU 或原子加，`six.c:960-968`），再走正常 intent 解锁（含唤醒 intent 等待者，`six.c:816` + 表 `six.c:59`）。
- 调用链：`__bch2_btree_path_downgrade`（`locking.c:1126`）→ `mark_...READ_LOCKED`；`bch2_btree_node_write_trans` 写完读持有者降回（`write.c:666-667`）；`cache.c:1150` 非 path 填充降级。
- 权衡：两步复合但顺序不可换（先加读再解 intent，无中间无锁态）；不可失败使调用方无回退负担。

### 4.2 `six_lock_tryupgrade`（`six.c:886-911`）

```c
bool six_lock_tryupgrade(struct six_lock *lock);
	u32 old = atomic_read(&lock->state), new;
	do {
		new = old;
		if (new & SIX_LOCK_HELD_intent) return false;
		if (!lock->readers) { ...; new -= l[read].lock_val; }
		new |= SIX_LOCK_HELD_intent;
	} while (!atomic_try_cmpxchg_acquire(&lock->state, &old, new));
	if (lock->readers) this_cpu_dec(*lock->readers);
	six_set_owner(lock, SIX_LOCK_intent, old, current);
```

- 参数/返回：bool。可失败（已有 intent 直接 false，CAS 循环隐含竞争失败重试但遇 intent 即退）。
- 双模式：非 per-CPU 把读计数减回（`new -= 1`，`six.c:898`）；per-CPU 减本 CPU 槽（`six.c:905`）。owner 按 `old` 是否已有 intent 判定（`six_set_owner`，`six.c:81`）。
- 调用链：`bch2_btree_node_upgrade`（`locking.c:943-945`：已持锁→tryupgrade，未持→`six_relock_type(intent, lock_seq)`）→ 失败再试"seq 匹配+别处已持→increment+解旧"（`locking.c:948-952`）→ 仍失败记 `btree_path_upgrade_fail`（`locking.c:954`）返回 false，上层转事务 restart（`__bch2_btree_path_upgrade`，`locking.c:1026`）。
- 权衡：升级永不睡眠，调用方必须有回退（restart/重走）；EBUG 断言非 per-CPU 时必有读计数（`six.c:897`）防"无读升 intent"误用。

### 4.3 `six_trylock_convert`（`six.c:924-940`）

```c
bool six_trylock_convert(struct six_lock *lock,
			 enum six_lock_type from, enum six_lock_type to);
	if (to == from) return true;
	if (to == SIX_LOCK_read) { six_lock_downgrade(lock); return true; }
	else return six_lock_tryupgrade(lock);
```

- 约束：`EBUG_ON(to==write||from==write)`（`six.c:928`）——write 转换另走 `__btree_node_lock_write`（`locking.h:378`），见 7.3。
- 权衡：同型短路 true；降级永真、升级可假，调用方只需处理一个 false 分支。

### 4.4 `six_lock_increment`（`six.c:953-979`）+ `six_lock_counts`（`six.c:1026-1039`）+ `six_lock_readers_add`（`six.c:1061-1071`）

```c
void six_lock_increment(struct six_lock *, enum six_lock_type);
struct six_lock_count six_lock_counts(struct six_lock *); /* n[3] */
void six_lock_readers_add(struct six_lock *, int nr);
```

- `increment`：read→per-CPU/原子加（`six.c:960-968`，断言已持读或 intent）；write→`write_lock_recurse++` 后 fallthrough 到 intent（`six.c:970-976`，intent 断言 + `intent_lock_recurse++`）；write 不许"真重入"，只计数（DOC `six.h:85-86`）。
- `counts`：读（per-CPU 求和 vs 状态低 26 位）、intent（持有位 + recurse）、写（持有位），供诊断打印（`locking.c:822-827,1090`）。
- `readers_add(nr)`：上层实现"暂借读计数拿写锁"——`bch2_btree_node_lock_write_contended` 先 `-readers`（`locking.c:742`，因 `six_unlock` 要等读归零才唤醒，注释 `locking.c:735-739`），拿写锁后再 `+readers`（`locking.c:747`）。DOC 在 `six.c:1041-1060`。
- 权衡：per-thread 持有追踪完全交上层（`btree_path.nodes_locked` 位图，`locking.h:174`），原语零线程局部存储；代价是上层必须维护精确（`verify_locks` 用 BUG_ON 兜底，`locking.c:1334`）。

**可学之处**：升级必须可失败且调用方有回退；降级必须无中间态；write 的"重入"是计数而非真锁。

---

## 五、等待队列：RCU 加槽位打包 + 定向唤醒

### 5.1 `l[]` 锁值表与 `unlock_wakeup` 映射（`six.c:48-67`）

```c
[read]   {.lock_val=1, .lock_fail=HELD_write, .held_mask=HELD_read,   .unlock_wakeup=write};
[intent] {.lock_val=HELD_intent, .lock_fail=HELD_intent, ... .unlock_wakeup=intent};
[write]  {.lock_val=HELD_write, .lock_fail=HELD_read, ... .unlock_wakeup=read};
```

- 解读：读拿锁 +1，遇写则败；intent 遇 intent 败（与读兼容体现在 `lock_fail` 不含读）；写是"计数器式"（`lock_fail=HELD_read` 即有任何读/低位非零则败，`held_mask` 却是 bit27，见 5.2）。
- `unlock_wakeup`：释放 read→唤 write 等待者；释放 intent→唤 intent；释放 write→唤 read。配合 `six_lock_wakeup` 的 WAITING 位检查（`six.c:441`）实现定向。
- 权衡：表驱动消除分支；但 write 的"值 vs 掩码"不对称是理解门槛（根源：读计数占低 26 位，写必须感知"有读"而非单 bit）。

### 5.2 `__do_six_trylock`（`six.c:122-214`）：三分支快路

```c
static int __do_six_trylock(struct six_lock *lock, enum six_lock_type type,
			    struct task_struct *task, bool try);
```

- 返回三值：`>0` 成功；`0` 失败；`<0` 为 `-1-wakeup_type`（per-CPU 模式下伪失败需补唤醒，注释 `six.c:113-121`）。
- 分支 1（`six.c:159-169`）：intent 或非 per-CPU——读状态 CAS 加 `lock_val`，`lock_fail` 命中则败；**非 try 的写只做 `smp_mb` 不 CAS**（`six.c:163`：慢路径写已预加 `HELD_write`，此处只验读归零，见 5.4）。
- 分支 2（`six.c:170-185`）：per-CPU 读——先 `this_cpu_inc` 宣称持有 + `smp_mb`，再验 `HELD_write`；败则减回 + 补读屏障，遇 `WAITING_write` 返回 `-1-write`（`six.c:183-184`，无锁双变量算法，注释 `six.c:133-158`）。
- 分支 3（`six.c:186-205`）：per-CPU 写——`try` 才 `atomic_add(HELD_write)`（慢路径已加则跳过，`six.c:187-188`），`smp_mb` 后 `pcpu_read_count` 求和（`six.c:103-111` 逐 CPU 累加）；try 失败回减，遇 `WAITING_read` 返回 `-1-read`（`six.c:200-204`）。
- 成功收尾 `six_set_owner`（`six.c:207-208`）；EBUG 自检写 try 失败不残留 `HELD_write`（`six.c:210-211`）。
- 调用链：`do_six_trylock`（`six.c:449`，`<0` 就地补唤醒）→ `six_trylock_ip`（`six.c:470`）/`six_lock_ip_waiter` 快路（`six.c:749`）；慢路径重试 `__do_six_trylock(try=false)`（`six.c:613`）。
- 权衡：per-CPU 读快路零 CAS（只有本 CPU 计数 + 屏障），代价是写侧 `pcpu_read_count` 要扫全部 CPU + 伪失败补唤醒协议。

### 5.3 等待表增删改：`insert/remove/shrink/realloc`（`six.c:220-328`）

```c
static inline int six_lock_wait_fifo_insert(struct six_lock *, struct six_lock_waiter *);
static inline void six_lock_wait_fifo_remove(struct six_lock_wait_fifo *, u16 idx);
static inline void six_lock_wait_fifo_shrink(struct six_lock_wait_fifo *);
noinline static int six_lock_wait_fifo_realloc(struct six_lock *, struct six_lock_waiter *,
					       struct six_lock_wait_fifo **);
```

- `insert`（`six.c:250-292`）：持 `wait_lock`；`next_free_hint` 命中即填（`six.c:256-258`），否则从头扫 `nr`（`six.c:260-262`），`nr<size` 扩高水位（`six.c:264-265`），满返回 0（`six.c:267`，调用方转 `realloc`）。发布顺序：先 `start_time` + `slot_idx` + `nr/hint`，最后 `smp_store_release(&slot->w, wait)`（`six.c:285-291`），配检测侧 `smp_load_acquire`（`locking.c:559`）。
- `remove`（`six.c:233-243`）：`WRITE_ONCE(slot->w,NULL)` + `hint=min(hint,idx)`，不缩 `nr`（懒缩）。
- `shrink`（`six.c:220-226`）：尾部墓碑 while 弹出 + hint 钳位；调用点：唤醒尾（`six.c:430-431`）、abort 摘除后（`six.c:675`）。
- `realloc`（`six.c:295-328`）：已有 2 倍新缓冲→`memcpy nr` + `rcu_assign_pointer` + 旧堆（非内联）转交调用方后 `kfree_rcu_mightsleep`（`six.c:303-308` + `six.c:693-694`）；否则解锁后 `kzalloc(2x)`（`six.c:315-321`，`GFP_KERNEL` 故必须先 `raw_spin_unlock`），上限 `1<<15` 报 `-ENOMEM`（`six.c:312-313`，上层转事务 restart `lock_waitlist_alloc`，`locking.h:331-332`）。
- 权衡：固定槽位 → RCU 读者永不见条目搬家（`six.h:167-178`）；扩容全拷 + RCU 延迟释，换检测侧无锁遍历。

### 5.4 `__six_lock_slowpath`（`six.c:585-698`）：睡眠全流程

```c
__always_inline static int __six_lock_slowpath(struct six_lock *lock, enum six_lock_type type,
			 struct six_lock_waiter *wait, six_lock_should_sleep_fn should_sleep_fn,
			 unsigned long ip);
```

- 写预加（`six.c:593-597`）：write 先 `atomic_add(HELD_write)` + `smp_mb__after_atomic`（让 per-CPU 读快路可见，后续 try 皆 `try=false` 不再加）。
- 入队前重试（`six.c:606-617`）：持 `wait_lock` 置 `WAITING<<type`（`six.c:612`，`six_set_bitmask` 条件置位省原子，`six.c:69-73`）→ `__do_six_trylock(try=false)` → `<0` 就地 `__six_lock_wakeup` 补唤醒（`six.c:614-617`）。
- 入队（`six.c:619-633`）：`insert ?: realloc`；`realloc` 返回 0（新缓冲就绪）→ `goto retry_relock`（`six.c:623-624`，重走 WAITING+try，覆盖解锁竞态）；`-ENOMEM` 且 write→清预加 + 唤 read（`six.c:626-629`）后 `goto out`。
- 睡前：`optimistic_spin` 或 `smp_load_acquire(lock_acquired)` 命中直接 `out`（`six.c:641-643`）；否则 `schedule()` 让一轮（`six.c:646`，注释"死锁检测前先让"）。
- 主循环（`six.c:648-689`）：`TASK_UNINTERRUPTIBLE` → acquire 验 `lock_acquired`（`six.c:656`，配唤醒侧 release，`six.c:368-375`）→ `should_sleep_fn`（即 `bch2_six_check_for_deadlock`）非零→持锁验 `acquired`（`six.c:669`）：未得则 `remove+shrink`（`six.c:674-675`），已得则 `do_six_unlock_type` 归还（`six.c:679-680`，注释 `six.c:661-667`：即使已拿锁也必须返回 detector 错误，因 detector 已改外部状态如发 restart）→ write abort 另清预加 + 唤 read（`six.c:681-683`）→ `schedule()`。
- 收尾 `kfree_rcu_mightsleep(new_wf)`（`six.c:693-694`）+ trace（`six.c:695`）。
- 权衡：`TASK_UNINTERRUPTIBLE` 不响应信号（死锁靠 detector 的 restart 中止，而非信号）；abort 即使竞赢也归还锁，保证 detector 语义优先。

### 5.5 `six_lock_ip_waiter` vs `six_lock_contended`（`six.c:739-790`，`six.h:268-279`）

```c
int six_lock_ip_waiter(struct six_lock *, enum six_lock_type,
		       struct six_lock_waiter *, six_lock_should_sleep_fn, unsigned long ip);
int six_lock_contended(struct six_lock *, enum six_lock_type,
		       struct six_lock_waiter *, six_lock_should_sleep_fn, unsigned long ip);
```

- 差异仅一行：前者先 `do_six_trylock(try=true)`（`six.c:749-750`），后者直进 `__six_lock_slowpath`（`six.c:779`）。lockdep 配对一致（非写 acquire→失败 release→成功 acquired，`six.c:746-757` vs `776-786`；写仅 acquired，因写前必须已持 intent，`six.c:834-840` EBUG）。
- 调用链：`btree_node_lock_nopath` 按 `contended` 分发（`locking.h:325-327`）；`btree_node_lock` 快路 try 失败→`slowpath(contended=false→nopath)`（`locking.h:366-367` + `locking.c:714` 传 false…`write_contended` 传 `!readers`，`locking.c:744-745`）。
- 权衡：快慢选择权交调用方，省一次已知竞争下的 CAS（`six.h:268-275` 注释）。

### 5.6 `__six_lock_wakeup` 定向唤醒（`six.c:338-432`）+ `six_lock_wakeup` 门卫（`six.c:435-446`）

```c
static void __six_lock_wakeup(struct six_lock *, enum six_lock_type lock_type);
__always_inline static void six_lock_wakeup(struct six_lock *, u32 state, enum six_lock_type);
```

- 门卫：write 释放但仍有读（`state & HELD_read`）直接回（`six.c:438-439`）；无对应 WAITING 位直接回（`six.c:441-442`）。`do_six_unlock_type` 传 `l[type].unlock_wakeup`（`six.c:816`）。
- 读释放（`six.c:348-378`）：唤醒**全部**同类 waiter（读读不冲突），逐个 `__do_six_trylock(read,false)`（`six.c:356`，`ret<=0` 即停 `goto out`）→ `get_task_struct` + `remove` + `smp_store_release(lock_acquired,true)` + `wake_up_process`（`six.c:365-377`，注释防"wakee 先退"需先 pin task）。
- intent/write（`six.c:379-421`）：扫全部槽选 `start_time` 最小者单唤（`six.c:389-400`）→ trylock（`six.c:403`）→ 同上唤醒；若还有同类排队（`n_matches>1`）跳过清 WAITING 位直接 `shrink`（`six.c:419-420`），下次解锁再进。
- 级联（`six.c:426-429`）：`ret<0` 说明 try 中发现对立等待者需补唤醒，切换 `lock_type` 重扫（`goto again`）。
- 权衡：读广播（无冲突全放行）+ 写单唤最老者（防饥饿近似 FIFO）；最老者按事务开始时间而非入队时间，跨锁全局可比，利于 abort 偏好一致性（见第六节）。

**可学之处**：等待表是"写少读多"结构（检测高频遍历）→ RCU + 固定槽；唤醒定向不广播（读除外）；`contended` 接口把快慢选择权交调用方。

---

## 六、死锁检测与中止偏好：阻塞时才付费

### 6.1 冲突判据 `lock_type_conflicts`（`locking.c:426-429`）

```c
static bool lock_type_conflicts(enum six_lock_type t1, enum six_lock_type t2)
	{ return t1 + t2 > 1; }
```

- 真值表：read+read=0 不冲突；read+intent=1 不冲突；其余（intent+intent=2，任何+write≥2）冲突。与 `l[].lock_fail`（`six.c:48-67`）同语义双实现（快路用位，检测用算术）。
- 调用点：`locking.c:564`（持有态 `lock_held` vs 等待态 `start_time&MASK`）。
- 权衡：一行函数，语义与三态编码耦合（改编码必改此式，`locking.h:179-180` BUILD_BUG_ON 钉住 read=0/intent=1 即为此）。

### 6.2 `bch2_check_for_deadlock` DFS 主循环（`locking.c:447-583`）

```c
int bch2_check_for_deadlock(struct btree_trans *trans, struct printbuf *cycle);
```

- 签名：`trans` 为睡眠者；`cycle` 非 NULL 表 debugfs 只检测不 abort（`locking.c:369-372`）。
- 前置（`locking.c:454-468`）：`guard(rcu)+guard(preempt)`（无睡内存 `GFP_NOWAIT`，下）；per-CPU `bch2_lock_graph`（`locking.c:112`）`nr=0`；`lock_must_abort` 已置则自 restart（`locking.c:460-466`）。
- 迭代 DFS（`locking.c:469-582`，显式栈免递归）：栈帧 `trans_waiting_for_lock`（`locking_types.h`，含 `trans/node_want/lock_want/path_idx/level/waitlist_idx/node_have/waitlist`）；`lock_graph_down` 压帧（`locking.c:231-253`，复用 `waitlist_snap` 缓冲，`locking.c:233-236` 注释）。
- 展开（`locking.c:475-479`）：`waitlist` 快照未消费完→`lock_graph_descend`（`locking.c:412`：栈中已见 `trans`→`break_cycle`，`locking.c:415-417`；栈满→`recursion_limit`，`locking.c:419-420`）。
- 持有边枚举（`locking.c:483-577`）：`rcu_dereference(paths)`（`locking.c:483`，trans->paths RCU 保护）；逐 path 逐 level 读 `btree_node_locked_type`（`locking.c:501`）；`node_have=READ_ONCE(path->l[level].b)->c`（`locking.c:508`，遇 `ERR/NULL` 说明对端在改 path→`remove_non_waiters` 重验，`locking.c:509-530`）。
- 等待边快照（`locking.c:550-570`）：`rcu_dereference(wait_fifo)` → `darray_for_each` 槽 → `smp_load_acquire(&i->w)`（`locking.c:559`，配 `six.c:290` release）→ `container_of_or_null(w, btree_trans, locking_wait)`（`locking.c:560`，非 btree 等待者自然滤掉）→ 自身排除 + 冲突过滤（`locking.c:562-564`）→ `darray_push_gfp(NOWAIT|NOWARN)`（`locking.c:565`，失败走 `waitlist_alloc_failed` 报专用 restart，`locking.c:431-445`，注释明示"静默截断会漏环，宁可 restart 可观测"，`locking.c:544-548`）。
- 权衡：只阻塞时运行，快路径零开销（`locking.c:96-98`）；per-CPU 图免分配；NOWAIT 分配失败转可计数 restart，不静默。

### 6.3 双校验 `lock_graph_remove_non_waiters`（`locking.c:273-290`）

```c
static bool lock_graph_remove_non_waiters(struct lock_graph *g,
					  struct trans_waiting_for_lock *from);
```

- 校验 1（`locking.c:278`）：`from->trans->locking != from->node_want`——对端已拿到锁走人，整条链假设失效，弹到 from。
- 校验 2（`locking.c:283-287`）：`i[0].node_have != i[1].node_want`——父帧看的节点 ≠ 子帧等的节点，边已过期，弹到 i+1。
- 调用点：疑似成环行动前（`break_cycle` 入口 `locking.c:366`）+ 读到 ERR/NULL path（`locking.c:516`）。
- 权衡：RCU 快照必有过期，行动前重验是"检测-行动"竞态的标准解；返回 true 表已弹栈、调用方重试（`break_cycle` 返回 0，`locking.c:366-367`）。

### 6.4 `break_cycle` + `btree_trans_abort_preference`（`locking.c:324-388`）

```c
static struct trans_waiting_for_lock *
btree_trans_abort_preference(struct trans_waiting_for_lock *l,
			     struct trans_waiting_for_lock *r);
static noinline int break_cycle(struct lock_graph *g, struct printbuf *cycle,
				struct trans_waiting_for_lock *from, int err);
```

- 偏好（`locking.c:328-334`）：`lock_may_not_fail` 不对称——不可败优先保（返回另一方 abort，`locking.c:330`）；否则**最年轻者 abort**（`time_after64(start)` 选大者，`locking.c:332-334`，事务开始时间早=老）。
- 行动（`locking.c:374-380`）：线性扫选 abort；全不可败→`break_cycle_fail` 打日志 BUG（`locking.c:337-357`，逐事务 backtrace）；自己（`i==g->g`）→ `bch2_trans_restart_foreign_task(would_deadlock)`（`locking.c:312-316`，trace 记 `print_cycle`，`locking.c:292`）；他人→`lock_must_abort=true + wake`（`locking.c:318-320`，对端下次进 detector 自 restart，`locking.c:460-466`）。
- 栈收缩（`locking.c:383-386`）：成功弹到 abort 帧（继续从此找环），远端 restart 失败（`ret`）则全清。
- 权衡：中止偏好写进代码（保不可败、杀年轻），不靠超时；debugfs 传 `cycle` 只打印（`print_cycle`，`locking.c:188`）不杀，供人工研判。

### 6.5 `bch2_six_check_for_deadlock` 睡前门卫（`locking.c:603-680`）

```c
int bch2_six_check_for_deadlock(struct six_lock *lock, struct six_lock_waiter *w);
```

- 签名：即 `should_sleep_fn`，`btree_node_lock_nopath` 注册（`locking.h:326-327`），在 `__six_lock_slowpath` 每次睡前调用（`six.c:659`）。
- 屏障（`locking.c:634` `smp_mb()`，注释 `locking.c:605-633`）：发布自身 waiter（store）→ 读他 waiter/hash（load）的 store→load 定序，双 litmus（双 waiter 互不见；重用检查 vs `wakeup_all` 互不见）都需全屏障（rmb 不够、release 单向不够，注释逐字论证）。
- 重用检查（`locking.c:657-660`）：`locking_node`（`locking.c:585-591`，cached 非 btree 返回 NULL 跳过）+ `node_reuse_race`（`locking.c:593-601`：`locking_hash_val` 快照 vs 现 `hash_val`，或 root id 比对）→ 命中返回 `no_btree_node_reused` restart，不睡幻影节点。快照由 `lock_with_path`（`locking.c:789`）/调用方 armed，0 表禁用（`locking.h:319-323` 注释：reclaim 不可能时才传 0）。
- wake_cpu 提示（`locking.c:674-676`，`CONFIG_SCHED_ALT` 外）：`shard_cpu` 写 `current->wake_cpu`，软亲和 L1/L2（注释 `locking.c:662-673`）。
- 尾调用 `bch2_check_for_deadlock(trans,NULL)`（`locking.c:679`）。
- 权衡：一道全屏障 + 一次 hash 比对，换"发布-发现"双不见与"睡幻影"两类极难复现 bug 的根除。

### 6.6 唤醒侧补唤醒协议（`six.c:152-157,426-429,614-617`）

- per-CPU 伪失败：try 暂时宣称持有又回退，可能让对端 try 误败 → 返回 `-1-type`，由 `do_six_trylock`（`six.c:454-457`）/慢路径（`six.c:614-617`）/唤醒级联（`six.c:426-429`）就地补唤醒。
- 权衡：无锁读算法的固有代价，用"失败方补唤醒"兜底，不丢事件、不伪唤醒死等。

**可学之处**：检测仅阻塞运行；中止偏好显式；快照+行动前重验；唤醒定向+补唤醒。

---

## 七、与 btree 的结合范式：原语与策略分离

### 7.1 父子逆序破环：读父→意子前先放父（`locking.c:41-62`）

```c
/* locking.c:59-62 大意：drop read locks on parents before taking intent on child;
   事后校验节点仍有效，否则重走 traversal */
```

- 死锁形（`locking.c:43-47` 表）：A 持父读等子 intent；B 持子 intent 等父写（split 收尾）。B 退不出（新节点未可见旧子未释放，`locking.c:55-57`），A 不放父读 B 永等写。
- 解法：取子 intent 前放父读锁（`locking.c:59-60`）→ 抢到 intent 后验节点有效（seq/`node_reuse_race`）→ 失效重遍历（`locking.c:60-62`）。
- 相关实现：`__bch2_btree_node_relock` 失败即上层 `btree_path_get_locks` 解整 path + 毒化 `ERR_PTR(no_btree_node_relock)`（`locking.c:873-884`），`traverse` 回上级重下。
- 权衡：放锁引入"节点被释放/重用"竞态，用 seq+hash 双保险换父子逆序死锁的根除。

### 7.2 取锁三层：`btree_node_lock` / `slowpath` / `nopath`（`locking.h:308-373`，`locking.c:686-725`）

```c
static inline int btree_node_lock(struct btree_trans *, struct btree_path *,
			 struct btree_bkey_cached_common *, unsigned, enum six_lock_type);
int bch2_btree_node_lock_slowpath(struct btree_trans *, struct btree_path *,
			struct btree_bkey_cached_common *, unsigned, enum six_lock_type);
static inline int btree_node_lock_nopath(struct btree_trans *,
			 struct btree_bkey_cached_common *, enum six_lock_type,
			 bool lock_may_not_fail, unsigned long ip, bool contended);
```

- `btree_node_lock`（`locking.h:357-373`）：`EBUG level` + `verify_not_unlocked` → `six_trylock_type` 快路（`locking.h:366`）→ 败转 slowpath（`locking.h:367`，`try()` 宏失败即返 restart）。
- `bch2_btree_node_lock_slowpath`（`locking.c:704-725`）：`btree_node_lock_increment`（`locking.c:686-702`：扫本 trans 所有 path，同节点同级已持 ≥want→`six_lock_increment` 短路，`locking.c:697`）→ 否则 `btree_node_lock_nopath(...,false,ip,true→contended?)`（`locking.c:714` 传 false…注意此处 contended=false，走 `six_lock_ip_waiter` 再 try 一次；真正的 contended=true 来自 `write_contended` 的 `!readers`，`locking.c:744`）。
- `btree_node_lock_nopath`（`locking.h:308-349`）：置 `lock_may_not_fail/locking`（`locking.h:315-317`，供 detector 回查）→ `contended? six_lock_contended : six_lock_ip_waiter`（`locking.h:325-327`，统一挂 `bch2_six_check_for_deadlock`）→ `BUG_ON(nofail&&ret)`（`locking.h:329`）→ `-ENOMEM` 转 `lock_waitlist_alloc` restart（`locking.h:331-332`）→ `WRITE_ONCE(locking,NULL)`（`locking.h:334`）→ DEBUG trace（`locking.h:338-347`）。
- 权衡：同事务跨 path 持锁复用（increment）避免自死；nopath 把"无 path 加锁"（reclaim/后台）也纳入 detector 可见（配 `lock_with_path` 临时 path，`locking.c:779-804`）。

### 7.3 写锁专用路：`__btree_node_lock_write` / `write_contended`（`locking.h:378-397`，`locking.c:727-753`）

```c
static inline int __btree_node_lock_write(struct btree_trans *, struct btree_path *,
				  struct btree_bkey_cached_common *, bool lock_may_not_fail);
int bch2_btree_node_lock_write_contended(struct btree_trans *, struct btree_path *,
				 struct btree_bkey_cached_common *, bool);
```

- 先标后拿（`locking.h:392`）：`mark WRITE_LOCKED` **先于** `six_trylock_write`，因 SIX 非公平、读在有写等时阻塞，detector 必须提前看见"我要写"（注释 `locking.h:387-391`）。
- 快路 `six_trylock_write`（`locking.h:394-396`）→ 败转 `write_contended`（`locking.c:727`）：清 `locking_hash/root`（`locking.c:731-732`，写期不做重用检查）→ 查本 trans 在此节点读数（`bch2_btree_node_lock_counts`，`locking.c:740`）→ `six_lock_readers_add(-readers)` 暂借（`locking.c:742`，注释 `locking.c:735-739`：读不归零 `six_unlock` 不唤醒，自持读会自死）→ `nopath(write, contended=!readers)`（`locking.c:744-745`，借了读则对方已退可再 try）→ 加回 readers（`locking.c:747`）→ 失败回标 INTENT（`locking.c:750`）。
- 解锁对称：`bch2_btree_node_unlock_write_inlined` 先回标 INTENT 再 `six_unlock_write`（`locking.h:267-268`），并预 `lock_seq++` 补偿（`locking.h:253`）。
- 权衡：写锁="intent 上下文中的短临界"，拿写前借读计数是整套"读改写同节点"不自死的钥匙。

### 7.4 relock/upgrade/downgrade 的 btree 封装（`locking.c:834-1141`）

| 函数（行号） | 签名/返回 | 要点 |
|---|---|---|
| `btree_path_get_locks`（`834`） | `(trans,path,upgrade,f,restart_err)→0/-1/-restart` | 逐 level `upgrade?bch2_btree_node_upgrade:relock`（`846-848`）；失败先 restart 再解锁（`865-873`，保 `should_be_locked` 断言）；毒化整链 `ERR_PTR` 防子节点误 relock（`880-884`） |
| `__bch2_btree_node_relock`（`889`） | `(trans,path,level,trace)→bool` | `race_fault` 注入（`896`）→ `six_relock_type(want,lock_seq)` 或 seq 匹配+increment（`899-901`）→ `mark_locked`（`902`）；失败记 `relock_fail` trace（`906-910`） |
| `bch2_btree_node_upgrade`（`916`） | 同上 →bool | `locks_want` 分发（`924-935`，WRITE 直接 BUG）；已持→tryupgrade，未持→relock intent（`943-945`）；次选 increment+解旧（`948-952`）；失败记 `upgrade_fail`（`954`） |
| `__bch2_btree_path_upgrade`（`1026`） | `(trans,path,new_want)→ret` | 同 btree 克隆 iter 联动升级（`1060-1072`，注释自称 ugly，`1041-1059`）；trace 含双 seq + 三计数（`1074-1098`） |
| `__bch2_btree_path_downgrade`（`1104`） | `(trans,path,new_want)→void` | restart 后直接回（`1113`）；高层先解（`1120-1124`），本层 intent→`six_lock_downgrade`+回标 READ（`1125-1128`）后即停 |
| `bch2_trans_relock` 系（`1207-1244`） | `__bch2_trans_relock(trans,trace)→ret` | 跳过 `!should_be_locked`（`1221`）；失败 `__bch2_trans_unlock` 全解 + verify（`1228-1229`）；成功置 locked + 重 arm SRCU 警告（`1234-1236`） |

- 权衡：relock/upgrade 失败一律转事务 restart（幂等假设，`locking.c:85-94`），不原地睡等——这是"检测-abort-重做"闭环的最后一环。

### 7.5 lockdep 集成（`six.c:21-22,746-757,776-786,843` + `locking.c:148`）

- 非写：`six_acquire(try?1:0, read?1:0)` 先占位（`six.c:747/777`）→ 失败 `six_release`（`six.c:753/782`）→ 成功 `lock_acquired`（`six.c:755/784`）；trylock 成功 `acquire(1,...)`（`six.c:476`）。
- 写：只 `lock_acquired`（`six.c:755` 注释外行为：`if(!ret)` 对写也执行，但进入前无 acquire——因写前必已持 intent，`six_unlock_ip` EBUG 反查 `HELD_intent`，`six.c:836-837`）。
- btree：`lockdep_set_notrack_class`（`locking.c:148`），排序交自有 detector。
- 权衡：DEBUG 可定位 + 运行时零负担（非 DEBUG 编译为空）。

**可学之处**：锁原语只暴露"等待表可遍历 + 睡前回调"（`six.h:104-124`），环检测、偏好、中止全在上层——原语与策略分离才可复用。

---

## 八、性能权衡清单（含函数级代价）

| 手段（位置） | 代价 | 收益 | 备注 |
|---|---|---|---|
| per-CPU 读计数（`six.c:170-185` 读快路 / `186-205` 写慢路） | 写要 `pcpu_read_count` 全 CPU 求和（`six.c:103-111`）+ 伪失败补唤醒 | 读快路零 CAS（本 CPU inc + mb） | 可分配失败回退，语义不变（`six.c:1119-1128`） |
| 内联 8 等待槽（`six.h:186`，`six.c:1104-1108`） | 结构变大 | 竞争者少时零分配 | 超限翻倍，上限 32K（`six.c:312`） |
| seq 单调增（`six.c:857-858`） | 每次写解锁一次加法 | 乐观 relock（`six.c:492`）+ 免重遍历 | 仅写解锁增；持有者侧预补偿（`locking.h:253`） |
| `contended` 跳检（`six.c:769-790`） | 调用方多一次判断（`locking.h:325`） | 省一次已知竞争 CAS | 选择权交调用方（`six.h:268-275`） |
| RCU 等待表（`six.c:295-328`） | 扩容全拷 + `kfree_rcu` | 检测无锁遍历（`locking.c:550`） | 固定槽位永不搬家（`six.h:167-178`） |
| 乐观自旋（`six.c:521-571`，`BCACHEFS_SIX_OPTIMISTIC_SPIN` 外默认关） | 10us 自旋 + NOSPIN 熔断（`six.c:545-558`） | 睡眠前偷赢 | 仅" sole waiter + 非写 + owner 运行"（`six.c:528-541`） |
| 定向唤醒（`six.c:338-432`） | 每次扫描 O(nr) + 打包比较 | 读全放行、写最老单唤防饥饿 | 级联补唤醒防丢事件（`six.c:426-429`） |
| 死锁检测（`locking.c:447-583`） | 阻塞时 DFS + NOWAIT 快照 | 根除死锁、有界延迟 | 快路径零开销；失败转可计数 restart |
| SRCU 预算截断（`iter.h:354-365`） | 虚假超时一轮 | 内存回收不被长等 stall | 与 SIX seq 正交 |
| lockdep（`six.c:746-757`） | DEBUG 开销 | 死锁可定位 | btree 用 notrack 交自有检测 |

---

## 九、设计启示（可学之处汇总）

1. 先量化"排斥权持有时长 vs 真修改时长"错配（`locking.c:19-21`），再决定加不加状态。
2. 锁结构为无竞争快路设计：per-CPU（`six.h:191`）、内联 8 槽（`six.h:186`）、零分配；`contended` 把快慢选择权给调用方（`six.h:268-279`）。
3. seq 把持有变版本（写解锁递增 `six.c:857-858`，双检 relock `six.c:495-501`），是乐观并发最小构件；SRCU 预算（`iter.h:354`）是正交的域锁截断。
4. 升级可失败（`six.c:886`）、降级原子一步（`six.c:870`，先加读后解 intent）；write 重入只是计数（`six.c:970-976`）。
5. 等待队列写少读多 → RCU + 固定槽（`six.h:167-178`）+ 位打包（`six.h:159-165`）；唤醒定向（读全唤 `six.c:348` / 写最老单唤 `six.c:379`）+ 伪失败补唤醒（`six.c:454`）。
6. 检测仅阻塞运行（`locking.c:96-98`）；中止偏好写进代码（保不可败、杀最年轻，`locking.c:328-334`）；快照+行动前双校验（`locking.c:273-290`）；睡前全屏障+重用检查（`locking.c:634-660`）。
7. 原语与策略分离：SIX 只给"等待表可遍历 + 睡前回调"（`six.h:104-124`），环检测全在 btree 层；写锁"先标后拿"（`locking.h:392`）+"暂借读计数"（`locking.c:740-747`）是结合范式的点睛之笔。
8. 头文件 DOC 讲透设计（`six.h:6-124` 共 119 行，`locking.c:3-99` 共 97 行）本身就是可学性。

---

## 复核途径（行号禁编造，本节命令均只读）

- `sed -n 6,124p fs/util/six.h` 通读 SIX DOC；`sed -n 3,99p fs/btree/locking.c` 通读 btree DOC。
- `grep -n "six_lock_downgrade\|six_lock_tryupgrade\|six_trylock_convert\|six_lock_increment\|six_lock_readers_add\|six_relock_ip\|__do_six_trylock\|__six_lock_wakeup\|six_lock_contended\|six_lock_ip_waiter" fs/util/six.c fs/util/six.h` 定位原语。
- `grep -n "bch2_check_for_deadlock\|bch2_six_check_for_deadlock\|lock_type_conflicts\|break_cycle\|btree_trans_abort_preference\|lock_graph_remove_non_waiters\|btree_node_lock_nopath\|btree_node_lock\b\|__btree_node_lock_write\|bch2_btree_node_upgrade\|__bch2_btree_node_relock\|bch2_trans_short_wait_budget" fs/btree/locking.c fs/btree/locking.h fs/btree/iter.h` 定位结合层。
- 抽查实现：`sed -n 122,214p fs/util/six.c`（trylock 三分支）、`sed -n 585,698p fs/util/six.c`（慢路径）、`sed -n 447,583p fs/btree/locking.c`（DFS 检测）。
