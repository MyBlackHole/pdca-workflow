# Triage Brief: T0215 rpc-epoll 多 Reactor 分片

## 分类

- 类别：enhancement（性能优化/重构）
- scenario_type：development
- 来源：T0214 工业对齐完成后用户询问"还有哪些工业优化推荐"，选定 A1 多 Reactor

## Claim 验证

- 已验证：当前 `rpc/rpc-epoll.cpp` 为单 Reactor（单个 `epoll_wait` 线程 + worker 池）
- bench_download（256MB×5轮）实测单连接 ~900MB/s，触及单核事件分发上限
- 多连接并发下单 Reactor 串行处理 accept/事件分发，为吞吐天花板
- 结论：多 Reactor 分片优化成立，收益预期与核数相关

## 查重

- 活跃任务：0731-pg-physical-ordered / T0164-0731-gm-tls-benchmark /
  T0210-0803-btree-node-sector-persistence —— 无 Reactor 相关
- knowledge 查重：仅 linux-epoll-eventloop/dynamic-deadline-wakeup.md（T0214 沉淀，
  含 epoll_wait 阻塞/唤醒机制）、debugging/rpc-epoll-blocking-fd-trap.md ——
  相关但不重复，属本任务前置知识
- 结论：无重复任务，可进入 Plan

## 信息缺口

1. 目标部署核数与多连接并发场景（影响默认 reactor_count 策略）
2. SO_REUSEPORT vs 主从 Reactor 的选择（影响架构与验收）
3. max_conn/max_workers 全局 vs 每 reactor 语义
4. 心跳/队列背压在多 reactor 下的保持方式

## 建议下一步

进入 P1 澄清 → P2 Grill（一次一问，优先确认架构选型与默认值策略）→ P3 PRD 合成
