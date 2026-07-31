# vmcore 崩溃根因分析报告

> **分析对象**：`/nbudata/vmcore/vmcore`  
> **符号文件**：`/usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux`  
> **源码基线**：`/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7`  
> **崩溃时间**：2026-07-23 10:01:20（系统时区）  
> **分析日期**：2026-07-29  
> **PDCA 任务**：T0144  
> **结论置信度**：代码级根因高；具体外部触发动作未确定

---

## 1. 系统基本信息

| 项目 | 内容 |
|---|---|
| **vmcore 主机名** | `shqddb2` |
| **crash 操作主机/pane** | `nbusvr103`，tmux `0:0.0` |
| **崩溃内核** | `3.10.0-1160.83.1.el7.x86_64` |
| **内核构建时间** | 2022-12-19 |
| **架构** | x86_64 |
| **CPU 数量** | 192 |
| **内存** | 1023.7 GB |
| **硬件** | WOQU R6900 G5 / RS65M2C11SA |
| **BIOS** | 5.71，2024-01-11 |
| **运行时间** | 805 天 22:41:50 |
| **崩溃 CPU** | CPU 137 |
| **崩溃任务** | `swapper/137` |
| **dump 类型** | `PARTIAL DUMP` |

### 1.1 crash 启动命令

```bash
crash \
  /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux \
  /nbudata/vmcore/vmcore
```

### 1.2 crash 启动输出

```text
KERNEL:   /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
DUMPFILE: /nbudata/vmcore/vmcore [PARTIAL DUMP]
CPUS:     192
DATE:     Thu Jul 23 10:01:20 2026
UPTIME:   805 days, 22:41:50
NODENAME: shqddb2
RELEASE:  3.10.0-1160.83.1.el7.x86_64
MEMORY:   1023.7 GB
PANIC:    "BUG: unable to handle kernel paging request at ffffbd16abacc048"
COMMAND:  "swapper/137"
CPU:      137
```

启动过程中存在：

```text
WARNING: kernel version inconsistency between vmlinux and dumpfile
```

该警告作为证据限制保留。后续通过 release、模块调试符号、结构偏移、寄存器、
反汇编和指定源码交叉校验；未发现改变本报告结论的结构或指令冲突。

---

## 2. 崩溃概要

```text
BUG: unable to handle kernel paging request at ffffbd16abacc048
IP: dm_softirq_done+0x61/0x2f0 [dm_mod]
Oops: 0000 [#1] SMP
CR2: ffffbd16abacc048
PTE: 0
```

| 项目 | 判定 |
|---|---|
| **异常类型** | 内核态页故障 |
| **直接位置** | device-mapper 请求完成 softirq |
| **直接对象** | `dm_rq_target_io.ti` 指向的旧 `dm_target` |
| **内存状态** | 旧 target 所在 vmalloc 页已解除映射 |
| **错误类别** | 跨 table 生命周期使用旧 target，属于 UAF |
| **严重程度** | 致命，系统 panic 并生成 vmcore |

---

## 3. 崩溃调用链

```text
CPU 137 / swapper/137
  └─ call_function_single_interrupt
      └─ irq_exit
          └─ do_softirq
              └─ __do_softirq
                  └─ blk_done_softirq
                      └─ dm_softirq_done+97
                          └─ page_fault
                              └─ crash_kexec
```

`bt` 关键输出：

```text
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
```

崩溃发生在 CPU idle 期间处理块设备完成 softirq，不是业务进程主动执行某个
系统调用时直接崩溃。

---

## 4. 崩溃点精确定位

### 4.1 关键寄存器

| 寄存器 | 值 | 正确含义 |
|---|---|---|
| **RIP** | `ffffffffc02a48f1` | `dm_softirq_done+97` |
| **R13** | `ffff9ff42a3f1a40` | `struct dm_rq_target_io *tio` |
| **RDI** | `ffffbd16abacc040` | `tio->ti`，即旧 `struct dm_target *` |
| **R12** | `ffff9ff862cf9600` | clone request |
| **RBX** | `0` | `tio->error=0`，不是 clone 指针 |
| **CR2** | `ffffbd16abacc048` | `tio->ti + 8`，即读取 `ti->type` 时 fault |

