# T0216 跟进：rpc-epoll worker 供给策略优化

## 背景

T0215（ADR-0014）多 Reactor 分片实测发现：worker 池按 Reactor 全额供给
（总线程 = reactor_count × max_workers）导致低并发（<16 连接）下 rc4 < rc1
（8 客户端 RPS 0.94×，24 个空闲 worker 的 futex 调度开销）。该现象记录为
ADR-0014 遗留项，AC-2 断言已据此放宽。

## 目标

消除低并发下多 Reactor 的 worker 过度供给，使 rc4 在低连接数下与 rc1 持平
或更优，且保持 32 客户端扩展性（1.22×）。

## 候选方案（Plan 阶段细化）

1. **总 worker 封顶 + 均摊**：auto 模式下总 worker 数 ≤ max_workers，按
   Reactor 均摊（每 reactor ceil(总/reactor_count)）
2. **按连接数动态收缩**：worker 池随本 Reactor 活跃连接数伸缩
3. **懒启动 worker**：低负载时仅保留 1 worker，连接增多再拉起

## 约束

- 保持 AC-4 语义：每 reactor 独立 worker 池/队列，零跨 reactor 同步
- N=1 行为不变
- 不破坏 conn_limit / multi_reactor / 集成测试既有断言

## 验收（待 Plan 定稿）

- 低并发（2/4/8 客户端）RPS：rc4 ≥ rc1 × 0.95（配对对比测量）
- 32 客户端 RPS 扩展保持 ≥ 1.1×
- 全量 xmake test 回归通过
