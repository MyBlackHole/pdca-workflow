# Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- priority: P1（Round 59 已明确客户端 namespace/write path 是下一处主要成本，但需要先测量）
- status: ready-to-plan

## 请求解释

“继续下一轮优化”解释为：基于 Round 59 的结果，继续优化客户端接收大量小文件
时的落盘路径，而不是重复服务端小文件打包。

## 查重

- 最近的 Round 59 已覆盖服务端 native TREE GET small-file blob/pack。
- 当前活跃任务中没有覆盖 `SmallLocalWriterPool` 的客户端背压/并行度。
- 已存在的 `--small-file-workers` 和 `benchmark_tree.sh` 属于可复用基础，不构成本任务重复。

## 事实验证

- `src/backupctl.cpp` 已实现客户端 `SmallLocalWriterPool`，队列上限为
  `max(8, workers * 8)`，满队列时生产者等待。
- pool worker 失败后会记录首个错误、清空排队任务、停止新任务，并由接收路径
  在 drain/析构边界恢复错误。
- 收到硬链接或 TREE_END 时会先 drain，以保护 inode 建立和目录元数据顺序。
- `tests/tls_tree_small_pack_integration.sh` 当前显式使用
  `--small-file-workers 0`，尚未覆盖并行 writer pool。

## 推荐下一步

1. P1/P2：明确指标、背压上界、错误语义和顺序屏障验收。
2. P3/P3.5：形成含声明测试接缝的 PRD，并请求用户确认测试边界。
3. P4/P5/P6：拆解、注入最小相关知识、提交完整方案终审。
4. 用户终审确认后，才通过 advance-phase 进入 Do。

## P4 拆解结果

本任务保持单任务执行，不创建子 task。writer pool 实现、接收循环错误边界、
顺序屏障、集成回归和 benchmark 共享同一外部行为契约，拆分会增加跨任务同步而
不会形成独立可验收的 PDCA 周期。

## P5 知识注入结果

- 已注入 `knowledge/benchmark/paired-comparison-noise.md`。
- 已注入 `knowledge/pdca-flow/real-project-mechanism-validation.md`。
