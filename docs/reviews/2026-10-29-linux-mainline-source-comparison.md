# Linux 主线源码与官方规范比对

日期：2026-10-29。用户要求继续完善 `linux-kernel-engineering`，读取本地最新主线实际代码并与官方规范比对；已授权将源码通过 Git 获取到用户 Documents 目录。

## 来源与范围

- 本地仓库：`/home/black/Documents/linux-mainline`。
- 实际 origin：`https://github.com/torvalds/linux.git`，分支 `master`。
- 完整提交：`c339f4010dea8b0d754f84ace70cd1b089878ef8`；提交时间 `2026-10-28T07:36:32-10:00`。
- 同轮从 `https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git` 查询的 `refs/heads/master` 与该提交一致。
- Makefile 声明 `7.3.0`，该提交标题为合并 `platform-drivers-x86-v7.4-1`；这是固定的主线开发快照，不能只看 Makefile 就等同于正式 v7.3 发布标签。
- 这是深度 1 的部分克隆，稀疏检出 24 个明确文件，不含完整历史/全量工作树。最初 Git 文件检出连接失败，所选文件随后从同一官方提交的 raw 端点补取，每份内容都与已克隆 Git tree 的 blob ID 比对后才写入对象库，再由 Git 检出；不是未经核验的文本副本。
- 文件及 blob 清单见 [源码清单](2026-10-29-linux-mainline-source-manifest.json)。`AGENTS.md` 在树中为指向 `README` 的链接，清单保留的是链接 blob，另列 README 正文。
- 清单界定获取与内容核验范围，代码理解限下列符号/章节，不表示逐行审计了这些大文件的全部实现。
- 已读文件与固定提交无内容差异。只读学习，不修改 Linux 源码，不构建/启动内核，不运行内核测试；没有写入 `/tmp` 的测试产物。

“最新”限定为本轮取得并核验的 master 快照，不保证之后远端不移动。浅历史也不能用于声称已完成历史回归调查。

## 逐项比对

### 1. 现代内核 C 的作用域清理

