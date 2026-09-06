# btree GC 全流程专题学习报告（T0527 代码级精讲版）

> 事实源：`fs/btree/check.c`（1476 行，`wc -l` 核实）、`fs/btree/check.h`（91 行）、
> `fs/btree/check_types.h`、`fs/btree/commit.c`、`fs/btree/interior.c`、`fs/btree/types.h`。
> 所有函数名与行号均经 `grep -n` / `Read` 核实，代码片段均为原文摘录（每段 ≤10 行）。
> 八节结构沿用原报告（T0493 B 深挖 10 条：GC 即 check.c，无独立 gc.c）。

---

## 一、全景：GC 即 check

btree 无独立 GC 文件，GC 就是 `fs/btree/check.c`：全树扫描加标记清扫，兼做一致性校验。
两大入口：`bch2_check_topology`（拓扑修复）与 `bch2_check_allocations`（标记清扫主流程）。
核心矛盾：扫描与并发提交互相覆盖（`commit.c`、`check.c`、`interior.c` 协同）。
**可学**：GC 与校验合一，一次遍历双重产出。

### 1.1 `bch2_check_topology`（check.c:636）——拓扑修复总入口

- **签名**：`int bch2_check_topology(struct bch_fs *c)`
- **参数**：`c` 文件系统对象。
- **返回**：0 成功；否则标准 errcode（含 `BCH_ERR_topology_repair_*` 系列内部重启信号）。
- **调用链**：recovery/mount 路径调用 → 逐 btree 调 `bch2_topology_check_root`（:567）→ 加读锁调
  `btree_check_root_boundaries`（:296）+ `bch2_btree_repair_topology_recurse`（:358）。
- **代码片段**（:642~:645，逐 btree 循环；:683~:685，加锁进递归）：
```c
for (unsigned i = 0; i < btree_id_nr_alive(c); i++) {
    bool reconstructed_root = false;
recover:
    try(lockrestart_do(trans, bch2_topology_check_root(trans, i, &reconstructed_root)));
```
```c
btree_node_lock_nopath(trans, &b->c, SIX_LOCK_read, true, _THIS_IP_, false);
int ret = btree_check_root_boundaries(trans, b) ?:
          bch2_btree_repair_topology_recurse(trans, b);
```
- **权衡**：用 `nofail` 读锁走自有 iter 基础设施而非 path（:650~:679 大段注释自述“需要重写”）；
  好处是复用旧拓扑遍历代码，代价是 cycle detector 不可见——仅因“mount/recovery 时无工作线程竞争”
  才安全，在线拓扑修复必须先重写到 path 上。

### 1.2 `bch2_check_allocations`（check.c:1139）——标记清扫总入口

- **签名**：`int bch2_check_allocations(struct bch_fs *c)`
- **参数/返回**：同上。
- **调用链**：`bch2_gc_accounting_start` → `bch2_gc_start`（:889）→ `bch2_gc_alloc_start`（:1042）→
  `bch2_gc_reflink_start` → `bch2_mark_superblocks`（:871）→ `bch2_gc_btrees`（:830）→
  `bch2_gc_alloc_done`（:1027）/`accounting_done`/`stripes_done`（:1107）/`reflink_done`。
- **代码片段**（:1143~:1146 持锁+排空；:1166~:1169 分段收尾）：
```c
guard(rwsem_read)(&c->state_lock);
guard(rwsem_write)(&c->gc.lock);
bch2_btree_interior_updates_flush(c);
```
```c
ret   = bch2_gc_alloc_done(c) ?:
        bch2_gc_accounting_done(c) ?:
        bch2_gc_stripes_done(c) ?:
        bch2_gc_reflink_done(c);
```
- **权衡**：外层 `state_lock(读)+gc.lock(写)` 全程持有，简单正确但阻塞其它 GC；
  以“全程持锁换遍历期间拓扑稳定”，并发只靠第四节的补标机制放行提交，不靠细粒度锁。

### 1.3 `bch2_gc_btrees`（check.c:830）——全 btree 调度器

