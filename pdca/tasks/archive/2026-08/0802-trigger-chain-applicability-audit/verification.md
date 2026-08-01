# T0179 验证记录

执行目录：`/home/black/Documents/subvol`。

| 命令 | 结果 |
|---|---|
| `cargo test -p subvol atomic_snapshot_trigger_updates_memory_table` | 通过 |
| `cargo test -p subvol generated_recovery_matches_the_model` | 通过 |
| `cargo test --workspace --no-fail-fast` | 178 个单元测试、10 个属性/集成测试通过；无失败 |
| `cargo fmt --check -p subvol` | 通过 |

编译过程报告既有 dead-code/unused 警告；无新增源文件修改，且命令以退出码 0 完成。
