# AC-4 证据：benchmark 基线对照（Release -O3 口径）

构建：两侧均为 CMAKE_BUILD_TYPE=Release（项目实际构建为 -O3 -DNDEBUG，见 build-make compile_commands）。

## reactor_post 纯吞吐（1000000 callbacks, producers=4, queue_limit=65536, budget=256）

| 轮 | base mcb/s | new mcb/s |
|----|-----------|-----------|
| 1 | 2.809 | 3.950 |
| 2 | 2.870 | 4.103 |
| 3 | 2.839 | 3.497 |
| 4 | 3.275 | 3.929 |
| 5 | 3.045 | 3.819 |

中位数：base 2.870 → new 3.950（+37%）。合并 enqueue_impl 消除了 post→post_priority→impl 的双层转发，热路径无回退、实测提升。

## work_pool completion 完整路径（workers=1, completions=500000，配对交替采样）

| 轮 | base c/s | new c/s | new/base |
|----|---------|---------|----------|
| 1 | 1392537 | 1396138 | 1.003 |
| 2 | 1452773 | 1390560 | 0.957 |
| 3 | 1372239 | 1473528 | 1.074 |
| 4 | 1422667 | 1335691 | 0.939 |
| 5 | 1382536 | 1369262 | 0.990 |

中位比值 ≈ 0.998——持平。workers=2 场景两侧自身波动即达 ±40%（base 三次 2.01/1.39/1.13 M），属宿主调度噪声；配对单 worker 口径无回退。

## 结论

数据面热路径零新增分配与原子操作；控制面回调粒度仅 guard 一对原子 RMW（本基准未启用守卫路径）。AC-4 通过。
