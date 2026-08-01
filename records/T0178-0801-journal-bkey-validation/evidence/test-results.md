# T0178 验证结果

## 定向回归

`cargo test -p subvol journal::tests::replay_ -- --nocapture`

- 5/5 通过；包含新增：
  - `replay_drops_noncurrent_key_and_keeps_current_neighbor`
  - `replay_truncates_btree_key_entry_at_zero_or_overlong_key`
- 运行时间约 0.01 秒。

新增测试使用 checksum 完整的内存 journal record，直接经过
`bch2_journal_replay()`：

- 非当前 format 的坏 key 被删除，同行当前 format 键仍进入 overlay；
- 不足一个 bkey 头、零 `u64s`、超过 entry 尾部三种输入均截断 entry，且不进入
  overlay。

## 全量验证

`cargo test --workspace --no-fail-fast`

- lib：178 passed，0 failed（约 10.13 秒）；
- `btree_proptest`：10 passed，0 failed；
- 所有测试均远低于一分钟限制。

`cargo fmt --check -p subvol` 与 `git diff --check` 均通过。