### 4.2 fault 指令

```text
dm_softirq_done+81:  mov 0x8(%r13),%rdi
dm_softirq_done+92:  test %rdi,%rdi
dm_softirq_done+95:  je ...
dm_softirq_done+97:  mov 0x8(%rdi),%rdx   ← fault
dm_softirq_done+103: mov 0x60(%rdx),%r8
```

寄存器关系：

```text
R13 + 8 = tio->ti
RDI     = tio->ti = ffffbd16abacc040
RDI + 8 = ti->type
CR2     = ffffbd16abacc048 = RDI + 8
```

### 4.3 DWARF 结构验证

```text
crash> mod -s dm_mod
crash> struct -o dm_rq_target_io

struct dm_rq_target_io {
    [0]  struct mapped_device *md;
    [8]  struct dm_target *ti;
    [16] struct request *orig;
    [24] struct request *clone;
    [88] int error;
}
```

对象内容：

```text
crash> struct dm_rq_target_io ffff9ff42a3f1a40

md    = ffff9ff81b1b7000
ti    = ffffbd16abacc040
orig  = ffff9ff42a3f18c0
clone = ffff9ff862cf9600
error = 0
```

### 4.4 对应 C 表达式

`drivers/md/dm-rq.c:354–364`：

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
}
```

因此 fault C 表达式为：

```c
tio->ti->type
```

---

## 5. 非法指针状态证明

### 5.1 直接读取

```text
crash> rd ffffbd16abacc040 4
rd: invalid kernel virtual address: ffffbd16abacc040
```

### 5.2 页表遍历

```text
crash> vtop ffffbd16abacc040

VIRTUAL           PHYSICAL
ffffbd16abacc040  (not mapped)

PGD → PUD fc3ec6e067
    → PMD 27b845e067
    → PTE 0
```

结论：

- 地址所在页的 PTE 本身为 0；
- 不是“页表有效但 partial dump 没保存物理页”；
- 该 vmalloc 地址在崩溃时确实已经解除映射。

---

## 6. 证明它是旧 dm table target

### 6.1 同一 mapped_device 当前状态

```text
crash> struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name \
       ffff9ff81b1b7000

map                   = ffff9f8c1029bc00
immutable_target      = ffffbd16abbd2040
immutable_target_type = ffffffffc17f8040
use_blk_mq             = true
name                   = "253:19"
```

```text
crash> sym ffffffffc17f8040
ffffffffc17f8040 multipath_target [dm_multipath]
```

当前 table：

```text
highs         = ffffbd16abbd2000
targets       = ffffbd16abbd2040
num_allocated = 8
num_targets   = 1
type          = DM_TYPE_MQ_REQUEST_BASED
```

### 6.2 分配几何

`drivers/md/dm-table.c:160–182`：

```c
n_highs = dm_vcalloc(num + 1,
                     sizeof(struct dm_target) + sizeof(sector_t));
n_targets = (struct dm_target *)(n_highs + num);
t->highs = n_highs;
t->targets = n_targets;
```

当前 `num_allocated=8`：

```text
8 × sizeof(sector_t)
= 8 × 8
= 0x40
```

地址关系：

```text
当前 target = ffffbd16abbd2000 + 0x40
            = ffffbd16abbd2040

失效 target = ffffbd16abacc000 + 0x40
            = ffffbd16abacc040
```

结合 `dm_mq_queue_rq()` 把 `md->immutable_target` 保存到 `tio->ti`，可确定
faulting request 保存的是同一 md 请求提交时使用的旧 table target。

---

## 7. dm-19 底层设备映射

### 7.1 对象遍历路径

```text
mapped_device
  → immutable_target
    → dm_target.private
      → struct multipath
        → priority_groups
          → pgpaths
            → dm_path.dev
              → dm_dev.bdev
                → block_device.bd_disk
                  → gendisk.disk_name
```

### 7.2 当前 multipath 状态

```text
nr_priority_groups = 1
nr_valid_paths     = 2
queue_mode         = DM_TYPE_MQ_REQUEST_BASED
```

两个 path：

```text
pgpath 1
  dm_dev = ffff9fdda4d0e7d8
  name   = 259:54
  disk   = nvme37n1

