# T0179 Trigger 链适用性审计

## 调研目标

判定本地 bcachefs 的 transactional 与 GC trigger 机制，是否对 subvol 当前
可达的 `KEY_TYPE_cookie`、`KEY_TYPE_deleted`、`KEY_TYPE_snapshot` 及内部 snapshot
update 构成未实现的一致性缺口。

## 方法

1. 仅读取本地 `/home/black/Documents/bcachefs-tools/fs`：
   `fs/btree/commit.c:507-656`、`fs/btree/types.h:1255-1292` 和
   `fs/snapshots/snapshot.[ch]:488-560`。
2. 追踪 subvol 的键编码、update 元数据、commit 路径、snapshot marker 与
   `bch_fs` 状态：`engine.rs:806-870,1146-1162`、`btree/update.rs:1983-2055,
   2294-2301`、`snapshot.rs:475-525`、`btree/types.rs:495-510`。
3. 运行 snapshot 原子 trigger 单测、生成式普通事务恢复单测、完整 workspace
   测试和格式检查。

## 发现

### 上游三阶段的实际前提

| 阶段 | 本地 bcachefs 前提 | 对当前 subvol 的判定 |
|---|---|---|
| Atomic | `commit.c:1153-1160` 要求 node type 具备 atomic trigger；`types.h:1265-1272` 的 snapshots 在 atomic 掩码中 | `KEY_TYPE_snapshot` 已由 `update.rs:2294-2301` 运行 `run_one_mem_trigger(..., BTREE_TRIGGER_atomic)`；**已覆盖**。 |
| Transactional | `commit.c:552-646` 只对 `btree_node_type_has_trans_triggers()` 为真的类型循环；掩码为 extents/alloc/inodes/stripes/reflink/subvolumes/btree，明确不含 snapshots（`types.h:1255-1263`） | 当前可达的 snapshot 不要求此阶段；cookie/deleted 无 trigger 回调；**不适用**。 |
| GC | `commit.c:649-656` 同时要求具 trigger 的 node type、非 `norun` 及 `gc_visited(...)` | `bch_fs` 仅含 btree/journal/snapshots 等字段，没有 bcachefs GC position/visited 状态（`btree/types.rs:495-510`）；**不适用**。 |

### 当前键和路径映射

| 键/路径 | 生成与可达性 | Atomic | Transactional | GC |
|---|---|---|---|---|
| `KEY_TYPE_cookie` | 公共 `put` 经 `engine.rs:806-870` 调用 `encode_key()`；该函数在 `1146-1162` 编码 cookie | 不适用：`bch2_key_trigger()` 只派发 snapshot（`update.rs:1983-1992`） | 不适用：无 key trigger；即使 bcachefs runner 被调用也返回无 trigger 的零效果 | 不适用：无 GC 状态，且无 key trigger |
| `KEY_TYPE_deleted` | 公共 `delete` 复用同一编码路径，`encode_key()` 选择 deleted | 不适用：同上 | 不适用：同上 | 不适用：同上 |
| `KEY_TYPE_snapshot` | 内部 snapshot update 可经 `bch2_trans_update()` 入队；现有单测构造并提交该键（`snapshot.rs:710-742`） | 已覆盖：old/new 为 snapshot 时准确保留 insert/overwrite 分支（`update.rs:2022-2052`）；marker 更新 table（`snapshot.rs:475-525`） | 不适用：上游 snapshot 仅在 atomic 掩码 | 不适用：当前没有上游 GC 扫描模型 |
| journal replay | `journal.rs:1925-1934` 使用 `BTREE_TRIGGER_norun` 重放 | 不适用：显式抑制 | 不适用 | 不适用 |

`insert_trigger_run` / `overwrite_trigger_run` 在 subvol update entry 中存在且当前未由
transactional runner 消费，这与上游 `commit.c:552-646` 的循环结构相符；但这不是
当前缺陷的充分条件。要成立还必须有一个可达且属于 transactional-trigger node type
的键路径。上述枚举没有这样的路径。

### 验证结果

- `cargo test -p subvol atomic_snapshot_trigger_updates_memory_table`：通过，证明
  snapshot commit 后内存 snapshot table 更新。
- `cargo test -p subvol generated_recovery_matches_the_model`：通过，普通事务模型
  恢复保持正确。
- `cargo test --workspace --no-fail-fast`：178 个 unit tests 与 10 个 integration/
  property tests 全部通过；最长报告的单项为 10.12 秒。
- `cargo fmt --check -p subvol`：通过。

## 结论与建议

**不存在当前适用且缺失的 transactional 或 GC trigger 缺口。** 现有 snapshot
atomic trigger 已覆盖其上游对应阶段；普通 cookie/deleted 键没有 trigger 语义；GC
runner 缺少的是完整 bcachefs GC visited 模型，而该模型不在本项目当前范围。

不创建 bugfix 后续任务，也不改动引擎代码。将来若引入 extents、alloc、inodes、
stripes、reflink、subvolumes 或 btree-internal 等上游 transactional-trigger 类型，
必须先重新审计该新路径，并在同一 PDCA 周期中引入 bcachefs 的多轮 sort-order
transactional runner；若引入 bcachefs 等价 GC，则同时审计 `gc_visited()` 条件。

## 参考资料

- `/home/black/Documents/bcachefs-tools/fs/btree/commit.c:507-656,1153-1160`
- `/home/black/Documents/bcachefs-tools/fs/btree/types.h:1255-1292`
- `/home/black/Documents/bcachefs-tools/fs/snapshots/snapshot.c:488-560`
- `/home/black/Documents/subvol/crates/subvol/src/btree/update.rs:1983-2055,2294-2301`
- `/home/black/Documents/subvol/crates/subvol/src/engine.rs:806-870,1146-1162`
- `/home/black/Documents/subvol/crates/subvol/src/snapshot.rs:475-525,710-742`
- `/home/black/Documents/subvol/crates/subvol/src/btree/types.rs:495-510`
