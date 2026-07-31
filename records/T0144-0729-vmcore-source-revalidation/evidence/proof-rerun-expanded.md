# T0144 crash 根因证明复跑步骤

本文件在复跑前创建。每一步的命令、目的和预期信号预先固定，执行后再追加实际输出解释。

## 会话输入

```text
tmux pane: 0:0.0
vmlinux: /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
vmcore: /nbudata/vmcore/vmcore
```

## P0：确认 pane 位于 shell

- 目的：保证本次从新 crash 进程开始，不复用上一次 `crash>`。
- 操作：控制端 `tmux capture-pane -p -S -20 -t 0:0.0`。
- 预期：末行是 `root@nbusvr103` shell prompt。

## P1：启动独立 crash 会话

- 目的：重新加载用户指定的 vmlinux/vmcore，确认 release 和 panic 摘要。
- 操作：

```text
crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore

      KERNEL: /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
    DUMPFILE: /nbudata/vmcore/vmcore  [PARTIAL DUMP]
        CPUS: 192
        DATE: Thu Jul 23 10:01:20 2026
      UPTIME: 805 days, 22:41:50
LOAD AVERAGE: 12.35, 11.25, 11.23
       TASKS: 5243
    NODENAME: shqddb2
     RELEASE: 3.10.0-1160.83.1.el7.x86_64
     VERSION: #1 SMP Mon Dec 19 10:44:06 UTC 2022
     MACHINE: x86_64  (2300 Mhz)
      MEMORY: 1023.7 GB
       PANIC: "BUG: unable to handle kernel paging request at ffffbd16abacc048"
         PID: 0
     COMMAND: "swapper/137"
        TASK: ffff9f80a4830000  (1 of 192)  [THREAD_INFO: ffff9f80a482c000]
         CPU: 137
       STATE: TASK_RUNNING (PANIC)
```

- 预期：进入 `crash>`；release 为 `3.10.0-1160.83.1.el7.x86_64`。

## P2：固定系统摘要和异常调用栈

- 目的：证明 panic 地址、CPU/task、RIP、寄存器和完成 softirq 调用链。
- crash 命令：