规范：[Scope-based cleanup helpers](https://docs.kernel.org/core-api/cleanup.html)。同提交 `Documentation/core-api/cleanup.rst` 第 7 行通过 kernel-doc 引用 `include/linux/cleanup.h`；规范正文实际位于该头文件第 9 行起，不能只读短入口文件。

实现与契约：`include/linux/cleanup.h` 的 `DEFINE_FREE`、`__free`、`no_free_ptr` 和 `return_ptr`；`include/linux/mutex.h:253` 的 mutex guard 定义。声明逆序、guard 的实际作用域及成功移交共同决定清理正确性。

特别注意：头文件第 119 行起的示例是**故意演示错误**，先声明需要持锁清理的对象、后声明 guard，会先解锁再清理；第 139 行起才是修正顺序。不能因为示例位于主线就照抄它。

结论：与官方规范一致。技能允许在目标树支持并接受时采用这些 C 机制，保留旧树/用户态的现有清理方式；用户禁止 C++ 库不等于禁止它们。作用域清理不替代异步退出协议。

### 2. mutex 的状态与对象存活是两项契约

规范：[Generic mutex subsystem](https://docs.kernel.org/locking/mutex-design.html)；本地 `Documentation/locking/mutex-design.rst:104` 起。

实现：`kernel/locking/mutex.c:560` 的 mutex_unlock kernel-doc 明确要求 mutex 活到函数返回；其快/慢路径不是对对象生命周期的统一隐式引用。

结论：完全一致。技能新增“观察到锁可获取不能证明旧 unlock 已结束访问”，防止把嵌入 mutex 的对象提前释放。现有允许合法 mutex 内睡眠的规则保留。

### 3. epoll 的缩锁有完整状态机

源码：`fs/eventpoll.c:80` 起说明可睡眠 `ep->mtx` 的用途；第 97 行起给出字段保护，第 131 行起描述 ready-list 状态机。`ep_start_scan:965` 在短暂持有 `ep->lock` 时转移 ready list 并切换扫描状态；`ep_done_scan:986` 合并期间到达的项目并退出扫描。

`ep_send_events:2128` 在整个扫描/交付期间仍持有 **ep->mtx**，只在批量遍历期间放开 **ep->lock**。删除保护、回调进入溢出链表、失败/未处理项回队都是协议的一部分。

第 1523 行注释使用“we can hold no locks”的宽泛措辞；与第 2146 行实际取得的 mutex 对照，不能按字面升级为禁止所有锁。源码注释也要结合实际保护范围核对。

结论：它是“缩小特定队列锁范围，同时维持其他保护和交接协议”的实际例子，不能概括成完全无锁，更不能把 copy_to_user 前一律释放所有 mutex 当成规范。技能将这一比对方法明确化，不复制 epoll 的内部实现到普通队列。

### 4. socket 记账覆盖在途对象，但流控阈值不是严格配额证明

源码：`net/core/sock.c:2772` 的 `skb_set_owner_w` 挂接析构责任并按 `skb->truesize` 增加 `sk_wmem_alloc`；`sock_wfree:2717` 回收计量并参与 socket 的最后释放。`sock_alloc_send_pskb:3063` 结合发送阈值、错误、信号和等待分配。

可迁移的是“按实际分配成本计量，追踪在途存活，回收时归还”。源码中阈值检查和之后的分配/计量不能直接当作严格服务配额的原子预留算法；具体 socket 协议、锁和阈值允许的语义仍需单独调查。

结论：技能原有严格预算是任务需要硬上限时的工程设计，不伪称内核所有队列都采用同一硬上限机制。

### 5. mempool 的保留量不等于最大内存用量

源码：`mm/mempool.c:543` 的契约及 `mempool_alloc_noprof:558`：先调用底层分配器，失败后取保留元素；`mempool_alloc_from_pool:425` 按标志区分等待与非等待路径。

结论：`min_nr` 不是最大活跃对象数，非等待场景也可能失败。技能新增这一区别：池的进展保证、耗尽处理和业务硬额度分别设计，不能用“已采用 mempool”替代内存预算或死锁证明。

### 6. GFP、系统资源归属和 RT 限制

规范：[Memory allocation guide](https://docs.kernel.org/core-api/memory-allocation.html)；本地 `Documentation/core-api/memory-allocation.rst:47` 起区分 KERNEL、NOWAIT、ATOMIC 及用户触发分配的 accounting。实现契约见 `include/linux/gfp_types.h:306` 起；NOWAIT 与 ATOMIC 的保留资源和上下文语义不能混为一谈。

同一头文件指出 NMI 和 RT 下显式禁抢占/raw 锁等限制。[RT differences](https://docs.kernel.org/core-api/real-time/differences.html) 进一步说明分配与释放涉及内部锁。该 RT 文档本地补取遇到 HTTP 429，未计入本地已读清单；本条 RT 结论依据已读头文件及在线官方页，不冒充本地该页核验。

两份在线官方页对于传统非 RT 原子分配的标志示例措辞不同：分配指南区分 NOWAIT 与有理由使用保留资源的 ATOMIC，RT 差异页为解释背景使用 ATOMIC。采用时应按标志与目标上下文契约判断，不把背景示例变成唯一允许值；这里只记录差异，不声称已验证所有架构的分配器路径。

技能新增系统计量与服务预算的区别，避免局部字节上限被误当成 memcg/kmem 归属保障。

### 7. 回收工作项的进展需要依赖图

规范：本地 `Documentation/core-api/workqueue.rst:214` 的 WQ_MEM_RECLAIM，以及 [Workqueue](https://docs.kernel.org/core-api/workqueue.html)。实现：`kernel/workqueue.c:4015` 的 `check_flush_dependency` 检查回收相关任务等待没有相应保障的队列。

结论：有保留元素不代表有执行该工作项的上下文，有 rescuer 也不代表没有锁/资源循环。技能要求同时核对内存资源、工作项执行资源与等待关系，而不是无条件加入某个 flag。

### 8. devm 不代替停止活动工作

源码：`drivers/base/devres.c:540` 的逆序释放，及 `devres_release_all:558` 摘取资源后在资源锁外执行释放。实际调用例子 `drivers/input/misc/gpio-vibra.c` 使用 devm 资源，但 `gpio_vibrator_close:93` 和 suspend 路径仍显式取消 work 并停止设备。

结论：支持技能原有“自动资源管理不消除回调生命周期责任”。本次没有读取 input core 的全部 close/remove 契约，不能仅凭这个驱动就证明其所有并发路径或所有类似驱动均安全。

### 9. 新 helper 与构建语义必须分开确认

`include/linux/slab.h:1117` 起提供类型化的对象、数组与柔性数组分配 helper，部分接口默认 GFP_KERNEL，并配套大小/计数字段处理。目标树提供它们并不代表旧树也提供，调用简短也不代表上下文适用。

当前 Makefile 第 819 行仍声明 `-std=gnu11`。不能仅从某个头文件里的词法写法推断全树语言标准，更不能将内核宏和编译环境直接用于用户态 C 风格 C++。

## 技能修订与验证边界

技能升级 1.1.0 → 1.2.0：新增固定来源/证据分层的比对方法，补充 C 作用域清理、mutex 完整解锁期间存活、mempool 保留量与硬上限、accounting、RT 和回收进展，以及类型化分配 helper 的版本/默认标志检查。C++ 不使用 C++ 库的约束保留。

修改前独立应用基线 `/root/mainline_skill_baseline` 在四个场景中已能给出正确技术判断，包括 cleanup 顺序、mutex 存活、系统计量和旧树边界。本轮补充属于将源码/官方依据显式纳入技能，而非声称基线已经复现错误输出。

修订后 `/root/mainline_skill_retest` 只读取技能，独立处理以下六个请求；未向其提供预期答案或本报告：

| 请求 | 实际应用结果 |
| --- | --- |
| 现有 C 函数先声明需持锁清理的对象、后声明 guard，新增失败出口；禁止 C++ 库 | 指出逆序错误，先 guard 后初始化资源，成功移交，保留 C 清理机制 |
| A 正在 mutex_unlock，B 已能获取锁便准备释放容器 | 拒绝以锁空闲证明存活，要求保护覆盖 unlock 返回及其他使用者 |
| 用户可控内核分配已有服务额度，是否免查系统计量 | 区分准入预算和 memcg/kmem 归属，核对已有计量及目标配置 |
| 旧树无新 helper、个别驱动与文档示例不同 | 保留旧树可用机制，固定版本并核对契约、调用者及反例，拒绝凭个例推广 |
| RT raw 锁内改 ATOMIC 并采用 min_nr=64 的 mempool，声称活跃分配最多 64 | 拒绝该推论，要求可用上下文及独立额度，保留量不是上限 |
| 仿 epoll 摘链后把禁止并发删除的对象 mutex 也解锁 | 要求逐把核对保护，保留或补齐存活/字段同步和重新合并协议，不将队列锁外等同完全无锁 |

只读独立证据审查 `/root/mainline_evidence_review` 复读了技能、报告及获准的对应本地符号，未发现阻断性技术问题；其指出的 epoll 注释措辞补强点已经根审查核实并纳入本报告。它未独立核对远端最新性、下载过程、基线响应或在线 RT 页面，这些不冒充独立审查覆盖。

机械事实核验：24 个本地文件/链接内容重新计算的 Git blob ID 与清单及固定 tree 全部吻合；这些源码路径相对 HEAD 无内容差异。技能格式、Markdown 本地链接及提交差异检查通过。上述结果是静态/文档应用证据，不等价于实际并发实现、内核行为或性能验证。

本报告是精确选点的静态比对，不是整个内核的安全审计、构建测试或性能证明；没有对未读调用者、历史版本或架构作通过声明。
