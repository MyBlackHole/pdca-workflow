# T0187 Check 证据

- 本地 bcachefs 对照：`source-audit.md` 已记录 buckets/background/backpointers/discard/recovery 锚点。
- Rust 变更提交：`bfaea0a`、`ee73ce3`、`d3c557d`、`2172a85`、`446bb13`。
- 验证命令：`RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets`、`cargo fmt --all -- --check`、`git diff --check`。
- 结果：workspace 测试通过，subvol 单元测试 187/187 通过，格式与 diff gate 通过。
- 已验证：alloc/free/need_discard 状态、generation 编码、freespace 索引、反向引用拒绝、恢复重建与事务重试。
- 遗留范围：完整 discard worker、open-bucket GC、完整后台 GC 不在本任务 PRD 范围内。