```text
sys
      KERNEL: /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
    DUMPFILE: /nbudata/vmcore/vmcore  [PARTIAL DUMP]
        CPUS: 192
        DATE: Thu Jul 23 10:01:20 2026
      UPTIME: 805 days, 22:41:50
LOAD AVERAGE: 12.35, 11.25, 11.23
       TASKS: 5243
    NODENAME: shqddb2
     RELEASE: 3.10.0-1160.83.1.el7.x86_64
     VERSION: #1 SMP Mon Dec 19 10:44:06 UTC 2022
     MACHINE: x86_64  (2300 Mhz)
      MEMORY: 1023.7 GB
       PANIC: "BUG: unable to handle kernel paging request at ffffbd16abacc048"

bt
PID: 0      TASK: ffff9f80a4830000  CPU: 137  COMMAND: "swapper/137"
 #0 [ffffa0797e643b40] machine_kexec at ffffffff83269514
 #1 [ffffa0797e643ba0] __crash_kexec at ffffffff83329d72
 #2 [ffffa0797e643c70] crash_kexec at ffffffff83329e68
 #3 [ffffa0797e643c88] oops_end at ffffffff839bc818
 #4 [ffffa0797e643cb0] no_context at ffffffff8327974c
 #5 [ffffa0797e643d00] __bad_area_nosemaphore at ffffffff83279a2a
 #6 [ffffa0797e643d50] bad_area_nosemaphore at ffffffff83279b54
 #7 [ffffa0797e643d60] __do_page_fault at ffffffff839bf8d0
 #8 [ffffa0797e643dd0] do_page_fault at ffffffff839bfb05
 #9 [ffffa0797e643e00] page_fault at ffffffff839bb7b8
    [exception RIP: dm_softirq_done+97]
    RIP: ffffffffc02a48f1  RSP: ffffa0797e643eb0  RFLAGS: 00010282
    RAX: 0000000000000001  RBX: 0000000000000000  RCX: dead000000000200
    RDX: ffffa0797e643ee8  RSI: ffffa0797e658480  RDI: ffffbd16abacc040
    RBP: ffffa0797e643ed8   R8: ffff9ff42a3f1940   R9: 0000000000000001
    R10: 0000000000000035  R11: ffffe8d5b248cb00  R12: ffff9ff862cf9600
    R13: ffff9ff42a3f1a40  R14: ffff9f80a482c000  R15: 0000000000000001
    ORIG_RAX: ffffffffffffffff  CS: 0010  SS: 0018
#10 [ffffa0797e643ee0] blk_done_softirq at ffffffff83572386
#11 [ffffa0797e643f20] __do_softirq at ffffffff832a9585
#12 [ffffa0797e643f90] call_softirq at ffffffff839c8aac
#13 [ffffa0797e643fa8] do_softirq at ffffffff83230825
#14 [ffffa0797e643fc8] irq_exit at ffffffff832a9935
#15 [ffffa0797e643fe0] smp_call_function_single_interrupt at ffffffff8325c4e9
#16 [ffffa0797e643ff0] call_function_single_interrupt at ffffffff839c7772
--- <IRQ stack> ---
#17 [ffff9f80a482fdf8] call_function_single_interrupt at ffffffff839c7772
    [exception RIP: native_safe_halt+11]
    RIP: ffffffff839b9e1b  RSP: ffff9f80a482fea8  RFLAGS: 000002c6
    RAX: ffffffff839b9bc0  RBX: 00f7637e2fd43ec0  RCX: 0100000000000000
    RDX: 0000000000000000  RSI: 0000000000000000  RDI: 0000000000000046
    RBP: ffff9f80a482fea8   R8: 0000000000000000   R9: 0000000000000001
    R10: 0000000000006e1c  R11: 7fffffffffffffff  R12: 00f7637e2fd43ec0
    R13: 0000000000000089  R14: 00f7637d9658dd00  R15: e16d589bd8d40527
    ORIG_RAX: ffffffffffffff04  CS: 0010  SS: 0018
#18 [ffff9f80a482feb0] default_idle at ffffffff839b9bde
#19 [ffff9f80a482fed0] arch_cpu_idle at ffffffff83239570
#20 [ffff9f80a482fee0] cpu_startup_entry at ffffffff833080fa
#21 [ffff9f80a482ff28] start_secondary at ffffffff8325d3a7
#22 [ffff9f80a482ff50] start_cpu at ffffffff832000d5

```

- 预期：CR2/fault address 为 `ffffbd16abacc048`，RIP 为 `dm_softirq_done+97`，RDI 为 `ffffbd16abacc040`，栈含 `blk_done_softirq`。

## P3：反汇编 fault 指令

- 目的：证明 fault 指令访问 `RDI+8`，并证明 RDI 从 `tio+8` 读取。
- crash 命令：

```text
dis dm_softirq_done

0xffffffffc02a48dd <dm_softirq_done+77>:	shr    $0x16,%rax
0xffffffffc02a48e1 <dm_softirq_done+81>:	mov    0x8(%r13),%rdi
0xffffffffc02a48e5 <dm_softirq_done+85>:	xor    $0x1,%rax
0xffffffffc02a48e9 <dm_softirq_done+89>:	and    $0x1,%eax
0xffffffffc02a48ec <dm_softirq_done+92>:	test   %rdi,%rdi
0xffffffffc02a48ef <dm_softirq_done+95>:	je     0xffffffffc02a48fd <dm_softirq_done+109>
0xffffffffc02a48f1 <dm_softirq_done+97>:	mov    0x8(%rdi),%rdx
0xffffffffc02a48f5 <dm_softirq_done+101>:	test   %al,%al
0xffffffffc02a48f7 <dm_softirq_done+103>:	mov    0x60(%rdx),%r8
0xffffffffc02a48fb <dm_softirq_done+107>:	jne    0xffffffffc02a4940 <dm_softirq_done+176>

```


