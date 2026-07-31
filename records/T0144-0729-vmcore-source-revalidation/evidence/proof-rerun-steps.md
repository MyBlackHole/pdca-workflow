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

## P1：启动第二个独立 crash 会话

- 目的：重新加载用户指定的 vmlinux/vmcore，确认 release 和 panic 摘要。
- 操作：

  ```text
  crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore
  ```

- 预期：进入 `crash>`；release 为 `3.10.0-1160.83.1.el7.x86_64`。

## P2：固定系统摘要和异常调用栈

- 目的：证明 panic 地址、CPU/task、RIP、寄存器和完成 softirq 调用链。
- crash 命令：

  ```text
  set scroll off
  sys
  bt
  ```

- 预期：CR2/fault address 为 `ffffbd16abacc048`，RIP 为 `dm_softirq_done+97`，RDI 为 `ffffbd16abacc040`，栈含 `blk_done_softirq`。

## P3：反汇编 fault 指令

- 目的：证明 fault 指令访问 `RDI+8`，并证明 RDI 从 `tio+8` 读取。
- crash 命令：`dis dm_softirq_done`
- 预期：`+81 mov 0x8(%r13),%rdi`；`+97 mov 0x8(%rdi),%rdx`。

## P4：加载 dm_mod DWARF 并还原 tio

- 目的：证明 `R13+8` 是 `dm_rq_target_io.ti`，并核对 md/clone/error。
- crash 命令：

  ```text
  mod -s dm_mod
  struct -o dm_rq_target_io
  struct dm_rq_target_io ffff9ff42a3f1a40
  ```

- 预期：`ti@8`；`ti=ffffbd16abacc040`；`clone=ffff9ff862cf9600`。

## P5：验证旧 ti 的页表状态

- 目的：区分 partial dump 漏页与运行时 PTE 已清零。
- crash 命令：

  ```text
  rd ffffbd16abacc040 4
  vtop ffffbd16abacc040
  ```

- 预期：`invalid kernel virtual address`、`not mapped`、`PTE 0`。

## P6：证明同一 md 当前已换成新 multipath target

- 目的：对比请求保存的旧 ti 与当前有效 target/map。
- crash 命令：

  ```text
  struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name ffff9ff81b1b7000
  sym ffffffffc17f8040
  struct dm_target.table,type,begin,len,private ffffbd16abbd2040
  struct dm_table.highs,targets,num_allocated,num_targets,type ffff9f8c1029bc00
  ```

- 预期：设备 `253:19`、当前 target `ffffbd16abbd2040`、multipath、highs `ffffbd16abbd2000`、targets 为 highs+0x40。

## P7：验证 orig/clone 请求和底层磁盘

- 目的：证明 faulting orig 属于 dm-19，clone 属于 NVMe，不是 iSCSI sd path。
- crash 命令：

  ```text
  struct request.q,rq_disk,tag,start_time_ns,end_io,end_io_data,errors ffff9ff42a3f18c0
  struct request.q,rq_disk,tag,start_time_ns,end_io,end_io_data,errors ffff9ff862cf9600
  struct gendisk.disk_name,major,first_minor ffff9ff99b7d2800
  struct gendisk.disk_name,major,first_minor ffff9fe872286c00
  ```

- 预期：orig=`dm-19`；clone=`nvme38n1`；clone end_io_data 回指 tio。

## P8：验证 dm-19 的全部 multipath path

- 目的：证明当前 map 两条 path 都是 NVMe，审查 iSCSI 对象同一性。
- crash 命令：

  ```text
  mod -s dm_multipath
  struct multipath.ti,nr_priority_groups,priority_groups,current_pgpath,current_pg,nr_valid_paths,flags ffff9f8c1029a400
  struct dm_dev ffff9fdda4d0e7d8
  struct dm_dev ffff9fdda4d0e758
  struct block_device.bd_disk ffff9ff83fbab0c0
  struct block_device.bd_disk ffff9ff83fbabdc0
  struct gendisk.disk_name,major,first_minor ffff9fe872280c00
  struct gendisk.disk_name,major,first_minor ffff9fe872286c00
  ```

- 预期：两条 dm_dev 为 `259:54/259:55`，对应 `nvme37n1/nvme38n1`。

## P9：固定时间线、当前状态和硬件错误反证

