# 异步生命周期契约迁移：plain/ingress/lane 域

parent: T0381（优化异步对象生命周期处理）

## 问题陈述

- **现状**: plain 域模块（backup_agent、agent_plain_ingress、client_data_lane_runtime、agent_lane_registry）共约 48 处 reactor post/timer 调用点，仍使用旧的多变体 post API 与注释约定所有权。
- **目标**: 全部调用点迁移到统一生命周期守卫原语，功能行为等价。
- **差距**: 调用点未切换。

## 边界

- 仅迁移上述四个 plain 域文件的 post/timer 调用点。
- 不动 TLS 域、业务 runtime、旧 API 删除。
- 迁移后跑完整测试保持绿。

## 验收标准

- [ ] AC-1: 上述四文件中旧 post 变体调用点数为 0（grep 验证）。
- [ ] AC-2: 全仓编译零警告通过，完整测试套件绿。
- [ ] AC-3: plain_*_integration.sh 全部通过，行为与迁移前等价。
- [ ] AC-4: thread/address/leak sanitizer 构建下 plain 集成套件通过。

## Seam 分析

### 声明的测试接缝

- seam: tests/plain_tree_reactor_integration.sh -> src/backup_agent.cpp, src/agent_plain_ingress.cpp
- seam: tests/plain_data_lane_reactor_integration.sh -> src/client_data_lane_runtime.cpp, src/agent_lane_registry.cpp
