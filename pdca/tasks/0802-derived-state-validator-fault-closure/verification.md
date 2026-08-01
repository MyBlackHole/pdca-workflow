# T0185 验证记录

## 代码结果

- 新增只读 derived validator：从 primary extent/btree pointer/btree pointer v2 推导 alloc
  bucket 与 backpointer 集合，比较 generation、dirty sectors、owner、level、bucket length
  和 owner position。
- recovery 的 `JournalSnapshot` replay 与 persistent journal replay 均在 rebuild 后执行 validator；
  mismatch 返回 transaction error，未做隐式修复。
- 代码提交：`336c570`、`8f1f189`。

## 命令证据

- `cargo fmt --all -- --check`：通过。
- `RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets`：184 个 unit tests 与 10 个
  property tests 全部通过。
- 单个定向 engine/update 测试均在一分钟内完成。

## 限制

当前验证器在 recovery 之后执行；故障点仍复用现有 transaction restart 与 journal write 注入，
未新增独立的中间 publication API。allocator/GC/LRU/stripe/fsck 仍明确不在范围内。
