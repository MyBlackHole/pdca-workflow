# T0144 crash 逐步调查日志

## 记录约定

每一步均按“目的 → 假设 → 预期信号 → 命令 → 实际结果 → 解释 → 下一步”记录。原始终端输出保存于 `crash-session.log`。

## Step 0 — 建立本轮新会话

### Step 0.1：确认 pane 状态

- **目的**：确认 `0:0.0` 当前位于 `nbusvr103` shell，避免把 crash 命令误发到旧 crash 提示符或正在运行的程序。
- **待验证假设**：pane 当前为空闲 shell。
- **预期信号**：末行是 `[root@nbusvr103 kernel-rpm]#`。
- **命令**：控制端执行 `tmux capture-pane -p -S -20 -t 0:0.0`。
- **实际结果**：pane 末行是 `[root@nbusvr103 kernel-rpm]#`，为空闲远端 shell。
- **解释**：可以安全启动本轮新 crash；pane 中更早的内容不属于本轮，本轮以 `__T0144_CRASH_BEGIN__` 为边界。
- **下一步**：启用 transcript 并启动指定 crash。

### Step 0.2：启动指定 crash 输入

- **目的**：建立完全独立的新分析会话，并验证 vmlinux 与 vmcore 能被 crash 正确加载。
- **待验证假设**：两个远端文件存在、符号与 dump 匹配，crash 可进入 `crash>` 提示符。
- **预期信号**：启动摘要显示指定 KERNEL/DUMPFILE、release `3.10.0-1160.83.1.el7.x86_64`，随后出现 `crash>`。
- **命令**：`crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore`
- **实际结果**：crash 7.2.3 成功进入 `crash>`。摘要确认 KERNEL 与 DUMPFILE 为指定路径，dump 为 `PARTIAL DUMP`，`RELEASE` 为 `3.10.0-1160.83.1.el7.x86_64`；192 CPU、1023.7 GB、panic task 为 CPU 137 的 `swapper/137`。加载期间出现 `WARNING: kernel version inconsistency between vmlinux and dumpfile`。
- **解释**：输入可被解析且 release 与目标版本一致，但版本一致性警告必须保留为潜在证据风险。后续需用结构偏移、符号、反汇编与日志互相校验，若出现系统性冲突则停止使用该符号解释。`PARTIAL DUMP` 意味着不可读页面不能自动等同于运行时未映射或已释放。
- **下一步**：执行 `sys` 固定基础元数据和 panic 字符串，再取主调用栈。

## Step 1 — 固定最小崩溃现场

### Step 1.1：读取系统与 panic 摘要

- **目的**：由 crash 命令重新输出系统元数据，确认启动摘要中的 panic、时间、版本和任务环境。
- **待验证假设**：panic 是内核页故障，release 与给定源码版本相符。
- **预期信号**：`sys` 显示 release `3.10.0-1160.83.1.el7.x86_64`、panic 地址和崩溃时间。
- **命令**：`sys`
- **实际结果**：`sys` 确认 release `3.10.0-1160.83.1.el7.x86_64`、时间 `Thu Jul 23 10:01:20 2026`、uptime 805 天、192 CPU、partial dump，panic 为 `BUG: unable to handle kernel paging request at ffffbd16abacc048`。
- **解释**：直接异常类型是内核页故障，fault address 为 `ffffbd16abacc048`；尚不能判断该地址为何无效。release 与指定源码版本一致。
- **下一步**：执行 `bt` 获取异常 RIP、寄存器及调用链。

### Step 1.2：获取 panic task 主调用栈

- **目的**：确认 faulting 函数、异常 RIP、寄存器和从 fault 到 panic 的调用链。
- **待验证假设**：`bt` 能恢复 CPU 137 的 exception frame，且 fault address 可由某个寄存器加字段偏移解释。
- **预期信号**：栈中存在 `<IRQ>` 或进程上下文的异常帧、`RIP`、`RSP`、`RFLAGS`、通用寄存器和 panic 路径。
- **命令**：`bt`
- **实际结果**：`bt` 显示 exception RIP 为 `dm_softirq_done+97`（`ffffffffc02a48f1`），fault address 为 `ffffbd16abacc048`。异常帧中 `RDI=ffffbd16abacc040`，二者差值为 `8`；`R12=ffff9ff862cf9600`、`R13=ffff9ff42a3f1a40`。调用链从 `dm_softirq_done` 经 `blk_done_softirq`、`__do_softirq`、IRQ exit 返回 idle。输出因 crash 分页器停在中途。
- **解释**：已确认直接 fault 位于块层 softirq 完成路径。`fault_address == RDI + 8` 强烈提示 fault 指令访问以 RDI 为基址、偏移 8 的字段，但对象类型必须由反汇编和结构偏移继续证明。分页导致本次 `bt` 不完整，不能遗漏后半段。
- **下一步**：退出分页、关闭 scroll 分页后重新执行完整 `bt`。

### Step 1.3：关闭交互分页并重取完整栈

- **目的**：避免长输出停在分页器导致 transcript 和证据不完整。
- **待验证假设**：当前处于 crash 内部分页器；`q` 返回 `crash>`，`set scroll off` 可让后续命令一次输出完整。
- **预期信号**：出现 `crash>`，设置后重跑 `bt` 不再显示分页提示并回到 `crash>`。
- **控制输入/命令**：分页器输入 `q`；随后 `set scroll off`；再次执行 `bt`。
- **实际结果**：分页器 `q` 返回后，`set scroll off` 显示 `scroll: off`；重跑 `bt` 完整输出到 `crash>`。后半栈确认 CPU 137 原本在 `native_safe_halt → default_idle → cpu_startup_entry`，由中断进入 softirq 完成路径。
- **解释**：完整栈已保存。崩溃发生在 idle CPU 处理块完成 softirq 时；当前栈没有进程上下文中的业务线程。
- **下一步**：反汇编 `dm_softirq_done`，确认 `+97` 指令及寄存器来源。

## Step 2 — 锁定 fault 指令及 C 语义

### Step 2.1：反汇编 faulting 函数