- 预期：`+81 mov 0x8(%r13),%rdi`；`+97 mov 0x8(%rdi),%rdx`。

## P4：加载 dm_mod DWARF 并还原 tio

- 目的：证明 `R13+8` 是 `dm_rq_target_io.ti`，并核对 md/clone/error。
- crash 命令：

```text
mod -s dm_mod
     MODULE       NAME                             SIZE  OBJECT FILE
ffffffffc02ab860  dm_mod                         128595  /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/kernel/drivers/md/dm-mod.ko.debug

struct -o dm_rq_target_io

struct dm_rq_target_io {
    [0] struct mapped_device *md;
    [8] struct dm_target *ti;
   [16] struct request *orig;
   [24] struct request *clone;
   [32] struct kthread_work work;
   [88] int error;
   [96] union map_info info;
  [104] struct dm_stats_aux stats_aux;
  [120] unsigned long duration_jiffies;
  [128] unsigned int n_sectors;
  [132] unsigned int completed;
}


struct dm_rq_target_io ffff9ff42a3f1a40

struct dm_rq_target_io {
  md = 0xffff9ff81b1b7000,
  ti = 0xffffbd16abacc040,
  orig = 0xffff9ff42a3f18c0,
  clone = 0xffff9ff862cf9600,
  work = {
    node = {
      next = 0x0,
      prev = 0x0
    },
    func = 0x0,
    done = {
      lock = {
        {
          rlock = {
            raw_lock = {
              val = {
                counter = 0
              }
            }
          }
        }
      },
      task_list = {
        next = 0x0,
        prev = 0x0
      }
    },
    worker = 0x0
  },
  error = 0,
  info = {
    ptr = 0xffff9ff42a3f1ac8
  },
  stats_aux = {
    merged = false,
    duration_ns = 0
  },
  duration_jiffies = 0,
  n_sectors = 0,
  completed = 524288
}

```

- 预期：`ti@8`；`ti=ffffbd16abacc040`；`clone=ffff9ff862cf9600`。

## P5：验证旧 ti 的页表状态

- 目的：区分 partial dump 漏页与运行时 PTE 已清零。
- crash 命令：

```text
rd ffffbd16abacc040 4
rd: invalid kernel virtual address: ffffbd16abacc040  type: "64-bit KVADDR"

vtop ffffbd16abacc040
VIRTUAL           PHYSICAL
ffffbd16abacc040  (not mapped)

PGD DIRECTORY: ffffffff83e10000
PAGE DIRECTORY: 2ffe01067
   PUD: 2ffe012d0 => fc3ec6e067
   PMD: fc3ec6eae8 => 27b845e067
   PTE: 27b845e660 => 0

```

- 预期：`invalid kernel virtual address`、`not mapped`、`PTE 0`。

## P6：证明同一 md 当前已换成新 multipath target

- 目的：对比请求保存的旧 ti 与当前有效 target/map。
- crash 命令：

```text
struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name ffff9ff81b1b7000

map = 0xffff9f8c1029bc00
immutable_target = 0xffffbd16abbd2040
immutable_target_type = 0xffffffffc17f8040
use_blk_mq = true
name = "253:19\000\000\000\000\000\000\000\000\000"

sym ffffffffc17f8040
ffffffffc17f8040 (d) multipath_target [dm_multipath]

struct dm_target.table,type,begin,len,private ffffbd16abbd2040

table = 0xffff9f8c1029bc00
type = 0xffffffffc17f8040
begin = 0
len = 3125609132
private = 0xffff9f8c1029a400


struct dm_table.highs,targets,num_allocated,num_targets,type ffff9f8c1029bc00

highs = 0xffffbd16abbd2000
targets = 0xffffbd16abbd2040
num_allocated = 8
num_targets = 1
type = DM_TYPE_MQ_REQUEST_BASED
```

