# T0186 验证记录

- 新增公开 `StorageEngine::verify_derived_state()` 与 `DerivedStateMismatch`。
- 新增 `RecoveryFaultPoint::{AfterJournalReplay, DuringDerivedRebuild, BeforePublication}`
  和 `recover_with_fault()`。
- fault matrix 测试确认三个阶段均返回错误，不发布成功恢复状态；无 fault baseline 会执行
  public validator。
- `RUSTFLAGS='-Awarnings' cargo test --workspace --all-targets`：185 个单测、10 个属性测试
  全部通过。
- `cargo fmt --all -- --check`：通过。
- 代码提交：`d544fed`、`2dd20e3`。
