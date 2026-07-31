# T0144 vmcore 根因完整证明过程

> 复核状态：本证明链已于 `2026-07-29 14:39–14:42 +08:00` 在 tmux
> `0:0.0` 中重新启动第二个独立 crash 进程，严格按 P1–P10 顺序复跑。
> 第二次原始输出为 `crash-proof-rerun.log`，SHA-256
> `838b78c6e89b8046b35c9510bfc3ef17e2806a565e873d8fcdfde2c18b00dc9c`；
> 预定信号全部重现。

## 1. 证明目标、输入与证据规则

目标是只使用本轮重新执行的 crash 输出，证明：

1. 内核在哪条指令崩溃；
2. 指令正在解引用什么 C 结构字段；
3. 该字段为什么成为无效地址；
4. 对象如何从请求提交跨越到异步完成；
5. 哪个源码同步缺口允许对象在完成前被释放；
6. iSCSI 是否构成直接或间接触发。

本轮输入：

```text
vmlinux: /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
vmcore:  /nbudata/vmcore/vmcore
source:  /home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7
tmux:    0:0.0
```

证据分层：

- **事实**：crash、DWARF、反汇编或指定源码直接显示；
- **确定推导**：所有必要前提均由事实覆盖；
- **证据支持的机制推断**：静态 vmcore 无法记录过去事件本身，但现场状态、源码路径和已知修复共同支持；
- **未证实**：缺少对象或时间窗口连接，不写成确定因果。

完整原始输出为 `records/T0144-0729-vmcore-source-revalidation/evidence/crash-session.log`，SHA-256：

```text
d5ff1d02fa95fbc723720d8941265eee59a3307b4434aa50942904c945050f0a
```

## 2. 操作一：独立启动 crash

### 目的

证明本次不是复用历史 crash 会话，并固定符号文件、dump、release 和 panic task。

### 操作

```text
crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore
```

### crash 关键输出

```text
__T0144_CRASH_BEGIN__ 2026-07-29T13:42:16+0800
crash 7.2.3-11.el7_9.1

KERNEL:   /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
DUMPFILE: /nbudata/vmcore/vmcore  [PARTIAL DUMP]
CPUS:     192
RELEASE:  3.10.0-1160.83.1.el7.x86_64
PANIC:    "BUG: unable to handle kernel paging request at ffffbd16abacc048"
COMMAND:  "swapper/137"
CPU:      137
```

加载时存在：

```text
WARNING: kernel version inconsistency between vmlinux and dumpfile
```

### 解释

- 指定 vmlinux/vmcore 已由本轮新进程成功加载，release 与指定源码版本一致。
- 版本警告是证据限制，不能隐藏。因此后续不单独依赖源码行号，而用模块 DWARF 偏移、寄存器、反汇编和源码互相校验。
- dump 是 partial dump，所以“地址读不到”本身不能证明已释放；必须继续检查页表 PTE。

## 3. 操作二：确定异常上下文和调用链

### 目的

取得 fault RIP、CR2、寄存器和调用路径，判断崩溃发生于哪个子系统。

### 操作

```text
crash> sys
crash> set scroll off
crash> bt
```

`set scroll off` 的目的是关闭分页，防止长调用栈停在 less 中而遗漏后半段。

### crash 关键输出

```text
PID: 0  CPU: 137  COMMAND: "swapper/137"

[exception RIP: dm_softirq_done+97]
RIP: ffffffffc02a48f1
RDI: ffffbd16abacc040
R12: ffff9ff862cf9600
R13: ffff9ff42a3f1a40

#10 blk_done_softirq
#11 __do_softirq
#12 call_softirq
#13 do_softirq
#14 irq_exit
...
#17 native_safe_halt
#18 default_idle
```

内核日志中的异常帧进一步给出：

```text
CR2: ffffbd16abacc048
IP: dm_softirq_done+0x61/0x2f0 [dm_mod]
```

### 解释

事实：

- CPU 137 原本 idle，在块设备完成 softirq 中进入 `dm_softirq_done()`。
- fault virtual address 为 `ffffbd16abacc048`。
- fault 时 RDI 为 `ffffbd16abacc040`，因此 `CR2 == RDI + 8`。

下一步必须确认 `+97` 指令是否确实访问 `RDI+8`，以及 RDI 的 C 类型。

