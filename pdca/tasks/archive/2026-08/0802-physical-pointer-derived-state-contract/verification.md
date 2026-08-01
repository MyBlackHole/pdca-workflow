# T0181 设计验证

本任务未修改 `/home/black/Documents/subvol` 产品代码；验证的是合约所依赖的现有
transaction/journal/split 恢复接缝。

| 命令 | 结果 | 用时 |
| --- | --- | --- |
| `cargo test -p subvol replay_restarts_after_a_leaf_split` | 通过 | 小于 1 秒 |
| `cargo test -p subvol btree_roots_round_trip_through_current_journal_entry` | 通过 | 小于 1 秒 |
| `cargo test -p subvol full_root_leaf_splits_grows_root_and_retries_insert` | 通过 | 小于 1 秒 |
| `cargo test --workspace --no-fail-fast` | 178 unit + 10 integration/property 通过 | 10.12 秒 |
| `cargo fmt --check -p subvol` | 通过 | 包含在同一 gate 命令 |

输出含既有 dead-code/unused warnings，无失败；每项均低于一分钟。

## 接手检查

- T0182 的 PRD 已以本设计的 main/derived 边界为前置，负责 sort-order/multi-round
  runner、extent/btree pointer dispatch 与 split persistence trace。
- T0183 的 PRD 已以 T0181/T0182 为前置，负责 alloc/backpointer 写入、rebuild、
  validator 与 crash/fault 验证。
- 任何一项在 T0181 未 confirmed 前均未进入 Do；当前仍保持 Plan。
