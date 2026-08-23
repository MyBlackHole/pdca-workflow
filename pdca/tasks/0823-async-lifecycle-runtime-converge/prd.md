# 异步生命周期收敛：业务 runtime 所有权标志与 force_destroy 收编

parent: T0381（优化异步对象生命周期处理）
dependencies: T0382（TLS 域迁移）、T0383（plain 域迁移）

## 问题陈述

- **现状**: 业务 runtime 模块散布手动所有权管理：agent_exec_io_pump 的 async_owned/owned_connection 布尔标志、agent_exec_runtime(10 处 post)、agent_lane_group(16 处 post)，以及 tree/file/restore/data_lane/lane_group 各自的 force_destroy 手工拆卸路径（agent_reactor_teardown 统一入口）。
- **目标**: 业务 runtime 的所有权标志收敛到统一契约语义；子 Reactor 拆卸走销毁栅栏（强销毁保证），force_destroy 语义等价保留（强制停机模式）。
- **差距**: 标志未收编，拆卸未接栅栏。

## 边界

- 覆盖 exec/tree/file/restore/data_lane/lane_group 六个业务域 + teardown 入口。
- 不动核心 Reactor 实现、旧 API 删除。
- 强销毁保证语义由父任务原语提供，本任务只做调用侧收敛。

## 验收标准

- [ ] AC-1: async_owned/owned_connection 等布尔所有权标志被守卫原语替代或消除（grep 计数为 0 或仅存等价性注释）。
- [ ] AC-2: 子 Reactor 优雅销毁路径全部经销毁栅栏；强制停机 force_destroy 行为与现状等价（既有集成测试不改动断言即通过）。
- [ ] AC-3: 全仓编译零警告通过，完整测试套件绿。
- [ ] AC-4: sanitizer 全开下 exec/tree/file/restore 集成套件通过。

## Seam 分析

### 声明的测试接缝

- seam: tests/plain_exec_shared_reactor_integration.sh -> src/agent_exec_runtime.cpp, src/agent_exec_io_pump.cpp
- seam: tests/plain_restore_reactor_integration.sh -> src/agent_restore_reactor.cpp
- seam: tests/tls_tree_reactor_integration.sh -> src/agent_tree_runtime.cpp
