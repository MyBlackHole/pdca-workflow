# vmcore 崩溃分析报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 崩溃时间 | Thu Jul 23 10:01:20 2026 |
| 运行时间 | 805 days, 22:41:50 |
| 主机名 | shqddb2 |
| 硬件 | WOQU R6900 G5, 192 CPUs, 1023.7 GB RAM |
| 内核 | 3.10.0-1160.83.1.el7.x86_64 #1 SMP Mon Dec 19 10:44:06 UTC 2022 |
| Panic | BUG: unable to handle kernel paging request at ffffbd16abacc048 |
| 崩溃线程 | swapper/137 (PID: 0, CPU: 137) |
| 内核 Taint | P (proprietary module), OE (module loaded) |

## 加载模块

涉及 Oracle ACFS/ADVM/OKS、CAS cache、NVMe over RDMA、Mellanox、knem、xpmem 等第三方/专有模块。

## 崩溃回溯 (bt)

```
#0  machine_kexec
#1  __crash_kexec
#2  crash_kexec
#3  oops_end
#4  no_context
#5  __bad_area_nosemaphore
#6  bad_area_nosemaphore
#7  __do_page_fault
#8  do_page_fault
#9  page_fault
    [exception RIP: dm_softirq_done+97]  ← CRASH
#10 blk_done_softirq
#11 __do_softirq
#12 call_softirq
#13 do_softirq
#14 irq_exit
#15 smp_call_function_single_interrupt
#16 call_function_single_interrupt
--- <IRQ stack> ---
#17 call_function_single_interrupt
#18 default_idle
#19 arch_cpu_idle
#20 cpu_startup_entry
#21 start_secondary
```

## 执行流程

```
CPU 137 idle (native_safe_halt)
  → 收到 IPI (call_function_single_interrupt)
  → IRQ 退出时处理 softirq (irq_exit → do_softirq)
  → 块层完成 softirq (blk_done_softirq)
  → dm 请求完成处理 (dm_softirq_done) ← 崩溃点
```

## 崩溃指令分析

**RIP**: `dm_softirq_done+0x61/0x2f0` = `0xffffffffc02a48f1`

**崩溃指令**: `48 8b 57 08` = `mov 0x8(%rdi),%rdx`
（从 `rdi` 指向地址 + 8 字节处加载到 `rdx`）

**崩溃地址 CR2**: `ffffbd16abacc048` = `rdi + 8`，页表项 PTE=0（未映射）

## 寄存器映射

| 寄存器 | 值 | 含义 |
|--------|------|------|
| RDI | ffffbd16abacc040 | `tio->ti` (dm_target 指针)，无效地址 |
| R12 | ffff9ff862cf9600 | `clone` (struct request *)，有效 |
| R13 | ffff9ff42a3f1a40 | `tio2` (clone->end_io_data)，有效 |
| RBX | 0 | `tio->error`，0 表示无错误 |
| RAX | 1 | `mapped` 标志位 |

## 反汇编关键帧对应源码

```
dm_softirq_done (dm-rq.c:394)
  +41: lea 0x180(%rdi),%r13    → r13 = rq + 0x180 = tio (blk_mq_rq_to_pdu)
  +48: mov 0x18(%r13),%r12     → r12 = tio->clone = clone  (dm-rq.h:25)
  +52: test %r12,%r12          → if (!clone) goto skip    (dm-rq.c:401)

  +61: mov 0x48(%rbx),%rax     → rax = rq->cmd_flags
  +65: mov 0x58(%r13),%ebx     → ebx = tio->error         (dm-rq.h:27)

  内联 dm_done (dm-rq.c:354)
  +69: mov 0x170(%r12),%r13    → r13 = clone->end_io_data (dm-rq.c:357)
  +77: shr $0x16,%rax          → 提取 REQ_FAILED 位
  +81: mov 0x8(%r13),%rdi      → rdi = tio2->ti           (dm-rq.c:360)
  +85: xor $0x1,%rax
  +89: and $0x1,%eax           → mapped = !(rq->cmd_flags & REQ_FAILED)
  +92: test %rdi,%rdi          → if (tio->ti)             (dm-rq.c:360)
  +95: je +109                 → NULL 则跳转
→+97: mov 0x8(%rdi),%rdx      → rdx = ti->type           (崩溃在 dm-rq.c:361)
  +101: test %al,%al           → if (mapped && rq_end_io) (dm-rq.c:363)
  +103: mov 0x60(%rdx),%r8     → r8 = type->rq_end_io
```

