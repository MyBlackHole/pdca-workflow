# 控制面性能判据（承接 T0292 AC-5）

状态：本轮（T0293）定为有效判据基准，替代此前仅凭 agent_threads 峰值判定的口径。

## 双维度判据

### 维度一：行为判据（结构性，防退化）
- 反应器线程必须保持非阻塞：任一控制帧处理路径不得在 reactor 线程上执行文件 I/O、
  阻塞式系统调用或 work-pool 等待（v81 非阻塞约束不变式）。
- 控制帧完成回调需经 work pool 提交/投递，会话读取侧受 in-flight 上限钳制，
  业务（business）帧在控制响应排空前不得抢占（保序）。
- 单会话有序性：同一 channel 的控制响应不得乱序；业务帧与 in-flight 控制
  必须按 v81_control_frame_integration.sh 的断言保序。
- 验收信号：`tests/v81_control_frame_integration.sh` 全绿 + `tests/plain_ingress_integration.sh` 全绿。

### 维度二：对称基线判据（数值，同脚本同口径）
- 基准：`tests/benchmark_control_plane.sh <build> 32 7`，取 median_ms（单批 32 会话
  HELLO+PING 壁钟中位数）与 p99_upper_ms（=批次总耗时/会话数上界）及 agent_threads。
- 基线参照：v80（T0291/T0290 归档）median=48.97ms / p99=4.56ms / threads=4；
  v81 优化前（本轮 opt_in_cp.log）median=54.45ms / p99=12.03ms / threads=7。
- 通过阈值：优化后 median 较 v81 优化前（54.45ms）明显下降，且无回归（data-path ≥ v80 97%）。

## 相对旧判据的修正要点（T0292 立意）
- 旧判据仅盯 agent_threads 峰值；新判据以「行为判据（结构不变式）」+「对称基线（median/p99）」
  双维度评估，单独线程数下降不作为通过依据，避免把"线程少"误判为"性能好"。
- 明确 v81 非阻塞架构固有增加 control-worker + reactor 汇聚线程，故线程数与 v80 阻塞模型
  不可直接逐线程可比；线程维度仅在行为判据通过前提下，作为资源节省的辅助信号。

## 评估结论（本轮 O1+O3）
- median: 54.45ms → 51.9ms（约 -5%，多次采样稳定 51.6~52.3）
- p99_upper: 12.03ms → 11.4ms
- agent_threads: 7（未降，v81 非阻塞固有，架构级分片属范围外）
- 行为判据：v81_control_frame_integration.sh / plain_ingress_integration.sh 全绿；
  data-path put 约持平（521~545 range，控制路径不触碰 data path 核心）。
- 结论：行为判据通过；对称基线较 v81 优化前明显改善且无回归，达到本判据通过标准。
  （未追平 v80 绝对值归因于单 Reactor 汇聚 + 独立 control worker 的架构成本，属范围外。）