- 目的：取得 iSCSI 事件/panic 时间线、resume 后 md 状态，并筛查竞争性硬件错误解释。
- crash 命令：

  ```text
  log | grep -E 'scsi host11112|11112:0:0:|BUG: unable|dm_softirq_done'
  struct mapped_device.flags,pending,immutable_target,map ffff9ff81b1b7000
  log | grep -Ei 'mce|machine check|hardware error|memory failure|corrupt|Oops:'
  ```

- 预期：iSCSI 事件早于 panic 约 45–76 秒；panic 时新 target 已生效且 pending 非零；无独立硬件错误记录。

## P10：结束并校验 transcript

- 目的：形成明确会话边界，确保原始证据不混入后续操作。
- 操作：

  ```text
  echo __T0144_PROOF_RERUN_COMPLETE__
  quit
  echo __T0144_PROOF_RERUN_END__ <timestamp>
  ```

- 预期：返回 shell，关闭 pipe-pane，计算 transcript SHA-256。

## 复跑实际结果

| 步骤 | 实际结果 | 判定 |
|---|---|---|
| P0 | pane 位于 `[root@nbusvr103 kernel-rpm]#`；没有运行中的 crash | 通过 |
| P1 | 新进程于 `2026-07-29T14:39:15+08:00` 启动；指定 KERNEL/DUMPFILE、release 和 panic 摘要一致；重新出现 version inconsistency 警告并保留 | 通过，有已知证据限制 |
| P2 | CPU 137、`swapper/137`；RIP=`dm_softirq_done+97`；RDI=`ffffbd16abacc040`；R13=`ffff9ff42a3f1a40`；调用链含 `blk_done_softirq/__do_softirq` | 通过 |
| P3 | `+81 mov 0x8(%r13),%rdi`；faulting `+97 mov 0x8(%rdi),%rdx` | 通过 |
| P4 | dm_mod debug object 成功加载；`dm_rq_target_io.ti@8`；tio 中 ti、clone 分别与 RDI、R12 相等 | 通过 |
| P5 | `rd` 报 invalid KVADDR；`vtop` 显示 `(not mapped)` 和 `PTE ... => 0` | 通过，排除 partial dump 单纯漏页 |
| P6 | 同一 md 当前 target=`ffffbd16abbd2040`，类型 multipath；当前 highs=`ffffbd16abbd2000`、targets=`highs+0x40`；旧 ti 也为另一页 `+0x40` | 通过 |
| P7 | orig=`dm-19`，clone=`nvme38n1`；clone `end_io=end_clone_request`，`end_io_data` 回指 tio；partial dump 对无关页产生 `page excluded` 警告但目标字段均成功输出 | 通过，有非阻断警告 |
| P8 | 当前 multipath 有 2 条 valid path；`259:54/259:55` 映射到 `nvme37n1/nvme38n1` | 通过，直接 iSCSI path 排除 |
| P9 | iSCSI host/LUN 事件和 panic 时间线再次输出；panic 状态为 flags=64、pending={2,0}、新 target/map 生效；硬件错误关键词只返回本次 Oops | 通过；iSCSI 间接因果仍无对象链 |
| P10 | `__T0144_PROOF_RERUN_COMPLETE__` 后正常 `quit`；结束于 `2026-07-29T14:42:44+08:00` | 通过 |

## transcript 完整性

```text
file: evidence/crash-proof-rerun.log
lines: 714
bytes: 42823
sha256: 838b78c6e89b8046b35c9510bfc3ef17e2806a565e873d8fcdfde2c18b00dc9c
```

marker 行：

```text
2   __T0144_PROOF_RERUN_BEGIN__
50  __P2_SYSTEM_AND_BT__
113 __P3_FAULT_DISASSEMBLY__
304 __P4_TIO_DWARF__
367 __P5_STALE_TI_PAGETABLE__
383 __P6_CURRENT_DM_TABLE__
409 __P7_REQUEST_AND_DISKS__
467 __P8_MULTIPATH_PATHS__
519 __P9_TIMELINE_STATE_ALTERNATIVES__
710 __T0144_PROOF_RERUN_COMPLETE__
714 __T0144_PROOF_RERUN_END__
```

第二次独立复跑的所有预期信号均满足，未出现与第一次调查相冲突的关键对象、寄存器、页表或设备路径结果。
