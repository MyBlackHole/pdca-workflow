# Evidence — T0143 vmcore-deep

## 1. 崩溃线程上下文

- **CPU**: 137 of 192
- **TASK**: swapper/137 (idle)
- **CR2**: `ffffbd16abacc048` (PTE=0, unmapped)
- **CRASH**: `BUG: unable to handle kernel paging request`

## 2. 寄存器状态（崩溃时刻）

| 寄存器 | 值 | 含义 |
|--------|------|------|
| R12 | `ffff9ff862cf9600` | clone request |
| R13 | `ffff9ff42a3f1a40` | `struct dm_rq_target_io` (tio) |
| RDI | `ffffbd16abacc040` | `tio->ti` (STALE!) |
| RBX | 0 | 已被 `tio->error` 覆盖 |

## 3. 栈回溯

```
<IRQ>
dm_softirq_done+0x61  ← crash at dm-rq.c:361
blk_done_softirq+0x96
__do_softirq+0xf5
call_softirq+0x1c
do_softirq+0x65
irq_exit+0x115
smp_call_function_single_interrupt+0x39
call_function_single_interrupt+0x172
<EOI>
native_safe_halt  (idle loop)
```

## 4. 代码定位

**dm_softirq_done 反汇编** (crash at +0x61):

```
0xe1 <+81>:  mov 0x8(%r13),%rdi   ; R13 = tio, R13+0x08 = ti → RDI = tio->ti = ffffbd16abacc040
0xe5 <+85>:  xor $0x1,%rax
0xe9 <+89>:  and $0x1,%eax
0xec <+92>:  test %rdi,%rdi        ; if (tio->ti) — not null!
0xef <+95>:  je <skip>
0xf1 <+97>:  mov 0x8(%rdi),%rdx   ; *** CRASH *** RDI+8 = ti->type → ffffbd16abacc048 (unmapped)
```

源文件: `dm-rq.c:360-361`
```c
if (tio->ti) {                              // line 360: tio->ti NOT null
    rq_end_io = tio->ti->type->rq_end_io;   // line 361: ** BOOM **
```

## 5. dm_rq_target_io (tio) 结构

- `ti` = `0xffffbd16abacc040` ← **悬空指针（失效）**
- `md` = `0xffff9ff81b1b7000` ← 有效 mapped_device
- `orig` = `0xffff9ff42a3f18c0` ← 有效原始请求
- `clone` = `0xffff9ff862cf9600` ← 有效克隆请求
- `error` = 0
- `completed` = 524288

## 6. mapped_device (dm-19)

- `name[16]` = `253:19` (dm-19)
- `map` (RCU) = `0xffff9f8c1029bc00` ← 有效 dm_table
- `immutable_target` = `0xffffbd16abbd2040` ← **当前有效目标**
- `immutable_target_type` = `multipath_target [dm_multipath]`
- `use_blk_mq` = true
- `tag_set` = valid (blk-mq)

## 7. dm_table

- `type` = `DM_TYPE_MQ_REQUEST_BASED`
- `num_targets` = 1
- `targets` = `0xffffbd16abbd2040` ← **当前目标数组**
- `singleton` = true
- `all_blk_mq` = true
- `immutable_target_type` = `0xffffffffc17f8040` = `multipath_target [dm_multipath]`

## 8. dm_target（当前有效）

- `table` = `0xffff9f8c1029bc00` (matching dm_table)
- `type` = `0xffffffffc17f8040` = `multipath_target [dm_multipath]`
- `begin` = 0
- `len` = 3125609132 sectors (~1.49 TB)
- `private` = `0xffff9f8c1029a400` (per-target private data)

## 9. 原请求 (orig)

- `tag` = 124
- `cmd_flags` = 268435456 (= REQ_WRITE | REQ_SYNC)
- `__sector` = 388402176
- `nr_phys_segments` = 128（大 I/O）
- `ioprio` = 0
- `rq_disk` = `0xffff9ff99b7d2800`

## 10. 克隆请求 (clone)

- `tag` = 21
- `end_io` = `end_clone_request`
- `end_io_data` = `0xffff9ff42a3f1a40` (= tio, back-pointer)
- `rq_disk` = `0xffff9fe872286c00`

## 11. crash 前系统日志——SCSI 热添加

~45 秒前 SCSI 磁盘被热添加（同一 Actifio 存储阵列）：

```
[69474366.358835] sd 11112:0:0:6: [sdg] Attached SCSI disk
[69474366.412672] sd 11112:0:0:8: [sdi] Attached SCSI disk
...
[69474411.952107] BUG: unable to handle kernel paging request at ffffbd16abacc048
```

## 12. 关键地址比较

| 地址 | 含义 | 状态 |
|------|------|------|
| `ffffbd16abbd2040` | 当前有效 dm_target | ✅ 可访问 |
| `ffffbd16abacc040` | tio->ti (被引用) | ❌ 未映射 |
| 偏移 | 0x106000 (1,073,728 bytes) | — |

同一 `0xffffbd16ab` 内存区域，但 tio->ti 指向的地址已被释放/回收。

## 13. 内核同步机制分析

**`_bind()` table swap 代码路径 (`dm.c:2027-2082`)：**

1. `rcu_assign_pointer(md->map, t)` ← 原子切换 table
2. `md->immutable_target_type = ...` ← 更新 immutable 目标类型
3. `dm_sync_table(md)`: `synchronize_srcu()` + `synchronize_rcu_expedited()`
4. 返回 old_map → 随后 `dm_table_destroy(old_map)` 释放旧目标

**`dm_mq_queue_rq` (I/O 提交 `dm-rq.c:889-927`)：**

```c
struct dm_target *ti = md->immutable_target;   // 无保护地获取
...
tio->ti = ti;                                   // 保存指针
```

**`dm_done` (I/O 完成 `dm-rq.c:354`)：**

```c
if (tio->ti) {                                  // 使用保存的指针（无保护）
    rq_end_io = tio->ti->type->rq_end_io;      // ← 悬空指针解引用
```

## 14. 根本原因链

```
┌────────────────────────────────────────────────────────┐
│  SCSI 热添加 (新 Actifio LUN 出现)                      │
│  → multipathd 检测到新路径                              │
│    → dmsetup reload + resume (dm 表重载)               │
│      → dm_swap_table() → __bind()                     │
│        → synchronize_srcu + synchronize_rcu            │
│        → dm_table_destroy(old_map) 释放旧目标           │
│                                                        │
│  ┌── 同时 ──────────────────────────────────────┐      │
│  │ dm_mq_queue_rq: tio->ti = md->immutable_target│     │
│  │                                                   │  │
│  │ I/O 提交后，tio 仍指向旧目标                      │  │
│  │ md->immutable_target 已指向新目标                  │  │
│  │ (但 tio->ti 是复制值，不会自动更新)              │  │
│  └───────────────────────────────────────────────┘      │
│                                                        │
│  I/O 完成 → dm_softirq_done → dm_done                  │
│    → tio->ti->type  (tio->ti = 已释放的旧目标)        │
│      → **CRASH**   (use-after-free)                    │
└────────────────────────────────────────────────────────┘
```