- **目的**：确认 `dm_softirq_done+97` 的准确指令、内存操作数，以及 RDI 在此前由哪个对象字段加载。
- **待验证假设**：fault 指令访问 `0x8(%rdi)`，此前 RDI 从 R13 所指对象的某个字段加载。
- **预期信号**：反汇编中 RIP `ffffffffc02a48f1` 对应以 RDI 为基址的内存读取，且此前指令可以解释 R13、R12 等寄存器的来源。
- **命令**：`dis dm_softirq_done`
- **实际结果**：反汇编确认 `+81: mov 0x8(%r13),%rdi`，`+92: test %rdi,%rdi`，faulting `+97: mov 0x8(%rdi),%rdx`，随后 `+103: mov 0x60(%rdx),%r8`。fault 时 `R13=ffff9ff42a3f1a40`、`RDI=ffffbd16abacc040`，因此 `RDI+8=ffffbd16abacc048` 与 CR2 完全相等。
- **解释**：RDI 是从 `R13+8` 取出的非 NULL 指针，fault 是再次读取 `RDI+8` 时发生。后续的 `RDX+0x60` 表明 RDI+8 很可能是另一个含函数指针的类型对象，但必须由源码和 DWARF 结构布局证明。
- **下一步**：在指定源码树定位 `dm_softirq_done`，找出对应 C 表达式与局部对象类型。

### Step 2.2：在指定源码树定位函数

- **目的**：确定反汇编序列对应的 C 文件、函数和实际行号，避免仅凭汇编猜测类型。
- **待验证假设**：源码树包含 `dm_softirq_done`，其中存在一个对象字段的两级解引用，对应 `R13+8 → RDI` 和 `RDI+8 → RDX`。
- **预期信号**：检索命中唯一实现；带行号上下文可与 error、请求完成回调及后续间接调用对应。
- **本地只读命令**：`rg -n "dm_softirq_done" <source-tree>`，随后 `nl -ba` 查看函数上下文。
- **实际结果**：`rg` 唯一实现命中 `drivers/md/dm-rq.c:394`，另有两处回调注册。首次 `nl` 误取 `320–390`，只显示了被 `dm_softirq_done` 调用的 `dm_done()`：其 357 行从 `clone->end_io_data` 取 `tio`，360–364 行执行 `tio->ti->type->rq_end_io` 两级解引用。结构定义命中 `drivers/md/dm-rq.h:22`。
- **解释**：首次行号范围没有包含 394 行起的 `dm_softirq_done`，这是一次取证范围错误，已保留；但显示的 `dm_done` 与反汇编两级解引用高度吻合。仍需查看 394 行函数及结构定义，不能仅凭吻合确认寄存器类型。
- **下一步**：补取 `dm-rq.c:390–420` 和 `dm-rq.h` 结构定义，再用 crash DWARF 偏移交叉验证。

### Step 2.3：补取准确源码上下文和结构定义

- **目的**：修正 Step 2.2 的行号范围错误，完整取得 `dm_softirq_done` 到 `dm_done` 的调用关系及 `dm_rq_target_io` 字段顺序。
- **待验证假设**：`dm_softirq_done` 从 request 找到 `tio`/clone 后调用 `dm_done`；`dm_rq_target_io.ti` 的运行时偏移与反汇编 `R13+8` 一致。
- **预期信号**：源码显示清晰调用链，头文件显示 `md`、`ti`、`orig`、`clone` 等字段。
- **本地只读命令**：查看 `dm-rq.c:390–420` 与 `dm-rq.h:1–70` 的带行号内容。
- **实际结果**：`dm-rq.c:394–418` 显示 `dm_softirq_done()` 在 397 行通过 `tio_from_request(rq)` 取得 `tio`、398 行取 `tio->clone`，418 行调用 `dm_done(clone, tio->error, mapped)`。`dm-rq.h:22–33` 显示 `dm_rq_target_io` 的首字段为 `md`，第二字段为 `ti`，随后为 `orig`、`clone`。
- **解释**：源码层面的调用链为 `dm_softirq_done:418 → dm_done:354`。按普通 x86_64 指针布局，第二字段 `ti` 应位于偏移 8，与反汇编 `R13+8` 一致；但必须由 dump 对应 DWARF 确认。
- **下一步**：加载 `dm_mod` 调试符号，验证运行时结构偏移。

## Step 3 — 还原关键内核对象

### Step 3.1：加载 dm_mod 模块调试符号

- **目的**：取得 dump 对应模块的 DWARF 类型信息，避免只依赖源码推定结构布局。
- **待验证假设**：远端 debug tree 包含与 dump 中 `dm_mod` 模块匹配的调试信息。
- **预期信号**：`mod -s dm_mod` 成功加载符号文件，之后 crash 能识别 `dm_rq_target_io`。
- **命令**：`mod -s dm_mod`
- **实际结果**：`mod -s dm_mod` 成功加载 `/usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/kernel/drivers/md/dm-mod.ko.debug`，模块基址 `ffffffffc02ab860`。
- **解释**：可以使用模块 DWARF 解析 device-mapper 私有结构；这也提供了独立于本地源码的布局校验来源。
- **下一步**：查询 `dm_rq_target_io` 的实际字段偏移。

### Step 3.2：验证 dm_rq_target_io 字段偏移

- **目的**：证明 `R13` 所指对象中偏移 8 的字段确实是 `ti`，并验证其他寄存器可能对应的 `clone`、`error` 字段。
- **待验证假设**：`dm_rq_target_io.ti` 偏移为 `0x8`，`clone` 和 `error` 偏移与反汇编读取一致。
- **预期信号**：`struct -o` 输出 `md@0x0`、`ti@0x8`、`orig@0x10`、`clone@0x18`，以及后续字段偏移。
- **命令**：`struct -o dm_rq_target_io`
- **实际结果**：DWARF 输出 `md@0`、`ti@8`、`orig@16`、`clone@24`、`error@88`，结构大小 136 字节。
- **解释**：运行时布局确认 fault 前 `mov 0x8(%r13),%rdi` 正是读取 `tio->ti`；`mov 0x58(%r13),%ebx` 对应 `tio->error`。这不是仅凭本地源码推定。
- **下一步**：以 `R13=ffff9ff42a3f1a40` 解析完整 `tio`，验证 `ti`、`clone`、`error` 值与寄存器一致。

