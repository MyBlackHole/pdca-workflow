# T0195 双轴代码审查报告（review-report）

审查范围：subvol 提交 `fb9e85a`（engine.rs 新增 fsck_image + lib.rs 导出 + bin/subvol-fsck.rs + tests/fsck_cli.rs），对照上游 fsck.rs 当前版（Rust 版）。

## A 轴：上游语义对齐

| 检查点 | 上游锚点 | 本实现 | 结论 |
|---|---|---|---|
| 打开→全量 pass→首错退出 | fsck.rs:419-447（fsck_errcode 流程） | `fsck_image` = open_persistent + `verify_all()`（拓扑→派生→桶索引→守卫，首错优先，engine.rs:739） | 对齐 |
| no-repair 模式 | fsck.rs:266-269 `no_repair` → `fix_errors=no`+`nochanges` | bin 接受 -n/--no-repair；引擎无修复路径，天然仅检查 | 对齐 |
| 参数表 | fsck.rs:38-56（no_repair `-n`、force `-f`、devices 位置参数） | -n/--no-repair、-f/--force 接受、路径位置参数、-h 帮助 | 对齐（仅保留相关子集） |
| 失败输出错误名 | fsck.rs:419-447 eprintf 错误 | stderr "ERROR: {error}"（DerivedState 变体名）、"cannot open {path}: {io 错误名}" | 对齐 |
| 退出非零 | fsck.rs exit(ret) | 0/1/2 分层（终审确认） | 对齐 |
| 打开即重建 derived | engine.rs:1716（恢复语义） | 未改动；CLI 损坏场景=打开失败，索引不一致由库级 verify_all 错误名覆盖（round 3 澄清） | 一致 |

无新增上游不存在的行为分支：fsck_image 仅组合既有 open_persistent/verify_all；bin 仅参数解析与退出码映射。

## B 轴：安全/健壮性

- 路径参数直接透传 `open_persistent`，无 shell 拼接（Command 集成测试不经过 shell）；无注入面。
- 错误路径完整：Io → exit 2（具体 io 错误名）；校验 → exit 1；全部错误均输出到 stderr，stdout 仅 "OK"。
- 文件过短/无效内容：attach_persistent_journal 检查长度（engine.rs:1673-1681 UnexpectedEof），不会越界。
- 无 panic 路径：解析失败/缺参数 → usage → exit 2；`BtreeKey::new` Result 已 unwrap 但仅测试内使用固定合法值。
- 集成测试以 `CARGO_BIN_EXE` 跑真实二进制，进程级验证退出码与输出；临时文件唯一命名（pid+线程名），测试清理完整。

## 结论

两轴通过；无阻塞项。残留：lib 既有 never-used 警告（非本次引入）。
