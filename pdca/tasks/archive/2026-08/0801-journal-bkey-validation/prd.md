# T0178 补 journal btree key 逐键布局校验并锁定恢复隔离行为

## 问题陈述

- **现状**：恢复期对 `BCH_JSET_ENTRY_btree_keys` 未在 overlay/replay 前完成
  bcachefs 式的逐键布局处理；checksum 完整但 key u64s 为零、越过 entry 或
  format 非当前版本的记录可进入后续路径，非当前 format 已可触发断言 panic。
- **目标**：在 overlay/replay 前按本地 bcachefs 当前
  `journal_validate_key()` / `journal_entry_btree_keys_validate()` 的
  type-independent 布局分支逐键验证并处理坏 key，使其不能影响恢复树状态。
- **差距**：本地 bcachefs `fs/journal/validate.c:53-139` 对零 u64s、越界和
  非当前 format 的 key 执行截断或删除/紧缩；subvol 仅在后续循环返回错误或
  触发断言。

## 解决方案

先逐段对照本地 bcachefs `fs/journal/validate.c:53-139`。按相同顺序，在
subvol journal 恢复入口逐键处理：零 u64s 截断该 entry、key 超出 entry
截断该 entry、非当前 format 删除该 key 并紧缩剩余 payload。确保后续 overlay
和 replay 仅遍历剩余合法布局的键。不得引入自定义 key-type 规则、数据格式或
恢复分支。

## Seam 分析

### 测试接缝

- journal replay：构造当前固定布局的、checksum 完整的 `jset` 记录，并直接
  调用恢复入口。
- 可观察行为：恢复返回值、overlay 是否含该 key、目标 btree 是否未被该 key
  修改。
- 既有先例：`journal.rs` 的 root journal round-trip/invalid-size 测试，以及
  `btree_proptest.rs` 的 journal corruption 测试。

### 验收可测性

- 每个损坏类别均以确定性 record 注入并观察返回值及恢复后状态。
- 正常合法 key 的 replay 保持现有行为，防止校验误拒绝。
- 定向和全量测试均须在一分钟内完成。

## 用户故事

作为存储引擎使用者，我希望恢复过程不会接受 checksum 虽正确但内容语义非法
的 journal btree key，以便介质或故障注入造成的异常记录不会污染可恢复数据。

## 实现决策

- 验证来源唯一为本地 bcachefs：`journal_validate_key()` 与
  `journal_entry_btree_keys_validate()` 的控制流，及
  `bch2_bkey_validate()` 的适用语义。
- 校验位置在 overlay/replay 之前；不改变 journal 顺序、checkpoint 或数据格式。
- 只覆盖当前 subvol 支持的 btree id/type 集合；缺少的 bcachefs fs 层类型
  继续受 AGENTS.md 第 14 条范围豁免。
- 若逐段对照证明某 bcachefs validator 前提在同步 write-ahead 架构不存在，
  在结论中记录不适用依据，而不臆造替代逻辑。

## 测试决策

- 先写失败测试：current-format 但语义非法的 key 不进入 overlay/重放。
- 覆盖 key u64s 为零、key 越过 entry、非当前 format，以及格式正确的合法键。
- 覆盖合法的多 key entry 仍完整恢复，及坏 key 与合法邻键共存时 bcachefs
  删除/紧缩后的行为。
- 运行定向单测、`cargo test --workspace --no-fail-fast` 与
  `cargo fmt --check -p subvol`。

## 验收标准

- [ ] AC-1: 修改前已逐段读取本地 bcachefs `journal/validate.c:53-139`，实现的零 u64s、越界、非当前 format 分支均有明确源码锚点且保持该顺序。
- [ ] AC-2: checksum 完整但布局非法的 btree key 不会进入 journal overlay 或修改恢复后的 btree；零 u64s/越界按 bcachefs 截断语义处理，非当前 format 按删除/紧缩语义处理。
- [ ] AC-3: 合法 btree key（含同一 entry 的多个 key）仍可恢复；坏 key 与合法邻键共存时只剔除坏 key，合法邻键仍可进入 overlay/replay。
- [ ] AC-4: 覆盖 key u64s 为零、超出 entry、非当前 format 与合法 format 四类确定性输入；每个测试有明确 pass/fail 断言。
- [ ] AC-5: 定向测试、`cargo test --workspace --no-fail-fast` 和 `cargo fmt --check -p subvol` 全部通过；任何单测在一分钟内完成。

## 范围外

- seq_blacklist 或 seq 环回（T0176 已确认不适用/非 bcachefs 语义）。
- bcachefs fs 层 key type/size/position/snapshot 语义校验：subvol btree id
  独立且现有 cookie 键不满足 extents 树规则，直接移植将误拒当前合法数据。
- 事务 trans/gc trigger 链、递归 fsck、write-buffer 完整路径、多版本数据格式
  迁移与运行时依赖 bcachefs-tools。

## 备注

- 来源：T0168 D5（journal 仅有 jset 头校验、缺逐 key 语义校验）。
- 本任务是恢复正确性 bugfix，不改变单一格式版本。