### Step 3.3：解析 fault 时的 dm_rq_target_io

- **目的**：还原 fault 请求上下文，验证 `tio->ti`、`tio->clone` 和 `tio->error` 的实际值。
- **待验证假设**：`tio@R13` 可读，`ti` 等于 fault 时 RDI，`clone` 等于 R12，`error` 等于 RBX 低 32 位。
- **预期信号**：结构输出中 `ti=ffffbd16abacc040`、`clone=ffff9ff862cf9600`、`error=0`。
- **命令**：`struct dm_rq_target_io ffff9ff42a3f1a40`
- **实际结果**：结构可完整解析：`md=ffff9ff81b1b7000`、`ti=ffffbd16abacc040`、`orig=ffff9ff42a3f18c0`、`clone=ffff9ff862cf9600`、`error=0`、`completed=524288`。`ti` 与 RDI、`clone` 与 R12、`error` 与 RBX 完全一致。
- **解释**：fault 请求上下文自身仍可读且字段自洽；直接异常由其中保存的非 NULL `ti` 指针触发。仅凭 `ti` 不可访问仍不能区分运行时 unmap、partial dump 缺页或其他破坏。
- **下一步**：直接读取 `ti` 地址，确认 crash 的地址访问行为。

### Step 3.4：检查 ti 指针目标的可读性

- **目的**：确认 `tio->ti` 指向的内存是否可由 vmcore 地址转换并读取。
- **待验证假设**：fault 地址附近不可读；若是完全无页表映射，`rd` 会报告 invalid kernel virtual address。
- **预期信号**：读取 `ffffbd16abacc040` 失败，并给出地址转换错误；若读取成功，则需重新考虑 fault 时页表与 dump 读取差异。
- **命令**：`rd ffffbd16abacc040 4`
- **实际结果**：`rd` 返回 `invalid kernel virtual address: ffffbd16abacc040 type: "64-bit KVADDR"`。
- **解释**：crash 无法把 `tio->ti` 作为有效内核虚拟地址读取。这与 fault 一致，但尚未说明是页表项不存在还是 dump 未保存对应物理页。
- **下一步**：执行 `vtop` 显示页表遍历结果。

### Step 3.5：检查 ti 地址页表映射

- **目的**：区分“虚拟地址没有有效 PTE”与“有映射但 partial dump 未保存物理页”。
- **待验证假设**：`tio->ti` 位于 vmalloc 区，页表遍历最终得到 PTE 0 或 not present。
- **预期信号**：`vtop` 输出 PGD/PUD/PMD/PTE 层级，并显示无有效 PTE；若有物理地址但页缺失，则只能判为 dump 缺页。
- **命令**：`vtop ffffbd16abacc040`
- **实际结果**：`vtop` 显示地址 `(not mapped)`；页表遍历为 `PGD → PUD fc3ec6e067 → PMD 27b845e067 → PTE 0`。
- **解释**：PTE 本身为 0，排除了“有有效映射但 partial dump 未保存物理页”。`tio->ti` 在崩溃页表中确实是未映射虚拟地址。它符合已解除映射/失效对象，但释放来源仍未证明。
- **下一步**：检查仍有效的 `tio->md` 当前 map/target 状态，判断是否存在同一设备的新对象。

### Step 3.6：检查 mapped_device 当前映射

- **目的**：确认该请求所属 mapped_device 是否仍有效，以及它当前引用的 map/target 是否与请求保存的未映射 `ti` 不同。
- **待验证假设**：`md=ffff9ff81b1b7000` 可读，并包含一个当前有效的 map 或 immutable target；当前 target 地址不同于 `ffffbd16abacc040`。
- **预期信号**：选定字段显示有效 `map`、`immutable_target`、`immutable_target_type` 和 blk-mq 状态。
- **命令**：`struct mapped_device.map,immutable_target,immutable_target_type,use_blk_mq,name ffff9ff81b1b7000`
- **实际结果**：`md` 可读：`map=ffff9f8c1029bc00`、`immutable_target=ffffbd16abbd2040`、`immutable_target_type=ffffffffc17f8040`、`use_blk_mq=true`、`name="253:19"`。
- **解释**：请求所属设备是 blk-mq device-mapper 设备 `253:19`。其当前 immutable target 地址 `ffffbd16abbd2040` 与请求保存且未映射的 `ffffbd16abacc040` 不同，证明请求保存的是一个旧/不同 target 指针；尚未证明替换发生的原因。
- **下一步**：解析 `immutable_target_type` 符号，识别 target 驱动。

### Step 3.7：识别当前 target 类型

- **目的**：确定 mapped_device 当前 target 属于哪个 device-mapper 驱动，为后续对象和 iSCSI 关联分析定界。
- **待验证假设**：`immutable_target_type=ffffffffc17f8040` 可解析为某个已加载 DM target 类型。
- **预期信号**：`sym` 返回明确模块符号。
- **命令**：`sym ffffffffc17f8040`
- **实际结果**：`sym` 解析为 `multipath_target [dm_multipath]`。
- **解释**：崩溃请求属于 device-mapper multipath 的 request-based blk-mq 路径。iSCSI 是否参与仍需从 multipath path 对应的 SCSI transport 和日志证明，不能由 multipath 类型直接推出。
- **下一步**：解析当前 `dm_target`，确认其 table、type 和 private 对象。

### Step 3.8：解析当前有效 dm_target

- **目的**：验证 `md->immutable_target` 当前对象的内部字段与 map/type 自洽，并取得后续 multipath 私有对象入口。
- **待验证假设**：当前 target 可读，其 `table` 等于 `md->map`、`type` 等于 `multipath_target`。
- **预期信号**：`table=ffff9f8c1029bc00`、`type=ffffffffc17f8040`，并有有效 `private` 指针。
- **命令**：`struct dm_target.table,type,begin,len,private ffffbd16abbd2040`
- **实际结果**：当前 target 可读，`table=ffff9f8c1029bc00` 与 `md->map` 相等，`type=ffffffffc17f8040` 与 `multipath_target` 相等，`private=ffff9f8c1029a400`。
- **解释**：当前 md/map/target 链完整自洽，而 in-flight 请求保存的 `tio->ti` 已无映射。该“旧请求指针 vs 当前有效 target”分离是生命周期问题的重要证据，但替换/释放代码路径尚待定位。
- **下一步**：在指定源码树中反向追踪所有 `tio->ti` 赋值点。

