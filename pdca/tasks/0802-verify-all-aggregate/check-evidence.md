# T0194 Check 证据

## AC 对照

| AC | 证据 | 位置 |
|----|------|------|
| AC-1 | ac1-source-anchors.md（0. pass 驱动 `?:` 语义/1-4. 四个校验现状锚点） | pdca/tasks/0802-verify-all-aggregate/ac1-source-anchors.md |
| AC-2 | verify_all 顺序 拓扑→派生→桶索引→守卫，全部执行首个错误优先（`first_err.get_or_insert` 对应 `?:`） | engine.rs:742-775 |
| AC-3 | 35 处断言切换 verify_all（22 处桶索引 + guard + 属性测试 2 处）；not_rw 非法态 1 处保留单校验（正确） | engine.rs:2851+ 批量 |
| AC-4 | verify_all_keeps_first_error_when_multiple_checks_fail：桶索引坏 + 守卫坏 → 返回首个 NeedDiscardSet；runs_later_checks 验证顺序 | engine.rs:3025-3058 |
| AC-5 | 属性测试 2 处 prop_assert verify_all（3605/3774） | engine.rs:3605,3774 |
| AC-6 | workspace 211 lib + 10 集成全绿（10.19s/38.34s ≤1min）；fmt 通过；diff +136/-32 单文件 | subvol 9e6d564..新提交 |

## 验证命令

```
cargo fmt && cargo test --workspace
# lib: 211 passed, 10.19s; integration: 10 passed, 38.34s
```

## 审查

双轴审查 0 blocking / 0 MEDIUM / 0 LOW；顺序与 `?:` 首个错误优先语义
对齐 recovery.c:68-98；无跨调用持锁；发现 not_rw 非法态测试点保留单校验
（正确行为，非缺陷）。

## 边界

- not_rw 设备上 free 桶是测试故意构造的非法态，verify_all 在此状态必然
  失败——该测试点保留 verify_bucket_indexes 单校验（记录于审查报告）。