## 4. 操作三：由 fault 指令映射到 C 表达式

### 目的

排除“只凭函数名猜测”，用机器指令证明具体字段解引用。

### 操作

```text
crash> dis dm_softirq_done
```

### crash 关键输出

```text
dm_softirq_done+81:  mov 0x8(%r13),%rdi
dm_softirq_done+92:  test %rdi,%rdi
dm_softirq_done+95:  je ...
dm_softirq_done+97:  mov 0x8(%rdi),%rdx
dm_softirq_done+103: mov 0x60(%rdx),%r8
```

### 指定源码对应

[`drivers/md/dm-rq.c:354–364`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:354)：

```c
static void dm_done(struct request *clone, int error, bool mapped)
{
        struct dm_rq_target_io *tio = clone->end_io_data;
        dm_request_endio_fn rq_end_io = NULL;

        if (tio->ti) {
                rq_end_io = tio->ti->type->rq_end_io;
                if (mapped && rq_end_io)
                        r = rq_end_io(tio->ti, clone, error, &tio->info);
        }
```

[`drivers/md/dm-rq.c:394–418`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:394)：

```c
static void dm_softirq_done(struct request *rq)
{
        struct dm_rq_target_io *tio = tio_from_request(rq);
        struct request *clone = tio->clone;
        ...
        dm_done(clone, tio->error, mapped);
}
```

### 解释

反汇编的两级读取对应：

1. `R13+8 → tio->ti`
2. `RDI+8 → ti->type`
3. 后续 `RDX+0x60 → type->rq_end_io`

fault 指令是第二步，即读取 `tio->ti->type`。

## 5. 操作四：用模块 DWARF 验证对象类型和偏移

### 目的

避免本地源码结构与 dump 模块实际布局不一致；用 dump 对应模块的 DWARF 验证 `R13+8`。

### 操作

```text
crash> mod -s dm_mod
crash> struct -o dm_rq_target_io
crash> struct dm_rq_target_io ffff9ff42a3f1a40
```

### crash 关键输出

```text
MODULE: dm_mod
OBJECT:
/usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/kernel/drivers/md/dm-mod.ko.debug

struct dm_rq_target_io {
    [0]  struct mapped_device *md;
    [8]  struct dm_target *ti;
    [16] struct request *orig;
    [24] struct request *clone;
    [88] int error;
}

struct dm_rq_target_io @ ffff9ff42a3f1a40 {
  md    = ffff9ff81b1b7000
  ti    = ffffbd16abacc040
  orig  = ffff9ff42a3f18c0
  clone = ffff9ff862cf9600
  error = 0
}
```

### 解释

- DWARF 明确证明 `ti` 偏移为 8。
- `R13` 正是 `tio`，`R13+8` 得到的值与异常帧 RDI 完全相等。
- `clone` 与异常帧 R12 完全相等。
- 因此 fault C 表达式不是推测，而是由寄存器、DWARF 偏移和源码三方闭合：

```text
R13 = tio
*(R13+8) = tio->ti = RDI = ffffbd16abacc040
*(RDI+8) = tio->ti->type → page fault
```

## 6. 操作五：证明 fault 指针在崩溃页表中已解除映射

### 目的

区分：

- partial dump 没保存物理页；
- 地址存在但内容损坏；
- 页表映射本身已经不存在。

### 操作

```text
crash> rd ffffbd16abacc040 4
crash> vtop ffffbd16abacc040
```

### crash 关键输出

```text
rd: invalid kernel virtual address: ffffbd16abacc040

VIRTUAL           PHYSICAL
ffffbd16abacc040  (not mapped)

PGD → PUD fc3ec6e067
    → PMD 27b845e067
    → PTE 0
```

### 解释

PTE 本身为 0，证明该虚拟页在崩溃时没有映射。它不是“有映射但物理页被 partial dump 排除”。这与 vmalloc 对象经 `vfree()` 后的状态一致。

此时仍需证明该地址原来是什么对象，不能仅凭 PTE=0 直接称为 UAF。

## 7. 操作六：证明它是旧 dm table 的 target

### 目的

检查同一个 `mapped_device` 当前对象，比较失效 `ti` 和当前 target 的类型、地址几何。

### 操作

