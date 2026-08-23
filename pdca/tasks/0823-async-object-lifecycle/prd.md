# 优化异步对象生命周期处理

## 问题陈述

- **现状**: backupstream 异步基础设施（Reactor / work_pool / 业务子 Reactor）的所有权管理机制多套并存、互相独立：
  - reactor post 回调有 6+ 个变体（post / post_priority / post_priority_kind / post_wait_priority / post_wait_priority_timestamped / post_wait_priority_observed[_kind][_owned]），所有权转移靠注释约定与 discard 回调参数；
  - 事件源 slot 复用依赖 generation 计数防 ABA；timer 与 source 各有一套销毁约定；
  - 业务 runtime（tree/file/restore/exec/lane）各自维护布尔所有权标志（async_owned、owned_connection 等）与 force_destroy 手工拆卸路径。
  - 调用方必须理解并正确组合多套协议，心智负担高；悬垂/泄漏风险靠纪律而非机制防范。
- **目标**: 以一套统一的 C 风格生命周期契约 + 守卫原语收敛全部异步对象管理逻辑：强销毁保证（对象销毁后其回调绝不派发）、API 面积收缩、调用方零所有权心智负担。
- **差距**: 无统一原语；旧 API 变体未删除；业务侧散落所有权标志未收编。

## 解决方案

按 ADR-0029 执行：

1. **父任务（本任务）交付统一守卫原语**：在 Reactor 核心落地统一 owned-post 协议（单一入口覆盖优先级/观察/owned-discard 维度）、销毁栅栏（destroy 时排空或安全丢弃在途回调后才完成销毁）、句柄校验守卫；reactor/work_pool 自身调用点先行迁移。
2. **子任务逐模块迁移**：tree / file / restore / exec / lane / plain-ingress / tls-bridge / client-reactor 各业务模块的布尔所有权标志与 force_destroy 收敛到统一契约，每个子任务独立 PDCA 周期验收。
3. **收尾删除旧 API**：全部调用点迁移完成后删除旧 post 变体与废弃标志，以编译错误保证无遗漏。
4. **验证手段**：新增生命周期不变量压力测试；sanitizer（thread/address/leak）全开跑集成套件；既有 benchmark 基线不回退。

## 用户故事

1. 作为 Reactor 调用方，我只需通过单一 owned-post 入口提交回调并声明 discard 函数，无需分辨多个 wait/timestamped/observed 变体——编译期即确定唯一正确用法。
2. 作为业务 runtime 作者，我销毁一个子 Reactor 时无需先手工排空在途回调或检查布尔标志——销毁栅栏保证回调不再到达已释放内存。
3. 作为维护者，我在 sanitizer 全开的压力测试下并发创建/销毁对象与提交回调，不出现 use-after-free、泄漏或二次释放。
4. 作为性能负责人，我对照既有 benchmark 基线确认数据面吞吐与控制面延迟无可测量回退。

## Seam 分析

### 测试接缝

- 新增生命周期不变量压力测试：并发注册/注销源与定时器、并发 post 回调与对象销毁竞争，在 thread+address+leak sanitizer 下验证无 UAF/泄漏/二次释放。
- 复用现有 Reactor 集成套件（callback/plain_*/tls_* integration.sh）验证功能等价。
- 性能基线以 benchmark_reactor_post、benchmark_work_pool_completion 等既有脚本为口径。

### 声明的测试接缝

- seam: tests/reactor_lifecycle_stress_test.cpp -> src/reactor.cpp, src/work_pool.cpp
- seam: tests/callback_reactor_integration.sh -> src/reactor.cpp
- seam: tests/work_pool_init_integration.cpp -> src/work_pool.cpp

## 实现决策

- 保持 C 风格 API；不引入智能指针/refcount（ADR-0029）。
- 数据面热路径零新增分配与原子操作；控制面允许纳秒级开销。
- 一次性替换策略：迁移完成后旧变体直接删除，不留兼容层。

## 验收标准

- [ ] AC-1: Reactor 核心落地统一守卫原语（单一 owned-post 入口覆盖优先级/观察/owned-discard 维度 + 销毁栅栏强保证），reactor/work_pool/reactor_group 内部调用点完成自迁移，旧 API 保留（expand 契约测试断言旧接口存在）。
- [ ] AC-2: 新增生命周期不变量压力测试 tests/reactor_lifecycle_stress_test.cpp，在 thread/address/leak sanitizer 全开下并发创建/销毁 × post 竞争无 use-after-free、泄漏、二次释放。
- [ ] AC-3: callback_reactor_integration.sh 与 work_pool_init_integration.cpp 行为等价通过。
- [ ] AC-4: benchmark_reactor_post、benchmark_work_pool_completion 基线无可测量回退（数据面热路径零新增分配/原子操作）。
- [ ] AC-5: 子任务树 T0382–T0385 创建并登记依赖，全部子任务归档后父任务方可收口；旧 post 变体最终删除（grep 计数为 0）。

## 范围外

- plain 路径整体 Reactor 化实施（归 0815-plain-reactor-converge 蓝图后续任务）。
- SBT 模块网络层改造（归 0819-sbt-rpc-session 系列）。
- 协议字节布局与帧语义变更。

## 备注

- 本任务为父子任务树的父任务；子任务拆解见 P4 产出，子 PRD 各自含独立验收标准。
- 强销毁保证要求 Reactor 销毁路径区分"排空后销毁"与"立即销毁+丢弃"两种模式（对应优雅停机与强制停机），实现时保留现有 force_destroy 语义等价性。
