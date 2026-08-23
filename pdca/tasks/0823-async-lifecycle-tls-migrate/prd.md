# 异步生命周期契约迁移：TLS 域

parent: T0381（优化异步对象生命周期处理）

## 问题陈述

- **现状**: TLS 域模块（tls_reactor、agent_tls_runtime、agent_tls_control_runtime、tls_sync_bridge）共约 55 处 reactor post/timer 调用点，仍使用旧的多变体 post API 与注释约定所有权。
- **目标**: 全部调用点迁移到父任务交付的统一生命周期守卫原语，功能行为等价。
- **差距**: 调用点未切换。

## 边界

- 仅迁移上述四个 TLS 域文件的 post/timer 调用点。
- 不动 plain 域（backup_agent/plain_ingress/data_lane/lane_registry）、业务 runtime（exec/tree/file/restore）、旧 API 删除（归收尾任务）。
- expand 阶段旧 API 仍在且可用；本批迁移后跑完整测试保持绿。

## 验收标准

- [ ] AC-1: 上述四文件中旧 post 变体调用点数为 0（grep 验证），全部经统一原语提交。
- [ ] AC-2: 全仓编译零警告通过，完整测试套件绿。
- [ ] AC-3: tls_*_integration.sh 全部通过，行为与迁移前等价。
- [ ] AC-4: thread/address/leak sanitizer 构建下 TLS 集成套件通过。

## Seam 分析

### 声明的测试接缝

- seam: tests/tls_reactor_state_machine.cpp -> src/tls_reactor.cpp
- seam: tests/callback_reactor_integration.sh -> src/reactor.cpp, src/tls_sync_bridge.cpp