```text
crash> struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name ffff9ff81b1b7000
crash> sym ffffffffc17f8040
crash> struct dm_target.table,type,begin,len,private ffffbd16abbd2040
crash> struct dm_table.highs,targets,num_allocated,num_targets,type ffff9f8c1029bc00
```

### crash 关键输出

```text
map                   = ffff9f8c1029bc00
immutable_target      = ffffbd16abbd2040
immutable_target_type = ffffffffc17f8040
use_blk_mq             = true
name                   = "253:19"

ffffffffc17f8040 multipath_target [dm_multipath]

current target:
  table   = ffff9f8c1029bc00
  type    = ffffffffc17f8040
  private = ffff9f8c1029a400

current table:
  highs         = ffffbd16abbd2000
  targets       = ffffbd16abbd2040
  num_allocated = 8
  num_targets   = 1
  type          = DM_TYPE_MQ_REQUEST_BASED
```

地址比较：

```text
fault request saved ti = ffffbd16abacc040
current table target   = ffffbd16abbd2040

old candidate page base + 0x40 = ffffbd16abacc000 + 0x40
current highs base     + 0x40 = ffffbd16abbd2000 + 0x40
```

### 指定源码对应

[`drivers/md/dm-table.c:160–182`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-table.c:160)：

```c
n_highs = dm_vcalloc(num + 1,
                     sizeof(struct dm_target) + sizeof(sector_t));
n_targets = (struct dm_target *)(n_highs + num);
t->highs = n_highs;
t->targets = n_targets;
```

当前 `num_allocated=8`，8 个 `sector_t` 占 `8×8=0x40` 字节，所以首个 target 必然位于 highs 基址 `+0x40`。

### 解释

事实和确定推导：

- 当前 target 正好是当前 vmalloc block `+0x40`。
- fault request 保存的指针也正好是另一个 vmalloc 页 `+0x40`。
- 同一 md 当前 target 已经变化。
- 旧地址的 PTE 已为 0。

因此 `ffffbd16abacc040` 高度确定为同一 md 之前某张 dm table 的首个 `dm_target`，而非随机野指针或普通 NULL。

## 8. 操作七：证明旧 target 的释放路径

### 目的

从指定源码连接“target 被替换”到“页表解除映射”。

### 指定源码证明

#### 8.1 reload 先 suspend，再交换 table

[`drivers/md/dm-ioctl.c:1033–1044`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-ioctl.c:1033)：

```c
if (new_map) {
        if (!dm_suspended_md(md))
                dm_suspend(md, suspend_flags);
        old_map = dm_swap_table(md, new_map);
}
```

#### 8.2 bind 写入新 target 和新 map

[`drivers/md/dm.c:2056–2072`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm.c:2056)：

```c
dm_stop_queue(q);
md->immutable_target = dm_table_get_immutable_target(t);
old_map = rcu_dereference_protected(md->map, ...);
rcu_assign_pointer(md->map, (void *)t);
```

#### 8.3 resume 后销毁旧 table

[`drivers/md/dm-ioctl.c:1057–1068`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-ioctl.c:1057)：

```c
if (dm_suspended_md(md))
        r = dm_resume(md);
...
if (old_map)
        dm_table_destroy(old_map);
```

#### 8.4 destroy 对分配块执行 vfree

[`drivers/md/dm-table.c:234–255`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-table.c:234)：

```c
for (i = 0; i < t->num_targets; i++) {
        struct dm_target *tgt = t->targets + i;
        if (tgt->type->dtr)
                tgt->type->dtr(tgt);
}
vfree(t->highs);
```

### 解释

targets 与 highs 属于同一 vmalloc block。`vfree(t->highs)` 会解除包含 target 的 vmalloc 映射，准确解释旧 `ti` 的 PTE=0。

至此已经证明“请求持有旧 target，当前 table 已换新，旧 target 所在页已解除映射”。剩余问题是正常 suspend 本应等待 I/O，为什么仍出现悬空请求。

## 9. 操作八：证明请求跨异步完成保存裸 target 指针

### 目的

找出 `tio->ti` 的赋值点，判断是否有引用计数或覆盖整个 I/O 生命周期的 SRCU。

### 指定源码证明

[`drivers/md/dm-rq.c:889–923`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:889)：

