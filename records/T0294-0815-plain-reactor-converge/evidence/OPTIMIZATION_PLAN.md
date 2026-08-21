# backupstream plain 路径综合性能提升 — 优化方案

状态：方案设计（T0294），供后续实施任务作为蓝图。

## 一、现状与瓶颈

backupstream 80.0.0 的 Agent 存在两条并发路径，性能特性差异显著：

| 维度 | plain（非 TLS）路径 | TLS 路径 |
|------|-------------------|---------|
| 事件循环 | 单 Reactor（1 线程） | Reactor Group 分片（N 线程） |
| TREE | 阻塞 worker 同步 | tree_pool 异步 |
| 控制帧 | v81 起 reactor 侧 control_pool 异步 | control_pool 异步 |
| EXEC | 阻塞 setup + 共享 shard | Reactor 拥有，异步 |
| FILE PUT/GET | 阻塞 worker 同步 | lane + storage 异步 |
| blocking session worker | 弹性按需 | 0 |

plain 路径的核心瓶颈（源码实证）：

1. **单 Reactor 吞吐天花板**：plain 路径所有连接的 ingress 解析、控制帧渲染、PONG 响应均串行于单一 Reactor 线程。`reactor_group` 分片基建已存在，但仅 TLS 路径使用。
2. **业务帧整体占用阻塞 worker**：TREE/FILE/restore 的同步 handler 整个事务（可数秒）钉住一个弹性 worker。弹性池只能按需扩缩，无法让单个长事务并发切分。
3. **TREE 全局互斥**：同一根的并发 TREE PUT 被全程 `flock(LOCK_EX)` 串行化。
4. **非阻塞收益在 handoff 后丢失**：业务帧 handoff 到阻塞 worker 后，`session_dispatch_loop` 中的后续控制帧会退回阻塞路径同步执行。

## 二、基线数据（本机实测，方案"起点"）

采集命令：`tests/benchmark_control_plane.sh`、`tests/benchmark_data_path.sh`。

| 指标 | plain 当前值 |
|---|---|
| 控制面 32 并发 median | 48.49 ms |
| 控制面 p99_upper | 4.56 ms |
| 控制面 agent_threads | 7 |
| 数据面 PUT（256 MiB） | 595 MiB/s |
| 数据面 GET（256 MiB） | 562 MiB/s |
| 数据面 agent_threads | 8 |

对照基准：
- TLS 路径 blocking session worker 为 0（全异步）。
- v81 控制面判据基线（AC-5，双维度）：v80 median=48.97ms / p99=4.56ms / threads=4；v81 优化前 median=54.45ms / p99=12.03ms / threads=7。
- 阶段 C 目标参考：把 plain 的弹性阻塞 worker 数量级向 TLS 的 0 收敛。

## 三、分阶段改造设计

目标：吞吐（突破单 Reactor）、延迟（业务帧异步化）、线程/资源（阻塞 worker 收敛）综合提升。

### 阶段 A — plain ingress 接入 reactor_group 分片

- **风险等级**：低-中
- **预期收益**：突破单 Reactor 吞吐天花板；高并发会话下控制面与 ingress 处理并行化。
- **改造设计**：
  - 复用现有 `reactor_group` 基建（TLS 已在用）。
  - 将 plain ingress 从单 reactor 迁移到 N 个 shard，按 fd/会话 hash 分配归属。
  - 处理 accept/ingress 跨 shard 归属、connection_acquire 计数的分片化。
  - 保持 v81 控制帧异步分发与每会话保序语义（跨 shard 后 control_pool 完成回调投递到归属 shard）。
- **独立验证**：`benchmark_control_plane.sh` 高并发（如 256）下 median/p99 较单 Reactor 基线下降；`plain_ingress_integration.sh`、`v81_control_frame_integration.sh` 全绿。
- **验收信号**：grep `control-plane: concurrency=256` 行，p99/median 较单 Reactor 基线显著下降。

### 阶段 B — 业务帧异步化（核心）

