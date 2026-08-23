# 异步生命周期收尾：删除旧 post 变体，全局验证与基线对照

parent: T0381（优化异步对象生命周期处理）
dependencies: T0382、T0383、T0384

## 问题陈述

- **现状**: 全部调用点已迁移至统一守卫原语，但旧 post 变体（post/post_priority/post_priority_kind/post_wait_priority 及 timestamped/observed/owned 派生变体）仍在 reactor.hpp/cpp 中保留。
- **目标**: 删除全部旧变体与废弃所有权标志，以编译错误保证无遗漏引用；产出全局 sanitizer 验证与性能基线对照结论。
- **差距**: 旧 API 未删除，全局终验未做。

## 边界

- 仅删除已被替代的旧 API 与死代码；不新增功能。
- 全局验证覆盖完整测试套件 + benchmark 基线对照。

## 验收标准

- [ ] AC-1: 旧 post 变体符号在 src/ 中 grep 计数为 0；全仓编译通过证明无遗漏引用。
- [ ] AC-2: thread/address/leak sanitizer 全开跑完整集成套件绿。
- [ ] AC-3: 新增生命周期不变量压力测试（并发创建/销毁 × post 竞争）在 sanitizer 下通过。
- [ ] AC-4: benchmark_reactor_post、benchmark_work_pool_completion 等既有基线无可测量回退（对照报告落盘 evidence）。

## Seam 分析

### 声明的测试接缝

- seam: tests/reactor_lifecycle_stress_test.cpp -> src/reactor.cpp, src/work_pool.cpp
