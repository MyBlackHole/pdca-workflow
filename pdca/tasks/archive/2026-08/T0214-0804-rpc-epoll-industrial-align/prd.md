# rpc-epoll 事件循环对齐工业实现 — 规格文档

## 问题陈述

- **现状**: T0213 迁移后 rpc-epoll 事件循环与 ADR-0011 声明（对齐 Netty/muduo）存在四项偏差：① 固定 100ms tick 轮询（`RPC_EPOLL_TICK_MS`），而非「epoll_wait timeout = 最近 deadline」；② 连接表为单向链表，`conn_find` 每次 O(n) 扫描；③ 心跳 tick 每 100ms 全表 O(n) 扫描；④ rpc-epoll.h 默认值仅注释，与 rpc-config 常量不一致。
- **目标**: 事件循环对齐工业实现（muduo/Netty/libuv 风格）：最小堆定时器驱动动态 epoll_wait deadline、epoll data.ptr 直接连接对象 O(1) 查找、心跳只处理到期条目、默认值落地为代码常量。
- **差距**: 见四项偏差。工业实现中：定时器（muduo TimerQueue 最小堆 / libuv min-heap / nginx 红黑树）+ `epoll_wait(timeout = 最近到期时间)`；文件事件用 `data.ptr` 指向连接上下文，O(1) 取回；空闲无定时器时完全阻塞（零 CPU 空转）。

## 解决方案

在保持 `rpc_epoll_config` / `rpc_conn_handler` API 与外部行为完全不变的前提下重写 rpc-epoll 内部：

1. 引入自研最小堆定时器（C，`struct rpc_epoll_timer`，按时点排序），替代固定 tick：`epoll_wait` 超时 = 堆顶最近到期时间；堆空时 -1（阻塞）。
2. `epoll_event.data.ptr` 指向 `struct rpc_conn_entry`，事件到达 O(1) 取连接对象，删除链表 `conn_find` 与 `conns` 链表。
3. 心跳改为定时器驱动：每连接一个保活定时器（keepalive_interval / 2×interval 两级），只处理到期条目，删除 `heartbeat_tick` 全表扫描。
4. 默认值落地：rpc-epoll.h 定义 `RPC_EPOLL_DEFAULT_MAX_CONN 8` / `RPC_EPOLL_DEFAULT_MAX_WORKERS 4` / `RPC_EPOLL_DEFAULT_QUEUE_CAPACITY 8` 常量；`rpc_epoll_new(NULL)` 支持使用默认值（当前为 NULL 拒绝）。

## Seam 分析

### 测试接缝
- 连接层（conn_limit 测试：echo/max_conn/queue_full/heartbeat/keepalive_timeout/graceful_stop）—— 外部行为不变，全量回归。
- rpc_server_epoll_integration 集成测试（真实 RpcService + epoll 调度）—— 回归 18/18。
- 新增：定时器最小堆单测（插入/到期顺序/取消/提前到期精度）；动态 deadline 行为测试（空闲时 CPU 阻塞，用 tick 间隔可观测性验证）。

### 验收可测性
- 每 AC 独立 pass/fail 信号（见验收标准）。
- 边界：堆空阻塞、到期时间相等、定时器在 worker 归还连接时重挂、stop 清理定时器。

## 用户故事

1. 作为服务端运行者，我希望事件循环空闲时完全阻塞而不是 100ms 轮询，以便空闲 CPU 占用趋近于零（对齐工业实现）。
2. 作为服务端运行者，我希望心跳判定精确到到期时刻而不是 ±100ms 粒度，以便 keepalive 超时行为符合配置语义。
3. 作为维护者，我希望连接查找 O(1)、定时器只处理到期条目，以便 max_conn 提升时扩展性不受链表扫描影响。
4. 作为集成者，我希望 `rpc_epoll_new(NULL)` 使用代码内默认值，以便缺省配置路径可用且注释与实现一致。

## 实现决策

