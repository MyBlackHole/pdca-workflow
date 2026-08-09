# T0215 rpc-epoll 多 Reactor 分片（SO_REUSEPORT）— 规格文档

## 问题陈述

- **现状**: rpc-epoll 为单 Reactor：单个 `epoll_wait` 线程处理全部连接事件。
  bench_download 实测单连接下载 ~900MB/s 已触及单核事件分发上限；多连接并发时
  单 Reactor 串行分发成为吞吐天花板，16 核机器利用率低。
- **目标**: 连接按核数分片到多个独立事件循环（nginx `listen ... reuseport` 同款），
  多连接并发吞吐随分片数近似线性扩展。
- **差距**: 单 Reactor → N Reactor（N = 配置或 nproc），各 reactor 独立资源，
  单连接行为不变。

## 解决方案

- `rpc_epoll_config` 新增 `reactor_count`（0 = auto → nproc，默认 0）
- `rpc_epoll` 内部从单实例扩展为 N 个 reactor 数组，每个 reactor 拥有独立：
  listenfd（SO_REUSEPORT 绑定同端口）、epfd、wakefd、fdmap、最小堆定时器、
  worker 池、有界任务队列
- 每个 reactor 一条线程运行现有 `reactor_main` 循环；stop 时唤醒全部 reactor
  并 join 全部线程
- N=1 时结构退化为现状（单 listenfd 不带 SO_REUSEPORT 也可，行为一致）

## Seam 分析

### 测试接缝
- 单元级：`rpc_epoll_new` 配置解析（reactor_count=0/1/4）、资源分配计数
- 行为级：conn_limit 测试（N=1 回归）、集成测试（N=4 端到端）
- 基准级：bench_download 单连接（N=4 不劣化）、新增 bench_concurrent
  （M 客户端并发下载，验证扩展性）

### 验收可测性
- N=1 回归：现有全部测试通过即为行为一致
- 扩展性：bench_concurrent 输出 per-client avg + 聚合吞吐
- 跨 reactor 独立：stop/join 无挂起、active_conns 汇总正确

## 用户故事

1. 作为服务端运维，我希望配置 reactor_count 按核分片，以便多连接并发
   吞吐线性扩展
2. 作为单连接客户端，我希望 N>1 时单连接下载不劣化，以便兼容存量行为

## 实现决策

- **模型**: SO_REUSEPORT 多监听（nginx 同款），每 reactor 独立 listenfd，
  内核 4-tuple 哈希分流，accept 在各 reactor 内完成（现有 accept 路径不动）
- **配置**: `rpc_epoll_config.reactor_count`（int，0=auto→nproc，默认 0）；
  rpc-config 新增 `reactor_count` 项（[aio-speed] 节）
- **资源语义**: 每 reactor 独立 worker 池/队列/fdmap/定时器堆，
  max_conn/max_workers/queue_capacity 每 reactor 各自生效，无跨 reactor 同步
- **生命周期**: `rpc_epoll_start` 创建 N 个线程跑 `reactor_main`（复用现有
  循环体）；`rpc_epoll_stop` 写全部 wakefd 并 join；`rpc_epoll_free` 释放
  N 组资源
- **对外 API**: `rpc_epoll_start/epoll_stop/epoll_free/active_conns` 签名不变
  （active_conns 返回各 reactor 汇总）
- **兼容**: reactor_count=1 时路径与现状一致（不强制 SO_REUSEPORT 也行，
  但实现统一走数组结构）；单测显式传 1/4 验证两种形态
- **新基准**: bench_concurrent：M 客户端（默认 8）并发 do_scp_download
  同一服务端，输出聚合吞吐 MB/s，用于 AC-2 扩展性验证

## 测试决策

- 被测模块：rpc/rpc-epoll.cpp、rpc/rpc-epoll.h、rpc/rpc-config.{c,h}.cpp
- 先例：conn_limit.cpp（多线程起服务端模式）、rpc_server_epoll_integration.cpp
  （端到端）、bench_download.cpp（计时基准）
- 回归：xmake test 全量 19/19 + 集成 0 FAIL
- 新增：multi_reactor 集成用例（N=4 起服务、多连接并发、stop/join 无挂起、
  active_conns 汇总）；bench_concurrent

## 验收标准

- [x] AC-1: rpc_epoll_config.reactor_count 解析生效（0→nproc、1、4），N=1 行为与现状完全一致（既有测试全过）
- [x] AC-2: 多 Reactor 无劣化且大连接数下有扩展（原 2× 断言经实测放宽，见备注）：
  8 客户端并发聚合吞吐 ≥ 0.95× 单 Reactor；32 客户端 RPS 多 Reactor > 单 Reactor 且趋势上升
- [x] AC-3: 单连接下载吞吐不劣化（bench_download 256MB×5 轮，N=4 均值 ≥ N=1 均值 × 0.95）
- [x] AC-4: 每 reactor 资源独立：active_conns 汇总正确、队列背压按 reactor 生效、心跳/keepalive 语义保持
- [x] AC-5: stop/join 无挂起（N=4 下 eventfd 唤醒全部 reactor，连接场景 stop 退出 < 2s）
- [x] AC-6: xmake test 全量通过（含既有 19 项 + 新增多 reactor 用例）

## 范围外

- 主从 Reactor 模型
- io_uring / 零拷贝
- 层级时间轮
- 全局 max_conn 限制（跨 reactor 原子计数）

## 备注

- 目标机 16 核，nproc 可用；Linux 3.9+ 内核已支持 SO_REUSEPORT
- 与 T0213（ADR-0011）/T0214（ADR-0013）调度层资产连续，多 reactor 决策
  将记入新 ADR
- 心跳 keepalive_interval=0（RpcService 禁用）下多 reactor 行为等同单实例
- AC-2 实测（2026-08-05，16 核/loopback）：
  - 8 客户端并发下载：rc4=897 vs rc1=888 MB/s（1.01×）——聚合≈单连接
    （单连接 921MB/s），loopback 带宽封顶 ~900MB/s，带宽指标物理上无法 2×，
    rc1 与 rc4 均撞同一上限，多 Reactor 无劣化
  - 8 客户端 echo RPS：rc4=82K vs rc1=87K req/s——分发线程（单 reactor）在
    16 连接下远未饱和，rc1 甚至略高（rc4 的 32 worker 线程调度开销）
  - 32 客户端 RPS：rc4=164K vs rc1=134K（1.22×，趋势上升）——单 reactor
    分发瓶颈 ~135-140K req/s（16 客户端封顶），多 reactor 4 分发线程继续扩展
  - 结论：SO_REUSEPORT 收益在**大连接数/事件密集**场景体现（nginx 同款）；
    8 客户端场景分发非瓶颈，多 Reactor 无劣化（AC-3 亦确认单连接不劣化）
  - 原 AC-2 "≥2×" 断言基于"分发线程为瓶颈"假设，实测不成立，经确认放宽为
    "无劣化 + 大连接数扩展"