pgpath 2
  dm_dev = ffff9fdda4d0e758
  name   = 259:55
  disk   = nvme38n1
```

### 7.3 faulting I/O 实际设备

```text
orig request  → dm-19
clone request → nvme38n1
```

因此本次实际完成的底层 I/O 路径为：

```text
dm-19 → nvme38n1
```

---

## 8. 旧 target 的销毁路径

### 8.1 reload 时序

`drivers/md/dm-ioctl.c:1033–1068`：

```text
dm_suspend(md)
→ dm_swap_table(md, new_map)
→ dm_resume(md)
→ dm_table_destroy(old_map)
```

### 8.2 安装新 target

`drivers/md/dm.c:2056–2072`：

```c
dm_stop_queue(q);
md->immutable_target = dm_table_get_immutable_target(t);
old_map = rcu_dereference_protected(md->map, ...);
rcu_assign_pointer(md->map, (void *)t);
```

### 8.3 释放旧 target

`drivers/md/dm-table.c:234–255`：

```c
for (i = 0; i < t->num_targets; i++) {
        struct dm_target *tgt = t->targets + i;
        if (tgt->type->dtr)
                tgt->type->dtr(tgt);
}

vfree(t->highs);
```

`highs` 与 `targets` 位于同一 vmalloc block，因此 `vfree(t->highs)` 会解除
包含旧 target 的虚拟页映射，与 vmcore 中的 PTE=0 一致。

---

## 9. 代码级根因

### 9.1 请求如何保存 target

`drivers/md/dm-rq.c:889–923`：

```c
static int dm_mq_queue_rq(...)
{
        struct dm_rq_target_io *tio = blk_mq_rq_to_pdu(rq);
        struct mapped_device *md = tio->md;
        struct dm_target *ti = md->immutable_target;

        if (ti->type->busy && ti->type->busy(ti))
                return BLK_MQ_RQ_QUEUE_BUSY;

        dm_start_request(md, rq);
        init_tio(tio, rq, md);
        tio->ti = ti;
        map_request(tio);
}
```

特点：

- `ti` 是裸指针；
- 请求提交时保存到 `tio->ti`；
- 底层 I/O 异步运行；
- 完成 softirq 再次解引用；
- 安全性依赖 suspend 在销毁旧 table 前阻止新请求并排空已进入请求。

### 9.2 正常 suspend 协议

`drivers/md/dm.c:2536–2559`：

```text
set DMF_BLOCK_IO_FOR_SUSPEND
→ dm_stop_queue()
→ dm_wait_for_completion()
→ set DMF_SUSPENDED
```

设计不变量：

```text
DMF_BLOCK_IO_FOR_SUSPEND == 1
    ⇒ 不允许新请求进入 target mapping
```

### 9.3 本版本缺失保护

当前 `dm_mq_queue_rq()` 在读取 `md->immutable_target` 后，没有检查：

```c
DMF_BLOCK_IO_FOR_SUSPEND
```

如果 blk-mq queue 在 DM suspend 期间被外部事件再次允许 dispatch，请求仍会：

```text
读取旧 target
→ pending++
→ tio->ti = old target
→ 下发 clone
```

随后：

```text
table swap
→ old map destroy
→ old target vfree
→ clone 完成
→ dm_softirq_done 解引用旧 tio->ti
→ page fault
```

### 9.4 根因判定

> **request-based Device Mapper 的 blk-mq 提交路径缺少 suspend 期间的第二道
> 请求准入检查，允许请求携带旧 `dm_target` 跨越 table swap/destroy，最终在
> 完成 softirq 中形成 UAF。**

---

## 10. 完整根因链

```text
┌──────────────────────────────────────────────────────────────┐
│ 第 1 层：dm-19 正在进行 table reload                         │
│                                                              │
│ DM 设置 DMF_BLOCK_IO_FOR_SUSPEND                             │
│ → quiesce queue                                              │
│ → 等待 pending I/O                                           │
└───────────────────────────┬──────────────────────────────────┘
                            ↓
┌───────────────────────────┴──────────────────────────────────┐
│ 第 2 层：暂停期间 queue 再次可以 dispatch                     │
│                                                              │
│ 具体外部动作未从静态 vmcore 唯一恢复                         │
│ 可能类型包括 queue 属性更新、elevator 或其他 unquiesce       │
└───────────────────────────┬──────────────────────────────────┘
                            ↓
