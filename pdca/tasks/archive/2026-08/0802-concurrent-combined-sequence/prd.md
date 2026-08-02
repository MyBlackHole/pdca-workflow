# T0203 并发组合序列：多写者 × alloc op × 崩溃恢复精确断言

## 问题陈述

T0202 已用单写者组合模型验证 alloc/btree op 域的崩溃恢复精确断言；
T0201 验证了多写者并发下崩溃恢复的最终一致。两者之间留有空白：
**并发 + 精确断言**（多写者交错提交后，崩溃恢复状态须等于已提交
op 的确定性重放模型，而非仅"一致"）。该空白是事务一致性的核心
承诺——并发提交顺序即持久化顺序。

## 目标

多写者线程（2-3）各自执行 btree/alloc 组合 op，经全局提交日志捕获
实际提交顺序；崩溃恢复后按提交日志重放模型做精确断言。提交日志 =
精确性的确定性来源（锁序 append + 崩溃点 sync 落盘）。

## 验收标准

- [ ] AC-1: 开始修改前复核本地 bcachefs 源码提交/落盘边界（journal
       replay 语义、btree_trans_commit 顺序、后台 alloc op 入口），
       并记录 T0199/T0201/T0202 已核对锚点的复用与新增点。
- [ ] AC-2: 子进程组合并发模式：N(2-3) 写者线程 Barrier 起跑，各自
       执行 combined op（put/delete/allocate/reclaim/queue_discard/
       run_discard_worker_once），每次成功提交后追加全局提交日志
       （锁保护，记录 op 类型与参数）；崩溃点 = 全线程完成 + 日志
       落盘 + sync + abort。
- [ ] AC-3: 崩溃恢复精确断言：父进程按提交日志重放 BucketModel
       （T0202 三态 + VecDeque + btree 模型），open_persistent 后
       engine 状态须与模型**精确相等**（btree 内容、alloc 树投影、
       发现/队列语义），非仅最终一致。
- [ ] AC-4: 确定性验证：固定种子下多次运行断言一致（日志决定模型，
       交错仅影响日志内容不影响可重放性）；并发边界覆盖——空间耗尽
       竞争（-28）、重复 queue（-17 并发幂等）、worker 回旋。
- [ ] AC-5: 定向、故障/属性和全量 workspace 测试通过，单项不超过
       一分钟（验证基线 --test-threads=4）。

## 范围外

GC trigger、stripe/EC、open/close/set_rw 守卫域（T0197 候选）、
真实磁盘故障、性能基准。

## 备注

复用：T0202 的 BucketModel/combined_op_strategy/rebuild_bucket_state
（crates/subvol/tests/btree_proptest.rs）；T0201 的
process_crash_child/concurrent_crash_child/Barrier/abort 框架
（engine.rs 测试区）。
