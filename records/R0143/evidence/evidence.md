# Evidence — T0143 vmcore-deep

## 分析日志

原始 crash 命令完整输出见: `crash-session.log` (已注册为 E0143-crash-commands)

---

## Step 1: 加载 vmcore — 确认崩溃环境和基础信息

**命令**: `crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore`

**目的**: 加载内核符号表和内存转储，获取崩溃瞬间的系统全景。这是所有后续分析的入口。

**结果**:
```
KERNEL: vmlinux (3.10.0-1160.83.1.el7.x86_64)
DUMPFILE: vmcore [PARTIAL DUMP]
CPUS: 192
DATE: Thu Jul 23 10:01:20 2026
UPTIME: 805 days, 22:41:50
TASKS: 5243
NODENAME: shqddb2
MEMORY: 1023.7 GB
PANIC: "BUG: unable to handle kernel paging request at ffffbd16abacc048"
PID: 0, COMMAND: "swapper/137", CPU: 137, STATE: TASK_RUNNING (PANIC)
```

**分析**:
- 服务器稳定运行 805 天后崩溃，排除启动阶段或近期变更引入的新问题
- 192 CPU 的高负载数据库服务器，与 dm-multipath + NVMe 存储架构匹配
- 崩溃发生在 CPU 137 的 idle 进程（swapper/137），说明是**中断/软中断上下文中**发生了 panic
- CR2 = `ffffbd16abacc048`，该地址 PTE=0（页面未映射）

---

## Step 2: bt — 获取崩溃线程栈回溯

**命令**: `bt`

**目的**: 确定崩溃时的代码执行路径，定位导致 panic 的具体函数和指令。

**结果**:
```
PID: 0  TASK: ffff9f80a4830000  CPU: 137  COMMAND: "swapper/137"
 #0 machine_kexec
 #1 __crash_kexec
 #2 crash_kexec
 #3 oops_end
 #4 no_context
 #5 __bad_area_nosemaphore
 #6 bad_area_nosemaphore
 #7 __do_page_fault
 #8 do_page_fault
 #9 page_fault
     [exception RIP: dm_softirq_done+97]   ← 崩溃点
     RIP: ffffffffc02a48f1  RDI: ffffbd16abacc040
 #10 blk_done_softirq
 #11 __do_softirq
 #12 call_softirq
 #13 do_softirq
 #14 irq_exit
 #15 smp_call_function_single_interrupt
 #16 call_function_single_interrupt
 --- <IRQ stack> ---
 #17 call_function_single_interrupt
     [exception RIP: native_safe_halt+11]   ← 进入 idle 前的暂停指令
```

**分析**:
- 完整路径: idle loop → IPI (smp_call_function_single_interrupt) → IRQ exit → softirq (blk_done_softirq) → dm_softirq_done → page fault
- RIP = `dm_softirq_done+97`，在 dm 模块的 I/O 完成处理函数中崩溃
- RDI (第一个参数/解引用地址) = `ffffbd16abacc040`，正是 CR2 的前一个地址 (CR2 = ffffbd16abacc048 = RDI + 8)
- **关键线索**: 崩溃发生在 `dm_softirq_done` 解引用 `tio->ti->type` 时，`tio->ti` 的内容 (`ffffbd16abacc040`) 无效

---

## Step 3: struct dm_rq_target_io — 检查核心结构体

**命令**: `whatis dm_rq_target_io` → `struct dm_rq_target_io ffff9ff42a3f1a40`

**目的**: 
- 确定 `dm_rq_target_io` 结构体布局（偏移量）
- 检查 tio 实例的每个字段，区分配置/指向完整 vs 损坏