```c
static int dm_mq_queue_rq(...)
{
        struct dm_rq_target_io *tio = blk_mq_rq_to_pdu(rq);
        struct mapped_device *md = tio->md;
        struct dm_target *ti = md->immutable_target;       /* line 895 */

        if (ti->type->busy && ti->type->busy(ti))
                return BLK_MQ_RQ_QUEUE_BUSY;

        dm_start_request(md, rq);                          /* line 908 */
        init_tio(tio, rq, md);
        tio->ti = ti;                                      /* line 916 */
        if (map_request(tio) == DM_MAPIO_REQUEUE) ...
}
```

完成路径在本文件 394–418 行，最终回到 360–364 行重新使用保存的 `tio->ti`。

### 解释

- target 是裸指针；
- 赋值后底层 I/O 异步运行；
- 直到完成 softirq 才再次解引用；
- 没有为 target 单独增加跨完整 I/O 的引用计数；
- 因此安全性依赖 suspend 确保所有已进入请求完成后才能销毁旧 table。

## 10. 操作九：定位真正同步缺口

### 目的

解释为什么正常 suspend 的 queue quiesce 和 pending drain 没有阻止此次 UAF。

### 正常 suspend 源码

[`drivers/md/dm.c:2536–2559`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm.c:2536)：

```c
set_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags);
...
dm_stop_queue(md->queue);
...
r = dm_wait_for_completion(md, task_state);
if (!r)
        set_bit(dmf_suspended_flag, &md->flags);
```

正常情况下：

1. 设置 block flag；
2. quiesce queue；
3. 等待 pending=0；
4. 才允许 table swap。

### 当前版本缺口

本版本 `dm_mq_queue_rq()` 在读取 `md->immutable_target` 后，没有：

```c
test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)
```

相反，同一 `dm.c` 的其他 I/O 路径在 1599、1620 行会检查该 flag，说明 flag 的语义就是 suspend 期间阻止新 I/O。

### 上游对应修复

上游提交：

```text
b4459b11e84092658fa195a2587aff3b9637f0e7
dm rq: don't queue request to blk-mq during DM suspend
```

补丁在读取 `md->immutable_target` 后增加：

```c
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_STS_RESOURCE;
```

上游提交说明的原因是：blk-mq 的 unquiesce 可能来自 DM 之外的事件，例如 elevator 切换、更新 `nr_requests` 等；这样请求可能在 DM suspend 中重新进入，所以必须让 blk-mq 重排队。

### 完整竞态时序

```text
CPU A / DM suspend-reload                 CPU B / 外部 blk-mq 与 I/O
--------------------------------------    --------------------------------
set DMF_BLOCK_IO_FOR_SUSPEND
quiesce dm queue
wait pending == 0
                                          外部事件 unquiesce blk-mq queue
                                          dm_mq_queue_rq() 重新进入
                                          读取 old md->immutable_target
                                          （本版本未检查 block flag）
                                          dm_start_request(): pending++
                                          tio->ti = old target
                                          下发 NVMe clone I/O
dm_swap_table(): 安装 new target
dm_resume()
dm_table_destroy(old_map)
vfree(old table block) → old ti PTE=0
                                          NVMe I/O 完成
                                          dm_softirq_done()
                                          dm_done()
                                          读取 tio->ti->type
                                          page fault
```

### crash 的恢复后状态

操作：

```text
crash> struct mapped_device.flags,pending,immutable_target,map ffff9ff81b1b7000
```

输出：

```text
flags = 64
pending = {{ counter = 2 }, { counter = 0 }}
immutable_target = ffffbd16abbd2040
map = ffff9f8c1029bc00
```

解释：

- panic 时已经 resume，block bit 0 已清除；
- new target/map 已生效；
- pending 仍包含在途请求；
- 这与“请求在 suspend 的错误窗口进入、table 更换后才完成”一致；
- 也反证 fault 前当前请求已提前 `rq_completed()` 的解释。

## 11. 操作十：确认 faulting I/O 的底层路径并审查 iSCSI

### 目的

判断 iSCSI 是否是发生 fault 的直接 I/O path，或能否证明其通过 multipath 状态变化间接进入竞态。

### 操作与输出