┌───────────────────────────┴──────────────────────────────────┐
│ 第 3 层：dm_mq_queue_rq 缺少 block flag 检查                 │
│                                                              │
│ 读取 old md->immutable_target                                │
│ → dm_start_request                                           │
│ → tio->ti = old target                                       │
│ → 下发 nvme38n1 clone I/O                                    │
└───────────────────────────┬──────────────────────────────────┘
                            ↓
┌───────────────────────────┴──────────────────────────────────┐
│ 第 4 层：旧 table 被销毁                                     │
│                                                              │
│ 安装 new target                                              │
│ → resume                                                     │
│ → dm_table_destroy(old_map)                                  │
│ → vfree(old table block)                                     │
│ → old ti PTE=0                                               │
└───────────────────────────┬──────────────────────────────────┘
                            ↓
┌───────────────────────────┴──────────────────────────────────┐
│ 第 5 层：异步完成访问旧 target                               │
│                                                              │
│ nvme38n1 clone 完成                                          │
│ → blk_done_softirq                                           │
│ → dm_softirq_done                                            │
│ → tio->ti->type                                              │
│ → 访问未映射地址                                             │
│ → kernel panic                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 11. iSCSI 触发因素审查

### 11.1 时间线

```text
[69474335.486168] scsi host11112: iSCSI Initiator over TCP/IP
[69474362.72–63.05] host11112 LUN Synchronizing SCSI cache
[69474366.19–66.42] host11112 LUN 重新枚举和 attach
[69474411.952107] kernel panic
```

### 11.2 四层判定

| 门槛 | 结果 | 证据 |
|---|---|---|
| **iSCSI 事件存在** | 通过 | panic 前约 45–76 秒存在 host/LUN 事件 |
| **同一 faulting I/O path** | 不通过 | clone 实际为 `nvme38n1` |
| **同一当前 multipath map** | 不通过 | dm-19 当前两条 path 都是 NVMe |
| **iSCSI→multipathd→dm-19 reload** | 未证实 | 缺少 ioctl/map/WWID 对象链 |
| **进入约 61 ms bug 窗口** | 未证实 | iSCSI 日志不能连接到该短窗口 |

### 11.3 iSCSI 结论

- **直接触发：排除。**
- **间接促成：证据不足，保持 inconclusive。**

不能因为 iSCSI 事件时间上接近 panic，或相关模块已加载，就把它写成确定根因。

---

## 12. 替代解释审查

| 候选解释 | 审查结果 |
|---|---|
| **partial dump 漏页** | 排除；PTE 本身为 0 |
| **普通 NULL 指针** | 排除；`tio->ti` 非 NULL，且具有 target 分配几何 |
| **随机野指针/bit flip** | 低概率；指针来源、旧新对象和 `page+0x40` 几何一致 |
| **pending 提前递减** | 不支持；fault 在 `rq_completed()` 前，pending 仍为 `{2,0}` |
| **重复完成/请求重用** | 不支持；orig/clone/end_io_data/start_time 自洽 |
| **硬件内存错误** | 无正向证据；日志无 MCE、Memory Failure 或先行 Oops |
| **普通 reload 本身必然 UAF** | 排除；正常 quiesce+drain 设计可保护，需叠加准入缺口 |

---

## 13. 内核 Tainted 分析

```text
Tainted: P           OE  ------------ T
```

| 标志 | 含义 | 本报告处理 |
|---|---|---|
| **P** | 加载 proprietary 模块 | 记录为环境因素 |
| **O** | 加载 out-of-tree 模块 | 记录为环境因素 |
| **E** | 加载 unsigned 模块 | 记录为环境因素 |
| **T** | 曾发生 forced module unload | 记录为风险因素 |

这些 taint 标志会降低上游对现场的可复现性保证，但本次 fault 指令、对象布局、
旧新 target 和缺失 suspend guard 已形成独立证据链。当前没有证据证明某个
第三方模块直接破坏了 `tio->ti`。

### 关键模块