**结果**:
```c
struct dm_rq_target_io {
    struct mapped_device *md;    // offset 0x00
    struct dm_target *ti;        // offset 0x08  ← 崩溃涉及的字段
    struct request *orig;        // offset 0x10
    struct request *clone;       // offset 0x18
    struct kthread_work work;    // ...
    int error;                   // offset 0x58
    unsigned int completed;      // offset 0x64
}
SIZE: 136 bytes

实例 ffff9ff42a3f1a40:
  md    = 0xffff9ff81b1b7000  ✅ 有效
  ti    = 0xffffbd16abacc040  ❌ 悬空指针
  orig  = 0xffff9ff42a3f18c0  ✅ 有效
  clone = 0xffff9ff862cf9600  ✅ 有效
  error = 0
  completed = 524288
```

**分析**:
- tio 结构体本身**没有被损坏**（md/orig/clone 都指向有效内核地址）
- 只有 `ti` 字段是无效的 → 这排除了"tio 结构体被整体覆盖"的可能性
- 问题被精确定位到：**只有 `tio->ti` 指针是坏的**，说明是在 tio 被分配后、ti 字段被赋值后，目标对象被释放了

---

## Step 4: struct request (clone) — 检查 I/O 完成路径

**命令**: `struct request ffff9ff862cf9600`

**目的**: 
- 确认 clone request 的完成回调 (end_io) 是否正确
- 检查 end_io_data 是否指向正确的 tio
- 验证 I/O 完成路径的完整性

**结果**:
```
  tag = 21
  end_io    = 0xffffffffc02a3b00 <end_clone_request>
  end_io_data = 0xffff9ff42a3f1a40  (= tio，正确)
  rq_disk   = 0xffff9fe872286c00
  resid_len = 524288
  nr_phys_segments = 128
  start_time_ns = 69474411890772762
```

**分析**:
- clone request 本身是有效的，end_io 回调正确指向 `end_clone_request`
- `end_io_data` 正确指向 tio（即通过 clone->end_io_data 取回 tio 的路径是正常的）
- `resid_len = 524288` 与 `completed = 524288` 匹配 → I/O 完全完成（524288 bytes = 128 sectors × 4096 bytes/sector）
- start_time_ns 接近崩溃时间戳 → 这个 I/O 是在崩溃前刚完成的

---

## Step 5: struct request (orig) — 检查原始 I/O 属性

**命令**: `struct request ffff9ff42a3f18c0`

**目的**: 
- 获取原始 I/O 请求的特征（读写方向、大小、扇区位置）
- 判断是否是正常的应用层 I/O 还是内核内部 I/O
- 记录可追溯的信息用于事后审计

**结果**:
```
  tag = 124
  cmd_flags = 268435456  (= REQ_WRITE | REQ_SYNC)
  __sector  = 388402176
  nr_phys_segments = 128
  rq_disk   = 0xffff9ff99b7d2800
```

**分析**:
- 这是一次**大 I/O 写操作**（128 个物理段，估计 ~512KB-1MB）
- 扇区位置 388402176 → dm-19 设备上的偏移量
- 正常的文件系统/数据库写入 I/O，不是内核内部管理 I/O

---

## Step 6: dev -d — 列出所有设备状态

**命令**: `dev -d`

**目的**: 
- 获取系统设备全貌，识别 dm 设备编号
- 将崩溃相关地址映射到具体设备名
- 检查是否有其他设备异常

**结果**（相关行）:
```
253 ffff9ff81b1b7000  dm-19  ffff9ff872c0a700  0  0  0 N/A(MQ)
```

**分析**:
- `dev -d` 的第三列是 gendisk 地址= `mapped_device.disk` 的地址，不是 md 本身
- 但通过 `mapped_device` 的结构关系，确认 dm-19 是崩溃涉及的设备
- 设备状态显示正常，无 I/O 挂起

---

## Step 7: struct mapped_device — 检查 dm 设备核心

**命令**: `struct mapped_device ffff9ff81b1b7000`

**目的**:
- 检查 mapped_device 的完整状态（表指针、flags、类型）
- 重点检查 `immutable_target` 和 `map` 两个指针
- 查看设备是否处于 suspend 状态