## Step 4 — 追踪对象来源和生命周期

### Step 4.1：定位 tio->ti 赋值点

- **目的**：查明请求何时保存 target 指针，以及保存时是否持锁、RCU 读侧保护或引用计数。
- **待验证假设**：request queue/map 路径将某个 `dm_target *` 直接存入 `tio->ti`，且该保存值跨越异步 I/O 完成。
- **预期信号**：源码中存在明确赋值点，并可沿调用链连接到 `dm_softirq_done/dm_done`。
- **本地只读命令**：在 `drivers/md` 中检索 `tio->ti` 的赋值和使用，并查看相关函数带行号上下文。
- **实际结果**：当前 `md->use_blk_mq=true` 对应 `dm_mq_queue_rq()`（`dm-rq.c:889–927`）。895 行直接读取 `md->immutable_target`；910–916 行初始化 `tio` 并把该裸指针保存到 `tio->ti`；919 行后 I/O 异步运行；完成回调在 `dm_mq_ops.complete=dm_softirq_done`（929–932 行）。保存期间没有可见的引用计数或覆盖整个 I/O 生命周期的 SRCU 临界区。
- **解释**：请求提交时复制了 target 裸指针，并在完成时再次使用。若 `immutable_target` 所属 table 在 I/O 完成前被替换和释放，`tio->ti` 不会自动更新。这是候选生命周期竞态机制，仍需证明 target 替换/销毁路径允许发生。
- **下一步**：定位 `md->immutable_target` 的所有写入点、table swap 同步和旧 table 销毁。

### Step 4.2：追踪 immutable_target 替换路径

- **目的**：确定当前 target 如何替换旧 target，以及替换时采用的同步是否覆盖保存于 in-flight `tio` 的裸指针。
- **待验证假设**：table bind/swap 会更新 `md->immutable_target`，同步只等待 map 读者，随后旧 table/target 可销毁；它不等待已提交的 blk-mq 请求完成。
- **预期信号**：源码中能连出 `immutable_target` 更新、RCU/SRCU 同步、旧 table 返回及 destroy/free 路径。
- **本地只读命令**：检索 `immutable_target`、`dm_sync_table`、table swap/bind、`dm_table_destroy` 和 target 数组分配/释放，并查看实际行号上下文。
- **实际结果**：`dm.c:2027–2082` 的 `__bind()` 在 request-based table 上先 `dm_stop_queue()`，2063 行把新 table 的 immutable target 写入 `md->immutable_target`，2070–2072 行替换 `md->map/type`，旧 map 存在时仅调用 `dm_sync_table()` 后返回旧 map。`dm-table.c:234–263` 的 `dm_table_destroy()` 调用 target destructor，并在 255 行 `vfree(t->highs)`；检索显示 targets 与 highs 来自同一 vmalloc 块。初次范围未显示 `alloc_targets` 起始和 `dm_sync_table` 实现。
- **解释**：旧 target 具有被 `vfree` 解除映射的明确销毁路径，与 PTE=0 一致；但仍不能确认它在 in-flight I/O 完成前可销毁，因为 `dm_stop_queue`、suspend 和 swap 调用者可能提供 drain 保障。
- **下一步**：精确检查 `alloc_targets`、`dm_sync_table`、`dm_stop_queue`、`dm_suspend`、`dm_swap_table` 及 ioctl 对返回旧 table 的销毁时机。

### Step 4.3：审查 suspend/queue drain 是否覆盖 in-flight I/O

- **目的**：验证 table swap 的同步边界是否包含已提交但尚未进入 `dm_softirq_done` 的请求。
- **待验证假设**：stop/suspend 只阻止新映射或只等待某类 pending 计数，不足以保护 blk-mq `tio->ti`；或者某条非正常 swap 路径绕过 drain。
- **预期信号**：能从源码明确判断 queue stop、pending wait、SRCU grace period和旧 table destroy 的先后关系及覆盖对象。
- **本地只读命令**：查看上述函数实现和 `dm_swap_table` 调用者的带行号上下文。
- **实际结果**：正常 reload 路径为 `dm-ioctl.c:1008–1068 do_resume()`：有新 map 时先 `dm_suspend()`，再 `dm_swap_table()`，resume 后销毁 old map。`dm.c:2481–2578 __dm_suspend()` 在 2545 行 quiesce request queue、2557 行 `dm_wait_for_completion()` 等待 `md_in_flight()==0`，成功后才置 suspended。`dm_swap_table:2405–2407` 又拒绝未 suspended 设备。`dm_sync_table:579–583` 本身只等待 SRCU/RCU。`alloc_targets:160–182` 通过 `vzalloc` 同块分配 highs+targets，destroy 时 `vfree(highs)`。
- **解释**：正常 suspend/swap 路径在设计上应排空已计入 `md->pending` 的请求，因此“任何普通 table reload 都会直接 UAF”受到反证，当前不能确认。若旧 target 确实被 table destroy 提前解除映射，必须存在 pending 计数提前归零、绕过正常 suspend、特殊 destroy 路径或内存破坏等更具体机制。
- **下一步**：先验证当前 target 在 vmalloc 块中的几何布局，再审查请求 pending 计数从开始到完成的增减时机。

### Step 4.4：验证 dm_target 的 vmalloc 分配几何

- **目的**：判断失效 `ti` 地址是否具有 table target 数组的固定页内偏移，而不是随机损坏地址。
- **待验证假设**：当前 `dm_table.highs` 是页对齐 vmalloc 基址，`targets=highs+num_allocated*sizeof(sector_t)`；当前和失效 ti 具有相同页内 target 偏移。
- **预期信号**：当前 table 显示 `targets=ffffbd16abbd2040`、`highs=ffffbd16abbd2000`，差值 `0x40`；失效 ti 也以 `0x40` 结尾。
- **命令**：`struct dm_table.highs,targets,num_allocated,num_targets,type ffff9f8c1029bc00`
- **实际结果**：当前 table 为 `DM_TYPE_MQ_REQUEST_BASED`，`num_allocated=8`、`num_targets=1`，`highs=ffffbd16abbd2000`、`targets=ffffbd16abbd2040`，target 相对 vmalloc 页基址精确偏移 `0x40`。失效 `ti=ffffbd16abacc040` 同样位于页内偏移 `0x40`。
- **解释**：结合 `alloc_targets:170–182` 的固定布局，失效指针不是随机地址：它高度确定地指向另一个/旧的 dm_table target 数组首元素；该数组所在 vmalloc 页现已被解除映射。由此可将“旧 table target 已 vfree”提升为强证据支持，但提前销毁的同步缺口仍未定位。
- **下一步**：追踪 `md->pending` 的增加/减少以及 clone/multipath 完成顺序。

