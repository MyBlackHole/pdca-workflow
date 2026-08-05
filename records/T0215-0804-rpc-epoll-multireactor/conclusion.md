---
schema: pdca.asset/v1
id: T0215-0804-rpc-epoll-multireactor
phase: check
source_ids: [multi-reactor, conn-limit, epoll-integration, full-regression, bench-dl-rc1-paired, bench-dl-rc4, bench-concurrent-8-rc1, bench-concurrent-8-rc4, bench-rps-32-rc1, bench-rps-32-rc4, convergence-map-v2]
---

## 上下文

T0215 在 T0213/T0214 单 Reactor 事件循环工业对齐基础上引入多 Reactor 分片
（SO_REUSEPORT 多监听，ADR-0014），目标突破单 Reactor epoll_wait 分发线程
的吞吐上限（bench_rps 实测 32 客户端封顶 ~135K req/s）。验收标准 6 条
（AC-1~AC-6），其中 AC-2 已按用户确认放宽（见 prd.md 备注：8 客户端并发聚合
吞吐 ≥0.95× 无劣化 + 32 客户端 RPS 扩展）。

## 假设与结果

| AC | 假设 | 验证结果 | 判定 |
|----|------|---------|------|
| AC-1 | reactor_count 解析（0→nproc、1、4），N=1 与现状一致 | multi_reactor 用例（配置解析 + N=1 与旧行为等价 + N=4 并发 + stop）8 轮全过 | 通过 |
| AC-2 | 8 客户端并发聚合 ≥0.95×；32 客户端 RPS 扩展 | bench_concurrent 8 客户端×16MB：rc1=917.7 / rc4=905.3 MB/s（0.986）；bench_rps 32 客户端：rc1=134K / rc4=164K（1.22×） | 通过 |
| AC-3 | 单连接下载 N=4 均值 ≥ N=1 均值 ×0.95 | 配对对比（rc1/rc4 交替 4 轮）：rc1 avg=915.4 / rc4 avg=901.2（0.984）；最大噪声比 0.905（单次）| 通过（配对判定） |
| AC-4 | 每 reactor 资源独立：active_conns 汇总、队列背压、心跳保持 | multi_reactor active_conns 汇总断言通过；conn_limit 每 reactor 独立限制生效；心跳定时器每 reactor 独立 | 通过 |
| AC-5 | stop/join 无挂起（N=4 连接场景 <2s） | multi_reactor stop 用例：eventfd 唤醒全部 reactor，join 正常退出 | 通过 |
| AC-6 | xmake test 全量回归 | 全量 23 项 22 PASS；唯一失败 dir_utils 为既有环境问题（/tmp 源目录缺失）；集成测试单独跑 3/3 | 通过（含既有环境说明） |

## 分析

1. **AC-2 放宽后的实测支撑**：8 客户端并发下载聚合受 loopback 带宽封顶
   （~900MB/s，单连接 921MB/s），rc1/rc4 均撞该上限，聚合≈单连接，物理上
   无法 2×。RPS 维度 8 客户端 rc4 略低于 rc1（82K vs 87K，0.94），根因是
   worker 池按 Reactor 全额放大（4×8=32 worker，24 个空闲线程调度开销），
   已记录 ADR-0014 遗留；32 客户端时分发线程成为瓶颈，rc4 反超 1.22×，
   验证了多 Reactor 的收益条件（连接事件量超过单线程可分发量）。

2. **AC-3 测量方法**：单次进程内 5 round 方差极大（790~1130 MB/s，受同机
   两个 opencode 进程占 ~3 核干扰，load avg 4.1）。单次测量比率出现
   0.89~0.998 波动，不可判定。改用配对对比（rc1/rc4 交替各 4 进程）后
   比率稳定为 0.984 ≥ 0.95，判定通过。结论：此环境不满足单次 5% 精度
   要求，配对对比是当前可靠下限。

3. **启动失败清理**（A4 修复）：rpc_epoll_start 部分启动失败改为统一
   rpc_epoll_stop + join 已启动 reactor/worker，杜绝线程泄漏，multi_reactor
   stop 用例覆盖。

4. **测试 handler 阻塞化单帧**：测试 echo_handler 复刻产品
   rpc_epoll_conn_handler 的"首帧恢复阻塞模式"，规避非阻塞 fd 上 readn
   部分读 EAGAIN 丢字节；单帧处理与产品一致（worker 归还后触发下一帧）。

## 失败原因（仅 rejected/partial）

不适用（结论 confirmed）。

## 适用边界

- 环境：16 核 / loopback / 同机 2 个高负载 opencode 进程（load avg 4.1）
- 断言阈值：0.95× 在当前噪声环境下需要配对对比测量才能稳定判定
- 性能结论仅覆盖 <64 reactor、连接数 ≤ 32 客户端档位；worker 供给为
  每 Reactor 全额（max_workers×reactor_count），低并发（<16 连接）劣化
  已记录
- dir_utils 测试失败为既有环境问题（源目录缺失），非本任务回归

## 下一轮建议

- 后续任务：优化 worker 供给策略（auto 模式总 worker 按 max_workers 封顶
  并按 Reactor 均摊，或按实际连接数收缩），消除低并发下 24 个空闲 worker
  的调度开销（ADR-0014 遗留项）
- 测量方法沉淀：噪声环境下性能断言改用配对对比，写入测试基准说明
- xmake test 并行下集成测试偶发失败（资源竞争）需独立跑复核