- **签名**：`static int bch2_gc_btrees(struct bch_fs *c)`
- **参数/返回**：`c`；0/errcode。
- **调用链**：被 `bch2_check_allocations` 调用；内按 `btree_id_gc_phase_cmp` 排序后逐 btree 调
  `bch2_gc_btree`（:806）。
- **代码片段**（:839~:842 排序；:851 按触发器定靶深度）：
```c
enum btree_id ids[BTREE_ID_NR];
for (unsigned i = 0; i < BTREE_ID_NR; i++)
    ids[i] = i;
bubble_sort(ids, BTREE_ID_NR, btree_id_gc_phase_cmp);
```
```c
unsigned target_depth = BIT_ULL(btree) & btree_leaf_has_triggers_mask ? 0 : 1;
```
- **权衡**：`bubble_sort` 用于 `BTREE_ID_NR`（十余个）规模，O(n²) 无妨，换代码最简；
  规模若膨胀需换排序，但 btree 种类数基本恒定。

---

## 二、全序位点：引用前向搬移

phase>btree>level>pos 字典序，alloc/stripes 最先；排序定遍历序，保证引用只能前向搬移不漏标。
**可学**：全序位点是增量正确性的根基（`bch2_check_allocations` 注释 :1124~:1137 明示“引用只许前向搬移”）。

### 2.1 `gc_phase`（check.h:34）——阶段起点位点

- **签名**：`static inline struct gc_pos gc_phase(enum gc_phase phase)`
- **参数**：`phase`（`check_types.h`：`not_running/start/sb/btree`）。
- **返回**：`struct gc_pos`（phase 置位，其余零值即最小 btree/level/pos）。
- **调用链**：`bch2_mark_superblocks`（:873 `gc_phase(GC_PHASE_sb)`）、主流程 `:1155/:1173` 起止水位。
- **代码片段**（check.h:34~:37）：
```c
static inline struct gc_pos gc_phase(enum gc_phase phase)
{
    return (struct gc_pos) { .phase = phase, };
}
```
- **权衡**：零值填充天然成为该阶段最小位点，无需额外构造；依赖 C99 指定初始化器语义，清晰但隐含“零即最小”的约定。

### 2.2 `gc_pos_btree`（check.h:39）——树内位点构造函数

- **签名**：`static inline struct gc_pos gc_pos_btree(enum btree_id btree, unsigned level, struct bpos pos)`
- **参数**：btree 号、层级、键位置；**返回**：phase=`GC_PHASE_btree` 的完整位点。
- **调用链**：`bch2_gc_btree`（:816 逐键推进）、`bch2_gc_btree_root`（:801 封口）、
  `bch2_trans_commit_run_gc_triggers`（commit.c:678 判已访问）。
- **代码片段**（check.h:39~:48）：
```c
static inline struct gc_pos gc_pos_btree(enum btree_id btree, unsigned level,
                                         struct bpos pos)
{
    return (struct gc_pos) {
        .phase  = GC_PHASE_btree,
```
- **权衡**：纯值类型内联构造，调用点零开销；把“水位推进”收敛到单一构造方式，避免手写结构体散落。

### 2.3 `gc_btree_order`（check.h:50）——alloc/stripes 优先

- **签名**：`static inline int gc_btree_order(enum btree_id btree)`
- **参数/返回**：btree 号 → 排序键（alloc=-2，stripes=-1，其余按 id）。
- **调用链**：被 `gc_pos_cmp`（:62）与 `btree_id_gc_phase_cmp`（:825）调用。
- **代码片段**（check.h:50~:57）：
```c
static inline int gc_btree_order(enum btree_id btree)
{
    if (btree == BTREE_ID_alloc)
        return -2;
    if (btree == BTREE_ID_stripes)
        return -1;
    return btree;
}
```
- **权衡**：alloc/stripes 是“被引用记账”的宿主，必须先于引用者遍历；硬编码两特例换调度正确，
  新增记账型 btree 时必须同步修改此处（隐式耦合点）。

### 2.4 `gc_pos_cmp`（check.h:59）——四元组字典序