### Step 4.5：审查 request pending 生命周期

- **目的**：判断 suspend 的 `dm_wait_for_completion()` 是否可能在 clone/原请求仍将访问 `tio->ti` 时观察到 pending=0。
- **待验证假设**：某条完成、重排队或 multipath 路径可能在 `dm_done()` 解引用 `tio->ti` 之前或实际底层 I/O 完成前调用 `rq_completed()`。
- **预期信号**：源码明确给出 `dm_start_request` 增计数、`rq_completed` 减计数和所有调用点；可判断与 fault 行 360–364 的先后。
- **本地只读命令**：检索并查看 `dm_start_request`、`rq_completed`、`dm_end_request`、clone end_io、requeue 和 multipath map/end_io 相关实现。
- **实际结果**：`dm_start_request:702–708` 启动原请求后增加 `md->pending`；`dm_end_request:260–286` 在释放 clone、结束原请求后才调用 `rq_completed()` 减计数。当前 fault 位于 `dm_done:360–361`，发生在 `dm_end_request()` 之前。multipath `rq_end_io` 也尚未被成功读取和调用。没有发现当前完成路径在 fault 前提前减 pending。
- **解释**：pending 提前归零不是当前路径的直接原因。更窄的窗口位于 `dm_mq_queue_rq:895` 读取 `immutable_target` 与 908 行 `dm_start_request()` 增 pending 之间；如果 quiesce 未等待此时正在运行的 `queue_rq`，suspend 可错误观察 pending=0。
- **下一步**：审查本版本 `blk_mq_quiesce_queue()` 是否等待所有进行中的 `queue_rq` 回调，以及其与 queue stopped 状态的关系。

### Step 4.6：检查 blk-mq quiesce 语义

- **目的**：判断 suspend 是否封闭“已读取旧 ti、尚未计入 pending”的 queue_rq 竞争窗。
- **待验证假设**：该 RHEL 7.9 实现或调用方式存在 quiesce 等待缺口；若实现明确等待所有 queue_rq 返回，则该竞态应被否决。
- **预期信号**：源码展示 quiesce 如何停止 dispatch、等待 SRCU/RCU 或 active usage counter，以及 `blk_mq_queue_stopped` 早退条件。
- **本地只读命令**：检索并查看 `blk_mq_quiesce_queue`、`blk_mq_queue_stopped`、queue enter/dispatch 保护实现。
- **实际结果**：`blk_mq_quiesce_queue:221–237` 先置 `QUEUE_FLAG_QUIESCED`，再对各 hctx 的 `queue_rq_srcu` 或 RCU 执行 grace period；所有正常 dispatch/direct issue 的 `queue_rq` 调用均在对应 hctx RCU/SRCU 读侧区间内。因此正常 quiesce 会等待已进入 `dm_mq_queue_rq` 的回调返回，封闭 895→908 窗口。发现一处可疑边界：`dm_mq_stop_queue:96–102` 若 `blk_mq_queue_stopped(q)` 为真会直接返回；而 `blk-mq.c:1484–1508` 明确说明 stopped hw queue 不保证 drain/quiesce。但当前尚无证据表明 swap 时 DM queue 处于 stopped 状态。
- **解释**：正常 quiesce 路径否决了简单的 895→908 竞态。`stopped` 与 `quiesced` 混用是潜在同步缺口，但不能在缺少现场状态时宣称为此次根因。需检查 request 是否存在晚到/重复完成，使 pending 已经减掉但 stale softirq 仍访问旧 `tio`。
- **下一步**：解析 orig/clone request 的状态、tag、时间和 end_io 关系，检验晚到或重复完成假设。

### Step 4.7：检查原请求与 clone 的运行时状态

- **目的**：判断 faulting softirq 是正常首次完成，还是已经结束/重排队后的晚到或重复完成。
- **待验证假设**：request 的状态、tag、end_io_data 或时间字段可能显示它已被完成、重用，或 clone 与 orig 生命周期不一致。
- **预期信号**：DWARF 给出 request 关键字段偏移；解析两个地址后可比较 state/tag、q、end_io、end_io_data、start_time 等。
- **命令**：先执行 `struct -o request` 获取实际字段名和偏移，再按字段解析 `orig=ffff9ff42a3f18c0` 与 `clone=ffff9ff862cf9600`。
- **实际结果**：`struct -o request` 给出实际布局。orig：`q=ffff9ff872c0a700`、sector 388402176、tag 124、start_time_ns `69474411890753356`、atomic_flags 3、data_len 0、errors 0。clone：`q=ffff9fed57ab09c0`、相同 sector、tag 21、start_time_ns `69474411890772762`、atomic_flags 3、data_len 0、errors 0、`end_io=end_clone_request`、`end_io_data=ffff9ff42a3f1a40`。两者开始时间相差约 19.4 微秒。命令反复报告某个无关地址的 `page excluded`，属于 partial dump 读取限制。
- **解释**：clone→tio 回指正确，orig/clone 时间和字段一致，没有直接显示请求已被完全重用或长时间滞留。结合 panic dmesg 时间待精算，I/O 很可能只运行了几十毫秒。当前无足够证据支持“双完成/晚到很久”的替代解释，但 atomic_flags 的语义仍需谨慎。
- **下一步**：取得完整内核日志，精确定位 panic 时间，并检查崩溃前的存储/iSCSI/SCSI 事件。

## Step 5 — 建立时间线和 iSCSI 触发证据

### Step 5.1：导出完整内核日志

