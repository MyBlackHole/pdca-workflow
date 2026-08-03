# T0209 check 证据：快照表启动重建

提交：`3302e78`（crates/subvol/src/engine.rs +223、snapshot.rs +68，仅新增）

## AC-1 重开加载：完成

- `snapshot.rs` 新增 `bch2_snapshots_read(*mut bch_fs) -> i32`，对齐
  `snapshots/snapshot.c:783-806`：`bch2_btree_iter_peek_prev` + `rewind`
  反向遍历 id 0 快照树键（POS_MAX 起），过滤 `KEY_TYPE_snapshot` 后以
  `btree_trigger_op{old: bkey_s_c::default(), new: k, flags: 0}` 复用
  `bch2_mark_snapshot`（等价上游 801 行 `__bch2_mark_snapshot(trans,
  BTREE_ID_snapshots, 0, bkey_s_c_null, k, 0)` 直接调用，绕过 trigger
  dispatch；域内快照树 id 为自有编号，约束 14）。
- `engine.rs` `attach_persistent_journal` 在 `bch2_journal_replay` 后、
  `rebuild_derived_state` 前调用（对齐上游 snapshots_read 于 go_rw 前
  执行，snapshot.c:783 注释：bitmap 需祖先先初始化故反向遍历）。
- 验证：崩溃重开后逐字段断言表内容——ROOT(parent=0, children=[LEFT,
  RIGHT], tree=1)、LEFT(parent=ROOT, depth=1, skip=[ROOT,ROOT,ROOT])、
  LEAF(parent=LEFT, depth=2, skip=[LEFT,ROOT,ROOT])、RIGHT(parent=ROOT,
  tree=2)，四节点 state 均 live，与崩溃前（mark 填充）完全一致。

## AC-2 ancestor 语义重开可用：完成

- `bch2_snapshot_is_ancestor(LEAF, LEFT/ROOT)` true、`(RIGHT, LEFT)`
  false（跨分支）、`bch2_snapshots_same_tree(LEFT, ROOT)` true、
  `(LEFT, RIGHT)` false，重开前后一致。
- 过滤视图（`filtered_view(LEFT)`，raw iter `BTREE_ITER_not_extents |
  BTREE_ITER_snapshot_field` + `set_snapshot(LEFT)`，filter_snapshots
  自动启用）：崩溃前与重开后均等于 `[(1, ROOT), (2, LEFT)]`——即
  LEFT 视图可见祖先链 {root, left} 的键，LEAF（自身为 left 子孙）键
  经 iter.rs:2083 数值快路径滤除。证明 filter_snapshots 六步流程
  （iter.rs:2062-2152，对齐 iter.c:2808-2900）在重开后真实生效，
  不再依赖 all_snapshots 规避（engine.rs:2419 注释场景已消除）。

## AC-3 端到端一致性：完成

- 三层快照树（ROOT/LEFT/LEAF/RIGHT）raw 事务写入（KEY_TYPE_snapshot，
  u64s=12，值 56B 对齐 bch_snapshot 布局）→ `engine.sync()` 落盘 →
  drop（崩溃，不 flush）→ `open_persistent` 重开（journal 重放 +
  snapshots_read 重建）→ 表逐字段一致 + 过滤视图与崩溃前相等。
- 重开后继续 raw 写入 CHILD(LEAF 的子，depth=3) → 表同步（parent=LEAF、
  depth=3、is_ancestor(CHILD, ROOT/LEFT) true）——mark 与加载两路径
  共存一致。
- 空表幂等：既有 247 测试全部走 open_persistent（无快照键镜像），
  全量通过，加载空树无副作用。

## AC-4 门禁：完成

- `cargo test --lib`：248 passed（10.60s，新测试 0.02s），<1min（约束 9）。
- `cargo fmt --check`：干净。
- diff gate：仅 engine.rs/snapshot.rs 新增（+291），无既有逻辑改动。
- 无新警告（`cargo build --lib` 0 error 0 warning）。
