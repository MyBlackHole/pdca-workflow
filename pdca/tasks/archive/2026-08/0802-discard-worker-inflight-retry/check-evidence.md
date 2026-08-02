# T0190 Check 证据

- in-flight 去重：重复 queue 返回 EEXIST 类 `-17`，不重复插入。
- EAGAIN 重试：boundary 未满足时 worker 保留队列项并返回 `-11`，条件满足后重试成功。
- 状态收束：成功 discard 移除 in-flight，并保持 alloc/need_discard/freespace/generation 一致。
- 重启恢复：`discover_discard_buckets()` 从持久化 need_discard btree 重新发现未完成工作。
- 验证命令：`RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets`、`cargo fmt --all -- --check`、`git diff --check`。
- 结果：workspace 191 个测试通过，fmt/diff gate 通过。
- 代码提交：`1b3e85d`、`e0325ea`。