- **模块**：rpc/rpc-epoll.cpp + rpc/rpc-epoll.h（内部重构）；新增最小堆定时器（可内联于 rpc-epoll.cpp，或独立 libs/timer-heap 供复用——倾向独立小模块）。
- **接口不变**：`rpc_epoll_config` 四字段、`rpc_conn_handler`、`rpc_epoll_new/free/start/stop/active_conns/queue_len` 签名与语义全不变。
- **data.ptr 生命周期**：连接对象由 Reactor 分配/释放，`rpc_epoll_start` 与 worker 归还路径用 `EPOLL_CTL_MOD` 更新 data.ptr；关闭路径必须先从 epoll DEL 再释放（防 use-after-free），所有权转移语义（T0213）保持不变。
- **定时器设计**：二元最小堆（数组），key = 绝对到期时间（秒+毫秒或单调时钟 ms）；支持 insert / peek / pop / cancel（懒删除标记）；定时器不采用 timerfd（对齐 ADR-0011）。
- **架构决策**：更新 ADR-0011（或新增 ADR-0013）记录最小堆定时器与 data.ptr 落地。

## 测试决策

- 仅测外部行为（定时器单测除外，堆为纯函数可直测）。
- 被测模块：rpc-epoll（新 target `timer_heap_test` + 既有 conn_limit / rpc_server_epoll_integration / 全量 xmake test）。
- 现有测试先例：conn_limit.cpp（事件循环外部行为）、rpc_server_epoll_integration.cpp（真实调度）。

## 验收标准

- [ ] 最小堆定时器：插入乱序后按到期时间升序出堆；等时点条目 FIFO 稳定；cancel 后不触发；重复插入与堆增长正确（单测覆盖）
- [ ] epoll_wait 使用动态 deadline：堆顶最近到期时间作为超时；堆空时阻塞（timeout=-1），不再存在 RPC_EPOLL_TICK_MS 固定值（代码中无 100ms 心跳轮询残留）
- [ ] 连接事件用 data.ptr 直达连接对象：rpc-epoll.cpp 中无 conn_find 链表扫描路径，accept 与归还路径 data.ptr 均正确挂载
- [ ] 心跳定时器化：keepalive 精确到期判定（test_heartbeat / test_keepalive_timeout 保持通过，且验证到期时刻粒度由定时器驱动而非 tick 扫描）
- [ ] 默认值落地：rpc-epoll.h 定义 RPC_EPOLL_DEFAULT_* 常量；rpc_epoll_new(NULL) 生效默认配置（新增单测），rpc-config 默认值（DEFAULT_MAX_CONN 8 等）与之一致
- [ ] API 不变：rpc_epoll_config / rpc_conn_handler / rpc_epoll_* 签名与语义与 T0213 完全一致（编译 + 既有测试通过）
- [ ] 全量回归：xmake test 全部通过（含 conn_limit、rpc_server_epoll_integration、既有 RPC 测试），无新增失败
- [ ] ADR 记录：ADR-0011 更新或新增 ADR 记录最小堆定时器 + data.ptr 落地决策

## 范围外

- 复用 libs/ae（Redis 事件循环）：不采纳（定时器链表 O(n)，与现代最小堆有差距；不破坏 T0213 已落地的所有权转移/有界队列结构）
- 帧协议统一（心跳帧与裸消息协议兼容）：留作独立后续课题
- 多 Reactor（Netty 主从）架构：不在本次范围
- keepalive_interval 配置语义变更：不涉及

## 备注

- T0213 conclusion 已记录「固定 100ms tick 非动态 deadline、默认值仅注释」两项偏差，本任务正是其消项。
- conn_limit 心跳测试依赖 1.5s 收 Ping / 2s 断连，定时器精度提升后应更快收敛（断言窗口需宽松或按到期时刻精确断言）。
- 最小堆定时器若独立成模块，参考 muduo TimerQueue（std::set 红黑树在 C++ 侧；本项目 C 侧用数组最小堆，键为单调时钟 ms，避免 time() 秒级抖动）。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
