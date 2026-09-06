# bcachefs EC 纠删专题学习报告（T0516）

> 精读 `fs/data/ec/`（约 4600 行）DOC_LATEX 与关键流程；
> 6 个 EC 相关本体节点为辅。事实源为源码。

---

## 一、全景：后台整桶编码路线

bcachefs 纠删不切分前台写（`create.c:3-55 DOC_LATEX`）：
前台先多副本写，reconcile 攒桶后算 RS parity，原子改 extent
指针。五步：取数桶→分配 parity 桶→算 parity→写 parity→改指针
（去多余副本，加 parity 指针加重建读标志）。

**可学**：路线选择决定一切复杂度。后台整桶编码把写洞、RMW、
部分写三个难题一次性消灭，代价是空间放大窗口期（多副本到
EC 之间）。

## 二、无写洞的数学保证

写洞的本质是 parity 与数据非原子更新。后台路线下数据不可变，
parity 一次算定，btree 原子换指针——三者合起来数学上无写洞，
不需要电池/日志兜底（`create.c:29-31`）。
**可学**：用"不可变加原子切换"消灭一致性问题，优于"可变加
日志兜底"。

## 三、Stripe 生命期与复用

成 stripe 后桶整体锁定，直到全部数据死亡或迁走；copygc 感知
约束，整条疏散重写（`create.c:33-37`）。复用旧 stripe 时位图锚
活块，仅补新块加移 parity 槽，标签算法冗余一致才复用
（`may_reuse_stripe`、`get_old_stripe`）；读到即折叠，halving
缓冲占用（`a838b515b`）。
**可学**：大单元（stripe）整体生命周期管理；复用必须判一致性，
折叠尽早释放。

## 四、显式三态与双引用

`ec_stripe_new` 经 open/filling/in_flight 三态，富 dump 答为何不
完成（`8ca5d6212`）；双引用区分 IO 与条带持有，提交点明确
（`ec_stripe_new_get/put`）。
**可学**：异步对象状态必须显式枚举，富 dump 是可观测刚需。

## 五、先验后算与二次校验

重建前先验旧条，换入旧数据，生成编码与校验，只写动过部分，
同步后校验，失败计数；同事务提交键更新，再改全 extent
（`__ec_stripe_create:602-649`）。读先直读，失败才 RS 重构；
先验后算，超冗余直接报（`bch2_stripe_buf_validate`）。
**可学**：验算分离，先验后算；失败路径短路，不污染好数据。

## 六、修复：单坏即降级加疏散重试

遍历指针任一坏即降级（阈值 1）；入口先判已恢复则 trace 返回，
并发后来者无害化（`stripe_repair_race`）；缺口先疏散活块再重建，
压延后队列等 IO 排空重做（`bch2_stripe_repair:2044-2112`、
`do_retry_stripes`）；意图锁防空条误删。
**可学**：阈值显式；并发修复后来者无害化；设备不足先疏散后重建。

## 七、读路径：直读优先降级静默

直读数据桶，失败重建读（取存活加 parity 解码，映射存 stripes
树，`create.c:40-46`）；仅离线致失败静默，保 burst 给真错
（`88209f67b`）；成功降级写静默（`a088d5bca`）。
**可学**：快路直读，慢路重建；预期内降级静默，保错误预算。

## 八、设计启示

后台整桶、不可变加原子、整体生命期、显式三态、先验后算、
阈值显式、无害化并发、降级静默。

---

## 复核途径

- `sed -n 3,55p fs/data/ec/create.c` 通读 DOC_LATEX。
- `grep -n "bch2_stripe_repair\|__ec_stripe_create\|may_reuse_stripe" fs/data/ec/create.c` 定位关键函数。