```text
crash> struct gendisk.disk_name,major,first_minor ffff9ff99b7d2800
disk_name = "dm-19"
major = 253
first_minor = 19

crash> struct gendisk.disk_name,major,first_minor ffff9fe872286c00
disk_name = "nvme38n1"
major = 259
first_minor = 55
```

加载 `dm_multipath` DWARF 并遍历 dm-19 的两条 path 后：

```text
dm_dev 259:54 → nvme37n1
dm_dev 259:55 → nvme38n1
```

日志时间线：

```text
[69474335.486168] scsi host11112: iSCSI Initiator over TCP/IP
[69474366.19–66.42] host11112 LUN 重新枚举和 attach
[69474411.952107] panic
```

### 四层判定

| 门槛 | 结果 | 证明 |
|---|---|---|
| iSCSI 事件存在 | 通过 | panic 前约 76 秒创建 host，约 45.5 秒前 LUN 重枚举 |
| 同一 I/O path | 不通过 | faulting clone 是 nvme38n1；dm-19 全部 path 均为 NVMe |
| 状态转换连接 | 未证实 | 未发现 host11112 事件到 dm-19 reload 的 ioctl/map 对象链 |
| 进入约 61 ms bug 窗口 | 未证实 | iSCSI 日志相距约 45 秒，不能连接到请求跨 table 销毁的短窗口 |

判定：

- **直接 iSCSI 触发：排除（not triggered）。**
- **iSCSI uevent 经 multipathd 全局 reconfigure 间接促成：inconclusive。**

## 12. 操作十一：排查竞争性替代解释

### 12.1 partial dump 缺页

反证：`vtop` 显示 PTE=0，不是有效映射对应的物理页未保存。排除。

### 12.2 普通 table reload 必然 UAF

反证：正常 `dm_stop_queue()` 与 `dm_wait_for_completion()` 设计上会排空请求。必须叠加“外部 unquiesce + queue_rq 缺少 block flag guard”才解释此次事件。排除为单独根因。

### 12.3 pending 提前递减或请求重复完成

反证：

- fault 位于 `dm_done()` 读取 target，尚未到 `dm_end_request()/rq_completed()`；
- panic 时 pending 仍为 `{2,0}`；
- orig/clone 指针、end_io_data、sector、启动时间和 tag 均自洽。

不支持。

### 12.4 随机野指针或 bit flip

反证：

- 指针来自正确的 `tio->ti` 字段；
- 地址精确具有 dm table target 的 `page+0x40` 几何；
- 当前对象是另一个同样 `page+0x40` 的 target；
- 旧 table 有明确 `vfree()` 路径；
- 上游存在同路径、同机制修复。

概率显著低于生命周期 UAF。

### 12.5 硬件内存错误

操作：

```text
crash> log | grep -Ei 'mce|machine check|hardware error|edac|memory failure|corrupt|BUG:|Oops:|Call Trace'
```

输出只返回本次 BUG/Oops/Call Trace 和模块名 `skx_edac`，没有 MCE、Hardware Error、Memory Failure、corruption 或先行 Oops。没有正向证据支持硬件损坏；静默硬件错误无法由单份静态 dump 绝对排除。

## 13. 最终证明结论

### 直接原因

`dm_softirq_done()` 完成路径在 [`dm-rq.c:361`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:361) 读取：

```c
tio->ti->type
```

其中 `tio->ti=ffffbd16abacc040` 所在页 PTE=0，访问 `+8` 形成 CR2 `ffffbd16abacc048`。

### 根本原因

[`dm_mq_queue_rq()`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:889) 缺少 `DMF_BLOCK_IO_FOR_SUSPEND` 检查。DM suspend 后 queue 被外部事件重新 unquiesce 时，请求能够闯入并保存旧 table 的 target 裸指针；table swap/resume 随后 vfree 旧 table，而异步完成路径仍使用旧指针，形成 UAF。

### 证据强度

- fault 指令与 C 字段：**确定**
- `tio->ti` 是已解除映射的旧 dm target：**高置信确定**
- 缺失 suspend guard 是允许此次生命周期错误的源码 bug：**高置信**
- 具体由哪个外部动作执行 blk-mq unquiesce：**静态 vmcore 无法唯一识别**
- iSCSI 直接触发：**排除**
- iSCSI 间接促成：**未证实**

