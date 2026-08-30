---
schema: pdca.asset/v1
id: ontology:domain/core-persistent-concurrency-crash-recovery
type: domain
layer: Knowledge
status: active
summary: 持久化并发交错：并发写者 × 确定性崩溃点
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 持久化并发交错：并发写者 × 确定性崩溃点

> 沉淀自 T0201（V-T0201-001 confirmed），前置：T0195 崩溃子进程、
> T0196 故障矩阵、T0199 并发交错注入、T0200 修复路径故障注入。

## 核心概念

并发写者（btree put + alloc 混合）在确定性崩溃点（flush 前 / flush
后 / 进行中）abort，父进程 open_persistent 恢复后最终一致的组合
验证。核心承诺（bcachefs）：无论崩溃发生在并发的哪个时刻，恢复后
不变量成立（verify_all、无桶泄漏、数据可读）。

## 崩溃点设计（对齐上游）

| 崩溃点 | 写者状态 | flush | 恢复断言 |
|---|---|---|---|
| cc-flush-before | 全部完成（12 事务） | 无（JournalWrite 注入） | 0 键（未落盘必丢） |
| cc-flush-after | 全部完成（12 事务） | flush_journal | 12 键全存活 |
| cc-mid-write | 进行中（abort 打断） | 后台 reclaim 竞态 | 最终一致 + 子集 |

- 写者：4 线程 × 3 轮，Barrier(5)（4 写者 + 主线程全程参与，参与者
  数必须等于 waiters，T0199 规则），每轮 btree put + allocate +
  双 reclaim（freespace 回收，T0199 模式）。
- 注入：TransactionRestart 一次性（共享计数被并发写者消费）+ 可选
  JournalWrite 多次（写盘故障）。
- mid-write 用"barrier slack"定位：主线程等过起跑 barrier 和首轮
  结束 barrier 后返回，此时所有写者确定在第 2 轮中——abort 必落在
  写进行中，无需猜时序。

## 关键语义

1. **未落盘必丢的确定性需要排除后台 reclaim**：journal 初始即
   med=true（4 桶几何 clean*4 <= total*3 恰在边界），每次 commit 都
   schedule_reclaim_if_needed，worker 每 25ms 醒来 checkpoint——
   "abort 抢在 25ms 窗口前"是时序假设，不成立。确定性方案二选一：
   - 停 worker（stopping=true + join）**不可行**：request_reclaim_inner
     在 stopping 时返回 Transaction(-1)（stopping=只读，对齐 bcachefs
     ro 后拒新事务），停后 put 必失败。
   - **JournalWrite 注入（可行）**：bch2_journal_flush 在构造与推进
     seq 之前消费 fault_inject_write_error 并返回 -5（journal.rs:
     1009-1015）——任何 flush 尝试（含后台 reclaim）都失败，内存
     记录保留至 abort 后丢失；故障引擎局部，恢复时无注入。
2. **后台 reclaim 竞态是正常行为**：并发写者跑 >25ms 时部分事务
   已被后台落盘，崩溃后存活集不确定（与 bcachefs background
   journal reclaim 一致）——该场景只断言最终一致与存活集子集，
   禁止断言特定存活数（T0199 原则）。
3. **注入次数要覆盖整个崩溃窗口**：写者 3 轮约 100-200ms，worker
   每 25ms 醒一次，注入 20 次写盘故障覆盖全部唤醒；注入计数归零
   后无开销（fetch_update checked_sub）。
4. **崩溃点诊断永久化**：abort 前打印 journal 状态（seq_ondisk /
   space[clean,total] / closed / pin）经 rewrite_log_info! 输出——
   seq_ondisk 是"是否已落盘"的唯一人工审计锚点；用日志 API 而非
   临时 eprintln（避免每次调试重加日志）。

## 复用指南

- 新的崩溃恢复组合任务：复制 run_crash_child/process_crash_child
  子进程模式 + Barrier 写者 + 崩溃点选择 + 父进程 open_persistent
  恢复矩阵。
- 确定性"未落盘丢弃"场景：JournalWrite 注入（引擎局部故障），
  绝不依赖 abort 时序；"最终一致"场景：不注入，断言子集与一致。
- 断言铁律：并发场景只断言最终一致（verify_all + 无泄漏 + 键有序
  + 存活集约束），不依赖到达顺序或特定存活集。
