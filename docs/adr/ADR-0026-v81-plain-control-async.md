---
schema: pdca.adr/v1
id: ADR-0026
title: v81 后续控制帧非阻塞化 — plain 控制面 work-ready 分派
status: Accepted
date: 2026-08-15
---

# ADR-0026: v81 后续控制帧非阻塞化

## 背景

v80 仅隔离「业务前握手」：plain ingress 持有 fd 至 HELLO+认证+首个完整操作帧，之后整 fd 移交阻塞 worker，worker 在 `session_dispatch_loop` 内阻塞 `recv` 等待后续帧。TREE/FILE/System RPC 与后续 control-mux 的**等待阶段**仍长期占死 worker——慢客户端可耗尽有界 worker 池（ROUND80 known boundary）。

TLS 控制面已有完整蓝图：Reactor 持有 fd，每帧封装 work item 提交 work_pool，worker 完成经 reactor 回发响应，无 per-session 阻塞线程。

## 决策

1. **v81 目标**：plain 控制面认证后，fd 不再整移交阻塞 worker；ingress 持续非阻塞解析后续控制帧，每个**完整 work-ready 操作帧**封装 work item 提交 work_pool，worker 完成后经 reactor 发送响应。会话有序性按会话保持。
2. **能力位协商**：新增能力位（如 `CAP_PLAIN_CONTROL_ASYNC`），旧对端未设置时不启用非阻塞分派，回退 v80 整 fd handoff。协议 RSP/3 帧类型与字节布局不变，向后兼容。
3. **数据面（Data Lane）保持现状**：Data Lane 已是 Reactor-owned + bounded worker，不重构，仅验证并发正确与吞吐不回归。
4. **EXEC 不变**：维持 v79/v80 既有共享 shard 移交，不重构。
5. **TREE/FILE 状态机不复制**：不将 TREE/FILE 事务状态机改为异步；仅控制面（PING/TIME/SYS 等单帧 work-ready 类）进入非阻塞分派。
6. **改造落点**：`agent_plain_ingress` 增加 work-ready 分派路径；plain 模式需初始化独立 work_pool（复用 TLS 的 `control_pool` 语义），`backup_agent.cpp` 相应扩展初始化。
7. **持久状态**：schema 81 沿用 no-migration，v80 持久状态被 v81 拒绝。

## 备选方案

- **仅设计文档不实现**：用户否决（要求完整实现 v81）。
- **控制面+数据面全非阻塞化**：数据面重构风险过高，用户选定「数据面保持+验证」。
- **不引入能力位、直接全量切换**：破坏跨版本互操作，否决；保留协商降级。

## 影响

- `agent_plain_ingress`：新增 work-ready 分派（work item 生命周期、响应回发、会话有序）。
- `backup_agent.cpp`：plain 模式初始化 work_pool。
- 新增集成回归：`tests/v81_control_frame_integration.sh`。
- 跨版本互操作回归（新客户端↔旧 Agent 双向）。
- 性能基线由 T0290 提供（threads/RSS/throughput）。
