# T0195 检查证据（check-evidence）

## AC-1：修改前逐段记录上游 fsck CLI 与引擎持久化 API 锚点

证据：`ac1-source-anchors.md`（实现前撰写）。
- 上游流程锚点 fsck.rs:419-447：打开设备 → `bch2_fs_fsck_errcode()` 全量 pass → 首错即停 → `eprintf` 错误 → `exit(ret)`。
- 参数表锚点 fsck.rs:56-64：`-n/--no_repair`（"Don't repair, only check for errors"）、`-f/--force`、路径。
- 引擎锚点：`StorageEngine::open_persistent`（engine.rs:513）、`verify_all`（engine.rs:739，拓扑→派生→桶索引→守卫，首错优先）。

## AC-2：打开持久化引擎运行 verify_all，通过退出 0，失败非 0 输出具体错误

- lib 新增 `fsck_image(path)`（engine.rs）：打开 + `verify_all()`，打开失败为 `EngineError::Io`，校验失败为原错误（如 DerivedState 变体）。
- bin 映射：0=通过（stdout "OK"）；1=校验失败（stderr "ERROR: {error}"，含 DerivedState 变体名）；2=打开/IO 错误（stderr "cannot open {path}: {错误名}"）。
- 单元测试：`fsck_image_passes_on_healthy_image`（Ok）、`fsck_image_io_error_on_unreadable_image`（Err Io）。
- 集成测试：`fsck_cli_healthy_image_exits_zero_and_prints_ok`（exit 0 + "OK\n"）；`fsck_cli_corrupt_image_exits_nonzero_and_prints_error_name`（exit 2 + "cannot open" + 错误名）；`fsck_cli_missing_image_exits_two`（exit 2）。
- 实现期澄清（clarifications.jsonl round 3）：打开路径总执行 `rebuild_derived_state`（engine.rs:1716，对齐上游恢复语义），预置索引不一致会被打开流程修复，故损坏文件体现为打开失败（Io + exit 2）；索引不一致校验失败路径（OpenBucketFree/NeedDiscardSet 错误名）由库级 `verify_all` 测试覆盖（T0194 新增 2 个 + 既有）。

## AC-3：仅 no-repair 模式，参数表对齐上游

- bin 手写解析：`-n/--no-repair`、`-f/--force` 接受（仅提示 no-repair 模式）；`-h/--help` 打印 USAGE；路径为位置参数。无修复路径（上游 `-n` 语义）。
- 零依赖（仅 std）。

## AC-4：集成测试覆盖健康与损坏文件

- 见 AC-2 三个集成测试。索引不一致错误名路径由库级 verify_all 测试覆盖（`verify_all_keeps_first_error_when_multiple_checks_fail` 断言 NeedDiscardSet 名）。

## AC-5：库 API 不变

- 仅新增 `fsck_image` 导出；`verify_all` 及其余公开 API 未改动；行为不变（CLI 是调用方）。

## AC-6：workspace 全量测试、fmt、diff gate

- `cargo fmt` 通过；`cargo test --workspace` 全绿：213 lib + 10 btree_proptest + 3 fsck_cli = 226；单项 ≤40s（AC 上限 1min）。
- 提交：subvol `fb9e85a`（4 files, +179/-3）。

## 结论

六项 AC 全部达成；实现期发现（打开即重建 derived）已以 round 3 澄清记录，验收口径落实为"损坏文件=打开失败非 0+错误名；索引不一致=库级错误名覆盖"。