- **目的**：建立不受关键词选择偏差影响的完整日志基线，获得 panic 时间戳和此前系统事件。
- **待验证假设**：vmcore 保存了足够完整的 ring buffer，可覆盖崩溃前存储路径变化、iSCSI session/connection 事件和 panic trace。
- **预期信号**：`log` 完整返回到 `crash>`；transcript 中包含 panic 的精确 monotonic 时间戳及此前日志。
- **命令**：`log`
- **实际结果**：完整 `log` 成功返回。panic 精确时间为 `[69474411.952107]`。`scsi host11112: iSCSI Initiator over TCP/IP` 出现在 `[69474335.486168]`（约 76.47 秒前）；同一 host 的 LUN 0–8 随后出现。LUN 1–8 在 `[69474362.72–63.05]` 同步 cache，随后 `[69474366.19–66.42]` 再次枚举并 attach，距 panic 约 45.5 秒。日志确认模块包含 `iscsi_tcp/libiscsi/scsi_transport_iscsi` 与 `dm_multipath`。
- **解释**：iSCSI 事件存在性门槛通过，且发生了显著的设备/path 变化。但目前没有日志直接显示 faulting dm-19 使用 host11112 的哪一块盘，也没有直接记录 multipath table reload；时间相邻不能单独证明触发。
- **下一步**：把 orig/clone 的 `rq_disk` 映射到磁盘名，确认 faulting I/O 的 device-mapper 设备和底层 path 是否属于 host11112。

### Step 5.2：识别原请求与 clone 的磁盘

- **目的**：建立 iSCSI 事件与 faulting I/O 的对象同一性，避免把其他 LUN 的 attach 事件误认为触发。
- **待验证假设**：orig `rq_disk` 是 dm-19，clone `rq_disk` 是某个 SCSI `sdX` path；如果该 path 属于 host11112，才进入下一层因果检查。
- **预期信号**：`gendisk` 显示明确 `disk_name`、major 和 first_minor。
- **命令**：分别解析 `ffff9ff99b7d2800`（orig）和 `ffff9fe872286c00`（clone）的 `gendisk.disk_name,major,first_minor`。
- **实际结果**：orig `rq_disk` 解析为 `dm-19`（major 253, minor 19）；clone `rq_disk` 解析为 `nvme38n1`（major 259, first_minor 55），不是 `sdX`。
- **解释**：faulting I/O 此刻实际选择的是 NVMe path，而非 iSCSI/SCSI path。因此“iSCSI I/O 自身完成时直接触发 fault”受到明确反证。iSCSI 仍可能通过给同一 multipath map 增删 path、促成 table reload 而间接触发生命周期 bug，必须检查 dm-19 的 path group 是否包含 host11112 新设备或同一存储标识。
- **下一步**：加载 dm_multipath DWARF，解析 `private=ffff9f8c1029a400` 的 path group 和当前 path。

### Step 5.3：加载 dm_multipath 类型并解析 map 私有对象

- **目的**：取得 dm-19 的全部 path group/pgpath，判断新 iSCSI LUN 是否属于同一 map，以及 faulting clone 的 selected path。
- **待验证假设**：当前 multipath 对象可读，包含当前/可用 path 列表；selected path 可连接到 `nvme38n1`，列表中是否存在 `sdX` 将决定 iSCSI 对象同一性。
- **预期信号**：`mod -s dm_multipath` 成功，`struct -o multipath` 给出 `priority_groups/current_pgpath` 等字段偏移。
- **命令**：`mod -s dm_multipath`，随后 `struct -o multipath`。
- **实际结果**：模块符号加载成功。当前 multipath 私有对象 `ffff9f8c1029a400` 反向指向当前 `ti=ffffbd16abbd2040`，有 1 个 priority group、2 条 valid path；`current_pgpath=ffff9ff7591decc0`、`flags=0`、queue mode 为 MQ request-based。DWARF 给出 `priority_group.pgpaths@48` 和 `pgpath.path@32`。
- **解释**：当前 map 内只有两条有效 path。需要逐条映射磁盘名；如果都是 NVMe，则新 iSCSI sd 设备不属于 faulting map，iSCSI 对象同一性门槛失败。
- **下一步**：解析唯一 priority group 的 pgpaths 链表，并把每个 `dm_path.dev->bdev->bd_disk` 映射到磁盘名。

### Step 5.4：遍历 dm-19 的两条 path

- **目的**：确认当前 multipath map 的全部底层设备，判断是否包含 host11112 的 iSCSI `sdX`。
- **待验证假设**：priority group 链表有两项，current path 对应 faulting clone 的 `nvme38n1`；另一项可能是 NVMe 或 SCSI path。
- **预期信号**：priority_group 给出 pgpaths next/prev；两个 pgpath 的 `dm_path.dev` 可进一步解析到 gendisk 名称。
- **命令**：解析 `priority_group@ffff9fe80adffcc0`，再按链表地址解析两个 `pgpath`、`dm_path`、`dm_dev` 和 `gendisk`。
- **实际结果**：唯一 priority group 有两条 active path、fail_count 均为 0。两条 `dm_dev` 分别是 `259:54` 和 `259:55`；沿 bdev→gendisk 映射为 `nvme37n1` 与 `nvme38n1`。current_pgpath 是 `259:54/nvme37n1`，faulting clone 使用另一条 `259:55/nvme38n1`。当前 map 不包含任何 `sdX`。
- **解释**：iSCSI 作为同一底层 I/O path 直接触发得到反证：dm-19 全部 path 均为 NVMe。iSCSI 仍可能通过 multipathd 对 uevent 的全局 reconfigure 间接促成 dm-19 table reload，但需要 userspace/内核 table ioctl 的中间证据。
- **下一步**：检查 multipathd 任务现场和全机栈中是否存在 DM table load/suspend/resume/destroy 路径。

### Step 5.5：检查 multipathd 与并发 table 操作现场

