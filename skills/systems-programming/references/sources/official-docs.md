# 官方依据与覆盖映射

核对日期：2026-10-30（本轮专项：规范入口与贡献政策版本、kthread/workqueue 与用户态等待/I/O；其余主题沿用前次依据，按任务重新核对）。在线文档持续变化，不绑定本技能到“最新内核”。实践优先级：用户/项目要求 → 目标树 `Documentation/` 与子系统约定 → 匹配版本官方资料 → 在线参考；当前上游贡献政策另按其生效范围核对。差异结合声明、实现和调用者解释，记录版本与限制。

本表映射工程提炼和专项读取责任，不声称已将所有 Linux 文档、子系统细节或所有版本完整编入技能。**规则提炼**由对应资料维护；**专项核对**表示任务触及时必须读取目标原文及必要源码后才能作相应结论。链接存在、已经读到和已经运行验证是不同证据。按本次主题选择行，不全量加载本表链接。

## 风格、文档与贡献

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [开发文档总目录](https://docs.kernel.org/process/index.html)、[Development process](https://docs.kernel.org/process/development-process.html) | [贡献流程](../workflows/kernel-contribution.md)：上游贡献时核对完整流程、行为准则及子系统/维护树的附加要求；社区专门政策按实际主题读取 |
| [Linux kernel coding style](https://docs.kernel.org/process/coding-style.html) | [编码与文档](../principles/coding-and-documentation.md#linux-内核编码与文档)：提炼 C 风格、类型、宏与条件编译；原型、汇编等完整细则专项核对，不能凭摘要声称全文符合 |
| [Kernel-doc](https://docs.kernel.org/doc-guide/kernel-doc.html) | [编码与文档](../principles/coding-and-documentation.md#linux-内核编码与文档)：C 全局/导出接口与类型文档；源文件和公开头检查由验证资料维护 |
| [Submitting patches](https://docs.kernel.org/process/submitting-patches.html)、[stable 规则](https://docs.kernel.org/process/stable-kernel-rules.html) | [贡献流程](../workflows/kernel-contribution.md)：补丁系列、标签、修订、维护者和回补；只有实际准备对应贡献时启用 |
| [AI Coding Assistants](https://docs.kernel.org/process/coding-assistants.html)、[生成内容规范](https://docs.kernel.org/process/generated-content.html) | [AI 归属与人工认证](../workflows/kernel-contribution.md#ai-归属与人工认证)：Linux 贡献中的 DCO、工具来源披露、适用政策要求的归属标记和人工提交；该流程的必读原文须完整读取，滚动渲染页不能证明目标政策版本 |
| [Licensing rules](https://docs.kernel.org/process/license-rules.html) | [许可证与来源](../environments/kernelspace.md#许可证与来源)：文件 SPDX、UAPI 例外、模块信息与来源；不推广为用户态项目的 GPL 要求 |
| [Handling regressions](https://docs.kernel.org/process/handling-regressions.html)、[Security bugs](https://docs.kernel.org/process/security-bugs.html)、[Threat model](https://docs.kernel.org/process/threat-model.html) | [贡献流程](../workflows/kernel-contribution.md#回归与安全问题) 和 [安全分类](../workflows/security-review.md#linux-内核问题分类)：拟报告时完整核对版本、证据、分流及材料处理政策 |

## 构建与配置

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Linux Kernel Makefiles](https://docs.kernel.org/kbuild/makefiles.html)、[Kconfig Language](https://docs.kernel.org/kbuild/kconfig-language.html) | [构建与依赖](../workflows/build-and-dependencies.md#linux-kbuild-与-kconfig)：依赖、n/m/y、对象与选项作用域；配置或构建变化时核对目标树语法和符号可达性 |
| [Patch submission checklist](https://docs.kernel.org/process/submit-checklist.html) | [内核验证](../workflows/validation.md#内核构建与文档检查)：适用配置矩阵、独立输出、架构、文档及调试检查；声明上游检查完成前逐项对照，缺少条件如实记录 |

## 并发、生命周期与资源

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Lock types](https://docs.kernel.org/locking/locktypes.html)、[Generic mutex](https://docs.kernel.org/locking/mutex-design.html)、[Realtime differences](https://docs.kernel.org/core-api/real-time/differences.html) | [内核锁约束](../environments/kernelspace.md#锁内存序与生命周期)：类型、嵌套、RT 上下文和 unlock 存活；改变锁或上下文时专项核对 |
| [Atomic types](https://docs.kernel.org/core-api/wrappers/atomic_t.html)、[Volatile](https://docs.kernel.org/process/volatile-considered-harmful.html) | [同步设计](../principles/memory-and-locks.md#锁先减少共享再缩小临界区)：发布/反向交接与可见性；具体操作和 LKMM 排序由目标原文/源码核对 |
| [Adding krefs](https://docs.kernel.org/core-api/kref.html)、[Workqueue](https://docs.kernel.org/core-api/workqueue.html) | [生命周期](../principles/memory-and-locks.md#生命周期与退出协议) 与内核环境：取得引用、threaded/BH 和异步停止；具体 callback/取消语义专项核对 |
| [Sequence counters/seqlock](https://docs.kernel.org/locking/seqlock.html)、[What is RCU](https://docs.kernel.org/RCU/whatisRCU.html)、[RCU 与模块卸载](https://docs.kernel.org/RCU/rcubarrier.html) | [复杂读侧同步](../environments/kernelspace.md#复杂读侧同步)：采用这些机制前核对写者、抢占/读者上下文、家族、指针及回调回收条件 |
| [Memory allocation](https://docs.kernel.org/core-api/memory-allocation.html)、[GFP FS/IO scopes](https://docs.kernel.org/core-api/gfp_mask-from-fs-io.html) | [内核资源](../environments/kernelspace.md#内存资源与设备)：GFP、回收、计量及保留；预算设计另由 [内存与锁](../principles/memory-and-locks.md#内存先所有权和预算再分配器) 维护 |
| [Scope-based cleanup](https://docs.kernel.org/core-api/cleanup.html) | [C 作用域清理](../environments/kernelspace.md#c-作用域清理)：采用 helpers 前核对作用域、声明顺序与移交 |
| [Completions](https://docs.kernel.org/scheduler/completion.html)、[Driver basics](https://docs.kernel.org/driver-api/basics.html) | [等待与停止](../environments/kernelspace.md#等待per-cpu-与停止)：wait/completion、kthread 启动/合作停止及 task 存活、超时和轮次复用、timer 最终停止；调用上下文和具体版本按原文/声明核对 |
| [this_cpu operations](https://docs.kernel.org/core-api/this_cpu_ops.html) | [per-CPU](../environments/kernelspace.md#等待per-cpu-与停止)：单次本地操作、指针迁移、远端访问及复合状态的不同保证 |

## 数据结构与表示

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Linked lists](https://docs.kernel.org/core-api/list.html)、[XArray](https://docs.kernel.org/core-api/xarray.html) | [容器与身份](../principles/data-and-interfaces.md#容器与身份协议)：选择访问结构、侵入式节点、safe 遍历的范围、查找与对象存活；采用具体结构前专项核对 |
| [Kernel API](https://docs.kernel.org/core-api/kernel-api.html)、[snprintf(3)](https://man7.org/linux/man-pages/man3/snprintf.3.html) | [数据与缓冲](../principles/data-and-interfaces.md#数据表示与缓冲)：字符串/字节、实际写入与所需长度、有符号错误和解析；内核与 libc 的实际接口分别核对 |

## 接口、设备与子系统

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Stable API nonsense](https://docs.kernel.org/process/stable-api-nonsense.html)、[ioctl interfaces](https://docs.kernel.org/driver-api/ioctl.html)、[Botching up ioctls](https://docs.kernel.org/process/botching-up-ioctls.html) | [UAPI](../environments/kernelspace.md#uapiioctl-与不可信输入)：稳定外部契约、布局、compat、copy 和命令语义；历史 ioctl 经验以目标树及现代接口文档为准 |
| [Kernel hacking guide](https://docs.kernel.org/kernel-hacking/hacking.html)、[Deprecated interfaces](https://docs.kernel.org/process/deprecated.html) | 内核环境：上下文与旧接口的辨识线索；含历史内容，使用前核对目标树，不能直接推广旧例子 |
| [DMA guide](https://docs.kernel.org/core-api/dma-api-howto.html)、[Device I/O](https://docs.kernel.org/driver-api/device-io.html) | [内核资源](../environments/kernelspace.md#内存资源与设备)：地址、映射、方向、同步与 MMIO；涉及硬件访问时专项核对 |
| [Device drivers](https://docs.kernel.org/driver-api/driver-model/driver.html)、[Devres](https://docs.kernel.org/driver-api/driver-model/devres.html)、[Runtime PM](https://docs.kernel.org/power/runtime_pm.html) | [设备专项](../environments/kernelspace.md#设备时间与专项接口)：probe/defer、资源、解绑及 PM 的任务触发检查 |
| [Delay/sleep](https://docs.kernel.org/timers/delay_sleep_functions.html)、[Timekeeping](https://docs.kernel.org/core-api/timekeeping.html) | [时间与等待](../environments/kernelspace.md#设备时间与专项接口)：新增延迟、超时或时钟使用前核对上下文、精度和目标 API |
| [Sysfs](https://docs.kernel.org/filesystems/sysfs.html)、[Netlink introduction](https://docs.kernel.org/userspace-api/netlink/intro.html) | [专项接口](../environments/kernelspace.md#设备时间与专项接口)：具体属性/family、文档、交互与生命周期专项核对 |
| [VFS](https://docs.kernel.org/filesystems/vfs.html)、[mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html) | [文件操作与映射](../environments/kernelspace.md#文件操作poll-与映射)、[用户态](../environments/userspace.md#进程与事件循环)：poll 登记、非阻塞、flush/release、file/VMA 与设备资源的不同生命周期；mmap 入口演进按目标树处理 |
| [Kernel subsystem documentation](https://docs.kernel.org/subsystem-apis.html) | 文件系统、块层、网络、调度、MM、BPF、设备树、总线等的定位入口；任务触及时读取目标子系统原文、声明及实际调用者。这些领域保留专项核对责任，不声称摘要覆盖全部实现约束 |

## 验证工具与内核语言

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Kernel testing](https://docs.kernel.org/dev-tools/testing-overview.html)、[Checkpatch](https://docs.kernel.org/dev-tools/checkpatch.html)、[Sparse](https://docs.kernel.org/dev-tools/sparse.html)、[KCSAN](https://docs.kernel.org/dev-tools/kcsan.html) | [改动验证](../workflows/validation.md)：KUnit/kselftest、工具能力与局限；按风险和目标支持选择，工具无报告不代替证明 |
| [Printk basics](https://docs.kernel.org/core-api/printk-basics.html) | [可观测性](../environments/kernelspace.md#可观测性框架与-rust)：日志、动态调试和限速；具体格式符/地址披露专项核对 |
| [Rust general information](https://docs.kernel.org/rust/general-information.html)、[Rust coding guidelines](https://docs.kernel.org/rust/coding-guidelines.html) | [内核环境](../environments/kernelspace.md#可观测性框架与-rust)、[编码与文档](../principles/coding-and-documentation.md#linux-内核编码与文档)：no_std、树内抽象、FFI、rustdoc 与 Safety；新增 Rust 代码前核对目标树支持 |

## 用户态与语言

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [close(2)](https://man7.org/linux/man-pages/man2/close.2.html)、[write(2)](https://man7.org/linux/man-pages/man2/write.2.html)、[recv(2)](https://man7.org/linux/man-pages/man2/recv.2.html)、[send(2)](https://man7.org/linux/man-pages/man2/send.2.html)、[pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html) | [用户态](../environments/userspace.md)：返回值、短操作、空数据报、SIGPIPE、错误与线程；具体调用契约查目标系统 man pages/libc/POSIX |
| [POSIX 条件变量时钟](https://man7.org/linux/man-pages/man3/pthread_condattr_getclock.3p.html)、[glibc 显式时钟等待](https://sourceware.org/glibc/manual/latest/html_node/Waiting-with-Explicit-Clocks.html) | [线程等待](../environments/userspace.md#线程信号与取消)：截止时间与条件变量/等待接口使用相同时钟；默认与可选能力按目标平台核对，不能沿用历史 LinuxThreads 页面对现代实现的属性描述 |
| [signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html)、[fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)、[epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html) | [进程与事件循环](../environments/userspace.md#进程与事件循环)：fork/exec、信号、事件触发与 fd 存活；涉及这些路径时读取对应原文 |
| [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html)、[rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html) | [持久性](../environments/userspace.md#文件更新与持久性)：替换、文件/目录同步与失败阶段，最终保证另核对目标文件系统/存储契约 |
| [Rust atomics](https://doc.rust-lang.org/nomicon/atomics.html)、[C++ data races](https://eel.is/c++draft/intro.races) | 用户态语言模型与 FFI；C 风格 C++ 仍服从 C++ 语义，Rust 库选择不受 C++ 禁库规则影响；不能替代内核的具体抽象契约 |

维护或评估覆盖时，按上述官方入口检查新增/变更主题，给它确定唯一规则位置、适用条件和针对性场景。未读的专门规范、未采用的子系统以及未运行的配置都保留为明确边界，不用链接数或场景数计算“全部 Linux 规范通过率”。
