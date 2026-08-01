# T0180 验证记录

执行时间：2026-08-02（Asia/Shanghai）。本任务只变更 PDCA 审计工件，未变更
`/home/black/Documents/subvol` 产品代码。

| 命令 | 结果 | 用时 |
| --- | --- | --- |
| 五项定向 `cargo test -p subvol <test-name>`（iterator、root split、multi-level split、journal roots、split replay） | 5/5 通过 | 每项约 0.1 秒 |
| `cargo test --workspace --no-fail-fast` | 178 unit + 10 integration/property 通过 | 约 10.1 秒 |
| `cargo fmt --check -p subvol` | 通过 | 包含在上述 gate 命令内 |

测试输出含既有 `dead_code`/unused warnings；无失败。所有单项均小于项目要求的一分钟。
