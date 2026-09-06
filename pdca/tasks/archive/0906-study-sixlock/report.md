# bcachefs SIX 锁专题学习报告（T0512）

> 精读对象：`fs/util/six.h`（465 行，DOC 完备）、`fs/util/six.c`、
> `fs/btree/locking.c`。事实源为源码注释与实现。

---

## 一、为什么需要第三态：读写锁的死结

传统读写锁有个死结：**读不能升级为写**。树形多节点原子更新
（如 btree split 需改父改子）要么整路持写锁（并发塌陷），要么
读升写（与另一个同样操作的线程互等，必死锁）。

SIX 的洞察（`six.h:9-20`）：split 需要长期持有父节点的**排斥权**，
但真正改内存只有指针切换一瞬。排斥权与修改时长不匹配—— Cortes
第三态 `intent` 解耦二者：与读兼容、与 intent/写互斥。先拿 intent
占位锁定范围，读全程并发；逐节点短持写锁真改。

**可学之处**：识别"排斥权持有时长 vs 真修改时长"的错配，是设计
第三态的通用出发点。不要为加状态而加状态，先量化错配。

## 二、三态语义与数据结构

```c
enum six_lock_type { SIX_LOCK_read, SIX_LOCK_intent, SIX_LOCK_write; };
struct six_lock {
    atomic_t state; u32 seq;
    unsigned __percpu *readers;   /* 读计数 per-CPU，免缓存颠簸 */
    ...
    struct six_lock_wait_fifo __rcu *wait_fifo;  /* RCU 等待队列 */
    struct six_lock_wait_fifo inline_fifo;       /* 内联 8 槽，免分配 */
};
```

- 读计数 per-CPU：读多场景下原子变量不颠簸（`six.h:191`）。
- 等待队列内联 8 槽：绝大多数锁竞争者少，免堆分配
  （`SIX_LOCK_INLINE_WAITERS`）。
- `intent_lock_recurse/write_lock_recurse` + `owner`：上层可实现
  可重入（`six_lock_increment`），写仍只许一次。

**可学之处**：锁结构本身就要为"无竞争快"设计：per-CPU 计数、
内联等待槽都是零分配快路。recurse 计数把可重入交给上层，
原语保持最小。

## 三、seq 乐观重锁：掉锁做 IO 的答案

锁内嵌 seq，取/放写时递增（`six.h:48-64`）：

```c
six_lock_read(&foo->lock);
u32 seq = six_lock_seq(&foo->lock);
six_unlock_read(&foo->lock);
some_operation_that_may_block();   /* IO / 分配内存 */
if (six_relock_read(&foo->lock, seq)) { /* 如从未掉锁 */ }
```

长事务持锁做 IO 阻塞并发；直接放锁重拿无法确认数据未变。
seq 让"放锁-阻塞-重拿"变成可验证操作。btree 层叠加 SRCU 预算
切分长等（`bch2_trans_short_wait_budget`），超限先放读侧锁。

**可学之处**：任何"持锁做阻塞事"的代码都该问一句：能不能快照
seq 后放锁？seq 把"持有"从布尔变成版本，是乐观并发的最小构件。

## 四、升降级与转换：精细流转

- `six_lock_downgrade()`：intent→read，加读计数加解 intent，
  原子一步。
- `six_lock_tryupgrade()`：read→intent，CAS 确认无 intent 后转换，
  可失败（调用方回退重走）。
- `six_trylock_convert()`：read↔intent 分发，同型直接成功。

**可学之处**：升级必须可失败（tryupgrade），调用方必须有回退路；
降级必须原子一步，禁止"解锁再加锁"两步（中间态可被插足）。

## 五、等待队列：RCU 加槽位打包

```c
struct six_lock_wait_slot { six_lock_waiter *w; u64 start_time; };
/* 低 2 位塞 lock_want，高位为时间；同类比较免掩码 */
```

- 槽位固定不搬家：RCU 读者（死锁检测）永不见条目移动；删除写
  NULL，插入找空槽，高水位收缩（`six.h:167-184`）。
- 时间戳严格递增，可作遍历游标。
- 扩容全量拷贝加 `rcu_assign_pointer`，旧堆 `kvfree_rcu`
  （`six.c`）。
- `six_lock_contended()` 跳过首次 trylock 直进慢路径：调用方已知
  竞争时省一次 CAS（`six.h:268-279`）。

**可学之处**：等待队列是"写少读多"结构（死锁检测高频遍历），用
RCU 加固定槽位；位打包让唤醒扫描免解引用。`contended` 接口说明：
快慢路径选择权应交给调用方，而非锁内部猜。

## 六、死锁检测与中止偏好

睡眠前走事务等待图 DFS（`bch2_check_for_deadlock`）：
- 冲突判据 `t1+t2>1`（读读不冲突，其余皆冲突）。
- 遍历用 RCU 快照加无睡内存，防并发唤醒抖动。
- 双校验去非等待者。
- `break_cycle`：不可败事务优先保，否则最年轻者 abort。
- 睡眠前比对 hash 快照防复用幻影节点，配内存屏障
  （`locking.c:636-660`）。
- trylock 失败有对立等待者时返回要求调用方补唤醒，防伪唤醒丢
  事件（`__do_six_trylock`）。
- 唤醒定向：读唤醒全部同类，写按等待时间最早者单唤
  （`__six_lock_wakeup`）。

**可学之处**：死锁检测仅阻塞时运行，不污染快路径；中止偏好必须
显式（保谁杀谁写进代码）；唤醒必须定向，广播是懒惰。

## 七、与 btree 的结合范式

- 取子 Intent 前先放父读锁加事后校验，破父子逆序
  （`locking.c:59-62`）。
- btree 层 `should_sleep_fn` 回调跑环检测：锁只提供"睡前回调 +
  等待表可遍历"，环检测逻辑在上层（关注点分离，`six.h:104-124`）。
- lockdep 全程集成：非写走 acquire/release，写仅 acquired
  （`six.c:__six_lock_init`）。

**可学之处**：锁原语只暴露"等待表可遍历加睡前回调"，死锁策略
由上层定。原语与策略分离，SIX 才能被复用。

## 八、性能权衡清单

| 手段 | 代价 | 收益 |
|------|------|------|
| per-CPU 读计数 | 内存 | 读无竞争 |
| 内联 8 等待槽 | 结构变大 | 免分配 |
| seq 递增 | 每次写锁一次加法 | 乐观重锁 |
| contended 跳检 | 调用方多一次判断 | 省 CAS |
| RCU 等待表 | 扩容拷贝 | 检测无锁遍历 |
| lockdep | DEBUG 开销 | 死锁可定位 |

## 九、设计启示（可学之处汇总）

1. 先量化"排斥权持有时长 vs 真修改时长"错配，再决定加不加状态。
2. 锁结构为无竞争快路设计：per-CPU、内联、零分配。
3. seq 把持有变版本，是乐观并发最小构件。
4. 升级可失败、降级原子一步；快慢路径选择权给调用方。
5. 等待队列写少读多，用 RCU 加固定槽；唤醒定向不广播。
6. 死锁检测仅阻塞运行；中止偏好写进代码；原语与策略分离。
7. 头文件 DOC 把设计讲透（465 行头文件 124 行文档），是最好的
   可学性本身。

---

## 复核途径

- `sed -n 9,124p fs/util/six.h` 通读 DOC。
- `grep -n "six_lock_downgrade\|six_lock_tryupgrade\|break_cycle\|bch2_check_for_deadlock" fs/util/six.c fs/btree/locking.c` 定位关键函数。
