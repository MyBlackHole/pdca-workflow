# T0178 分诊简报

## 分类

- 类别：bug
- 场景：bugfix
- 优先级：P1（恢复期可接受 checksum 完整但布局非法的 btree key）

## 已核验事实

1. `journal.rs` 的恢复循环仅检查部分 entry/key 的 u64 长度边界，随后直接构建
   overlay 并重放；非当前 format 的 key 可进入底层 bkey 路径并触发断言。
2. 本地 bcachefs `fs/journal/validate.c:53-139` 对每个 btree key 调用
   `bch2_bkey_validate()`；非法 key 按其 fsck 分支从 entry 删除，不能进入
   后续 replay。
3. 本地 bcachefs `fs/btree/bkey_methods.c:213-295` 定义基础 bkey 语义：
   最小 u64s、适用于 btree/level 的 key type、size 与 position/snapshot
   约束，以及 key-value 验证。
4. 严格使用 bcachefs fs 层 type/size/snapshot 规则不可行：subvol 默认
   `BtreeId(0)` 写入 `KEY_TYPE_cookie,size=0,snapshot=0`，而 bcachefs 的
   id 0 extents 规则会拒绝这些当前合法记录。该差异受 AGENTS.md 第 14 条豁免。
5. 本地 `Cargo.toml` 已有 `proptest`；当前 `cargo test --workspace --no-fail-fast`
   基线通过（176 个单测与 10 个属性/集成测试）。

## 去重

- 已搜索 active/archive task 与 knowledge；没有“journal bkey semantic
  validation”同类进行中或已归档任务。
- T0172 的 journal 损坏属性测试和 T0176 的 seq 边界测试覆盖记录层/序号边界，
  不覆盖 checksum 完整的单 key 语义损坏，故不重复。

## 推荐

以本地 bcachefs 的 `journal_validate_key()` →
`journal_entry_btree_keys_validate()` 的 type-independent 前置布局分支为唯一
依据，在恢复前校验并剔除/截断坏 key；不移植依赖 bcachefs fs 层 btree-id 的
type/size/snapshot 规则。
