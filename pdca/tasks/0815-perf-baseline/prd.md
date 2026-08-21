# 性能量化：新增专用基准并建立 v80 基线

## 问题陈述

- **现状**: backupstream 80.0.0 性能指标散落于各轮 review（ROUND79/80 的慢客户端、短会话等量化），无统一、可复现、可跨版本对比的专用基准脚本。
- **目标**: 新增专用性能基准脚本，输出包含吞吐/时延/线程数/RSS 的对比结果，建立 v80 基线，供 v81 演进前后对比（T0291 的硬性目标以本任务基线为参照）。
- **差距**: 缺统一基准脚本与 v80 基线快照。

## 解决方案

1. 新增 `tests/benchmark_control_plane.sh`：控制面短会话（HELLO+PING 并发）、慢客户端不消耗 worker 场景，输出吞吐（ops/s）、时延（p99/中位数）、Agent 线程数、RSS。
2. 新增 `tests/benchmark_data_path.sh`：长 FILE/TREE 传输（复用既有 benchmark_data_lanes.sh 的执行模式），输出吞吐（MiB/s）与资源占用。
3. 量化口径与 ROUND79/80 一致（warm client、多次取中位数、线程数/ RSS 采样）。
4. 输出结构化对比表（v80 基线值可 grep），写入 evidence。

## Seam 分析

### 测试接缝
- 基准脚本调用既有测试框架工具与 Agent/backupctl 端到端路径；被测模块为 Agent 非阻塞前端与 TREE/FILE 数据路径。

### 声明的测试接缝
- seam: tests/benchmark_control_plane.sh -> src/agent_plain_ingress.cpp
- seam: tests/benchmark_data_path.sh -> src/agent_tree_runtime.cpp

### 验收可测性
- 脚本可独立运行，输出含可 grep 的指标行（ops/s、p99、threads、RSS、MiB/s）。

## 用户故事

1. 作为性能评估者，我希望一套脚本跑出可对比的 v80 基线，以便量化 v81 收益。

## 实现决策

- 复用既有 benchmark_data_lanes.sh 执行模式与 backupstream-event-bench 等工具。
- 指标：吞吐、时延、线程数峰值、RSS；以 v80 基线快照形式存入 evidence。
- 不修改生产代码（纯测量任务）。

## 测试决策

- 只测端到端外部行为（吞吐/时延/资源），不测实现细节。
- 现有先例：benchmark_data_lanes.sh、benchmark_tls_*.sh。

## 验收标准

- [ ] `tests/benchmark_control_plane.sh` 可独立运行，输出含吞吐、时延（p99/中位数）、线程数、RSS 的可 grep 指标行。
- [ ] `tests/benchmark_data_path.sh` 可独立运行，输出含吞吐（MiB/s）与资源占用的可 grep 指标行。
- [ ] 脚本运行完成，v80 基线值写入 evidence（含测试环境说明）。
- [ ] 脚本在连续两次运行中结果可复现（同一数量级）。

## 范围外

- 不做性能优化实现（仅测量）。
- 不做 v81 架构演进（T0291）。
- 不刷新滞后文档。
