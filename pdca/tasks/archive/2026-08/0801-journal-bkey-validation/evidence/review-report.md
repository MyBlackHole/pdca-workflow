# T0178 双轴代码审查

比较基点：工作树相对 `HEAD` 的 T0178 改动，仅涉及
`crates/subvol/src/journal.rs`。

## 标准轴

- unsafe 指针访问先以 entry 剩余 u64 数检查最小 `BKEY_U64S` 头，避免 Rust
  精确长度 Vec 在读取 header 前越界；此边界是 C 固定 journal buffer 与 Rust
  Vec 表示差异所必需的内存安全保护。
- 截断和紧缩后均调用对照 C 函数同名的 `journal_entry_null_range()`，后续扫描
  能以零 payload 的空 entry 前进。
- 新增测试从恢复入口观察 overlay 结果，未绑定私有辅助函数。
- 未发现 Blocking 或 Warning 级问题。

## 规范轴

- AC-1：source-alignment.md 逐段记录 `validate.c:64-91` 和不移植边界。
- AC-2/AC-3：坏 key 在 overlay/replay 前处理；format 坏键与合法邻键共存已验证。
- AC-4：覆盖不足一个 header、零 u64s、越界、非当前 format 和合法 format。
- AC-5：定向、全量、fmt 和 diff 检查均通过。
- 未发现范围蔓延：未增加 fs 层 type/size/snapshot 规则、格式变更或运行时依赖。

结论：标准轴 0 个 Blocking / 0 个 Warning；规范轴 0 个 Blocking。
