---
schema: pdca.asset/v1
id: T0144-0729-vmcore-source-revalidation
phase: check
source_ids:
  - crash-session
  - crash-proof-rerun
  - investigation-log
  - root-cause-proof
  - proof-rerun-expanded-reviewed-input
  - source-map
  - research-report
  - patch-equivalence-proof
  - logic-closure-review
  - root-cause-chain-nontechnical
  - vmcore-analysis-report
  - vmcore-analysis-report-detailed
---

## 上下文

本任务使用指定的：

```text
/usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux
/nbudata/vmcore/vmcore
```

在 tmux `0:0.0` 中从零启动 crash，独立完成两轮分析和证明复跑。源码行号基于：

```text
/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7
```

历史 R0142/R0143 未作为 Do/Check 的假设、证据或结论来源。

## 假设与结果

| 假设 | 结果 | 证据结论 |
|---|---|---|
| panic 位于 device-mapper 完成路径 | 成立 | RIP=`dm_softirq_done+97`，栈含 `blk_done_softirq` |
| fault 是 `tio->ti->type` 解引用 | 成立 | 反汇编、寄存器和 dm_mod DWARF 三方一致 |
| 非法地址只是 partial dump 漏页 | 否定 | `vtop` 显示 PTE 本身为 0 |
| `tio->ti` 是旧 dm table target | 高置信成立 | 指针来源、同一 md 新 target、`page+0x40` 分配几何和生命周期一致 |
| 旧 target 随 old table 销毁而解除映射 | 高置信成立 | reload/destroy/vfree 源码与现场 PTE=0 一致 |
| pending 提前递减或重复完成导致 UAF | 不支持 | fault 在 `rq_completed()` 前，panic 时 pending 仍为 `{2,0}` |
| 随机野指针或硬件内存损坏 | 低概率/无正向证据 | 地址具有精确对象几何，日志无 MCE/Memory Failure/先行 Oops |
| request-based blk-mq 缺少 suspend guard | 成立 | `dm_mq_queue_rq()` 不检查 `DMF_BLOCK_IO_FOR_SUSPEND` |
| b4459b11e840 修复同一安全不变量 | 高置信成立 | 模式、缺失点和故障后果一致；guard 静态切断必要路径 |
| iSCSI 是直接 faulting path | 否定 | clone=`nvme38n1`；dm-19 当前 path=`nvme37n1/nvme38n1` |
| iSCSI 间接促成 dm-19 reload | 未证实 | 缺少 iSCSI→multipathd→dm-19 ioctl/map 对象链 |

## 分析

### 直接原因

CPU 137 在块完成 softirq 中执行 `dm_softirq_done()`。faulting 指令：

```text
mov 0x8(%rdi),%rdx
```

其中：

```text
R13 = dm_rq_target_io
R13+8 = tio->ti = RDI = ffffbd16abacc040
RDI+8 = ti->type
CR2 = ffffbd16abacc048
```

`vtop ffffbd16abacc040` 显示该页 `not mapped`、PTE=0。因此直接原因是完成路径
解引用已解除映射的 `tio->ti`。

### 对象生命周期

faulting request 保存：

```text
tio->md = ffff9ff81b1b7000
tio->ti = ffffbd16abacc040
```

同一 md 当前为：

```text
map              = ffff9f8c1029bc00
immutable_target = ffffbd16abbd2040
type             = multipath_target
```

当前 target=`highs+0x40`；失效 target 同样为另一 vmalloc 页 `+0x40`。结合
`dm_mq_queue_rq()` 将 `md->immutable_target` 保存到 `tio->ti`，可判断请求持有
的是同一 md 的旧 table target。

reload 路径安装新 target/map，resume 后 `dm_table_destroy(old_map)`；
`dm_table_destroy()` 对包含 highs/targets 的同一 vmalloc block 执行 `vfree()`。
这解释了旧 target 的 PTE=0。

### 代码级根因