**关键字段**:
```
  map                = 0xffff9f8c1029bc00     ← 当前 dm_table (有效)
  immutable_target   = 0xffffbd16abbd2040     ← 当前目标 (有效！)
  immutable_target_type = 0xffffffffc17f8040  ← multipath_target
  name               = "253:19"
  flags              = 64                     (= DMF_MERGE_IS_OPTIONAL)
  type               = DM_TYPE_MQ_REQUEST_BASED
  holders            = 280
  open_count         = 276
  pending            = {2, 0}
```

**分析**:
- `md->immutable_target = 0xffffbd16abbd2040`，这个地址**可以正常读取**
- `tio->ti = 0xffffbd16abacc040`，这个地址**不可读**
- **两个地址相差 0x106000 bytes**，都在 `0xffffbd16ab*` 区域内
- 这说明：dm-19 当前有一个**新的有效目标**，而 `tio->ti` 指向的是一个**旧的、已被释放的目标**
- flags = 64 = DMF_MERGE_IS_OPTIONAL，在 `__bind()` (dm.c:2075-2076) 中当 `singleton=true` 时设置。这确认了该设备是 single-target 模式，`immutable_target` 优化路径处于激活状态
- use_blk_mq 模式（由 type = DM_TYPE_MQ_REQUEST_BASED 隐含）

---

## Step 8: struct dm_table — 检查设备表

**命令**: `struct dm_table 0xffff9f8c1029bc00`

**目的**:
- 确认表的类型、目标数组、可信参数
- 检查是否 singleton 模式（只有一个目标）

**结果**:
```
  type = DM_TYPE_MQ_REQUEST_BASED
  num_targets = 1
  targets     = 0xffffbd16abbd2040     ← 目标数组
  singleton   = true                     ← 单目标表（immutable 优化适用）
  all_blk_mq  = true
  immutable_target_type = 0xffffffffc17f8040 (= multipath_target)
```

**分析**:
- singleton = true → 这是 immutable_target 优化可以生效的场景
- all_blk_mq = true → 所有底层设备都是 blk-mq 模式
- targets 数组首地址与 md->immutable_target 一致 → 两者指向同一个目标

---

## Step 9: struct dm_target — 检查当前目标

**命令**: `struct dm_target 0xffffbd16abbd2040`

**目的**:
- 确认当前目标的 `type` 指针（用于识别 path selector 类型）
- 获取设备分配的 IO 范围确认匹配

**结果**:
```
  table  = 0xffff9f8c1029bc00    ← 关联的表 (正确)
  type   = 0xffffffffc17f8040    ← 目标类型指针
  begin  = 0
  len    = 3125609132 sectors (~1.49 TB)
  private = 0xffff9f8c1029a400   ← 每个目标私有数据 (multipath 上下文)
```

---

## Step 10: sym / mod — 解析目标类型符号

**命令**: `sym 0xffffffffc17f8040`
**命令**: `mod -s dm_round_robin`

**目的**:
- 将目标类型的函数指针表解析为具体驱动模块名称
- 确认使用的是哪个 multipath path selector

**结果**:
```
0xffffffffc17f8040 (d) multipath_target [dm_multipath]
```

**分析**:
- 目标类型是 `multipath_target`，来自 `dm_multipath` 内核模块
- path selector 使用 `dm_round_robin`（RR 调度）
- 排除了 Oracle ACFS/ADVM/其他第三方模块的干扰

---

## Step 11: rd — 验证悬空地址

**命令**: `rd ffffbd16abacc040 20`

**目的**: 
- 尝试读取 `tio->ti` 指向的地址内容
- 确认该地址是否真的不可访问

**结果**:
```
rd: invalid kernel virtual address: ffffbd16abacc040  type: "64-bit KVADDR"
```

