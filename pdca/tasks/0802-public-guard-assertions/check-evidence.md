# T0193 Check 证据

## AC 对照

| AC | 证据 | 位置 |
|----|------|------|
| AC-1 | ac1-source-anchors.md（0. 聚合入口/1. open skip/2. ioref skip/3. umount/4. while-耗尽 五组锚点） | pdca/tasks/0802-public-guard-assertions/ac1-source-anchors.md |
| AC-2 | verify_guard_invariants 拒绝 open∧FREE（OpenBucketFree）；测试 verify_guard_invariants_rejects_open_free_bucket | engine.rs:688, :2968 |
| AC-3 | open_bucket_count 查询 + drop 泄漏测试前置 count 断言 | engine.rs:736, :3119 |
| AC-4 | discard_queue_empty 查询不 hook；三处队列空断言（-11 轮转路径验证） | engine.rs:749, :3206/:3228/:3312 |
| AC-5 | drop 泄漏/队列轮转/T0189 守卫/属性测试全部切换公共断言；属性测试逐 op verify_guard_invariants | engine.rs:3146, :3502 |
| AC-6 | workspace 208 lib + 10 集成全绿（10.19s/37.51s ≤1min）；fmt 通过；diff +160/-7 单文件 | subvol 9e6d564 |

## 验证命令

```
cargo fmt && cargo test --workspace
# lib: 208 passed, 10.19s; integration: 10 passed, 37.51s
```

## 审查

双轴审查 0 blocking / 0 MEDIUM / 0 LOW；锁序 fs→open_buckets→rw_devs 与
reclaim/discard 一致，无新锁序，三个 API 均只读。
