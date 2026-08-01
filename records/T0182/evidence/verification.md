# T0182 验证结果

执行时间：2026-08-02（Asia/Shanghai）

命令：

```text
RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets
cargo fmt --check
git diff --check
```

结果：成功。workspace unit tests 为 184 passed、0 failed；`btree_proptest` 为
10 passed、0 failed；最长输出的全量测试总用时约 10.12 秒，低于一分钟限制。
fmt 与 diff 检查均无输出且退出成功。

覆盖的 T0182 接缝：

- raw extent transaction：有效 pointer 的 alloc/backpointer 只维护一次；offline、dead
  member、zero bucket size 和 out-of-bounds pointer 均返回错误，且 transaction 仍只有
  primary update、没有派生 update。
- runner：sort order（alloc 在 stripes 后）、multi-round update、insert/overwrite 与 norun
  replay 的无派生写入均有单测。
- physical interior：old/new pointer trigger、journal primary entry、split/grow/restart
  的写入与恢复路径均由 update/interior/engine 回归覆盖。
- recovery：派生树被清空后从 primary pointer 重建；journal crash/replay 与 property
  recovery tests 均通过。

提交基线：`7cebcc9`；交付提交：`64e6a49`、`e857bf1`、`7bd0fb0`、`3539402`、
`33773ac`、`ed16ccd`、`10b9463`。
