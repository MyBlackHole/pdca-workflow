## 当前状态

T0215（SO_REUSEPORT 多 Reactor）PDCA 已走完 Do→Check（verdict=confirmed）→
Act 知识沉淀阶段，disposition=projected。剩余 Ac6~Ac8（日志/提交/归档）。

## 未完成事项

- flow-act Ac6（journal）/ Ac7（git 提交）/ Ac8（归档）收尾
- 跟进任务 T0216（worker 供给优化）处于 plan 阶段，待 Plan 细化后执行

## 已知约束

- worker 池按 Reactor 全额放大（总线程=reactor_count×max_workers），低并发
  （<16 连接）rc4<rc1，ADR-0014 记录为遗留
- loopback 带宽封顶 ~900MB/s，扩展性验证须用 CPU 密集 RPS 基准（bench_rps）
- 性能断言在噪声环境须用配对对比测量（knowledge/benchmark/paired-comparison-noise.md）
- xmake test 全量唯一失败为既有 dir_utils 环境问题；集成测试并行下偶发失败
  需单独跑复核

## 推荐的下一步

1. 完成 T0215 Ac6-Ac8 归档
2. 执行 T0216：worker 供给策略优化（总 worker 封顶均摊 / 动态收缩 / 懒启动）

## 关键上下文文件列表

- ADR-0014: `docs/adr/ADR-0014-rpc-epoll-multireactor-so-reuseport.md`
- 结论: `records/T0215-0804-rpc-epoll-multireactor/conclusion.md`
- 知识: `knowledge/linux-epoll-eventloop/multireactor-so-reuseport.md`、
  `knowledge/benchmark/paired-comparison-noise.md`
- 实现: rpc-epoll.cpp/h（release 仓库）、测试 multi_reactor/conn_limit/bench_*
- 跟进任务: `pdca/tasks/active/0805-rpc-epoll-worker-supply-followup/`

## suggested skills

- flow-act、advance-phase（归档收尾）
- feature-commit-format（T0216 提交时）
- code-review-checklist（T0216 双轴审查时）