- **风险等级**：中-高
- **预期收益**：TREE/FILE/restore 长事务不再钉住一个 worker，可并发切分；多个备份任务可并行推进。
- **改造设计**：
  - 复用 TLS 已有的异步执行域模型（`agent_tree_worker_run` + tree_pool、lane_pool 等）。
  - 将 plain 的 `handle_put_tree_stream` / FILE PUT-GET / restore 从阻塞 worker 迁移到异步 work pool 执行域。
  - 业务帧在 ingress 前端识别后，直接提交到对应 work pool，done 回调投递回归属 Reactor。
  - 必须保持：每会话排序（业务帧与 in-flight 控制响应保序）、流控（窗口）、取消语义，与现有行为等价。
- **独立验证**：`benchmark_data_path.sh`（吞吐不回归）、`v81_control_frame_integration.sh`、`plain_ingress_integration.sh`、TREE/catalog/restore 集成脚本全绿。
- **验收信号**：grep `data-path:` 行 PUT/GET MiB/s 不低于基线 97%；控制面并发下 agent_threads 不随会话数线性增长。
- **注意**：TREE 全局 flock 可在本阶段或单独子任务中改为更细粒度（按子目录/文件粒度），提升并发。

### 阶段 C — 阻塞 worker 收敛（收尾）

- **风险等级**：低（在阶段 B 落地后）
- **预期收益**：plain 的弹性阻塞 worker 池大幅收敛/归零，线程与资源占用向 TLS 路径对齐。
- **改造设计**：
  - 业务帧异步化后，弹性阻塞 session worker 池可大幅缩减；EXEC setup 保留既有阻塞 setup + 共享 shard handoff。
  - 以 TLS 路径的 blocking_session_workers=0 为目标，逐步收敛配置默认值。
- **独立验证**：空闲 Agent 线程数较当前基线（7/8）显著下降；并发下不随会话数线性增长。
- **验收信号**：grep `agent_threads=` 行，空闲态线程数大幅低于当前基线。

## 四、基准与验收口径

- **控制面**：沿用 v81 AC-5 双维度判据（行为判据 + 对称基线）。行为判据：reactor 线程不得阻塞于文件 I/O / 阻塞 syscall / work-pool 等待；控制帧完成回调经 work pool 投递；单会话有序性保持。对称基线：`benchmark_control_plane.sh`，v80 基线 median=48.97ms / p99=4.56ms。
- **数据面**：`benchmark_data_path.sh`，吞吐不回归（≥ 基线 97%）。
- **线程/资源**：空闲态与并发态 agent_threads / RSS 记录对比，向 TLS 收敛。
- **正确性回归**：全量集成脚本（TREE/catalog/restore/data-lane/System RPC/ingress/EXEC）全绿；跨版本兼容（RSP/3）不破坏。

## 五、风险与缓解

| 阶段 | 风险 | 缓解 |
|------|------|------|
| A | 分片后连接归属与每会话排序破坏 | 复用 TLS 已验证的分片归属 + 完成回调投递机制；分片 hash 保证同会话归同 shard |
| B | TREE/FILE 事务状态机异步化改动面大 | 先复用 TLS 已有异步执行域，避免复制状态机；分文件类型（先 TREE 后 FILE）渐进推进 |
| B | 每会话排序 / 流控 / 取消语义破坏 | 用现有 v81 控制帧保序逻辑为模板；集成测试锁定排序与流控 |
| B | TREE flock 全局互斥 | 改为更细粒度锁，独立验证并发提升 |
| C | 阻塞 worker 收敛引入回归 | 收敛是阶段 B 的产物，B 回归全绿后再调整默认值 |

## 六、与 TLS 路径的对比结论

TLS 已证明"全异步 + 分片"架构可行且线程/资源占用低。plain 路径的 Reactor 化（A 分片 → B 业务帧异步化 → C worker 收敛）本质是**复用 TLS 已验证的基建与模式**，将 plain 路径对齐到同一架构，从而在吞吐、延迟、线程/资源三个维度同时取得提升。该路径的风险主要来自改造范围与行为等价性保持，而非未知架构可行性。

## 七、后续实施建议

- 阶段 A 独立可先行（低-中风险，收益直接）。
- 阶段 B 为核心高价值改造，建议拆分多个子任务（按业务帧类型渐进推进），每个子任务一个 PDCA 周期。
- 每阶段以现有 benchmark 脚本 + 集成脚本作为回归门禁。