- **签名**：`static inline int gc_pos_cmp(struct gc_pos l, struct gc_pos r)`
- **参数/返回**：两 `gc_pos`；`<0/=0/>0`。
- **调用链**：`gc_pos_set` 的 `BUG_ON(<0)`（:86）、`gc_visited` 的 `<=0` 判定（:75）。
- **代码片段**（check.h:59~:66）：
```c
static inline int gc_pos_cmp(struct gc_pos l, struct gc_pos r)
{
    return  cmp_int(l.phase, r.phase) ?:
            cmp_int(gc_btree_order(l.btree),
                    gc_btree_order(r.btree)) ?:
            cmp_int(l.level, r.level) ?:
            bpos_cmp(l.pos, r.pos);
}
```
- **权衡**：`?:` 链式比较短路求值，一次函数解决全序；level 正序意味着**自底向上**（level 0 叶最先），
  与第五节靶深度逻辑联动。

### 2.5 `btree_id_gc_phase_cmp`（check.c:825）——排序比较器

- **签名**：`static inline int btree_id_gc_phase_cmp(enum btree_id l, enum btree_id r)`
- **参数/返回**：两 btree id；比较 `gc_btree_order` 结果。
- **调用链**：仅 `bch2_gc_btrees` 的 `bubble_sort` 比较器。
- **代码片段**（:825~:828）：
```c
static inline int btree_id_gc_phase_cmp(enum btree_id l, enum btree_id r)
{
    return cmp_int(gc_btree_order(l), gc_btree_order(r));
}
```
- **权衡**：把“遍历序=比较器”显式化，排序与水位比较同源（都调 `gc_btree_order`），避免两处各写一套顺序。

---

## 三、单调水位发布

位点禁倒退；写序号锁发布，读无锁判已访问。
**可学**：水位单调加无锁读，发布订阅解耦（check.h:12~:31 大注释阐明并发标记清扫的锁约）。

### 3.1 `__gc_pos_set`（check.c:76）——序号锁发布原语

- **签名**：`static inline void __gc_pos_set(struct bch_fs *c, struct gc_pos new_pos)`
- **参数**：`c`，`new_pos`；**返回**：void（无单调检查，内部用）。
- **调用链**：被 `gc_pos_set`（:87）与收尾 `:1173`（`not_running` 允许“倒退”故绕过检查）调用。
- **代码片段**（:76~:82）：
```c
static inline void __gc_pos_set(struct bch_fs *c, struct gc_pos new_pos)
{
    guard(preempt)();
    write_seqcount_begin(&c->gc.pos_lock);
    c->gc.pos = new_pos;
    write_seqcount_end(&c->gc.pos_lock);
}
```
- **权衡**：`seqcount+禁抢占` 写端极轻（持有者仅 GC 线程，无竞争）；读端 `gc_visited` 可无锁重试，
  比 rwlock/mutex 少一次原子写，代价是读者可能重试（写极少，重试可忽略）。

### 3.2 `gc_pos_set`（check.c:84）——单调性断言封装

- **签名**：`static inline void gc_pos_set(struct bch_fs *c, struct gc_pos new_pos)`
- **参数/返回**：同上，void。
- **调用链**：`:801`（root 封口）、`:816`（逐键）、`:873`（sb 阶段）、`:1155`（start）。
- **代码片段**（:84~:88）：
```c
static inline void gc_pos_set(struct bch_fs *c, struct gc_pos new_pos)
{
    BUG_ON(gc_pos_cmp(new_pos, c->gc.pos) < 0);
    __gc_pos_set(c, new_pos);
}
```
- **权衡**：`BUG_ON` 把“倒退”从逻辑错误升级为崩溃级不变量，调试期立刻暴露；
  生产环境若水位构造有 bug 会直接宕机而非静默漏标——选 fail-fast 而非容错。

### 3.3 `gc_visited`（check.h:68）——无锁已访问判定

- **签名**：`static inline bool gc_visited(struct bch_fs *c, struct gc_pos pos)`
- **参数**：`c`，待判位点；**返回**：true=GC 已访问过该位点。
- **调用链**：提交路径 `bch2_trans_commit_run_gc_triggers`（commit.c:678）每次提交逐 update 调用；
  高频读端。