- 预期：设备 `253:19`、当前 target `ffffbd16abbd2040`、multipath、highs `ffffbd16abbd2000`、targets 为 highs+0x40。

## P7：验证 orig/clone 请求和底层磁盘

- 目的：证明 faulting orig 属于 dm-19，clone 属于 NVMe，不是 iSCSI sd path。
- crash 命令：

```text
struct request.q,rq_disk,tag,start_time_ns,end_io,end_io_data,errors ffff9ff42a3f18c0
q = 0xffff9ff872c0a700
rq_disk = 0xffff9ff99b7d2800
tag = 124
start_time_ns = 69474411890753356
end_io = 0x0
end_io_data = 0x0
errors = 0

struct request.q,rq_disk,tag,start_time_ns,end_io,end_io_data,errors ffff9ff862cf9600
q = 0xffff9fed57ab09c0
rq_disk = 0xffff9fe872286c00
tag = 21
start_time_ns = 69474411890772762
end_io = 0xffffffffc02a3b00 <end_clone_request>
end_io_data = 0xffff9ff42a3f1a40
errors = 0


struct gendisk.disk_name,major,first_minor ffff9ff99b7d2800
struct gendisk.disk_name,major,first_minor ffff9fe872286c00
```

- 预期：orig=`dm-19`；clone=`nvme38n1`；clone end_io_data 回指 tio。

## P8：验证 dm-19 的全部 multipath path

- 目的：证明当前 map 两条 path 都是 NVMe，审查 iSCSI 对象同一性。
- crash 命令：

```text
mod -s dm_multipath

ffffffffc17f81e0  dm_multipath                    27792  /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/kernel/drivers/md/dm-multipath.ko.debug

struct multipath.ti,nr_priority_groups,priority_groups,current_pgpath,current_pg,nr_valid_paths,flags ffff9f8c1029a400
ti = 0xffffbd16abbd2040
nr_priority_groups = 1
priority_groups = {
  next = 0xffff9fe80adffcc0,
  prev = 0xffff9fe80adffcc0
}
current_pgpath = 0xffff9ff7591decc0
current_pg = 0xffff9fe80adffcc0
nr_valid_paths = {
  counter = 2
}
flags = 0

struct dm_dev ffff9fdda4d0e7d8
struct dm_dev {
  bdev = 0xffff9ff83fbab0c0,
  dax_dev = 0x0,
  mode = 3,
  name = "259:54\000\000\000\000\000\000E\005\366", <incomplete sequence \372>
}

struct dm_dev ffff9fdda4d0e758
struct dm_dev {
  bdev = 0xffff9ff83fbabdc0,
  dax_dev = 0x0,
  mode = 3,
  name = "259:55\000\000\000\000\000\000E\005\366", <incomplete sequence \372>
}

struct block_device.bd_disk ffff9ff83fbab0c0

bd_disk = 0xffff9fe872280c00

struct block_device.bd_disk ffff9ff83fbabdc0
bd_disk = 0xffff9fe872286c00

struct gendisk.disk_name,major,first_minor ffff9fe872280c00

disk_name = "nvme37n1\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
major = 259
first_minor = 54

struct gendisk.disk_name,major,first_minor ffff9fe872286c00

disk_name = "nvme38n1\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
major = 259
first_minor = 55
```

- 预期：两条 dm_dev 为 `259:54/259:55`，对应 `nvme37n1/nvme38n1`。

## P9：固定时间线、当前状态和硬件错误反证

- 目的：取得 iSCSI 事件/panic 时间线、resume 后 md 状态，并筛查竞争性硬件错误解释。
- crash 命令：

```text
struct mapped_device.flags,pending,immutable_target,map ffff9ff81b1b7000

flags = 64
pending = {{
    counter = 2
  }, {
    counter = 0
  }},
immutable_target = 0xffffbd16abbd2040
map = 0xffff9f8c1029bc00
```

- 预期：iSCSI 事件早于 panic 约 45–76 秒；panic 时新 target 已生效且 pending 非零；无独立硬件错误记录。

