# T0203 check 阶段：AC 验收证据

## 实现清单

- subvol 新增 `crates/subvol/tests/concurrent_combined.rs`（无引擎改动，纯测试侧）：
  - `concurrent_combined_crash_child`：子进程模式（env 分派，T0201 框架）——
    WRITERS=3 写者线程 Barrier 起跑，各自执行组合 op（put/delete/allocate/
    reclaim/queue_discard/run_discard_worker_once），每次 op 在**测试锁内**
    完成"引擎提交 + 日志追加"（原子成对），日志顺序 == 引擎提交顺序；
    崩溃点 = 全线程完成 + 日志落盘 sync_all + engine.sync()（journal 落盘）
    + abort。
  - `concurrent_combined_crash_recovery_exact`：proptest 父测试（CASES=10，
    max_shrink_iters=0，计划 = WRITERS×6..=12 步随机组合）——子进程崩溃 →
    提交日志重放 BucketModel（btree BTreeMap + 三态 + queued + VecDeque，
    T0202 模型）→ open_persistent 后**精确断言**（非最终一致）：
    btree 内容 BTreeMap 精确相等、alloc 三态投影精确相等、discard 队列
    空（open_persistent 不自动入队）、discover 树位计数 == need-discard
    桶数、verify_all。
  - 模型重放 `replay()` 依赖日志行 `<op> | <result>` 二元组（err 编码），
    保证模型转换与真实提交序列同构；allocate 成功解析返回 offset 断言
    落在模型桶域。

## 上游锚点（AC-1）

见 ac1-source-anchors.md：journal replay 只回放已落盘记录
（fs/journal/read.c journal_replay_maybe_drop_overwrites，seq_ondisk 边界）
+ 提交顺序=持久化顺序（T0199 矩阵 + T0201）+ 组合 op 语义与队列持久性
（T0202 锚点表复用）+ 边界覆盖上游对应表。

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | ac1-source-anchors.md：提交/落盘边界复核（journal replay seq_ondisk / fs 锁提交串行化 / alloc op 入口），复用锚点表（T0199/T0201/T0202），新增点仅测试侧（计划生成器 / 日志协议 / alloc 投影） |
| AC-2 | 子进程组合并发模式 | concurrent_combined_crash_child：3 写者 Barrier 起跑 × 六种组合 op；锁内"提交+日志追加"原子成对；崩溃点 = 日志 sync_all + engine.sync + abort（ready 哨兵 durable-before-abort） |
| AC-3 | 崩溃恢复精确断言 | concurrent_combined_crash_recovery_exact：replay 日志重放模型后，btree BTreeMap 精确相等 + alloc 三态投影精确相等 + discard_queue_empty + discover 计数 == need-discard 桶数 + verify_all |
| AC-4 | 确定性验证 | 固定 CASES=10 连续 4 轮全过（日志决定模型，交错仅影响日志内容）；边界：-28 空间耗尽竞争（4 桶 × 并发 allocate）、-17 重复 queue 并发幂等、worker 回旋（非 need-discard 队首）、-11 空队 |
| AC-5 | 全量通过 | lib 230 passed（10.38s）、btree_proptest 15 passed（43.78s）、concurrent_combined 10 例×4 轮（约 4s/轮）、fsck_cli 5 passed、subvol-fsck 0/0；单项均 <1min（--test-threads=4） |

## 执行环境备注

- btree_proptest 首轮 600s 超时根因：/tmp 堆积 909 个旧测试残留目录
  （subvol-bucket-api-* 等）拖慢临时文件 IO；清理后 43.78s 正常，非代码问题。
- workspace 全量 `cargo test --workspace` 被中断后分包回归，结果如上。