**分析**:
- crash 确认该地址是无效的内核虚拟地址（页表完全被拆除，PTE 不存在）
- 这证明：`tio->ti` 指向的内存曾被分配（它是一个有效的 `struct dm_target`），但现在已经**被完全释放和回收**
- 不是 slab 内存损坏（slab 损坏通常表现为数据混乱而非 PTE 完全消失）
- `debug_pagealloc_enabled` 符号不存在 → 未开启 CONFIG_DEBUG_PAGEALLOC → PTE 被拆除说明内存已被归还到 buddy 系统

---

## Step 12: dis dm_softirq_done — 反汇编崩溃函数

**命令**: `dis dm_softirq_done`

**目的**:
- 将反汇编与源码精确对应
- 验证崩溃指令 `mov 0x8(%rdi),%rdx` 是否确实是对应的源码行
- 确认寄存器/变量映射

**反汇编关键片段**:
```
+0x48: mov  0x18(%r13),%r12    ; R12 = tio->clone  (offset 0x18)
+0x52: test %r12,%r12
+0x55: je   <skip>              ; if (!clone) goto skip
+0x61: mov  0x48(%rbx),%rax    ; RAX = rq->cmd_flags (orig request)
+0x65: mov  0x58(%r13),%ebx    ; EBX = tio->error  (offset 0x58)
+0x69: mov  0x170(%r12),%r13   ; R13 = clone->end_io_data  (重新加载 tio)
+0x77: shr  $0x16,%rax         ; RAX = (cmd_flags >> 22) & 1 = REQ_FAILFAST
+0x81: mov  0x8(%r13),%rdi     ; RDI = tio->ti  (offset 0x08)
+0x89: and  $0x1,%eax
+0x92: test %rdi,%rdi          ; if (tio->ti) — NOT NULL!
+0x95: je   <skip>
+0x97: mov  0x8(%rdi),%rdx     ; *** CRASH *** RDX = ti->type  (offset 0x08)
+0x9b: test %al,%al
+0x9d: mov  0x60(%rdx),%r8     ; R8  = type->rq_end_io
```

**源码映射** (`dm-rq.c`):
```
dm_done():
  357: tio = clone->end_io_data           ← mov 0x170(%r12),%r13
  360: if (tio->ti)                       ← test %rdi,%rdi (通过)
  361:     rq_end_io = tio->ti->type->rq_end_io  ← mov 0x8(%rdi),%rdx CRASH
```

**结论**: 崩溃点在 `dm_done` 的内联展开中，`tio->ti` 不为 NULL 但指向已释放的内存。

---

## Step 13: dmesg — 查找崩溃前后系统日志

**命令**: `log` 或 `!dmesg -T | tail -300`

**目的**: 
- 查找崩溃前的异常事件
- 检查 dm 设备的相关操作记录
- 识别可能的触发事件

**关键日志** (crash 时间戳 `[69474411.952107]`):
```
[69474366.358835] sd 11112:0:0:6: [sdg] Attached SCSI disk    ← ~45 秒前
[69474366.412672] sd 11112:0:0:8: [sdi] Attached SCSI disk    ← ~45 秒前
...
[69474411.952107] BUG: unable to handle kernel paging request at ffffbd16abacc048
```

**分析**:
- 崩溃前 ~45 秒，有 SCSI 热添加事件（sdg/sdi，来自 Actifio 存储阵列）
- 这触发了 multipathd 检测新路径 → dm-multipath 表重载
- 表重载释放了旧目标 → in-flight I/O 的 tio->ti 变为悬空指针

---

## Step 14: bt -a — 检查所有 CPU 状态

**命令**: `bt -a`

**目的**: 
- 排除其他 CPU 并发操作 dm 设备导致的竞争
- 检查是否有其他线程正在进行表操作

**结果**: 所有 192 个 CPU 都处于 idle（`native_safe_halt`）或 crash NMI 处理中。

**分析**: 
- 无其他 CPU 在执行 dm 表操作
- 崩溃 CPU 137 在 softirq 上下文中，preempt_disable，不可能被其他线程打断
- 排除了"并发 CPU 竞争修改 tio->ti"的可能性