- **代码片段**（check.h:68~:79）：
```c
static inline bool gc_visited(struct bch_fs *c, struct gc_pos pos)
{
    unsigned seq;
    bool ret;
    do {
        seq = read_seqcount_begin(&c->gc.pos_lock);
        ret = gc_pos_cmp(pos, c->gc.pos) <= 0;
    } while (read_seqcount_retry(&c->gc.pos_lock, seq));
    return ret;
}
```
- **权衡**：提交热路径上只做一次 `gc_pos_cmp`（纯整数比较），无锁无 CAS；
  `<=0` 的“等于亦算已访问”语义是关键：与 GC 持节点写锁的约定配合，避免 GC 与更新者“擦肩而过”时双漏
  （check.h:20~:30 注释：同位点靠 btree 节点写锁互斥）。

### 3.4 `bch2_gc_pos_to_text`（check.c:59）——位点可观测性

- **签名**：`__cold void bch2_gc_pos_to_text(struct printbuf *out, struct gc_pos *p)`
- **参数**：输出 buffer + 位点；**返回**：void。
- **调用链**：sysfs/debugfs 状态展示与报错打印。
- **代码片段**（:59~:66）：
```c
__cold void bch2_gc_pos_to_text(struct printbuf *out, struct gc_pos *p)
{
    prt_str(out, bch2_gc_phase_strs[p->phase]);
    prt_char(out, ' ');
    bch2_btree_id_level_to_text(out, p->btree, p->level);
```
- **权衡**：`__cold` 显式告诉编译器此为冷路径，保热路径 icache；`bch2_gc_phase_strs` 由
  `GC_PHASES()` 宏（:52~:57）统一生成，增删阶段不漏字符串表。

---

## 四、提交补标：边走边对账

并发提交对已访问更新补跑触发器，不丢计数。
**可学**：扫描与提交用补标对账，而非互斥停机。

### 4.1 `bch2_trans_commit_run_gc_triggers`（commit.c:673）——补标执行器

- **签名**：`static noinline int bch2_trans_commit_run_gc_triggers(struct btree_trans *trans)`
- **参数**：`trans` 当前提交事务；**返回**：0/errcode。
- **调用链**：`bch2_trans_commit` 提交路径（commit.c:1192~:1195）→ 逐 update 判 `gc_visited` →
  `run_one_mem_trigger(..., flags|BTREE_TRIGGER_gc)`。
- **代码片段**（commit.c:673~:682）：
```c
static noinline int bch2_trans_commit_run_gc_triggers(struct btree_trans *trans)
{
    trans_for_each_update(trans, i)
        if (btree_node_type_has_triggers(i->bkey_type) &&
            !(i->flags & BTREE_TRIGGER_norun) &&
            gc_visited(trans->c, gc_pos_btree(i->btree_id, i->level, i->k->k.p)))
            try(run_one_mem_trigger(trans, i, i->flags|BTREE_TRIGGER_gc));
    return 0;
}
```
- **权衡**：三条件短路——有触发器类型才查、显式 `norun` 可跳过、已访问才补跑；
  `noinline` 防热路径膨胀。语义是“GC 已扫过的地方，提交者自己把账补上”，GC 端无需回头。

### 4.2 提交路径门控（commit.c:1192）——GC 未跑时零开销

- **签名**：提交函数内联片段（非独立函数）。
- **参数/返回**：沿用提交返回值。
- **调用链**：`bch2_trans_commit` → 先跑 atomic 触发器 → 若 `c->gc.pos.phase != 0` 才进补标。
- **代码片段**（commit.c:1192~:1196）：
```c
if (unlikely(c->gc.pos.phase)) {
    ret = bch2_trans_commit_run_gc_triggers(trans);
    if (unlikely(ret))
        return trans_commit_fatal_err(trans, ret);
}
```
- **权衡**：`unlikely(c->gc.pos.phase)` 使无 GC 时补标逻辑对提交吞吐零影响（一个分支预测）；
  GC 运行期间提交多一次遍历 updates 的开销，换 GC 不停机。注意直接读 `c->gc.pos.phase`
  而非 `gc_visited`，是“GC 是否在跑”的粗门控，细判留给内层逐 key。

### 4.3 `BTREE_TRIGGER_gc` 语义（types.h:383）——重算而非记账