- **目的**：寻找 iSCSI uevent → multipathd reconfigure → dm-19 reload 的中间证据，并检查崩溃时是否仍有 table 操作在进行。
- **待验证假设**：multipathd 可能正处于或刚完成 device-mapper ioctl；若另一 CPU 栈仍在 table swap/destroy，可直接闭合并发窗口。
- **预期信号**：`ps` 找到 multipathd PID；其 `bt` 或全 CPU 栈出现 dm ioctl/suspend/swap/destroy。若任务睡眠且无相关栈，只能说明进程存在。
- **命令**：`ps | grep multipathd`，取得 PID 后 `bt <pid>`；再用 `bt -a` 检查并发内核栈。
- **实际结果**：`ps` 显示大量 multipathd 线程（TGID 36204）。抽查 PID 2652 在 futex wait；较新 PID 80510 在 `dm_wait_event → dev_wait → dm_ctl_ioctl` 等待 DM 事件。`bt -a` 过滤 `dm_swap_table/__bind/dm_table_destroy/do_resume/dm_suspend/dm_mq_queue_rq` 无匹配，崩溃瞬间没有 CPU 正在这些路径。
- **解释**：确认 multipathd 活跃且有大量 DM event watcher，但没有直接抓到 dm-19 reload 的执行栈。table destroy 很可能已在 panic 前完成，静态栈缺失并不反证 reload；同样也不能把 iSCSI→全局 reconfigure 当成已证明。iSCSI 专项暂定 `inconclusive`：直接 I/O path 已排除，间接促成缺中间 ioctl/map 证据。
- **下一步**：检查 dm-19 request_queue/hctx 在崩溃时是否处于 `STOPPED`，验证 `dm_mq_stop_queue` 的 stopped-vs-quiesced 缺口是否具有现场支持。

## Step 6 — 验证同步缺口与替代解释

### Step 6.1：检查 dm-19 blk-mq queue/hctx 状态

- **目的**：验证 `dm_mq_stop_queue:98` 早退条件在现场是否成立；该条件把 hw queue `STOPPED` 当作已经 quiesced，但 blk-mq 源码明确两者语义不同。
- **待验证假设**：dm-19 至少一个 hctx 的 `BLK_MQ_S_STOPPED` 位为 1，导致 suspend 可能跳过 `blk_mq_quiesce_queue()` 和 RCU/SRCU 等待。
- **预期信号**：request_queue 给出 hw context 数组；相关 `blk_mq_hw_ctx.state` bit 0 为 1。若全部为 0，则静态现场不支持该早退条件（但不能回溯 swap 时状态）。
- **命令**：解析 `request_queue@ffff9ff872c0a700` 的 `nr_hw_queues/queue_hw_ctx/queue_flags/mq_ops`，再解析各 hctx 的 `state/flags`。
- **实际结果**：dm-19 queue 有 1 个 hctx，`mq_ops=dm_mq_ops`。hctx `ffff9ff99b7d6c00` 的 `state=0`、`flags=9`；queue_flags 未置高位 `QUEUE_FLAG_QUIESCED`。崩溃现场既非 STOPPED，也非 QUIESCED。
- **解释**：现场不支持 `dm_mq_stop_queue()` 因 STOPPED 早退这一具体条件；不过该状态可能在 reload/resume 后改变，静态状态不能完全回溯。当前只能将其列为源码缺口候选，不能作为已确认根因。
- **下一步**：检查指定源码仓库和 RPM 补丁历史中与 immutable_target、blk-mq quiesce、table reload 相关的修订，再回到 vmcore 验证。

### Step 6.2：检查本地源码/补丁历史

- **目的**：寻找该版本之后或发行版补丁中对同一路径的修复说明，帮助识别精确竞态窗口；仍以 vmcore 为最终证据。
- **待验证假设**：本地 git/history 或 RPM patch 中存在针对 `dm_mq_queue_rq`、`immutable_target`、quiesce/table swap 的修订。
- **预期信号**：提交或 patch 明确修改对象获取、queue quiesce、pending/drain 或 target 生命周期。
- **本地只读命令**：检查源码 git 状态与相关文件历史，并在当前 kernel-rpm 中检索相关补丁文本。
- **实际结果**：指定源码树中的 `dm_mq_queue_rq()` 在 `drivers/md/dm-rq.c:889–927`：895 行读取 `md->immutable_target` 后直接检查 target busy、908 行增加 pending、916 行保存 `tio->ti`；该函数完全没有检查 `DMF_BLOCK_IO_FOR_SUSPEND`。同一源码树只在 bio-based 路径等位置检查该 flag（`dm.c:1599,1620`），而 suspend 在 `dm.c:2536` 明确设置它。上游提交 `b4459b11e84092658fa195a2587aff3b9637f0e7`（“dm rq: don't queue request to blk-mq during DM suspend”）正是在 `md->immutable_target` 读取后增加 `test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)`，命中则返回 RESOURCE 让 blk-mq 重排队。提交说明：外部事件（例如 elevator switch、更新 `nr_requests`）可能在 DM suspend 中 unquiesce blk-mq，使请求在 suspend 窗口进入；补丁用于修复 `nr_requests` 更新与 dm-mpath suspend/resume 压测中的 kernel panic。当前 3.10 源码缺少该保护。
- **解释**：该修复精确解释了此前正常 quiesce 语义无法闭合的矛盾：`__dm_suspend()` 虽先设置 block flag、quiesce 并等待 pending 为 0，但 blk-mq queue 可被 DM 之外的事件重新 unquiesce；本版本 request-based `queue_rq` 不检查 block flag，新请求因此可在 pending drain 之后进入。它读取旧 `immutable_target`、增加 pending并把裸指针保存到 `tio->ti`。随后 `dm_swap_table()` 替换 target，`do_resume()` 销毁旧 table；底层 I/O 完成时仍解引用旧 `tio->ti`，形成此次未映射地址 fault。这一机制同时解释了：旧 target 地址具有正确分配几何、PTE=0、当前 target 已变化、请求只运行约 61 ms，以及正常 suspend 代码表面上本应 drain 的反证。
- **下一步**：检查崩溃对象的当前 flag/pending、日志中的硬件错误，并形成替代解释矩阵；上游补丁只用作源码机制交叉验证，根因仍须由本次 vmcore 独立证据支撑。

### Step 6.3：检查崩溃时 mapped_device 状态

