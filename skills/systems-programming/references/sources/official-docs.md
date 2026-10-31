# 官方依据与覆盖映射

核对日期：2026-10-30。本轮比对对象是本地 `linux-7.3` 目录内本轮实际读取的获准文档与源码文件。未核实该目录的 Git 提交、Makefile 版本、上游来源或整树修改状态，因此不能据此称其为最新主线或已认证的完整 Linux 7.3.0 树。在线文档和目标树会变化，不绑定本技能到单一“最新内核”。实践优先级：用户明确要求 → 目标树 `Documentation/`、子系统约定和维护者要求 → 匹配版本官方资料 → 在线参考；上游贡献政策另按适用版本核对。差异结合声明、实现和调用者解释，记录版本与限制。

本技能把 Linux 内核工程经验作为强制工程基线。覆盖要求是：目标树文档总目录中的每个开发领域都必须有定位入口；任务涉及该领域时，AI **必须**读完适用的目标版本规范、子系统规则及相关声明/调用路径，并按其要求实现和验证。摘要和映射不能代替适用原文。Linux 文档自身仍在持续整理，因此不能声称任何固定摘要包含了所有版本、架构、硬件和子系统细节；未能从获准来源确认的要求必须列为未知，不能默默略过。链接存在、读过原文和实际运行验证是不同证据。

## 官方文档总目录的全域入口

按目标树 `Documentation/index.rst` 逐类定位。每项都是任务触发后必须走的入口；继续沿目标树的 `toctree` 找到具体章节，不得只读索引就宣称已经遵守规范。

| 官方文档领域 | 入口与覆盖范围 | AI 必须执行 |
| --- | --- | --- |
| 开发社区与上游流程 | `Documentation/process/index.rst`：开发过程、补丁与检查表、coding style、语言指南、社区政策、许可、回归/安全问题、maintainer handbook、deprecated API、syscall/ioctl 指引、AI/生成内容政策 | AI 参与 Linux 内核 bug 定位、复现或修复，以及准备上游变更时，按 [贡献流程](../workflows/kernel-contribution.md) 读取适用的完整原文；定位维护者并遵守子系统要求，不用本技能摘要替代政策正文 |
| 内核内部 API 与锁 | `Documentation/core-api/`、`Documentation/driver-api/`、`Documentation/locking/`、`Documentation/subsystem-apis.rst` | 识别真实子系统和回调上下文；读取其 API 契约、生命周期、错误和锁规则，再检查目标头文件、实现和调用者 |
| 子系统完整目录 | `Documentation/subsystem-apis.rst`：核心 `mm`、`power`、`scheduler`、`timers`、`locking`；人机接口 `input`、`hid`、`sound`、`gpu`、`fb`、`leds`；网络 `networking`、`netlabel`、`infiniband`、`mhi`；存储 `filesystems`、`block`、`cdrom`、`scsi`、`target`、`nvme`；其他 `accounting`、`cpu-freq`、`edac`、`fpga`、`i2c`、`iio`、`pcmcia`、`spi`、`w1`、`watchdog`、`virt`、`hwmon`、`accel`、`security`、`crypto`、`bpf`、`usb`、`PCI`、`misc-devices`、`peci`、`wmi`、`tee`，以及 `core-api`、`driver-api` | 对应任务必须沿目标树 `Documentation/<领域>/`、`MAINTAINERS`、该子系统已有模式及其 API 使用者核对；列表是完整路由目录，不代表本技能在此复制每个子系统的接口细节 |
| 开发工具与验证 | `Documentation/dev-tools/index.rst`、`Documentation/dev-tools/testing-overview.rst`：checkpatch、clang-format、Coccinelle、Sparse、KUnit、kselftest、KASAN、KMSAN、UBSAN、KCSAN、KFENCE、kmemleak、LKMM、kcov、KTAP 等；另有 `Documentation/kernel-hacking/`、`Documentation/process/debugging/`、`Documentation/fault-injection/`、`Documentation/trace/` | 按风险和改动选择适用工具；必须解释工具配置和结果能证明什么、不能证明什么，并按 [验证规则](../workflows/validation.md) 记录未运行项 |
| 文档与许可证 | `Documentation/doc-guide/index.rst`、`Documentation/process/license-rules.rst`、`Documentation/ABI/` | 修改文档或公开接口时核对 Sphinx、kernel-doc、ABI 分类/格式、许可和来源要求，并运行目标树对应文档检查 |
| 构建、配置与用户可见管理接口 | `Documentation/kbuild/`、`Documentation/admin-guide/`、`Documentation/admin-guide/reporting-issues.rst` | 构建/配置变更核对 Kbuild/Kconfig 和配置组合；新增管理接口或问题报告按对应流程阅读原文 |
| Linux 用户态 API | `Documentation/userspace-api/index.rst`、目标系统 man-pages、libc/POSIX 资料 | 跨内核/用户边界时必须区分 UAPI 契约与用户程序实现；内核编码风格不能替代 syscall、libc、POSIX、文件系统或协议的真实语义 |
| 随内核源码发布的用户态工具 | `Documentation/tools/index.rst` 及目标工具目录文档 | 修改 `tools/` 下程序时遵守该工具的语言、构建、测试及兼容约定，不把内核执行上下文套到用户态 |
| 固件与 Devicetree | `Documentation/firmware-guide/index.rst`、`Documentation/devicetree/index.rst` 及 bindings | 固件/ACPI/DT 变更必须核对 schema、绑定兼容、资源解析与相关子系统要求；不能只验证驱动 C 代码 |
| 架构相关规则 | `Documentation/arch/index.rst` 与具体 `Documentation/arch/<arch>/` | 汇编、内存模型、原子、缓存、ABI、异常/中断及屏障按目标架构逐项核对；不能由另一架构源码推断通用保证 |
| livepatch、Rust 与其他专门领域 | `Documentation/livepatch/`、`Documentation/rust/`、目标树其它专门文档；旧材料见 `Documentation/staging/` | 任务触及时读取专题全文和目标树实现；staging/历史材料先确认其仍适用，不把示例或过时说明当成当前规范 |
| 文档翻译 | `Documentation/translations/index.rst` 及对应语言目录 | 仅在修改翻译或多语言文档时核对翻译流程、源文档版本和同步要求；英文源文规范仍是技术契约依据 |