- **签名**：触发器标志位（`btree_trigger_flags` 枚举成员）。
- **参数/返回**：`types.h:383` 注释：“we're in gc/fsck: running triggers to recalculate e.g. disk usage”。
- **调用链**：GC 的 `bch2_gc_mark_key`（:784 `BTREE_TRIGGER_gc|BTREE_TRIGGER_insert`）与补标路径共用。
- **权衡**：同一套 trigger 代码双模式复用：正常提交做增量记账，GC/补标做重算；
  省一套重算代码，但 trigger 实现必须保证两种 flag 组合下都正确（测试矩阵翻倍）。

---

## 五、自底向上与靶深度

按靶深度逐键设位加进度加标记，尾部超位封口；有触发器从叶起，fsck 强制从叶。
**可学**：遍历方向与封口显式；靶深度自适应。

### 5.1 `bch2_gc_btree`（check.c:806）——单树逐层扫描

- **签名**：`static int bch2_gc_btree(struct btree_trans *trans, struct progress_indicator *progress, enum btree_id btree, unsigned target_depth, bool initial)`
- **参数**：`trans` 复用的长事务、`progress` 进度指示、`btree` 目标树、`target_depth` 起始层、
  `initial` 是否首轮（含版本校验与修键）。
- **返回**：0/errcode（`try` 宏 early-return）。
- **调用链**：`bch2_gc_btrees`（:864）→ 本函数 → 内层 `for_each_btree_key_continue` 逐键 →
  `bch2_gc_mark_key`（:818）；层尾调 `bch2_gc_btree_root`（:822）。
- **代码片段**（:811~:819）：
```c
for (unsigned level = target_depth; level < BTREE_MAX_DEPTH; level++) {
    struct btree *prev = NULL;
    CLASS(btree_node_iter, iter)(trans, btree, POS_MIN, 0, level, BTREE_ITER_prefetch);
    try(for_each_btree_key_continue(trans, iter, 0, k, ({
        gc_pos_set(trans->c, gc_pos_btree(btree, level, k.k->p));
```
- **权衡**：`target_depth→MAX` 自底向上，保证叶引用先于内点被标（内点只含 btree_ptr，不直接占 bucket）；
  每键一次 `gc_pos_set` 是水位粒度与开销的折中：键级水位让补标精确到键，代价是每次 seqcount 写
  （GC 本身是后台慢路径，可接受）。

### 5.2 `bch2_gc_btree_root`（check.c:791）——尾部超位封口

- **签名**：`static int bch2_gc_btree_root(struct btree_trans *trans, enum btree_id btree, bool initial)`
- **参数/返回**：`trans`、树号、首轮标志；0/errcode（含 `transaction_restart_lock_root_race` 重启）。
- **调用链**：每层扫描结束由 `bch2_gc_btree`（:822 `lockrestart_do` 包裹）调用。
- **代码片段**（:794~:803）：
```c
CLASS(btree_node_iter, iter)(trans, btree, POS_MIN, 0,
                             bch2_btree_id_root(c, btree)->b->c.level, 0);
struct btree *b = errptr_try(bch2_btree_iter_peek_node(&iter));
if (b != btree_node_root(c, b))
    return btree_trans_restart(trans, BCH_ERR_transaction_restart_lock_root_race);
gc_pos_set(c, gc_pos_btree(btree, b->c.level + 1, SPOS_MAX));
```
- **权衡**：封口位点是 `level+1/SPOS_MAX`——**超位**（比该树任何真实位点都大），语义“整树已扫完”；
  先验 root 身份防并发 split/merge 导致读到非 root，宁可 transaction_restart 重来也不错标。

### 5.3 靶深度决策（check.c:851~:862）——触发器/ fsck 自适应

- **签名**：`bch2_gc_btrees` 内联片段。
- **参数/返回**：沿用外层。
- **调用链**：排序后逐 btree 计算 `target_depth` 再进 `bch2_gc_btree`。
- **代码片段**（:851~:864）：
```c
unsigned target_depth = BIT_ULL(btree) & btree_leaf_has_triggers_mask ? 0 : 1;
...
if (test_bit(BCH_FS_in_fsck, &c->flags))
    target_depth = 0;
ret = bch2_gc_btree(trans, &progress, btree, target_depth, true);
```
- **权衡**：叶无触发器的树从 level=1 起跳过叶扫（叶引用不贡献记账，省一遍全叶遍历）；
  fsck 强制 `target_depth=0` 逐叶可读性检查（注释 :853~:860：RW 前必须确认每叶可读，否则
  `btree_lost_data` 无法 rewind 修复）。正常 GC 省 IO，fsck 保可修复性。

