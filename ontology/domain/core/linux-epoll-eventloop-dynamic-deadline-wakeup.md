---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop-dynamic-deadline-wakeup
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/linux-epoll-eventloop-dynamic-deadline-wakeup/1.0.0
summary: epoll 事件循环工业对齐：最小堆定时器 + data.ptr + eventfd 唤醒
domain:
- ontology:domain/linux-epoll-eventloop
relations:
  specializes:
  - ontology:domain/linux-epoll-eventloop
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'epoll 事件循环工业对齐：最小堆定时器 + data.ptr + eventfd 唤醒' ontology/domain/core/linux-epoll-eventloop-dynamic-deadline-wakeup.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# epoll 事件循环工业对齐：最小堆定时器 + data.ptr + eventfd 唤醒

来源: records/T0214-0804-rpc-epoll-industrial-align/conclusion.md

## 核心模式（对齐 muduo/Netty/libuv）

1. **动态 deadline**：`epoll_wait(timeout = 堆顶最近到期时间 - now)`；堆空时
   timeout = -1 完全阻塞（空闲零 CPU 空转）。替换固定 tick 轮询。
2. **最小堆定时器**：数组二叉堆，键 = 绝对到期时间（CLOCK_MONOTONIC ms，
   避免墙钟回拨）；同到期时间按插入序号 FIFO 稳定；取消用懒删除标记
   （不移动堆）；堆仅 Reactor 线程操作。
3. **data.ptr 直达对象**：`epoll_event.data.ptr` 直接指向连接对象（O(1)
   取回），listenfd/wakefd 用 `data.fd` 区分——data.ptr 时 data.fd 为
   垃圾值，不可混读。worker 归还路径用 fd→对象开放寻址 hash 表（锁内
   O(1)）替代链表扫描。
4. **eventfd 唤醒管道（易漏陷阱）**：固定 tick 轮询时代 epoll_wait 每
   tick 返回一次，stop 置标志即可退出；改为动态 deadline 后堆空时
   `epoll_wait(timeout=-1)` 无限阻塞，**仅置 stopping 标志无法唤醒**，
   stop/join 永久挂起。必须创建 eventfd 注册进 epoll，stop 时 write 8 字节
   打断阻塞。wakefd 生命周期：new 时初始化为 -1（calloc 后为 0 会误用
   stdin）、start 失败/退出路径 close。

## 已知边界

- 心跳判死两级语义：空闲 interval 发 Ping、再 interval 判死（总判定
  2×interval）；若需字面 2×interval 第二级需单独排定。
- 连接关闭顺序：EPOLL_CTL_DEL → close → 释放（防 use-after-free）；
  DEL 返回 EBADF（fd 已被外部关闭）时跳过 close 防误关被复用 fd，但仍
  须从 fd map 移除防悬垂指针残留。

## 验收信号

- 事件循环改造类任务在 Do 早期先跑 stop/join 回归（graceful_stop），
  避免阻塞性发现拖后。
