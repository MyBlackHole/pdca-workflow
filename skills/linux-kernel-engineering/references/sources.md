# 官方资料索引

整理日期：2026-10-29。以下链接用于查规范与 API；在线文档持续变化，不绑定本 skill 到“最新内核”。实践优先级：用户/项目要求 → 目标树 `Documentation/` 与子系统约定 → 匹配版本的官方资料 → 在线通用参考。遇到差异检查源码声明、实现与调用者，注明适用版本，不猜测 API 可用性。

本 skill 是选择性工程提炼，不复制手册，也不主张 Linux 内核的每一种技术都适合每个用户态项目。

## 风格与协作

- [Linux kernel coding style](https://docs.kernel.org/process/coding-style.html)：内核 C 风格、控制流、命名和清理原则。
- [Development process](https://docs.kernel.org/process/development-process.html)：子系统协作与开发流程。
- [Submitting patches](https://docs.kernel.org/process/submitting-patches.html)：单个逻辑变更、自包含说明、性能取舍及补丁准备。
- [Stable API nonsense](https://docs.kernel.org/process/stable-api-nonsense.html)：稳定用户接口与不保证稳定的内核内部接口的区别。
- [Deprecated interfaces](https://docs.kernel.org/process/deprecated.html)：旧接口、分配算术和 BUG/WARN 的使用边界。

## 并发与生命周期

- [Lock types and rules](https://docs.kernel.org/locking/locktypes.html)：锁类别、嵌套、PREEMPT_RT 差异。
- [Atomic types](https://docs.kernel.org/core-api/wrappers/atomic_t.html)：各操作的原子性与排序语义。
- [Volatile considered harmful](https://docs.kernel.org/process/volatile-considered-harmful.html)：volatile 不替代同步。
- [Adding krefs](https://docs.kernel.org/core-api/kref.html)：发布前取引用、查找与存活保护。
- [What is RCU?](https://docs.kernel.org/RCU/whatisRCU.html)：发布、读侧保护、宽限期与回收。
- [Workqueue](https://docs.kernel.org/core-api/workqueue.html)：threaded/BH 队列及取消、flush 等 API 契约。
- [Generic mutex subsystem](https://docs.kernel.org/locking/mutex-design.html)：mutex 语义及 unlock 调用期间的对象存活约束。
- [How realtime kernels differ](https://docs.kernel.org/core-api/real-time/differences.html)：RT 的上下文变化及分配/释放、等待的限制。

## 内存、设备与接口

- [Memory allocation guide](https://docs.kernel.org/core-api/memory-allocation.html)：分配类型、GFP 与失败处理。
- [Scope-based cleanup helpers](https://docs.kernel.org/core-api/cleanup.html)：内核 C 作用域清理、声明逆序、guard 与所有权移交。
- [GFP masks from FS/IO context](https://docs.kernel.org/core-api/gfp_mask-from-fs-io.html)：NOFS/NOIO 作用域与回收递归约束。
- [Managed device resources](https://docs.kernel.org/driver-api/driver-model/devres.html)：devres 生命周期与资源释放。
- [Dynamic DMA mapping guide](https://docs.kernel.org/core-api/dma-api-howto.html)：DMA 地址、方向、映射和一致性。
- [Bus-independent device access](https://docs.kernel.org/driver-api/device-io.html)：MMIO 与设备访问接口。
- [ioctl interfaces](https://docs.kernel.org/driver-api/ioctl.html)：新命令、布局、时间戳、compat 和错误约定；新接口优先参考这份资料。
- [(How to avoid) Botching up ioctls](https://docs.kernel.org/process/botching-up-ioctls.html)：历史经验和反例；时间等具体类型选择以目标树与较新的接口文档为准。
- [Kernel hacking guide](https://docs.kernel.org/kernel-hacking/hacking.html)：常见上下文及 uaccess 入门；含历史内容，现代上下文细节应对照目标树。
- [printk basics](https://docs.kernel.org/core-api/printk-basics.html)：日志级别、格式及使用方式。

## 验证与语言

- [Kernel testing guide](https://docs.kernel.org/dev-tools/testing-overview.html)：KUnit 与 kselftest 的职责。
- [Checkpatch](https://docs.kernel.org/dev-tools/checkpatch.html)、[Sparse](https://docs.kernel.org/dev-tools/sparse.html)、[KCSAN](https://docs.kernel.org/dev-tools/kcsan.html)：检查范围和局限。
- [Rust for Linux general information](https://docs.kernel.org/rust/general-information.html)：no_std、目标树文档和 Rust 检查入口。
- [Rust atomics](https://doc.rust-lang.org/nomicon/atomics.html)：Rust 用户态原子和内存模型；不替代内核的具体抽象契约。
- [C++ draft: data races](https://eel.is/c++draft/intro.races)：语言级数据竞争和同步；即使代码只采用 C 风格，C++ 编译仍须遵守它的语义。

- [Linux close(2)](https://man7.org/linux/man-pages/man2/close.2.html)：错误后 fd 复用及不能盲目重试 close 的原因。
- [Linux write(2)](https://man7.org/linux/man-pages/man2/write.2.html)：短写、错误、持久性和返回约定。
- [Linux pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html)：pthread 的错误返回约定及线程共享状态。
- [Linux signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html)：异步信号安全函数与信号处理器约束。

用户态其他接口细节查目标系统的 man pages、libc 文档和 POSIX，例如 `pthread_cond_wait`、`pthread_condattr_setclock` 和 `read`。不要把内核 handler 的规则直接套给 libc 包装函数。