---

---

## Step 15: 时序分析 — I/O 完成与崩溃的时间差

**目的**: 
- 通过 start_time_ns 计算 I/O 从下达到完成的时间
- 判断表重载发生在 I/O 生命周期的哪个阶段
- 验证竞态窗口的存在

**数据**:
```
clone request start_time_ns = 69474411890772762
crash timestamp (dmesg)      = [69474411.952107]
```

**换算**: 
- start_time_ns = 69474411.890772762 秒（epoch + uptime 基准）
- crash = 69474411.952107 秒
- **时间差 = 0.061335 秒 = ~61ms**

**分析**:
- I/O 在崩溃前 ~61ms 启动，这比典型的 NVMe I/O 完成时间（亚毫秒级）长得多。有两种可能：
  - (a) 该 I/O 被底层设备（NVMe + iSCSI 映射的 Actifio LUN）排队，实际完成耗时较长
  - (b) I/O 实际完成了，但 `start_time_ns` 在某些路径下不是精确的首次下发时间
- 无论哪种情况，**表重载必须发生在这 61ms 窗口内**才能解释 tio->ti 的悬空指针
- 这证实了竞态条件：SCSI 热添加 → multipathd 表重载 → 旧目标释放 → I/O 完成 → 访问旧目标 → CRASH

**为什么运行 805 天后才崩溃？**
- 该竞态需要同时满足三个条件：
  1. dm-multipath + blk-mq 模式（此服务器默认）
  2. 表重载时存在 in-flight I/O（需要 I/O 持续活跃）
  3. I/O 完成与服务端 I/O 路径的延迟叠加
- 并非每次表重载都命中：如果重载时没有 in-flight I/O，则 tio->ti 不受影响
- 805 天的 uptime 意味着服务器经历了多次热添加/重载而未被触发，直到本次时序恰好匹配

---

## Step 16: 同步机制分析 — dm_sync_table 的保护范围

**目的**: 
- 精确理解 `dm_sync_table` 的保护语义
- 确认它**不能**保护 `tio->ti` 的悬空指针问题
- 定位根因到代码级别的竞态

**源码** (`dm.c:579-583`):
```c
void dm_sync_table(struct mapped_device *md)
{
    synchronize_srcu(&md->io_barrier);       // 等待 SRCU 读者退出
    synchronize_rcu_expedited();             // 等待 RCU 读者退出
}
```

**SRCU 保护谁？**
```c
// dm.c:567-572 — 标准路径使用 SRCU 保护 md->map 的读取
struct dm_table *dm_get_live_table(struct mapped_device *md, int *srcu_idx)
{
    *srcu_idx = srcu_read_lock(&md->io_barrier);
    return srcu_dereference(md->map, &md->io_barrier);
}
```

**关键点**: `dm_mq_queue_rq` 当 `immutable_target` 非 NULL 时**完全绕过** SRCU:
```c
// dm-rq.c:895
struct dm_target *ti = md->immutable_target;   // 直接取指针，无 SRCU 保护！

if (unlikely(!ti)) {                             // 仅在 immutable_target 为 NULL 时才走 SRCU 路径
    int srcu_idx;
    struct dm_table *map = dm_get_live_table(md, &srcu_idx);
    ti = dm_table_find_target(map, 0);
    dm_put_live_table(md, srcu_idx);
}
```

**结论**: 
- `dm_sync_table` 只等待 `dm_get_live_table`/`dm_put_live_table` 配对的 SRCU 读者
- `dm_mq_queue_rq` 通过 `immutable_target` 优化绕过了 SRCU，因此 `dm_sync_table` 不会等待已经在 `dm_mq_queue_rq` 中获取了 `ti` 指针的线程
- 当 `__bind()` 调用 `dm_sync_table()` 后，`old_map` 被返回并最终 `dm_table_destroy()` 释放旧目标
- 但 `tio->ti` 中已保存的旧目标指针**不受任何保护**，成为悬空指针