---

## 六、mark 流水线与拓扑 journal

换节点才验拓扑；修版本位图键；有更新预留提交重启；跑触发器重算。拓扑重写走 journal，
先记日志再变异防重放。
**可学**：mark 分阶段；拓扑修复先记后改。

### 6.1 `bch2_gc_mark_key`（check.c:726）——五阶段 mark 流水线

- **签名**：`static int bch2_gc_mark_key(struct btree_trans *trans, enum btree_id btree_id, unsigned level, struct btree **prev, struct btree_iter *iter, struct bkey_s_c k, bool initial)`
- **参数**：`trans`、`btree_id/level`、`prev` 上次节点（换节点检测）、`iter`（可 NULL，root 路径）、
  `k` 当前键、`initial` 首轮标志。
- **返回**：0/errcode；若修键产生 updates 则提交并返回 `transaction_restart_commit`（:774~:775）强制重走。
- **调用链**：`bch2_gc_btree` 逐键（:818）与 `bch2_gc_btree_root`（:803）调用。
- **代码片段**（:733~:739 换节点验拓扑；:772~:776 预留提交）：
```c
if (iter) {
    struct btree_path *path = btree_iter_path(trans, iter);
    struct btree *b = path_l(path)->b;
    if (*prev != b)
        try(bch2_btree_node_check_topology(trans, b));
    *prev = b;
}
```
```c
if (bch2_trans_has_updates(trans)) {
    CLASS(disk_reservation, res)(c);
    return bch2_trans_commit(trans, &res.r, NULL, BCH_TRANS_COMMIT_no_enospc) ?:
        bch_err_throw(c, transaction_restart_commit);
}
```
```c
struct btree_trigger_op op = {
    .btree      = btree_id,
    .level      = level,
    .old        = old,
    .new        = unsafe_bkey_s_c_to_s(k),
    .new_buf_u64s = k.k->u64s,
    .flags      = BTREE_TRIGGER_gc|BTREE_TRIGGER_insert,
};
try(bch2_key_trigger(trans, op));
```
- **权衡**：五阶段顺序固定——①换节点验拓扑（摊销 O(节点) 次而非 O(键) 次）②首轮版本/未来版本修复
  （:749~:760）③位图键补标（:762~:768）④`bch2_bkey_check_repair`（:770，修键产生 updates 则**先提交再重启**，
  保证 trigger 看到的是修后键）⑤`bch2_key_trigger(GC|insert)` 重算引用。`old` 恒为空键（:742~:743），
  纯“加法”语义，简化 trigger 逻辑。

### 6.2 `bch2_btree_node_check_topology`（interior.c:294，调用点 check.c:738）——换节点断言

- **签名**：`int bch2_btree_node_check_topology(struct btree_trans *trans, struct btree *b)`
- **参数**：`trans`、`b` 待验节点；**返回**：0/errcode。
- **调用链**：mark 流水线换节点时调用；实现转 `bch2_btree_node_check_topology_msg`（interior.c:205）。
- **权衡**：GC 全程持 `gc.lock` 写锁（见七），拓扑应稳定，此检查是低成本断言而非修复；
  真正的修复只在 mount 期 `bch2_check_topology` 做——在线只断言不停机。

### 6.3 `commit_topology_repair_log`（check.c:202）——先记后改的日志提交

- **签名**：`static int commit_topology_repair_log(struct btree_trans *trans)`
- **参数/返回**：`trans`；提交结果。
- **调用链**：所有 `mustfix_fsck_err` 修复分支在执行非事务变异（`set_node_min/max` 走 journal 键）
  之前调用（:255/:266/:272/:280/:286/:347）。
