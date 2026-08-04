# ADR-0013: rpc-epoll 事件循环工业对齐 — 最小堆定时器 + data.ptr + eventfd 唤醒

- 日期: 2026-08-04
- 状态: 已确认

## 背景

T0213 将 rpc 服务端迁移到 rpc-epoll 调度层（ADR-0011），但落地与声明存在
四项偏差：固定 100ms tick 轮询（非动态 deadline）、连接查找 O(n) 链表扫描、
心跳全表扫描、默认值仅注释。T0214 按 ADR-0011 承诺对齐 muduo/Netty/libuv
工业实现。

## 决策

- **最小堆定时器**（rpc-timer-heap）：数组二叉堆，键 = 绝对到期时间
  （CLOCK_MONOTONIC ms，避免墙钟回拨）；同到期时间按插入序号 FIFO 稳定；
  取消用懒删除标记（不移动堆）；堆仅 Reactor 线程操作，取消可由持有者线程调用
- **动态 deadline**：`epoll_wait timeout = 堆顶最近到期时间 - now`；堆空时
  timeout = -1 完全阻塞（空闲零 CPU 空转）；不再存在固定 tick
- **data.ptr O(1) 取回连接**：`epoll_event.data.ptr` 直接指向 `rpc_conn_entry`，
  删除连接链表与 `conn_find`；listenfd/wakefd 用 `data.fd` 区分（data.ptr 时
  data.fd 为垃圾值，不可混读）
- **fd → 连接开放寻址 hash 表**：worker 归还路径（锁内）O(1) 找回连接对象，
  删除线性扫描；容量 ≥ 2×max_conn
- **心跳定时器化**：每连接一个保活定时器（空闲 interval 发 Ping、已 Ping
  再 interval 判死断开），只处理到期条目；删除 100ms 全表扫描
- **eventfd 唤醒管道**：stop 时写 eventfd 打断无限阻塞的 epoll_wait（堆空
  时 reactor 无事件可唤醒，仅置 stopping 标志会导致 join 永久挂起）
- **默认值落地**：rpc-epoll.h 定义 `RPC_EPOLL_DEFAULT_MAX_CONN 8` /
  `RPC_EPOLL_DEFAULT_MAX_WORKERS 4` / `RPC_EPOLL_DEFAULT_QUEUE_CAPACITY 8`；
  `rpc_epoll_new(NULL)` 生效默认配置

## 权衡

- 备选：复用 libs/ae（Redis 事件循环）—— 放弃（定时器链表 O(n)，与最小堆
  有差距；不破坏 T0213 已落地的所有权转移/有界队列结构）
- 备选：timerfd 驱动定时器 —— 放弃（单 timerfd 需频繁重设，多 timerfd 需
  epoll 注册管理，最小堆直接驱动 timeout 更简单，对齐 ADR-0011）
- 备选：红黑树定时器（nginx）—— 放弃（数组最小堆实现更简单，插入 O(log n)
  已满足连接数规模）
- 备选：stop 用信号打断 epoll_wait —— 放弃（信号处理侵入全局，eventfd
  为线程本地、无信号干扰）

## 影响

- rpc/rpc-epoll.cpp：Reactor 调度重写（定时器堆 + fdmap + data.ptr + 唤醒）
- rpc/rpc-timer-heap.{h,cpp}：新增最小堆定时器模块（供复用）
- rpc/rpc-epoll.h：默认值常量 + `rpc_epoll_new(NULL)` 语义
- 外部 API（rpc_epoll_config / rpc_conn_handler / rpc_epoll_* 签名语义）不变
- 新增测试 rpc/tests/timer_heap_test.cpp；conn_limit / 集成测试全量回归