上述总目录用于确认没有跳过开发领域，不要求每次把整棵文档树全部装入上下文。任务开始时，AI 必须识别其改动涉及的领域并读取对应原文；发生跨子系统、跨架构或跨 UAPI 边界时，必须分别读取相关规范。

## 风格、文档与贡献

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [开发文档总目录](https://docs.kernel.org/process/index.html)、[Development process](https://docs.kernel.org/process/development-process.html) | [贡献流程](../workflows/kernel-contribution.md)：上游贡献时核对完整流程、行为准则及子系统/维护树的附加要求；社区专门政策按实际主题读取 |
| [Linux kernel coding style](https://docs.kernel.org/process/coding-style.html) | [编码与文档](../principles/coding-and-documentation.md#linux-内核编码与文档)：提炼 C 风格、类型、宏与条件编译；原型、汇编等完整细则专项核对，不能凭摘要声称全文符合 |
| [Kernel-doc](https://docs.kernel.org/doc-guide/kernel-doc.html) | [编码与文档](../principles/coding-and-documentation.md#linux-内核编码与文档)：C 全局/导出接口与类型文档；源文件和公开头检查由验证资料维护 |
| [Submitting patches](https://docs.kernel.org/process/submitting-patches.html)、[stable 规则](https://docs.kernel.org/process/stable-kernel-rules.html) | [贡献流程](../workflows/kernel-contribution.md)：补丁系列、标签、修订、维护者和回补；只有实际准备对应贡献时启用 |
| [AI Coding Assistants](https://docs.kernel.org/process/coding-assistants.html)、[生成内容规范](https://docs.kernel.org/process/generated-content.html) | [AI 归属与人工认证](../workflows/kernel-contribution.md#ai-归属与人工认证)：AI 参与内核 bug 定位/复现/修复时完整读取适用的 AI 指引与开发流程；准备 Linux 贡献时另核对 DCO、工具来源披露及适用的归属标记。必读原文须完整读取，滚动渲染页不能证明目标政策版本 |
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
| [Linux Kernel Memory Consistency Model (LKMM)](https://docs.kernel.org/dev-tools/lkmm/index.html) | [内核并发内存模型证明义务](../principles/memory-and-locks.md#内核并发内存模型的证明义务)：自定义屏障、发布协议和无锁算法触发 litmus 推理；区分说明性示例与可执行 litmus |
| [Memory allocation](https://docs.kernel.org/core-api/memory-allocation.html)、[GFP FS/IO scopes](https://docs.kernel.org/core-api/gfp_mask-from-fs-io.html) | [内核资源](../environments/kernelspace.md#内存资源与设备)：GFP、回收、计量及保留；预算设计另由 [内存与锁](../principles/memory-and-locks.md#内存先所有权和预算再分配器) 维护 |
| [Scope-based cleanup](https://docs.kernel.org/core-api/cleanup.html) | [C 作用域清理](../environments/kernelspace.md#c-作用域清理)：采用 helpers 前核对作用域、声明顺序与移交 |
| [Completions](https://docs.kernel.org/scheduler/completion.html)、[Driver basics](https://docs.kernel.org/driver-api/basics.html) | [等待与停止](../environments/kernelspace.md#等待per-cpu-与停止)：wait/completion、kthread 启动/合作停止及 task 存活、超时和轮次复用、timer 最终停止；调用上下文和具体版本按原文/声明核对 |
| [this_cpu operations](https://docs.kernel.org/core-api/this_cpu_ops.html) | [per-CPU](../environments/kernelspace.md#等待per-cpu-与停止)：单次本地操作、指针迁移、远端访问及复合状态的不同保证 |

## MM、IRQ 与电源管理

| 主题与官方原文 | 技能内责任与触发条件 |
| --- | --- |
| [Process Addresses](https://docs.kernel.org/mm/process_addrs.html)、[Page Tables](https://docs.kernel.org/mm/page_tables.html)、[Physical Memory](https://docs.kernel.org/mm/physical_memory.html) | [进程地址与页表生命周期](../environments/kernelspace.md#进程地址与页表生命周期)：触及 VMA、fault、PTE/PMD、zap、页表回收或 backing page 时分别核对稳定性、锁与架构 helper；通用规则不替代 MM 专项原文 |
| [Generic IRQ handling](https://docs.kernel.org/core-api/genericirq.html) | [IRQ 与 PM 生命周期](../environments/kernelspace.md#irq-与-pm-生命周期)：区分 hardirq/threaded handler 的同步范围，核对共享中断、设备中断源及等待上下文 |
| [Device Power Management Basics](https://docs.kernel.org/driver-api/pm/devices.html) | [IRQ 与 PM 生命周期](../environments/kernelspace.md#irq-与-pm-生命周期)：设备依赖顺序、noirq 限制、回调跳过和 suspend/resume 期间设备/IRQ/DMA 静止；具体设备策略另读子系统规范 |
| [Lockdep design](https://docs.kernel.org/locking/lockdep-design.html) | [内核锁约束](../environments/kernelspace.md#锁内存序与生命周期)：涉及 IRQ-safe/unsafe 类别、锁嵌套、反向顺序或 lockdep assertion 时读取原文并验证实际调用链 |

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
| [Kernel testing](https://docs.kernel.org/dev-tools/testing-overview.html)、[KUnit](https://docs.kernel.org/dev-tools/kunit/index.html)、[Checkpatch](https://docs.kernel.org/dev-tools/checkpatch.html)、[Sparse](https://docs.kernel.org/dev-tools/sparse.html)、[Coccinelle](https://docs.kernel.org/dev-tools/coccinelle.html)、[KASAN](https://docs.kernel.org/dev-tools/kasan.html)、[KCSAN](https://docs.kernel.org/dev-tools/kcsan.html) | [改动验证](../workflows/validation.md)：按内存安全、竞争、接口和改写风险选择工具；区分采样/覆盖边界，工具无报告不代替证明 |
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
