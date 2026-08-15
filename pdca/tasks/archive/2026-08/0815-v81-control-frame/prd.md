# v81 架构演进：后续控制帧非阻塞化

## 问题陈述

- **现状**: v80 仅对「业务前握手」做了非阻塞隔离（ingress 持有 fd 至 HELLO+认证+首个完整操作）。首个操作提交后，TREE/FILE/System RPC/后续 control-mux 仍由阻塞 worker 全程持有，慢操作可占死 worker。
- **目标**: 实现 ROUND80 标记的 next bottleneck——公共非阻塞前端在认证后继续保留后续控制帧，解析出完整 work-ready 请求后再分派阻塞 worker；不复制 TREE/FILE 状态机、不削弱每会话有序性。
- **差距**: 后续控制帧非阻塞化未实现；数据面（Data Lane）保持现状仅验证；协议兼容性保持，必要时新增能力位。

## 解决方案

1. 扩展非阻塞 ingress：HELLO 认证后，后续 TREE/FILE/System RPC/control-mux 帧仍由前端非阻塞解析，仅将完整 work-ready 操作分派给阻塞 worker（延续 v80 preface 移交模式）。
2. 每会话有序性保持：单会话的帧解析→分派顺序不变。
3. EXEC 维持 v79/v80 既有 shard 移交，不做重构。
4. 数据面（Data Lane）保持既有 Reactor-owned+worker pool 架构，仅验证并发正确与吞吐不回归。
5. 协议向后兼容；若需新能力位，通过既有协商降级与跨版本互操作验证。

## Seam 分析

### 测试接缝
- 新增集成回归：HELLO 后分片发送后续控制帧、背压、慢会话不占 worker、超时、断连重试、会话有序。
- 复用既有：plain_ingress_integration.sh（分片 HELLO/首帧）、session_pool_integration.sh、protocol_version_integration.sh、跨版本互操作。

### 声明的测试接缝
- seam: tests/v81_control_frame_integration.sh -> src/agent_plain_ingress.cpp
- seam: tests/plain_ingress_integration.sh -> src/agent_plain_ingress.cpp
- seam: tests/benchmark_data_path.sh -> src/agent_tree_runtime.cpp

### 验收可测性
- 回归脚本 PASS/FAIL；慢会话场景断言线程数不随 stalled 会话增长；跨版本互操作 PASS；基准对比表（对照 T0290 基线）。

## 用户故事

1. 作为备份管理员，我希望客户端不发数据时不消耗业务 worker，以便慢客户端不耗尽 worker 池。
2. 作为开发者，我希望单会话不长期占死一个 worker，以便控制面并发稳定。

## 实现决策

- 沿用 v80 preface 移交模式的既有概念（preface 携带 negotiated limits/capabilities/首操作），扩展为「认证后每帧继续由 ingress 持有、work-ready 才分派」。
- 每会话有序性：以会话为单位的提交顺序保证，不跨会话重排。
- 新能力位若引入，遵循既有 CAP_ 协商机制，旧对端未设置时不发送。
- 架构决策同步记入 ADR。
- 数据面不改，仅验证。

## 测试决策

- 回归测行为：分片重构、背压、有序、超时、断连、慢会话资源隔离；不测实现细节。
- 现有先例：plain_ingress_integration.sh、session_pool_integration.sh、benchmark_data_lanes.sh。

## 验收标准

- [ ] `tests/v81_control_frame_integration.sh` 通过：HELLO 认证后分片发送后续控制帧可正确重构并分派，会话有序性保持。
- [ ] 慢客户端场景：不发送完整操作的会话不消耗业务 worker（线程数不随 stalled 会话增长）。
- [ ] 数据面并发验证：多通道并发传输结果正确，吞吐不低于 T0290 记录的 v80 基线 97%。
- [ ] 跨版本互操作：新客户端↔旧 Agent、旧客户端↔新 Agent 均通过既有互操作测试（新能力位协商降级正确）。
- [ ] 资源改善：相对 v80 基线，控制面会话线程数峰值下降 ≥50%，RSS 不上升。
- [ ] 既有全部回归测试（TREE/catalog/data-lane/System RPC/会话池/EXEC/生产）保持通过。

## 范围外

- 不做 TREE/FILE 事务状态机非阻塞重写。
- 不做 EXEC 事件域重构。
- 不做数据面每-session 线程改事件驱动重构。
- 不做持久状态 schema 迁移（schema 81 不迁移，沿用 no-migration）。
- 不刷新滞后文档。
