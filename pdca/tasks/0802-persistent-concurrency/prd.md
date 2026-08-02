# T0201 持久化并发交错：并发写者 + 崩溃恢复的组合验证

## 问题陈述

T0199 已验证并发交错下事务的最终一致（内存态断言：verify_all、
队列排空、无泄漏），T0195/T0196 已验证崩溃恢复的持久化边界
（journal 落盘 vs 未落盘）。但两个维度从未组合：**并发写者在
崩溃点（flush 前后）被打断后，恢复流程（journal replay 只回放
已落盘事务 + open_persistent 重建派生态）能否最终一致**。这正是
bcachefs 事务一致性的核心承诺：无论崩溃发生在并发的哪个时刻，
恢复后不变量必须成立。

## 目标

在持久化引擎上组合两个已验证模式：子进程并发写者（allocate/
reclaim/queue/discard worker 多线程）在确定性崩溃点（flush 前 /
flush 后 / 进行中）abort，父进程 open_persistent 恢复后
verify_all 通过、无桶泄漏、数据可读。验证恢复后的最终一致。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：崩溃恢复语义（journal replay
      只回放已落盘事务，replay.c）、flush 边界（fs.exit/umount
      语义）、并发提交（commit.c 锁序）与既有 T0195/T0196 崩溃
      测试模式、T0199 并发注入模式对应。
- [ ] AC-2: 并发崩溃子进程：子进程内 N 线程并发写者（Barrier
      起跑 + TransactionRestart 注入），主线程在确定性崩溃点
      abort；崩溃点覆盖 flush 前（部分并发事务落盘）、flush 后
      （全部落盘）、进行中（并发写未完成）。
- [ ] AC-3: 恢复验证矩阵：每个崩溃点后 open_persistent 恢复 +
      verify_all 通过 + 无桶泄漏（open_bucket_count==0）+ 数据可读
      （scan 完整）；崩溃点=flush 前的场景须实际丢弃未落盘事务
      （journal replay 语义实测）。
- [ ] AC-4: 并发注入与崩溃组合：注入下（TransactionRestart 共享
      计数被并发写者消费）崩溃恢复仍最终一致；断言只依赖最终
      一致不依赖到达顺序（对齐 T0199 原则）。
- [ ] AC-5: 生产代码零改动（仅测试新增）；不新增公开 API。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过
      一分钟（崩溃子进程测试需控制时间）。

## 实现决策

- 复用 run_crash_child / process_crash_child 既有子进程模式
  （engine.rs:5003-5044），扩展为并发写者 + 崩溃点。
- 崩溃点设计：flush 前（并发事务部分落盘，未落盘部分须被丢弃）、
  flush 后（全落盘，全部存活）、进行中（写者未完成时 abort）。
- 并发写者：allocate/reclaim/queue/discard worker 线程 + Barrier
  起跑 + TransactionRestart 注入（复用 T0199 模式）。
- 恢复断言：open_persistent + verify_all + open_bucket_count==0 +
  scan 完整；不依赖具体键值顺序（并发下顺序不定）。

## 范围外

模型 op 域扩展（属性测试模型加 op）、fsck 修复路径（T0200 已做）、
多镜像并发 fsck、真实磁盘故障模拟。

## 备注

前置：T0195（崩溃恢复子进程模式）、T0196（恢复故障矩阵）、T0199
（并发交错注入 + 最终一致断言）。引擎 Drop 不 flush（EngineState
drop 只停 worker + open 桶泄漏检查，engine.rs:1801-1836），abort
崩溃语义与真实 crash 一致。