### 结构体偏移验证

**struct dm_rq_target_io** (dm-rq.h:22):
```
offset 0x00: struct mapped_device *md
offset 0x08: struct dm_target *ti       ← tio2->ti = INVALID (ffffbd16abacc040)
offset 0x10: struct request *orig
offset 0x18: struct request *clone     ← clone = valid pointer
offset 0x58: int error                 ← tio->error = 0
```

**struct dm_target** (device-mapper.h:241):
```
offset 0x00: struct dm_table *table
offset 0x08: struct target_type *type   ← 试图访问时崩溃
```

**struct target_type** (device-mapper.h:169):
```
offset 0x60: dm_request_endio_fn rq_end_io  ← 崩溃后下一个访问目标
```

**struct request** (blkdev.h:110):
```
offset 0x38: struct request_queue *q
offset 0x48: u64 cmd_flags
offset 0xd0: void *special (non-mq) / mq_ops (mq)
offset 0x170: void *end_io_data        ← clone->end_io_data → tio2
```

### 源码精确位置

崩溃对应源码链：`drivers/md/dm-rq.c:361`

```
354: static void dm_done(struct request *clone, int error, bool mapped)
355: {
356:     int r = error;
357:     struct dm_rq_target_io *tio = clone->end_io_data;
358:     dm_request_endio_fn rq_end_io = NULL;
359: 
360:     if (tio->ti) {                              ← 检查通过（ti 非 NULL 但无效）
361:         rq_end_io = tio->ti->type->rq_end_io;  ← **崩溃点**
362: 
363:         if (mapped && rq_end_io)
364:             r = rq_end_io(tio->ti, clone, error, &tio->info);
365:     }
```

被 `dm_softirq_done` (dm-rq.c:394) 调用：
```
394: static void dm_softirq_done(struct request *rq)
395: {
396:     bool mapped = true;
397:     struct dm_rq_target_io *tio = tio_from_request(rq);
398:     struct request *clone = tio->clone;
399:     int rw;
400: 
401:     if (!clone) { ... return; }
402: 
403:     if (rq->cmd_flags & REQ_FAILED)
404:         mapped = false;
405: 
406:     dm_done(clone, tio->error, mapped);         ← 内联展开后在此崩溃
407: }
```

## 根因分析

**直接原因**：`dm_done()` 函数在访问 `tio->ti->type->rq_end_io` 时，`tio->ti` 指向无效地址 `ffffbd16abacc040`（该地址页表项为空，PTE=0），导致内核 page fault。

**数据流追踪**：
1. `rq`（原始请求）→ `tio_from_request` → `tio`（有效）
2. `tio->clone` → `clone`（有效，ffff9ff862cf9600）
3. `clone->end_io_data` → `tio2`（有效，ffff9ff42a3f1a40）
4. `tio2->ti` → **`ffffbd16abacc040`（无效！）**

**根本原因**（最可能场景）：
- DM 设备上的一个 I/O 请求已完成并交付给块层 softirq 完成处理
- 在该 I/O 请求创建和完成之间，对应的 DM target 已经被移除或重新配置
- `clone->end_io_data->ti` 指针是一个**悬空指针（dangling pointer）**：它指向的 `struct dm_target` 已经被释放，内存被回收或重新映射
- 函数中虽然有 `if (tio->ti)` 的 NULL 检查，但被释放后的指针可能不为 NULL（内存已被回收但内容尚未被覆写为零），从而绕过了检查

**触发条件**：
- 内核已加载 `dm_multipath`、`dm_round_robin`、`dm_mirror`、`dm_mod` 等 DM 模块
- 系统运行了 805 天，负载较高（load average 12+，5243 个任务）
- 软中断上下文中存在 DM 设备的 I/O 完成竞争条件

## 修复方向建议

1. 确认 DM target 的释放流程中是否存在使用计数（refcount）问题，确保在 target 被移除时所有关联的 I/O 已经完成
2. 在 `dm_done()` 的 `if (tio->ti)` 检查后增加更健壮的指针有效性验证
3. 检查与 Oracle ACFS/ADVM 等第三方模块的交互是否存在特殊场景
4. 检查是否有其他内核线程同时在操作同一个 DM 设备的 table