正常 suspend 协议：

```text
set DMF_BLOCK_IO_FOR_SUSPEND
→ quiesce queue
→ wait pending == 0
→ swap table
→ resume
→ destroy old map
```

但 request-based `dm_mq_queue_rq()` 在读取 `md->immutable_target` 后没有检查
`DMF_BLOCK_IO_FOR_SUSPEND`，随后即：

```text
dereference ti
→ dm_start_request()
→ tio->ti = ti
→ map_request()
```

因此，只要 queue 在 suspend 期间被再次 dispatch，请求仍可保存旧 target 并
跨越 table swap/destroy。完成时解引用已 vfree 的旧 target，形成 UAF。

**代码级根因：request-based DM blk-mq 提交路径缺少 suspend 期间的第二道请求
准入检查。**

### 修复对应

上游提交 `b4459b11e84092658fa195a2587aff3b9637f0e7` 在危险操作之前检查
`DMF_BLOCK_IO_FOR_SUSPEND`，置位时返回 RESOURCE 让请求重排队。

本 3.10 API 的语义等价返回值应为：

```c
BLK_MQ_RQ_QUEUE_BUSY
```

该 guard 能静态切断本次故障路径，因为命中后不会增加 pending、不会设置
`tio->ti`、不会下发 clone；resume 后重试时读取新 target。

尚未构建或压测 3.10 回移植，因此不能把“静态充分性”描述为“回移植二进制已
运行验证”。

### iSCSI

日志证明 panic 前约 45–76 秒存在 iSCSI host/LUN 事件，但本次 faulting clone
实际为 `nvme38n1`，不是 iSCSI `sdX`。所以 iSCSI 不是直接 I/O path。

iSCSI uevent 是否通过 multipathd 全局 reconfigure 间接促成 dm-19 reload，当前
没有完整对象链，判定保持 `inconclusive`。

### 验收结论

PRD AC-1 至 AC-10 均有已登记证据覆盖；convergence validator 返回
`valid: true`。两轮 crash 的 RIP、寄存器、DWARF、页表、旧/新 target 和设备
路径结果一致。

## 适用边界

- 直接崩溃点、无效对象和代码级安全不变量缺口为高置信结论。
- 静态 vmcore 不能唯一恢复具体由哪个进程或 sysfs 操作重新 unquiesce queue。
- 当前 map 证明崩溃时 dm-19 的两条 path 均为 NVMe；旧 table 已释放，无法再
  遍历其完整历史 path 列表。
- iSCSI 直接触发已排除，间接关系未证实。
- crash 报告 vmlinux/dumpfile version inconsistency 警告；但 release、模块
  DWARF、字段偏移、寄存器、反汇编和源码语义交叉一致。
- 上游修复不能机械 cherry-pick 到 3.10，需适配返回类型和 flag 可见性。

## 下一轮建议

1. 优先确认发行商支持的 kernel errata 是否包含语义等价 guard。
2. 如需自行回移植，增加：

   ```c
   if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
           return BLK_MQ_RQ_QUEUE_BUSY;
   ```

   并安全共享 flag 定义或内部 helper。
3. 使用未补丁/补丁内核做 A/B：fio、dm-mpath suspend/resume/table reload 与
   `nr_requests`/queue unquiesce 压力并发。
4. 观测 `flag=1` 时进入 queue_rq、被 requeue、继续 mapping 和 stale target
   的计数；补丁后必须满足 blocked mapping=0。
5. 若继续追查 iSCSI 间接关系，补充 multipathd debug/journal、udev 和 DM ioctl
   审计，按 map/WWID 连接事件链。

## Check 建议判定

建议 verdict：

```text
confirmed
```

理由：代码级根因和直接崩溃链已由两轮独立 crash、源码和替代解释审查闭合；
未闭合内容已严格限定为具体外部触发者、iSCSI 间接关系及回移植运行时验证，
不影响对本次内核 bug 根因的确认。