- **代码片段**（:202~:207，注释 :191~:201 阐明动机）：
```c
static int commit_topology_repair_log(struct btree_trans *trans)
{
    return bch2_trans_has_updates(trans)
        ? bch2_trans_commit(trans, NULL, NULL, BCH_TRANS_COMMIT_no_enospc)
        : 0;
}
```
- **权衡**：注释原文指出：拓扑修复经 journal 键（非事务更新），而 fsck 日志是事务更新，
  下一次 `bch2_trans_begin` 会静默丢弃未提交日志；且提交可能返回 transaction_restart，
  **先提交日志再做一次性变异**，使重启只重跑“检查+重排日志”，绝不重放非幂等变异。
  先记后改，防重放。

### 6.4 `set_node_min`（:114）/ `set_node_max`（:149）——经 journal 的边界修复

- **签名**：`static int set_node_min(struct bch_fs *c, struct btree *b, struct bpos new_min)`；
  max 同形。
- **参数**：`c`、目标节点、 new 边界；**返回**：0/errcode。
- **调用链**：gap/overlap 修复分支调用；经 `btree_ptr_to_v2`（:90）统一转 v2 →
  `bch2_journal_key_insert_take`/`bch2_journal_key_delete`。
- **代码片段**（:133~:145 min 路径；max 路径 :164 额外 unhash/rehash）：
```c
btree_ptr_to_v2(b, new);
b->data->min_key  = new_min;
new->v.min_key    = new_min;
SET_BTREE_PTR_RANGE_UPDATED(&new->v, true);
ret = bch2_journal_key_insert_take(c, b->c.btree_id, b->c.level + 1, &new->k_i);
```
```c
try(bch2_journal_key_delete(c, b->c.btree_id, b->c.level + 1, b->key.k.p));
```
- **权衡**：修复走 journal 键而非事务更新（pre-RW 环境事务子系统未全），`set_node_max` 需改 `k.p`
  故多一次 cache unhash/rehash（:182~:187）并 `BUG_ON` 断言状态机；`RANGE_UPDATED` 位置换显式传播。

### 6.5 `btree_check_node_boundaries`（:209）——gap/overlap 四路修复

- **签名**：`static int btree_check_node_boundaries(struct btree_trans *trans, struct btree *b, struct btree *prev, struct btree *cur)`
- **参数**：父 `b`、前驱 `prev`（可 NULL）、当前 `cur`；**返回**：0 或 `BCH_ERR_topology_repair_*` 重启信号。
- **调用链**：`bch2_btree_repair_topology_recurse` 主循环（:424~:425 `lockrestart_do` 包裹）逐邻接对调用。
- **代码片段**（:240 gap 分支；:262~:273 cur 覆盖 prev 分支）：
```c
if (bpos_lt(expected_start, cur->data->min_key)) {              /* gap */
    ...
    if (mustfix_fsck_err(trans, btree_node_topology_gap_between_nodes, ...)) {
        try(commit_topology_repair_log(trans));
```
```c
} else {                                                        /* overlap */
    if (prev && BTREE_NODE_SEQ(cur->data) > BTREE_NODE_SEQ(prev->data)) {
        if (bpos_ge(prev->data->min_key, cur->data->min_key)) { /* fully? */
```
- **权衡**：以 `expected_start = prev ? successor(prev->key.p) : b->min` 为唯一标尺；
  gap 先查 node-scan 能否找回丢失节点（level==1 且可扫描恢复，:243~:251），找得到发
  `did_fill_from_scan` 信号重走整轮而非就地补；overlap 用 `BTREE_NODE_SEQ` 判覆盖方向，
  全覆盖删节点、部分覆盖截断 max/min——seq 仲裁代替 wall-clock， crash 后仍确定。

### 6.6 `btree_check_root_boundaries`（:296）/ `btree_repair_node_end`（:322）——两端封口

- **签名**：`static int btree_check_root_boundaries(struct btree_trans *trans, struct btree *b)`；
  `static int btree_repair_node_end(struct btree_trans *trans, struct btree *b, struct btree *child)`。