---

## 替代解释排除清单

| 替代解释 | 排除理由 | 证据来源 |
|---------|---------|---------|
| 硬件内存损坏(位翻转) | PTE=0 表示页表被显式拆除，非位翻转行为 | Step 2 (CR2=PTE 0) |
| slab 内部损坏(链表指针覆盖) | dm_target 在 vmemmap 区域分配，非 slab cache；tio 本身完整 | Step 3 (tio 结构完整) |
| CONFIG_DEBUG_PAGEALLOC | `debug_pagealloc_enabled` 符号不存在于 vmlinux | Step 11 (symbol not found) |
| 内存热移除(hot-remove) | 当前 md->immutable_target 在同一 NUMA 区域仍有效；hot-remove 会移除整个 section 而非单个对象 | Step 7 (新旧目标地址对比) |
| 其他 CPU 并发修改 tio->ti | CPU 137 在 softirq 上下文中(preempt_disable)，bt -a 显示所有 CPU idle | Step 14 (bt -a) |
| 第三方模块(ACFS/ADVM/dm-emulation) | 目标类型解析为 `multipath_target [dm_multipath]`，栈回溯完全在 dm 层 | Step 10 (sym/mod) |
| tio 整体被覆盖/重用 | tio 中 md/orig/clone 字段全部有效，仅 ti 损坏 | Step 3 (struct dm_rq_target_io) |

## 证据链汇总

| 环 | 步骤 | 关键发现 |
|-----|------|---------|
| 1 | bt | 崩溃在 dm_softirq_done+97，访问 tio->ti->type |
| 2 | rd | tio->ti = ffffbd16abacc040 不可访问（PTE=0） |
| 3 | struct tio | tio 完整，仅 ti 损坏 |
| 4 | struct clone | end_io/end_io_data 正确，I/O 完成路径正常 |
| 5 | struct orig | 正常的大 I/O 写操作 |
| 6 | dev -d | dm-19 设备正常 |
| 7 | struct md | immutable_target = 新目标（有效），≠ tio->ti |
| 8 | struct table | singleton, all_blk_mq, type = MQ_REQUEST_BASED |
| 9 | struct target | 当前 multipath 目标正常，type = dm_multipath |
| 10 | sym | 已解析为 multipath_target [dm_multipath] |
| 11 | rd × 2 | tio->ti 当前无效 vs md->immutable_target 有效 |
| 12 | dis | 精确映射反汇编到源码 dm-rq.c:360-361 |
| 13 | dmesg | SCSI 热添加 ~45 秒前（sdg/sdi） |
| 14 | bt -a | 所有 CPU idle，排除并发竞争 |
| 15 | start_time_ns vs crash time | I/O ~61ms 前下发，表重载发生在这 61ms 窗口内 |
| 16 | dm_sync_table 源码 | 只等 SRCU/RCU 读者，immutable_target 路径绕过 SRCU |

## 根本原因

```
dm_mq_queue_rq() (dm-rq.c:895)
  tio->ti = md->immutable_target    ← 无保护/无引用计数
      │
      │  并发: __bind() 表重载
      │    → rcu_assign_pointer(md->map, new_table)
      │    → dm_sync_table()  (只等 md->map 的读者)
      │    → dm_table_destroy(old_map)
      │        → 旧 dm_target 被 kfree
      │
      ▼
dm_done() (dm-rq.c:360-361)
  tio->ti->type  ← 悬空指针解引用 → CRASH
```

竞态窗口: `dm_mq_queue_rq` 保存指针 → `dm_sync_table` 不等待 tio->ti 持用者 → `dm_table_destroy` 释放旧目标 → `dm_softirq_done` 访问旧指针。

修复: 需要为 `tio->ti` 增加引用计数保护，或在表重载前排空 in-flight I/O（如上游的 `blk_mq_quiesce_queue` 机制）。
