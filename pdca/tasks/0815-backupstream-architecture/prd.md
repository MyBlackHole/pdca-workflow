# backupstream 80.0.0 实现架构分析 — 规格文档

## 问题陈述

- **现状**: backupstream 80.0.0 源码约 2.9 万行 C++，项目 `docs/` 下已有 `ARCHITECTURE.md`、`NETWORK_MODEL.md`、`ASYNC_CALLBACK_MODEL.md`、`REACTOR.md`、`CONTROL_REACTOR.md`、`TLS_REACTOR.md`、`DATA_LANES.md` 等文档，但部分文档版本标注滞后（`NETWORK_MODEL.md`、`REACTOR.md` 标注 30.0，实际已演进到 80.0.0）。没有一份面向当前 80.0.0 实现、统一覆盖网络架构、线程架构、事件架构及其交互的实现视角报告。
- **目标**: 产出一份与 80.0.0 源码一致的实现架构分析报告，清晰回答"网络如何分层、线程如何组织、事件如何流转"三大问题，并指出与既有滞后文档的差异。
- **差距**: 既有文档是演进历史记录而非当前统一视图；读者需从 ROUND*_REVIEW 和分散文档自行拼装当前架构。

## 解决方案

新建 `docs/ARCH_IMPLEMENTATION.md`，以概念级架构分层 + 源码证据点（`src/*.cpp|hpp` 引用）双轨呈现。覆盖：

1. **总体架构**：client(backupctl) / agent(backup-agent) 双端部署与职责、进程边界（backup-dirtyd 独立进程）。
2. **网络架构**：TCP/TLS 双路径；Agent 端非 TLS plain ingress 反应器（v80）→ 有界会话池 → EXEC 共享事件域两次移交；TLS 端独立 Reactor 入口 + Reactor Group 分片；数据通道（Data Lanes）与 TLS Reactor 状态机；控制通道复用；System RPC 根目录约束。
3. **线程架构**：事件线程（main reactor、Reactor Group N shards）、有界工作池（work_pool_t：control/lane/lane_cpu/tree）、弹性会话池（--session-workers ceiling + 压力创建/空闲回收）、EXEC 事件域 shard（--plain-exec-reactors）、客户端 data lane 线程与小文件写入线程。
4. **事件架构**：epoll 事件循环（reactor_t）的 token/generation 防失效机制、LT 模式、回调预算、HIGH/NORMAL 双优先级 post 队列、eventfd 唤醒、timerfd 逻辑定时器、interest 更新合并（50.0）、事件等待器（event_waiter_t，epoll/poll 双后端）与 pidfd 等待。
5. **关键路径源码级**：连接接受 → plain ingress 解析 HELLO/首个操作帧 → 恢复阻塞模式提交会话池 → EXEC 移交共享事件域；TLS 握手 → Reactor 分片亲和 → 数据通道流转。
6. **既有文档滞后差异清单**：逐项列出 `NETWORK_MODEL.md`、`REACTOR.md`、`ASYNC_CALLBACK_MODEL.md`、`CONTROL_REACTOR.md` 等与 80.0.0 源码不一致的点（如 NETWORK_MODEL 的"非 TLS 仍同步"描述已被 v80 ingress 取代）。
7. **存储/数据架构概述**（上下文级）：client-owned catalog、SQLite/LMDB、目录队列 + getdents64 游标、hardlink 追踪、resume-state/restore-state，仅概述其在整体架构中的位置，不深入。

## Seam 分析

### 测试接缝

- research 场景，无测试产物。分析正确性通过源码引用可核验。
- 报告证据点均为 `src/` 源码路径引用，可由人工或 grep 复核存在性与版本号。

### 声明的测试接缝

research 场景无测试产物，跳过。

### 验收可测性

- 每个 AC 均可独立判定：报告文件存在、覆盖维度齐全、含源码证据、含滞后差异清单、与既有文档版本标注核对。

## 用户故事

1. 作为项目读者，我想要一份与当前 80.0.0 源码一致的实现架构总览，以便快速理解系统如何工作。
2. 作为维护者，我想要网络/线程/事件三大维度的明确分层与流转说明，以便定位热路径与资源边界。
3. 作为新接手者，我想要"既有文档 vs 当前实现"差异清单，以便知道哪些旧文档已过期、以何为准。

## 实现决策

- 新建 `docs/ARCH_IMPLEMENTATION.md`（项目侧交付物）；既有演进历史文档不改动。
- 同一报告副本写入 PDCA 记录 `records/T0287-0815-backupstream-architecture/evidence/` 作为本任务证据。
- 分析以源码为唯一事实来源；文档仅作背景参考，不复制其断言。
- 网络架构重点刻画 80.0 新增的非阻塞 plain ingress（`agent_plain_ingress`）与"两次移交"路径；线程架构重点刻画弹性会话池与共享 EXEC 事件域；事件架构重点刻画 token/generation、双优先级 post、interest 合并。
- 报告使用 ASCII/mermaid 图 + 源码引用（`src/file.cpp:line` 或模块级引用），保证可核验。

## 测试决策

- research 场景，不做代码测试。
- 质量校验手段：报告包含的每个源码引用均可 grep 到实际文件；AC-5 用 grep 验证滞后差异清单中至少 3 项对应源码已有更新实现。

## 验收标准

- [ ] AC-1: 报告文件写入 `docs/ARCH_IMPLEMENTATION.md`，包含"总体架构/网络架构/线程架构/事件架构/关键路径/存储概述"六节
- [ ] AC-2: 网络架构节描述非 TLS plain ingress（v80）与 TLS Reactor 双路径，并各含至少 2 个源码引用
- [ ] AC-3: 线程架构节枚举至少 5 类线程/池（main reactor、reactor shard、work pool、会话池、EXEC 事件域），各含源码引用
- [ ] AC-4: 事件架构节描述 token/generation 防失效、HIGH/NORMAL 双优先级、eventfd 唤醒、interest 合并，各含源码引用
- [ ] AC-5: "既有文档滞后差异清单"列出至少 3 项差异，且每项差异对应源码已有更新实现（grep 可核验）
- [ ] AC-6: 报告含关键路径图（ASCII 或 mermaid），覆盖"接受 → ingress → 会话池 → EXEC 移交"
- [ ] AC-7: 报告副本写入 PDCA 记录 evidence 目录
- [ ] AC-8: 报告全文为中文，术语首次出现含英文原名

## 范围外

- 不修改任何 `src/` 源码、Makefile、CMakeLists。
- 不修改既有 `NETWORK_MODEL.md`、`REACTOR.md` 等演进历史文档内容。
- 不深入 LMDB/MDB_VL32 内部实现细节（仅概述其作为存储后端的位置）。
- 不做基准测试、不做性能断言。
- 不逐文件穷举全部 ROUND*_REVIEW 内容。

## 备注

- 事实核查：`NETWORK_MODEL.md`、`REACTOR.md` 头部标注 30.0，而 README 明确 v80 已引入非阻塞 plain ingress，故滞后差异清单以此为起点。
- 事件等待器 `event_waiter_t`（`src/event_wait.hpp`）提供 epoll/poll 双后端，是 v78 pidfd 等待之外的通用等待原语，报告需覆盖。
