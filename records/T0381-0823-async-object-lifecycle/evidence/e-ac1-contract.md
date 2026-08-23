# AC-1 证据：统一守卫原语落地与核心自迁移

## 变更范围

- src/reactor.hpp：新增 `reactor_post_spec_t`（统一提交规格）、`reactor_post_flag_t`（WAIT / HIGH_PRIORITY 位标志）、`reactor_lifecycle_t` / `reactor_guard_t` 守卫类型及五个守卫函数声明。
- src/reactor.cpp：
  - 原 `reactor_post_priority_impl` 与 `reactor_post_wait_priority_impl` 合并为单一 `reactor_post_enqueue_impl`（flags 参数区分阻塞背压路径），消除两套并行入队协议。
  - 新增 `reactor_post_submit()` 统一入口 + `reactor_post_spec_init()`。
  - 旧 8 个 post 变体全部改为 `reactor_post_enqueue_impl` 薄封装，行为等价保留（expand 契约）。
  - 新增生命周期守卫实现：try_enter（CAS acquire）/ exit（release 减计数）/ begin_destroy（置位）/ destroy_wait（退避轮询）。
- src/work_pool.cpp：完成回发路径迁移到 `reactor_post_submit`（原 owned+observed+kind 变体调用点）。
- src/reactor_group.cpp：`reactor_group_post` 迁移到 `reactor_post_submit`。
- tests/reactor_lifecycle_stress_test.cpp：新增，8 个行为/竞争测试。

## 强销毁保证语义

- 提交成功 = 所有权转移恰好一次；destroy 放弃派发时 discard 恰好一次；提交失败所有权留在调用方且 discard 绝不执行（测试 2/3 断言）。
- 业务对象嵌入 `reactor_lifecycle_t`：回调窗口 guard_try_enter 固定存活，begin_destroy 后新窗口被拒，destroy_wait 排空在途窗口后释放——销毁后回调绝不触碰已释放内存（测试 6/7/8 断言）。

## 热路径开销

- 守卫进入/退出各一次原子 RMW（acquire/release），位于回调粒度而非字节路径；数据面传输与 hash 零新增分配/原子操作。
