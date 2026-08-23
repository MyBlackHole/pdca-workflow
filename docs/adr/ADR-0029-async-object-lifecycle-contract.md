---
schema: pdca.adr/v1
id: ADR-0029
title: 异步对象生命周期统一契约 — 强销毁保证与一次性 API 收敛
status: Accepted
date: 2026-08-23
---

# ADR-0029: 异步对象生命周期统一契约

## 背景

backupstream 异步基础设施的所有权管理机制分散且互相独立：reactor post 回调有 6+ 个变体（post / post_priority / post_priority_kind / post_wait_priority / post_wait_priority_timestamped / post_wait_priority_observed[_kind][_owned]），所有权转移靠注释约定与 discard 回调；事件源 slot 复用依赖 generation 计数防 ABA；业务 runtime（tree/file/restore/exec/lane）各自维护布尔所有权标志（async_owned、owned_connection 等）与 force_destroy 手工拆卸路径。多套并存的管理逻辑导致调用方心智负担高，悬垂/泄漏风险靠纪律而非机制防范。

## 决策

1. **强销毁保证**：异步对象进入销毁流程后，其在途 post/定时器回调要么被安全丢弃（discard 路径）要么排空完成后才完成销毁——销毁后回调绝不派发。调用方无需在各回调内自行校验存活性。
2. **C 风格统一契约 + 守卫原语**：不引入智能指针或引用计数；把分散的 generation/discard/force_destroy 约定收敛为一套显式生命周期原语（统一 owned-post 协议、销毁栅栏、句柄校验守卫）。
3. **一次性替换删旧**：新契约落地后全部调用点切换到统一原语，旧 post 变体与散落所有权标志直接删除，不留兼容层；以编译错误保证无遗漏。
4. **热路径近零开销**：数据面热路径（文件传输 I/O、hash）零新增分配与原子操作；控制面允许纳秒级开销；既有 benchmark 基线不回退。
5. **组织方式**：父任务负责契约设计 + 核心原语落地，子任务按模块迁移（tree/file/restore/exec/lane/plain-ingress/tls-bridge/client-reactor），每子任务独立 PDCA 周期验收。

## 备选方案

- **refcount 句柄基建**（被否）：post/定时器持引用可硬保证存活，但为每个对象引入原子计数违背热路径近零开销约束，且用户已明确选择纯契约路线。
- **全面智能指针化**（被否）：改动面最大，风格转变剧烈，热路径原子开销不可接受。
- **渐进迁移保留旧 API**（被否）：旧变体继续存在即延续"多套管理逻辑"现状，与简化目标相悖。

## 后果

- 正面：调用方不再需要理解多套所有权协议；销毁正确性由机制而非纪律保证；API 面积收缩。
- 负面：一次性切换的提交体积较大；迁移期间需父子任务树协调；强销毁保证要求销毁路径处理在途回调排空/丢弃，核心 Reactor 实现复杂度上升。
