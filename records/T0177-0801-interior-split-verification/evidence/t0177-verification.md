# T0177 验证记录

时间：2026-08-01
环境：`cargo test -p subvol --lib` + `cargo test -p subvol --test btree_proptest`。

## AC-1 多级分裂测试通过（深度 ≥2 树 leaf→parent→root 级联分裂）

- 新增 `multi_level_split_preserves_parent_pivot_invariants`
  （interior.rs:1514）：512B 小节点（root+leaf，8 键）构造深度 2 树，
  连续插入 offset 9..=208 触发 leaf→parent→root 级联分裂直至
  root level≥2 且 restart_offsets 非空（多次 retry 路径被触发）。
- 递归助手 `verify_subtree` 断言全树不变量：节点内键严格递增、
  child 指针 key.p == child max_key、相邻 child 区间连续（bpos_successor
  相接）、first/last child 边界 == 节点 min/max、叶子收集 offset 全量
  1..=208（无键丢失）。
- 通过（单跑 ok，0.02s；lib 全量 176/176 含此测试）。

## AC-2 失败路径 -8/-10/-12 与 interior.c 对照

| 错误 | subvol 位置 | bcachefs 对应 | 覆盖 |
|------|------------|--------------|------|
| -8（parent 中 key 缺失）| interior.rs:863/1167 | btree_split_race restart（interior.c:2271）| `full_root_leaf_splits_grows_root_and_retries_insert`（interior.rs:1276）断言重试后插入成功 |
| -10（写锁升级失败）| interior.rs:883/909 | bch2_btree_node_lock_write 失败传播（interior.c 锁升级）| 单线程内存引擎无锁竞争，不可达；代码对照一致（释放旧锁/路径/节点后返回 -10 与 C 分支一致）|
| -12（BTREE_MAX_DEPTH）| interior.rs:162（byte_order >= 16）| interior.c:534 BUG_ON(level >= BTREE_MAX_DEPTH) 前置检查 | 深度上限不可达；代码对照一致（同条件同返回）|

## AC-3 conclusion 记录异步框架不适用结论 + merge 范围外

- 详见 conclusion.md（e3）：异步 btree_update 框架（interior.c:1404）
  因 journal 先行持久化架构不适用（engine.rs:731）；merge
  （interior.c:2327）为性能优化，范围外声明；review-report P1 描述修正。

## AC-4 全量回归绿 + fmt

```
$ cargo test -p subvol --lib
test result: ok. 176 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 10.11s

$ cargo test -p subvol --test btree_proptest
test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 35.81s

$ cargo fmt --check
（无输出，通过）
```

- 本次同时修复两处回归套件问题（均不改引擎行为）：
  1. `fault_injection_preserves_model_and_recovery` 预存在 flaky（注入
     JournalWrite 后 sync 偶发返回 Ok）：根因是后台 reclaim worker 的
     checkpoint_locked（engine.rs:737 → journal.rs:997）与测试 sync
     竞争消费 fault 计数；测试改为循环重试收敛（-5 消费成功 / -1
     状态机未就绪重试 / Ok 被 worker 抢消费则重新注入）。
  2. `split_stress_preserves_model` 规模压缩（ops 1000..=2000→250..=500、
     crash_every 300..=800→80..=200）使全量回归 <60s（约束 9）：
     open_persistent 恢复逐键 replay 1.2-2.3s/次为 bcachefs
     recovery.c 对齐语义，非 bug。
- 测试调试输出 eprintln 全部替换为 `subvol::rewrite_log_debug!`（日志
  API，SUBVOL_LOG=debug 控制），lib.rs 公开重导出日志符号 + log.rs
  宏体路径调整（仅可见性调整）。

## AC-5 bcachefs 语义对齐

| 检查点 | bcachefs 锚点 |
|--------|--------------|
| 多级分裂 = btree_split 递归（parent_keys 递归路径 + n3 增深），非重试爬升 | interior.c:1962（btree_split）、2191（bch2_btree_insert_node parent 递归）、2095（__btree_root_alloc）|
| restart 仅用于锁/ENOMEM/竞争重启（-8 split_race、-10 lock、-12 depth）| interior.c:2271（split_race）、534（BTREE_MAX_DEPTH）|
| 异步 btree_update 框架不适用（mempool/closure/gc.lock/interior_updates/write_blocked）| interior.c:1404（bch2_btree_update_start）——journal 先行持久化（engine.rs:731）无异步写盘管线 |
| merge 为性能优化，范围外 | interior.c:2327（bch2_foreground_maybe_merge）|