- **参数/返回**：`trans` + 节点（+尾子节点）；0/errcode。
- **调用链**：前者在 `bch2_check_topology` 每树入口（:683）调用；后者在递归每层尾（:477~:478）调用。
- **代码片段**（:309~:312 root 下界；:327~:328 尾等即正常）：
```c
if (mustfix_fsck_err_on(!bpos_eq(b->data->min_key, POS_MIN),
            trans, btree_node_topology_bad_root_min_key, ...))
    try(set_node_min(c, b, POS_MIN));
```
```c
if (bpos_eq(child->key.k.p, b->key.k.p))
    return 0;
```
- **权衡**：root 上下界硬编码 `POS_MIN/SPOS_MAX`，简单可断言；尾子 `max==parent.p` 即闭合，
  否则与 gap 同逻辑尝试 scan 回填——两端封口与中间 gap 复用同一修复原语。

### 6.7 `bch2_btree_repair_topology_recurse`（:358）——双遍递归+`again` 重走

- **签名**：`static int bch2_btree_repair_topology_recurse(struct btree_trans *trans, struct btree *b)`
- **参数/返回**：`trans`、父节点；0/`topology_repair_*` 信号。
- **调用链**：`bch2_check_topology`（:684）→ 本函数 → 尾部第二遍对子逐个递归（:516）。
- **代码片段**（:429~:432 scan 回填转新一轮；:449~:466 删 prev 后 `goto again`，附防死锁注释）：
```c
if (bch2_err_matches(ret, BCH_ERR_topology_repair_did_fill_from_scan)) {
    new_pass = true;
    ret = 0;
}
```
```c
/*
 * cur is still read-locked, and goto again jumps over the
 * unlock at the end of the loop; drop it here or it leaks
 * (and later self-deadlocks a write lock on the same node).
 */
six_unlock_read(&cur->c.lock);
```
- **权衡**：第一遍修本层邻接、第二遍递归子层；任何结构性修复（删节点/scan 回填）置 `new_pass`
  从头 `again`，以 O(多轮) 换代码简单——mount 期低频可接受。EIO 节点直接 `journal_key_delete`
  删指针（:398~:406），stale 节点（seq 老于 scan 结果）同样驱逐（:412~:422）。

### 6.8 记账收尾三件套：`bch2_alloc_write_key`（:910）/ `bch2_gc_alloc_done`（:1027）/ `bch2_gc_write_stripes_key`（:1053）+ `bch2_gc_stripes_done`（:1107）

- **签名**：`static int bch2_alloc_write_key(struct btree_trans *trans, struct btree_iter *iter, struct bch_dev *ca, struct bkey_s_c k)`；
  `static int bch2_gc_alloc_done(struct bch_fs *c)`；
  `static int bch2_gc_write_stripes_key(struct btree_trans *trans, struct btree_iter *iter, struct bkey_s_c k)`。
- **参数/返回**：逐键比对 GC 重算值与盘上值，不一致则 `ret_fsck_err_on` 修键；0/errcode。
- **调用链**：`bch2_check_allocations` 尾部（:1166~:1169）依次调用。
- **代码片段**（:969~:977 data_type 不符即纠；:1009~:1010 全等即返回；:1097~:1099 stripe 计数重写）：
```c
if (ret_fsck_err_on(new.data_type != gc.data_type,
        trans, alloc_key_data_type_wrong, ...)) {
    new.data_type = gc.data_type;
```
```c
if (!bch2_alloc_v4_cmp(*old, new))
    return 0;
```
```c
for (unsigned i = 0; i < new->v.nr_blocks; i++)
    stripe_blockcount_set(&new->v, i,
        i < nr_data ? (m ? m->block_sectors[i] : 0) : 0);
```
- **权衡**：三处精妙：①空桶 `data_type` 取盘上 hint 而非 GC 值（:937~:954 长注释：GC 不跟踪
  need_discard/need_gc_gens 状态机，无条件覆盖会破坏降级兼容）；②`alloc_key_to_dev_counters(GC)`
  非重启安全，调后立即回写 `gc_m->data_type/dirty_sectors` 防重跑 double-count（:959~:966 “Ugly” 自述）；
  ③`bch2_trans_update(..., BTREE_TRIGGER_norun)`（:1023）写回时不跑触发器——计数已在 GC 中调过，
  避免二次记账；stripe 奇偶块 sector 计
...[truncated 4474 chars]