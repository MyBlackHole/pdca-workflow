# T0184 设计验证

本任务未修改 subvol 产品代码。

| 命令 | 结果 | 用时 |
| --- | --- | --- |
| `cargo test -p subvol superblock_fixed_layout_matches_local_format` | 通过 | 小于 1 秒 |
| `cargo test -p subvol validates_fixed_fields_and_members_v2_in_local_order` | 通过 | 小于 1 秒 |
| `cargo test -p subvol backup_scan_selects_highest_seq_and_recovers_without_primary` | 通过 | 小于 1 秒 |
| `cargo test --workspace --no-fail-fast` | 178 unit + 10 integration/property 通过 | 10.12 秒 |
| `cargo fmt --check -p subvol` | 通过 | 包含在同一 gate 命令 |

既有 dead-code/unused warnings 未产生失败；所有单项均在一分钟内。
