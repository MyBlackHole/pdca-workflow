# T0188 Check 证据

- 公开 API 端到端：覆盖多桶 geometry 边界、非法设备/越界 bucket、allocate→need_discard→free→reuse。
- 属性模型：16 组随机有限操作序列，每步校验 freespace 索引一致性。
- 故障注入：TransactionRestart 下 allocate 自动重试；JournalWrite 失败后状态保持一致。
- 重启：persistent journal flush 后 open_persistent，恢复后 verify_bucket_indexes 通过。
- 验证命令：`RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets`、`cargo fmt --all -- --check`、`git diff --check`。
- 结果：workspace 189 个测试通过，格式与 diff gate 通过。
- 代码提交：`bcab2e5`、`dc41723`、`798f5bf`。
