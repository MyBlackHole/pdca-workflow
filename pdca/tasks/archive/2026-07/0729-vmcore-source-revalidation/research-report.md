# T0144 vmcore 独立根因分析报告

## 结论

本次崩溃是 device-mapper request-based blk-mq 路径中的 **旧 `dm_target` 指针 use-after-free（UAF）**。

直接崩溃点是 `drivers/md/dm-rq.c:361`：

```c
rq_end_io = tio->ti->type->rq_end_io;
```

faulting request 的 `tio->ti=ffffbd16abacc040` 已无页表映射；该地址不是随机值，而是一个已被释放的旧 dm table 首个 target。当前同一 `mapped_device` 已改用新 target `ffffbd16abbd2040`。两者都位于各自 vmalloc 页基址 `+0x40`，与本版本 `alloc_targets()` 的分配布局完全相符。

根本源码缺陷是 `drivers/md/dm-rq.c:889–927` 的 `dm_mq_queue_rq()` 在 DM suspend 期间没有检查 `DMF_BLOCK_IO_FOR_SUSPEND`。外部 blk-mq unquiesce 可使请求在 suspend/pending drain 窗口重新进入，读取旧 `md->immutable_target` 并保存到 `tio->ti`；随后 table swap/resume 销毁旧 table。约 61 ms 后底层 NVMe I/O 完成，softirq 解引用已 vfree 的旧 target，触发页故障。

上游提交 [`b4459b11e84092658fa195a2587aff3b9637f0e7`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4459b11e84092658fa195a2587aff3b9637f0e7) 对同一路径增加 suspend flag 检查并要求 blk-mq 重排队；提交说明的故障机制正是 DM suspend 中 blk-mq 被外部事件 unquiesce。当前指定 3.10 源码不存在该保护。

**根因置信度：高。**

## 独立性与输入

- 本轮在 tmux `0:0.0` 重新启动全新 crash 会话。
- 实际命令：

  `crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore`

- crash 7.2.3 成功加载，release 为 `3.10.0-1160.83.1.el7.x86_64`。
- dump 为 partial dump；下述关键失效地址经 `vtop` 证明 PTE=0，不是 partial dump 漏存物理页。
- 本轮没有读取或引用 R0142/R0143 的分析内容。
- 原始 transcript：`evidence/crash-session.log`
- transcript SHA-256：`d5ff1d02fa95fbc723720d8941265eee59a3307b4434aa50942904c945050f0a`

## 证据链

### 1. 异常现场

- panic：`BUG: unable to handle kernel paging request at ffffbd16abacc048`
- CPU/task：CPU 137，`swapper/137`
- RIP：`dm_softirq_done+97`，`ffffffffc02a48f1`
- 调用路径：`dm_softirq_done → blk_done_softirq → __do_softirq`
- fault 时：
  - `R13=ffff9ff42a3f1a40`
  - `RDI=ffffbd16abacc040`
  - CR2=`ffffbd16abacc048=RDI+8`

反汇编：

- `+81 mov 0x8(%r13),%rdi`
- `+92 test %rdi,%rdi`
- `+97 mov 0x8(%rdi),%rdx` ← fault

DWARF 确认 `dm_rq_target_io.ti` 偏移为 8，因此 RDI 是 `tio->ti`；第二次 `+8` 是读取 `ti->type`。

### 2. fault 指针是旧 dm_target，不是随机地址

`struct dm_rq_target_io ffff9ff42a3f1a40`：

- `md=ffff9ff81b1b7000`
- `ti=ffffbd16abacc040`
- `orig=ffff9ff42a3f18c0`
- `clone=ffff9ff862cf9600`
- `error=0`

`vtop ffffbd16abacc040` 显示 PTE=0、`not mapped`。

同一 md 当前状态：

- `map=ffff9f8c1029bc00`
- `immutable_target=ffffbd16abbd2040`
- target type=`multipath_target`

当前 table：

- `highs=ffffbd16abbd2000`
- `targets=ffffbd16abbd2040`
- `num_allocated=8`

旧 `ti=ffffbd16abacc040` 与当前 `ti=ffffbd16abbd2040` 都是 vmalloc 页基址 `+0x40`。这精确对应 `dm-table.c:170–182` 将 `highs` 与 `targets` 同块分配、8 个 `sector_t` highs 后紧跟 targets 的布局。

### 3. 旧对象的释放路径

正常 reload 调用链：

1. `dm-ioctl.c:1033–1043`：有 new map 时 suspend 后 `dm_swap_table()`。
2. `dm.c:2056–2072`：`__bind()` 更新 `md->immutable_target` 和 `md->map`。
3. `dm-ioctl.c:1057–1068`：resume 后 `dm_table_destroy(old_map)`。
4. `dm-table.c:245–255`：析构每个 target，随后 `vfree(t->highs)`；由于 target 与 highs 同块分配，旧 target 页被解除映射。

这解释了旧 `tio->ti` 最终 PTE=0。

### 4. 缺失的同步保护

正常 suspend 设计：

- `dm.c:2536` 设置 `DMF_BLOCK_IO_FOR_SUSPEND`。
- `dm.c:2545` 停止/quiesce request queue。
- `dm.c:2557` 等待 pending I/O 归零。

但当前 request-based blk-mq 提交路径：

- `dm-rq.c:895` 读取 `md->immutable_target`。
- `dm-rq.c:905–906` 仅检查 target busy。
- `dm-rq.c:908` 才增加 pending。
- `dm-rq.c:916` 将裸 target 指针保存到 `tio->ti`。

该路径完全不检查 `DMF_BLOCK_IO_FOR_SUSPEND`。

因此，若 blk-mq 在 DM suspend 中被外部事件 unquiesce：

