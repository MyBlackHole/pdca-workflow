---
schema: pdca.asset/v1
id: T0214-0804-rpc-epoll-industrial-align
phase: check
source_ids: [timer-heap-unit, conn-limit-regression, epoll-integration, full-regression, defaults-consistency, adr-0013]
---

## 上下文

T0213 将 rpc 服务端迁移到 rpc-epoll 调度层后，与 ADR-0011 声明存在四项偏差：
固定 100ms tick 轮询（非动态 deadline）、连接查找 O(n) 链表扫描、心跳全表
扫描、默认值仅注释。T0214 目标：事件循环对齐工业实现（muduo/Netty/libuv）——
最小堆定时器驱动动态 epoll_wait deadline、data.ptr O(1) 取回连接、心跳只处理
到期条目、默认值落地为代码常量；外部 API 与行为不变。

## 假设与结果

| 假设（PRD AC） | 结果 |
|----------------|------|
| AC-1 最小堆定时器（乱序升序/FIFO/取消/增长） | ✅ timer_heap_test 4 组单测全过 |
| AC-2 动态 deadline（堆顶到期时间，堆空 -1 阻塞） | ✅ 无 RPC_EPOLL_TICK_MS 残留；空闲阻塞 |
| AC-3 data.ptr O(1) 直达连接对象 | ✅ 无 conn_find；accept/归还路径均挂载 data.ptr |
| AC-4 心跳定时器化（到期条目驱动） | ✅ test_heartbeat/test_keepalive_timeout 通过 |
| AC-5 默认值落地（常量 + rpc_epoll_new(NULL)） | ✅ 与 rpc-config DEFAULT_* 一致（8/4/8） |
| AC-6 API 不变 | ✅ 签名语义未变，编译通过 |
| AC-7 全量回归 | ✅ xmake test 19/19 |
| AC-8 ADR 记录 | ✅ ADR-0013 新增 |

## 分析

1. **Do 阶段发现并修复一处回归**：动态 deadline 化后堆空时
   `epoll_wait(timeout=-1)` 无限阻塞，`rpc_epoll_stop` 仅置 stopping 标志
   无法唤醒 → stop/join 永久挂起（conn_limit 卡死根因，T0213 固定 tick 掩盖）。
   修复采用工业标准 eventfd 唤醒管道（对齐 muduo wakeup-fd），graceful_stop
   测试覆盖该回归。
2. **性能**：空闲零 CPU 空转（堆空阻塞）；定时器插入/弹出 O(log n)；
   fdmap 开放寻址均摊 O(1)。无退化路径。
3. **安全**：连接关闭先 EPOLL_CTL_DEL 后释放防 use-after-free；对已外部
   关闭 fd（EBADF）跳过 close 防误关被复用 fd；max_conn 超限拒绝保留。
4. **双轴审查**：标准轴 1 Warning（conn_close_locked 重复分支，轻微）；
   规范轴 0 发现。Blocking = 0 通过门禁。

## 失败原因

无（未 rejected/partial）。

## 适用边界

- 心跳判死语义：实现为「空闲 interval 发 Ping，再 interval 判死」（总判定
  2×interval），与 PRD 字面「2×interval 两级」的第二级间隔略有差异；cfg=1
  时 2s 断连行为与既有测试一致，保持现状。
- fdmap 删除回填算法为经典线性探测删除，容量 ≥2×max_conn 未触发退化；
  超高负载哈希退化未压测（连接数规模场景不达）。
- eventfd 唤醒依赖 Linux（项目平台，非移植目标）。

## 下一轮建议

- （可选）心跳第二级间隔改为精确 2×interval，消除字面语义差异。
- （可选）fdmap 高负载（接近 2×max_conn 占用率）插入/删除压测。
- 无遗留 Blocking 项。
