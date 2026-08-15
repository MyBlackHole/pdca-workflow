# v81 控制面性能提升：对称吞吐/延迟 + 资源节省（承接 T0292 判据修正）

## 问题陈述

- **现状**: T0291（v81 后续控制帧非阻塞化）已落地，但 control-plane 对称负载基准显示：median_delay=52.3ms（v80=48.97ms）、p99=8.15ms（v80=4.56ms）、agent_threads=7（v80=4）、RSS=6960KiB（v80=6860）。同步全部建议落库，单 Reactor 成为控制帧回写汇聚点。
- **目标**: 提升控制面性能——(A) 对称负载下追赶并压过 v80 基准（median ≤ v80、p99 明显下降、线程减少到接近 v80）; (B) 不对称负载下（慢会话）验证资源节省不退化。
- **承接 T0292**: 上一轮遗留的 T0292「AC-5 线程判据口径修正」（research）由本轮吸收统一完成——先定正确判据，再据此实测性能。

## 解决方案（子代理瓶颈分析定位）

控制帧每个 PONG 往返，单 Reactor 线程经受至少 2 次 epoll_wait + 3 次 epoll_ctl(MOD) + 2 次 recv + 1 次 send，另有 1 次 eventfd write + 2 次 pthread_mutex + 1 次 cond_signal + futex 唤醒; 全部汇聚在同一主 Reactor 线程。低风险优化（work_pool.cpp / agent_plain_ingress.cpp / reactor.cpp）：

1. **O1 完成回调批序列化 + 合并 reactor_mod(WRITE)**: 每个 job_done 立即 `reactor_mod(WRITE)`，一帧一 mod。改为仅标记 tx_dirty，每会话每轮一次 mod + 统一 flush，减少 epoll_ctl 与 WRITE 往返。
2. **O2 控制完成投递提优先级**: 控制类 job 的完成从 `REACTOR_POST_NORMAL` 提到 HIGH（reactor_post_priority(REACTOR_POST_HIGH)），压低 p99 尾部排队。
3. **O3 纯 PONG/TIME 快速路径**: PING/TIME 无文件 I/O、响应恒为非空; 砍掉每帧 `new job` + `std::vector<Frame>` + `ingress_build_frame` memcpy，预分配复用 tx 缓冲单跳写入。
4. **O4 单 READ 回调批量提交**: 同会话一批控制帧先全部 enqueue 再统一返回，合并 worker 完成与 eventfd 唤醒。

## Seam 分析

### 声明的测试接缝
- seam: tests/benchmark_control_plane.sh -> src/agent_plain_ingress.cpp
- seam: tests/v81_control_frame_integration.sh -> src/agent_plain_ingress.cpp
- seam: tests/benchmark_data_path.sh -> src/agent_tree_runtime.cpp

### 验收可测性
- benchmark_control_plane.sh 输出 thread/RSS/median/p99; v81_control_frame_integration.sh 输出 PASS; data-path 基准用于确认无回归。

## 用户故事

1. 作为备份管理员, 我希望高并发控制面(大量并发会话)延迟低且线程占用少, 以便控制面不成为管理操作的瓶颈。
2. 作为负载工程师, 我希望看到一条明确的性能判据（不仅看线程峰值, 更看行为/吞吐/延迟），以便正确评估共享 work 池架构。

## 实现决策

- 延续 v81 非阻塞 ingest + control_pool 架构, 不做多 Reactor 分片（高风险, 留待后续）。
- 优化聚焦"降低单 Reactor 每帧 syscall 往返", 这是子代理报告第 5 点 O1-O4, 均局部、低风险。
- 性能判据修正: 承接 T0292, 定义"行为判据 + 对称基线"双指标（见验收标准）。

## 测试决策

- 用 benchmark_control_plane.sh 量对称负载（median/p99/thread/RSS）; v81_control_frame_integration.sh 保有序/不退化; benchmark_data_path.sh 确认数据面无回归。
- 不对称负载: 用 stalled 会话脚本验证业务 worker 不增长（复用 T0291 的 stall 场景思路）。

## 验收标准

- [ ] AC-1: 对称负载控制面 median_delay ≤ v80 基线 48.97ms，p99 < v80 5ms(或显著低于当前 v81 8.15ms)，agent_threads 比 v81 当前 7 下降。
- [ ] AC-2: data-path 吞吐不回归（≥ v80 基线 97%，沿用 T0290 口径）。
- [ ] AC-3: 不对称负载（stalled 控制会话）下业务 worker 不随会话数增长（线程数保持 baseline），v81_control_frame_integration.sh 全绿。
- [ ] AC-4: 每会话有序性与协议兼容不破坏（protocol_version / plain_ingress 回归全绿）。
- [ ] AC-5(判据修正,承接 T0292): 产出明确的控制面性能判据文档（行为判据+对称基线双维度），并据新判据评估 v81/v80 对比。

## 范围外

- 不做多 Reactor 分片、io_uring、worker 直写 socket（架构级, 高风险）。
- 不做数据面(Data Lane)重构。
- 不做 EXEC 事件域重构。
- 不刷新滞后文档（另立任务）。

## 备注

- 承接 T0292 到本轮: T0292 的 AC-5 判据修正目标由本轮 AC-5 一项覆盖; T0292 任务在其 PRD 目标被本轮吸收后按流程归档或标记 absorbed。