- **目的**：确认 faulting md 在崩溃时已恢复为当前新 table，且仍有正常计数的在途请求；避免误写为“panic 时仍处于 suspend”。
- **待验证假设**：`md->immutable_target` 已是新 target，block-for-suspend 位已经清除；pending 包含 faulting I/O。
- **预期信号**：target/map 等于此前的当前对象，flags 不含 bit 0，pending 非零。
- **命令**：`struct mapped_device.flags,pending,immutable_target,map ffff9ff81b1b7000`
- **实际结果**：`flags=64`（bit 0 `DMF_BLOCK_IO_FOR_SUSPEND` 已清除），pending 两个方向计数为 `{2,0}`；`immutable_target=ffffbd16abbd2040`、`map=ffff9f8c1029bc00`，均为此前识别的新对象。
- **解释**：panic 时设备已经 resume，不能从最终 flag 直接观察早先竞态窗口；但“新 target 已生效 + 旧 target 已 unmap + faulting request 尚计入 pending”与“请求在 suspend 窗口闯入、table swap 后才完成”一致。pending=2 也反驳 fault 前已错误减掉当前请求计数的假设。
- **下一步**：筛查日志中的硬件错误或更早内核破坏迹象。

### Step 6.4：检查硬件内存错误和先行内核异常

- **目的**：评估随机内存损坏、MCE/EDAC/Memory Failure 或更早 kernel Oops 是否更合理地解释失效指针。
- **待验证假设**：若为硬件/广泛内存破坏，崩溃日志可能出现 MCE、Hardware Error、EDAC、Memory Failure、corruption 或先行 Oops。
- **预期信号**：关键词筛查返回独立于本次 panic 的硬件错误或先行异常；空结果则降低该替代解释概率，但不能绝对排除静默损坏。
- **命令**：`log | grep -Ei 'mce|machine check|hardware error|edac|memory failure|corrupt|BUG:|Oops:|Call Trace'`
- **实际结果**：仅返回本次 `[69474411.952107] BUG`、本次 Oops/Call Trace，以及模块列表中名称含 `skx_edac`；未发现 MCE、Hardware Error、Memory Failure、corruption 或先行 Oops 记录。
- **解释**：日志不支持硬件错误/广泛内存损坏。更重要的是失效指针具有精确 `dm_target` 页内偏移 `0x40`，其来源字段、当前替代对象和上游同路径修复都自洽；随机 bit flip/野指针难以同时解释这些结构性信号。静默硬件损坏不能用静态 dump 绝对排除，但证据权重显著低。
- **下一步**：汇总主根因和替代解释，结束只读 crash 会话。

### Step 6.5：结束本轮独立 crash 会话

- **目的**：形成清晰会话终点，确保 transcript 完整落盘并避免后续操作混入本轮证据。
- **待验证假设**：crash 可正常退出到远端 shell，pipe-pane transcript 可停止并校验。
- **预期信号**：`quit` 后出现 shell prompt 和结束标记；本地文件具有稳定 SHA-256。
- **命令/控制操作**：在 crash 中输出 `__T0144_CRASH_ANALYSIS_COMPLETE__`，执行 `quit`，在 shell 输出 `__T0144_CRASH_END__`；随后关闭 tmux pipe-pane。
- **实际结果**：crash 正常退出，结束标记时间为 `2026-07-29T14:22:11+08:00`。`crash-session.log` SHA-256 为 `d5ff1d02fa95fbc723720d8941265eee59a3307b4434aa50942904c945050f0a`。
- **解释**：本次独立会话具有明确开始/结束边界；全程只执行只读 crash 命令，未修改远端系统、内核或设备状态。
- **下一步**：生成研究报告、源码映射和 evidence manifest，进入 Check。

## 替代解释矩阵

| 候选解释 | 支持信号 | 反证/限制 | 判定 |
|---|---|---|---|
| suspend 窗口请求闯入，旧 table target 被 vfree 后完成回调 UAF | fault 指针来自 `tio->ti`；地址为未映射 PTE；与当前 target 不同但均为 `vmalloc_base+0x40`；源码缺少 block flag 检查；上游同路径补丁；请求时间横跨 table 更换 | 静态 dump 不能直接记录触发 unquiesce 的具体外部动作 | 高置信根因 |
| 普通 table reload 本身总会 UAF | reload、destroy 路径存在 | 正常 quiesce + pending drain 应保护在途请求 | 否决；必须叠加缺失的 suspend guard/外部 unquiesce |
| pending 提前递减或重复完成 | 理论上可让 suspend 过早返回 | fault 发生在 `dm_end_request/rq_completed` 前；panic 时 pending 仍为 2；orig/clone 字段与时间自洽 | 不支持 |
| 随机 NULL/野指针或 bit flip | fault 是非法指针 | 指针非 NULL且精确对应 `dm_target` 分配几何、旧/新对象关系及上游已知竞态 | 低概率 |
| partial dump 丢页 | dump 标记为 partial | `vtop` 显示 PTE=0，而非有效映射的物理页未保存 | 排除 |
| 硬件内存损坏 | 长 uptime、超大内存使其理论可能 | 日志无 MCE/EDAC 错误；结构化对象链和已知源码缺陷更强 | 无证据支持，不能绝对排除静默错误 |

## iSCSI 四层触发审查

1. **事件存在**：通过。panic 前约 76 秒创建 iSCSI host11112，约 45.5 秒前发生 LUN cache sync、重新枚举和 attach。
2. **对象同一**：不通过直接路径。faulting orig 是 `dm-19`，clone 是 `nvme38n1`；dm-19 当前两条 path 全是 `nvme37n1/nvme38n1`，不含任何 iSCSI `sdX`。
3. **状态转换连接**：未证实。iSCSI uevent 可能使 multipathd 全局 reconfigure，但 vmcore/日志没有记录 host11112 事件导致 dm-19 reload 的 ioctl 对象链；崩溃瞬间全机栈也没有 table swap/destroy。
4. **bug 时间窗**：底层 faulting I/O 约在 panic 前 61 ms 启动，且必然跨越旧 target 销毁窗口；但没有证据把 45 秒前的 iSCSI 事件连接到这 61 ms 内的 DM suspend/unquiesce。

**iSCSI 判定：`inconclusive`（直接触发已排除，间接促成未证实）**。不能把时间相邻或模块已加载当作因果；若“触发”特指 faulting I/O/path，则判定为 `not_triggered`。