| 模块组 | 用途 |
|---|---|
| `dm_mod`, `dm_multipath`, `dm_round_robin` | Device Mapper 多路径 |
| `nvme`, `nvme_core`, `nvme_fabrics`, `nvme_rdma` | NVMe/NVMe-oF |
| `iscsi_tcp`, `libiscsi`, `scsi_transport_iscsi` | iSCSI |
| `oracleacfs`, `oracleadvm`, `oracleoks` | Oracle ACFS/ADVM |
| `cas_cache`, `cas_disk` | CAS 缓存 |

---

## 14. Bug 修复对应

### 14.1 上游修复

| 项目 | 内容 |
|---|---|
| **commit** | [`b4459b11e84092658fa195a2587aff3b9637f0e7`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4459b11e84092658fa195a2587aff3b9637f0e7) |
| **标题** | `dm rq: don't queue request to blk-mq during DM suspend` |
| **作者** | Ming Lei |
| **日期** | 2021-09-23 |
| **修改文件** | `drivers/md/dm-rq.c` |

上游增加：

```c
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_STS_RESOURCE;
```

修复原理：

```text
suspend flag 已置位
→ queue_rq 不再继续 mapping
→ 请求交回 blk-mq 重排队
→ 不保存旧 tio->ti
→ 不下发 clone
→ resume 后重新读取新 target
```

### 14.2 3.10 回移植要求

当前 3.10 blk-mq API 的等价返回值为：

```c
BLK_MQ_RQ_QUEUE_BUSY
```

语义等价逻辑：

```c
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_MQ_RQ_QUEUE_BUSY;
```

不能机械复制上游 8 行：

1. 返回类型不同；
2. `DMF_BLOCK_IO_FOR_SUSPEND` 当前只定义在 `dm.c`；
3. 需要安全共享 flag 定义或增加 DM internal helper；
4. guard 必须位于任何 `ti` 解引用、pending++、`tio->ti` 赋值和
   `map_request()` 之前。

### 14.3 当前验证状态

| 层次 | 状态 |
|---|---|
| **与上游 bug 的安全不变量一致** | 高置信成立 |
| **guard 静态切断本次故障路径** | 成立 |
| **3.10 补丁可编译** | 尚未实施 |
| **补丁内核运行验证** | 尚未实施 |
| **A/B 压测无复现** | 尚未实施 |

---

## 15. 建议

### 15.1 首选措施

1. 确认发行商支持的 kernel errata 是否包含与 b4459b11e840 语义等价的修复。
2. 优先使用发行商提供并支持的修复内核，不建议直接在生产系统应用未经验证的
   自制补丁。

### 15.2 如需自行回移植

1. 将 block flag 检查安全暴露给 `dm-rq.c`。
2. 在 `dm_mq_queue_rq()` 危险操作前返回 `BLK_MQ_RQ_QUEUE_BUSY`。
3. 编译并完成模块/KABI/静态检查。
4. 不在生产机直接执行复现压力。

### 15.3 A/B 验证

并发运行：

```text
流 1：fio 持续读写 dm-multipath 设备
流 2：dm table reload / suspend / resume
流 3：更新 nr_requests 或触发其他 blk-mq unquiesce
```

关键观测：

```text
C_enter_blocked   flag=1 时进入 queue_rq 的次数
C_mapped_blocked  flag=1 时仍继续 mapping 的次数
C_requeued        guard 命中并重排队次数
C_stale           completion 发现 stale target 的次数
```

补丁后必须满足：

```text
C_enter_blocked 允许 > 0
C_requeued 与 blocked 入口对应
C_mapped_blocked = 0
C_stale = 0
无 UAF / panic
resume 后请求全部完成
```

### 15.4 如继续追查外部触发

收集：

- multipathd debug/journal；
- udev event；
- DM ioctl 审计；
- queue `nr_requests`/scheduler 修改记录；
- map name、WWID 和 table reload 时间；
- iSCSI session/path 与 dm map 的对象对应。

目标是补齐：

```text
具体外部动作
→ blk-mq unquiesce
→ dm-19 suspend 窗口 request dispatch
```

---

## 16. 最终结论

### 16.1 直接原因

`dm_softirq_done()` 在处理 `nvme38n1` clone 完成时读取：

```c
tio->ti->type
```

