---
schema: pdca.asset/v1
id: T0246-0813-small-writer-pool
phase: check
source_ids: [small-pack-integration, directed-regressions, benchmark-matrix, build-matrix, ctest-tls-off, ctest-tls-on, review-report]
---

## 上下文

本轮优化客户端 `SmallLocalWriterPool` 的队列背压、首错传播、顺序屏障和运行时指标，并用配对基准评估显式并行度。

## 假设与结果

假设成立。AC-1 至 AC-7 全部满足：小文件 pack、blob、regular stream、hardlink、writer 指标和失败边界均通过 TLS 集成；既有 tree/FSM 回归通过；GNU Make TLS=0/1 与 CMake TLS OFF/ON 构建和测试通过。

完整基准执行 4 对样本，覆盖 workers=0 对 workers=1/2/4/8，以及 checksum=1、durability=strict 下 workers=0 对 workers=4。默认路径保持不变；worker=1 在无 checksum/无 durability 矩阵中慢于默认路径，worker=4 的平均吞吐在本轮最高，因此建议保留默认 0，并将显式 4 作为当前存储条件下的候选值，而不是自动改变默认值。

## 分析

队列上限仍为 `max(8, workers * 8)`。worker 首错会锁存、清空待处理任务并唤醒生产者；主循环在 enqueue/drain 失败后停止，不再处理后续 hardlink、目录元数据或 `TREE_END`。成功任务统计通过锁保护的 pool-local 汇总在 drain 时合并，避免 worker 与主线程竞争写共享统计。

代码审查双轴结论为 Blocking=0；未发现异常、线程生命周期、协议顺序或现有 C-style 约束回归。

## 适用边界

- 基准结论来自当前主机、10000 个小文件、4 对样本，不能外推到所有存储设备或文件分布。
- 只读目标根的失败回归依赖测试进程不是 root；当前执行环境满足该前提。
- 指标只在启用显式 small-file writer pool 且请求 `--progress` 时输出，协议格式未改变。

## 下一轮建议

保持默认 `--small-file-workers 0`；在部署环境用同一配对脚本复测，若本地盘稳定受益，可显式采用 4。后续若需要扩大收益，应先增加跨设备/文件分布的基准样本，再考虑自适应并行度。
