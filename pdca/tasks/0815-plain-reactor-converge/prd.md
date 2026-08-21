# plain 路径全面 Reactor 化：吞吐/延迟/资源综合提升 — 优化方案

## 问题陈述

- **现状**: backupstream 80.0.0 的 Agent 存在两条完全不同的并发路径。TLS 路径已全面 Reactor 化（Reactor Group 分片 + tree/lane/control work pool 异步执行），而非 TLS（plain）路径仍为"单 Reactor + 弹性阻塞 worker 池"。v81 已把 plain 的**控制帧**（PING/TIME/SYS）接入非阻塞前端异步执行，但**业务帧**（TREE/FILE/restore/EXEC setup）仍整体占用一个阻塞 worker 直至整个事务结束。
- **目标**: 产出一份"综合多维度提升"的优化方案文档，覆盖吞吐、延迟、线程/资源三方面，给出分阶段改造路径与可验证的基准口径，作为后续实施任务的蓝图。
- **差距**: 缺少一份聚焦"如何提升"的方案文档；现有 ROUND*_REVIEW 是演进记录，T0287 是现状架构报告，均未给出面向下一轮综合提升的改造设计与分阶段路径。

## 现状瓶颈（源码实证）

1. **单 Reactor 天花板**: plain 路径所有连接的 ingress 解析、控制帧渲染、PONG 均串行于单一 Reactor 线程（`backup_agent.cpp` 中 plain ingress 绑定单 `reactor`）。`reactor_group` 分片基建已存在但仅 TLS 使用。
2. **业务帧整体占用阻塞 worker**: TREE/FILE/restore 的同步 handler 整个事务（可数秒）钉住一个弹性 worker；弹性池只能按需扩缩，无法让单个长事务并发切分。
3. **TREE 全局互斥**: 同一根的并发 TREE PUT 被全程 `flock(LOCK_EX)` 串行化。
4. **非阻塞收益在 handoff 后丢失**: 业务帧 handoff 到阻塞 worker 后，`session_dispatch_loop` 中的后续控制帧会退回阻塞路径同步执行。

## 基线数据（本机实测，方案"起点"）

| 指标 | plain 当前值 |
|---|---|
| 控制面 32 并发 median | 48.49 ms |
| 控制面 p99_upper | 4.56 ms |
| 控制面 agent_threads | 7 |
| 数据面 PUT（256 MiB） | 595 MiB/s |
| 数据面 GET（256 MiB） | 562 MiB/s |
| 数据面 agent_threads | 8 |

（对照：TLS 路径 blocking session worker 为 0，全异步；v81 控制面判据基线 v80 median=48.97ms / p99=4.56ms / threads=4。）

## 解决方案：分阶段综合提升路径

### 阶段 A — plain ingress 接入 reactor_group 分片（低-中风险，先行）
复用现有 `reactor_group` 基建，按 fd/会话 hash 将 plain ingress 分配到 N 个 shard，突破单 Reactor 吞吐天花板。处理 accept/ingress 跨 shard 归属与 connection_acquire 分片化。独立可验证（控制面基准并发吞吐提升）。

### 阶段 B — 业务帧异步化（中高风险，核心）
将 TREE/FILE/restore 业务帧从阻塞 worker 迁移到异步 work pool 执行域（模仿 TLS 的 tree_pool/lane_pool 模型）。让长事务可并发切分、不再钉住 worker。需保持每会话排序、流控、取消语义，与现有行为等价。

### 阶段 C — 阻塞 worker 收敛（收尾）
业务帧异步化后，弹性阻塞 worker 池大幅收敛/归零，对齐 TLS 路径。线程与资源占用显著下降。

## 用户故事

1. 作为备份管理员, 我希望高并发 plain 控制面不再串行于单线程, 以便大量并发会话下管理操作不成为瓶颈。
2. 作为负载工程师, 我希望 TREE/FILE 长事务不钉死一个 worker, 以便多个备份任务可并发推进。
3. 作为运维, 我希望 plain 路径线程/资源占用向 TLS 路径收敛, 以便降低单 Agent 承载成本。

## 实现决策

- 本任务（design 场景）**只产出优化方案文档** `docs/OPTIMIZATION_PLAN.md`，不实施源码改造。
- 方案以源码为唯一事实来源，改造设计映射到具体模块概念（ingress/reactor_group/work_pool/session_pool），不写 `:line` 与文件路径以保证 durable。
- 每阶段改造标注预期收益、风险等级、独立验证方式与验收口径。
- 基准使用现有 `benchmark_control_plane.sh`、`benchmark_data_path.sh` 及 v81 控制面判据（AC-5 行为+对称基线双维度）。

## 测试决策

- design 场景无测试产物。方案可验证性通过：每阶段有独立基准脚本可运行、有明确验收信号、改造设计可映射到模块概念。
- 方案文档写入项目 `docs/OPTIMIZATION_PLAN.md`，并复制到 PDCA 记录 `records/T0294-0815-plain-reactor-converge/evidence/`。

## 验收标准

- [ ] AC-1: 方案文档写入 `docs/OPTIMIZATION_PLAN.md`，包含"现状与瓶颈/基线数据/分阶段改造设计/基准与验收/风险"五节
- [ ] AC-2: 分阶段改造设计（阶段 A/B/C）可映射到至少 3 个模块概念（ingress/reactor_group/work_pool/session_pool），各含明确收益与风险等级
- [ ] AC-3: 基线数据节给出 plain 控制面与数据面的本机实测数值（median/p99/threads/MiB/s）
- [ ] AC-4: 每阶段给出独立验证方式（引用现有 benchmark 脚本或 v81 控制面判据）与可 grep 的验收信号
- [ ] AC-5: 方案文档含与 TLS 路径的对比（说明 TLS 全异步、plain 现状差异）
- [ ] AC-6: 方案文档副本写入 PDCA 记录 evidence 目录
- [ ] AC-7: 方案文档全文为中文，术语首次出现含英文原名
- [ ] AC-8: 方案文档经用户确认后，作为后续实施任务拆分的蓝图（在 clarifications 中记录 final_confirmation）

## 范围外

- 不实施任何 `src/` 源码改造、不改 Makefile/CMakeLists（本任务仅出方案）。
- 不做 TLS 路径重构。
- 不做数据面（Data Lane）架构重构。
- 不产出可运行的代码测试。

## 备注

- 用户选择"先出方案文档再实施"，本任务为方案设计；实施在后续拆分任务中推进。
- 场景边界（T0273）：本任务产出文档（非脚本/测试），归 design 场景。
- 查重：与 T0287（现状架构报告）、T0291/T0293（控制面优化）不重复。