其中 `tio->ti=ffffbd16abacc040` 所在 vmalloc 页已经解除映射，访问
`ffffbd16abacc048` 触发页故障。

### 16.2 根本原因

request-based Device Mapper 的 blk-mq 提交路径缺少
`DMF_BLOCK_IO_FOR_SUSPEND` 检查。当 queue 在 suspend 期间再次可以 dispatch
时，请求仍能保存旧 table 的 target 裸指针；table swap/resume 随后释放旧
table，而异步完成路径仍解引用旧 target，形成 UAF。

### 16.3 触发边界

- 具体外部 unquiesce 动作：未确定；
- iSCSI 直接触发：排除；
- iSCSI 间接促成：未证实；
- 上游 guard 静态修复充分性：成立；
- 3.10 回移植运行时有效性：待 A/B 验证。

---

## 附录 A：关键源码位置

| 作用 | 文件与行号 |
|---|---|
| fault C 表达式 | `drivers/md/dm-rq.c:354–364` |
| softirq 完成入口 | `drivers/md/dm-rq.c:394–418` |
| pending 生命周期 | `drivers/md/dm-rq.c:702–731` |
| 保存 `tio->ti` / 缺失 guard | `drivers/md/dm-rq.c:889–923` |
| table bind/target 替换 | `drivers/md/dm.c:2027–2082` |
| suspend/quiesce/drain | `drivers/md/dm.c:2485–2578` |
| reload 调用顺序 | `drivers/md/dm-ioctl.c:1008–1068` |
| target 分配几何 | `drivers/md/dm-table.c:160–182` |
| old target `vfree` | `drivers/md/dm-table.c:234–255` |
| multipath 对象结构 | `drivers/md/dm-mpath.c:34–105` |

---

## 附录 B：关键 crash 命令

```text
set scroll off
sys
bt
dis dm_softirq_done

mod -s dm_mod
struct -o dm_rq_target_io
struct dm_rq_target_io ffff9ff42a3f1a40

rd ffffbd16abacc040 4
vtop ffffbd16abacc040

struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name \
       ffff9ff81b1b7000
sym ffffffffc17f8040
struct dm_target.table,type,private ffffbd16abbd2040
struct dm_table.highs,targets,num_allocated,num_targets,type \
       ffff9f8c1029bc00

mod -s dm_multipath
struct multipath.ti,nr_priority_groups,priority_groups,current_pgpath,current_pg,nr_valid_paths \
       ffff9f8c1029a400
struct priority_group.m,pg_num,nr_pgpaths,pgpaths,bypassed \
       ffff9fe80adffcc0
struct pgpath.pg,fail_count,path,is_active ffff9ff7591decc0
struct pgpath.pg,fail_count,path,is_active ffff9ff7591dfc80

struct dm_dev ffff9fdda4d0e7d8
struct dm_dev ffff9fdda4d0e758
struct block_device.bd_disk ffff9ff83fbab0c0
struct block_device.bd_disk ffff9ff83fbabdc0
struct gendisk.disk_name,major,first_minor ffff9fe872280c00
struct gendisk.disk_name,major,first_minor ffff9fe872286c00

log | grep -E 'scsi host11112|11112:0:0:|BUG: unable|dm_softirq_done'
log | grep -Ei 'mce|machine check|hardware error|memory failure|corrupt|Oops:'
quit
```

---

## 附录 C：证据文件

| 证据 | 说明 |
|---|---|
| `crash-session.log` | 第一轮完整 crash 调查 transcript |
| `crash-proof-rerun.log` | 第二轮独立证明复跑 transcript |
| `investigation-log.md` | 每步目的、假设、结果、解释和下一步 |
| `root-cause-proof.md` | 根因完整证明 |
| `source-map.md` | 源码位置索引 |
| `patch-equivalence-proof.md` | 上游修复同源性与充分性 |
| `logic-closure-review.md` | 逻辑闭合审查和技术图 |
| `root-cause-chain-nontechnical.md` | 非技术版根因链路图 |

第二轮 transcript：

```text
行数：714
大小：42,823 bytes
SHA-256：838b78c6e89b8046b35c9510bfc3ef17e2806a565e873d8fcdfde2c18b00dc9c
```