1. suspend 已认为 queue quiesced，并可能已观察 pending=0；
2. 新请求重新进入 `dm_mq_queue_rq()`；
3. 读取旧 target，增加 pending并保存裸指针；
4. suspend/swap 继续，旧 table 被 vfree；
5. 底层 I/O 完成后用旧 `tio->ti` 调用 target end_io；
6. 在读取 `ti->type` 时访问未映射页并 panic。

上游修复正是在 `md->immutable_target` 读取之后增加：

```c
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_STS_RESOURCE;
```

本地 3.10 API 的等价返回值需要按该树的 `BLK_MQ_RQ_QUEUE_BUSY`/状态接口适配，不能机械照搬新内核返回类型。

## 源码位置映射

| 证据环节 | 指定源码位置 | 作用 |
|---|---|---|
| softirq 完成入口 | `drivers/md/dm-rq.c:394–418` | 从 orig request 取得 `tio/clone`，调用 `dm_done()` |
| fault C 表达式 | `drivers/md/dm-rq.c:354–364` | `tio->ti->type->rq_end_io` 两级解引用 |
| 保存旧 target | `drivers/md/dm-rq.c:889–916` | 读 `immutable_target`、增加 pending、保存裸 `tio->ti` |
| 缺失 suspend guard | `drivers/md/dm-rq.c:895–905` | 读取 target 后没有检查 `DMF_BLOCK_IO_FOR_SUSPEND` |
| 设置 block flag | `drivers/md/dm.c:2536` | suspend 阶段宣布禁止新 I/O |
| quiesce/drain | `drivers/md/dm.c:2540–2559` | 停 queue、等待 pending=0 |
| 更换 target/map | `drivers/md/dm.c:2027–2082` | `__bind()` 写入新 immutable target 和 map |
| reload 调用时序 | `drivers/md/dm-ioctl.c:1008–1068` | suspend → swap → resume → destroy old map |
| target 分配几何 | `drivers/md/dm-table.c:160–182` | highs/targets 同一 vmalloc 块 |
| 旧 target unmap | `drivers/md/dm-table.c:234–255` | target dtr 后 `vfree(t->highs)` |

## iSCSI 是否触发

判定：**`inconclusive`；直接触发已排除，间接促成未证实。**

| 门槛 | 结果 | 本轮证据 |
|---|---|---|
| iSCSI 事件存在 | 通过 | panic 前约 76 秒出现 host11112，约 45.5 秒前有 LUN 重枚举/attach |
| 同一设备/对象 | 直接路径不通过 | orig 为 dm-19；faulting clone 为 `nvme38n1`；dm-19 两条 path 是 `nvme37n1/nvme38n1`，无 `sdX` |
| 状态转换连接 | 未证实 | iSCSI uevent 可能触发 multipathd 全局 reconfigure，但日志和 vmcore 没有 host11112 → dm-19 reload 的 ioctl 对象链 |
| 进入 bug 窗口 | 未连接 | faulting I/O 约在 panic 前 61 ms 启动并跨越旧 target 销毁；无法把 45 秒前 iSCSI 事件连接到这 61 ms 窗口 |

如果“iSCSI 触发”仅指 faulting I/O 或 dm-19 的直接 path，结论是 **`not_triggered`**。若包括 userspace 全局 reconfigure 的间接促成，只能保持 `inconclusive`，不能用时间相邻证明因果。

## 替代解释

- **partial dump 漏页**：排除。失效地址的 PTE 本身为 0。
- **普通 reload 必然造成 UAF**：排除。正常 quiesce/pending drain 在设计上应保护在途 I/O；本次需要 suspend 中外部 unquiesce 加缺失 guard。
- **pending 提前递减/重复完成**：不支持。fault 发生在 `dm_end_request()/rq_completed()` 前，panic 时 md pending 仍为 `{2,0}`；orig/clone 关系和时间自洽。
- **随机野指针/bit flip**：低概率。地址精确匹配旧 target 分配几何，且旧/新对象、释放路径与上游同类修复构成一致证据链。
- **硬件内存损坏**：日志无 MCE、Hardware Error、Memory Failure 或先行 Oops；静默硬件错误不能绝对排除，但没有正向证据。

## 证据限制

- crash 启动报告 `kernel version inconsistency between vmlinux and dumpfile`。但 release、模块调试符号、结构偏移、寄存器、反汇编和源码语义均交叉一致；未发现会改变本结论的布局冲突。
- dump 是静态快照，无法直接看到 table swap 前触发 `blk_mq_unquiesce_queue()` 的具体线程/外部设置操作。
- 崩溃瞬间没有 CPU 停在 dm table swap/destroy 栈，这符合旧 table 已销毁后底层 I/O 才完成，但不能识别发起 reload 的用户态事件。
- 未在生产环境复现竞态，也未对内核打补丁；本任务范围仅为静态根因分析。

## 建议

1. 优先采用发行商提供且包含等价修复的受支持 kernel errata；核对补丁是否覆盖 request-based `dm_mq_queue_rq()` 的 suspend flag guard。
2. 若必须回移植，在本 3.10 树中按其 blk-mq 返回接口适配上游逻辑，并进行 `dm-multipath suspend/resume + 外部 queue unquiesce（如 nr_requests/elevator 变更）+ I/O` 并发压测。
3. 线上缓解应避免在 multipath table reload/suspend-resume 压力期间并发修改可导致 blk-mq unquiesce 的 queue 属性；这只是降低窗口，不能替代补丁。
4. 若仍要追查 iSCSI 的间接促成关系，需要补充 panic 前 userspace multipathd debug/journal、udev event 和 DM ioctl 审计，按 WWID/map 名把 host11112 事件连接到 dm-19 reload。

