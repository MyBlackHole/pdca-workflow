# T0176 验证记录

时间：2026-08-01
环境：`cargo test -p subvol --lib` + `cargo test -p subvol --test btree_proptest`。

## AC-1 flush 在 seq 溢出时返回 -2 且 seq 不推进

- 新增 `flush_returns_shutdown_at_seq_overflow`：`journal::default()` 后置
  `seq = JOURNAL_SEQ_MAX`（同步 ring[1].seq 满足 flush 内
  old_buf.seq==old_seq 断言），`bch2_journal_flush` 返回 -2，seq 保持
  JOURNAL_SEQ_MAX 不推进。
- 通过（单跑 ok；lib 全量 175/175 含此测试）。

## AC-2 恢复路径超上限 seq 拒绝（-5）有测试覆盖

- 新增 `journal_read_rejects_seq_above_max`：带设备 bch_fs（bucket
  start=32 nr=4、bucket_size=2）bucket 起始写入
  `seq = JOURNAL_SEQ_MAX + 1` 的记录（合法 magic/version/flags），
  `bch2_journal_read` 返回 -5（journal.rs:1349 条件组），cur_seq 不推进。
- 通过。

## AC-3 结论沉淀（D2 纠误 + 锚点）

- 溢出=emergency read-only（journal.c:442），非环回；-2 行为保持。
- seq_blacklist 不适用（seq_blacklist.c:13-38 前提 + write-ahead 顺序），
  详见 conclusion.md。

## AC-4 全量回归绿 + fmt

```
$ cargo test -p subvol --lib
test result: ok. 175 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 10.11s

$ cargo test -p subvol --test btree_proptest
test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 105.18s

$ cargo fmt --check -p subvol
（无输出，通过）
```

## AC-5 bcachefs 语义对齐

| 检查点 | bcachefs 锚点 |
|--------|--------------|
| JOURNAL_SEQ_MAX = (1<<56)-1 | fs/journal/types.h:18 |
| 溢出 → emergency read-only + shutdown | fs/journal/journal.c:442、init.c:499 |
| seq_blacklist 用途（忽略过新 bset） | fs/journal/seq_blacklist.c:13-38 |
| 恢复拒绝超上限 seq | journal.rs:1349（与 bcachefs read.c 同条件） |
