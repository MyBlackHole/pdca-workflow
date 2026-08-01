# T0180 Do：extent/alloc/btree/backpointer trigger 依赖审计

## 结论

用户指出的两个边界均成立：空间分配/范围 key 需要 transaction trigger；
`BKEY_TYPE_btree`（内部 btree pointer）也在 transaction trigger mask 内。反向桶
（backpointer）不是独立触发源，而是 extent 或 btree pointer 的 pointer 处理在同一
事务中派生写入的 btree。当前 subvol 尚未提供真实物理 extent/分配器，所以这不是
现有公开 cookie API 的已证实数据损坏；但这些能力一旦进入生产路径，缺少该链会
导致 alloc、backpointer、accounting 与恢复状态失配。

## 上游语义锚点与完整链路

`fs/btree/commit.c:507-656` 的 transaction runner 按 trigger sort-order 运行
update；trigger 追加 update 后会再轮转，直到所有 update 已处理。每个 update 分别
标记 insert/overwrite trigger 已运行。GC runner 只在 key 属于可触发 node type、未被
`norun` 抑制，且 `gc_visited(c, gc_pos_btree(...))` 成立时运行。

`fs/btree/types.h:1239-1311` 表明 level > 0 的 node type 是 `BKEY_TYPE_btree`，且
extent、alloc、stripe、reflink、subvolume 与 **btree** 在 transaction mask 中；这不等同
于每条内部操作都走同一入口：interior 的 `skip_triggers` 路径可显式 `norun` 或手动
调用相应逻辑，必须在实际持久化路径上逐段确认。

```text
extent leaf key / internal BKEY_TYPE_btree pointer
                  |
                  | transaction trigger（按顺序、多轮，可追加 update）
                  v
          bch2_trigger_extent()
             |          |             \
             |          |              \-- replica/compression/accounting/reconcile
             |          v
             |   bch2_trigger_alloc(): bucket state/index/LRU/gen/counters
             v
 bch2_bucket_backpointer_mod()
             |
             +--> backpointers / stripe_backpointers btree（派生键，供扫描、校验）

journal/recovery: 若 replay 使用 BTREE_TRIGGER_norun，必须有明确的重建或受控重放设计
GC: 仅在完整 GC state + gc_visited 前提下运行，不能孤立移植
```

具体边：`fs/data/extents.h:419-446` 将 extent、`btree_ptr` 和 `btree_ptr_v2` 绑定到
`bch2_trigger_extent()`；`fs/alloc/buckets.c:620-930` 的 pointer 处理先启动 alloc
update、标记 pointer，再调用 `bch2_bucket_backpointer_mod()`，并完成 accounting/reconcile；
`fs/alloc/background.c:1232-1480` 的 alloc trigger 更新 bucket state、free index、LRU、
generation/device counters；`fs/alloc/backpointers.c:162+` 用同一 transaction 更新对应
backpointer btree。`fs/data/move.c:515` 的数据移动遍历 backpointer 与 stripe-backpointer
树，证明其是派生索引而非独立业务写入源。

## subvol 可达性与缺口

| 范围 | 可达性/现状 | 判定 |
| --- | --- | --- |
| 公共 StorageEngine 写入 | `engine.rs:806-870` 总是带 `BTREE_ITER_not_extents`；`1146-1162` 只产生 cookie/deleted | 现有 API 不产生物理 range/extent pointer，不能据此声称当前用户数据已漏记 alloc |
| raw range/extent 更新 | `btree/iter.rs:83-87` 可标记 extent iterator，`btree/update.rs:1510-1513` 可分派 `bch2_trans_update_extent()` | 路径存在，但没有 extent pointer 生产者及对应 trigger 维护；未来启用时缺口成立 |
| 内部 btree pointer | `btree/interior.rs:695-717` 在分裂时创建 `KEY_TYPE_btree_ptr_v2`，后续直接写 bset/parent | 确有 pointer key 构造；须在后续实现前审计其最终持久化路径，不能假定其已通过 transaction runner |
| alloc/backpointer 类型与状态 | `bset.rs` 有格式常量；`btree/types.rs`/`bch_fs` 仅有当前 btree、journal、snapshot 等核心字段 | 没有 bucket 状态、alloc/backpointer btree 的生产者、派生写入或校验器 |
| journal/recovery | `journal.rs:1890+` replay key update 使用 `BTREE_UPDATE_nojournal | BTREE_TRIGGER_norun` | 现有恢复不能自动维护未来派生状态；需要明定重建或受控 replay |
| GC | 未找到 `gc.pos`、`gc_visited`、GC bucket state 或 GC trigger runner | 不具备上游 GC trigger 的前提，单独移植不成立 |

在 subvol 中仅有 snapshot 的 memory trigger：`btree/update.rs:1983-2055` 与
`2294-2301`。未发现 transaction trigger runner、`bch2_trigger_extent`、
`bch2_trigger_alloc`、`bch2_bucket_backpointer_mod`、disk accounting 或 GC visited 状态。

## 确认缺失与拆分

以下项同时满足“上游存在语义、subvol 有可延展生产边界、没有等价维护”，但都只在
subvol 引入物理 extent/btree-pointer 存储能力后才应进入 Do：

1. **物理指针、alloc/backpointer 的持久化与恢复合约**：先定义最小数据模型、哪些是
   主数据/派生索引、以及 `norun` replay 后如何重建。这是 runner 的前置，不应凭空实现。
2. **transaction trigger runner 与 pointer/extent dispatch**：按上游 multi-round /
   sort-order 语义运行，且把 split 内部 pointer 的真正提交路径纳入覆盖。
3. **alloc/backpointer 派生维护与崩溃恢复验证**：在有前两项模型和 runner 后，实现
   pointer 增删对应的 bucket/backpointer 原子更新，并验证故障后无悬挂或遗漏索引。

GC 不创建开发任务：它依赖尚不存在的 GC position、visited 与 bucket GC 模型，先作为
未来完整 GC 设计前置审计，而非把不完整 runner 接入事务。

## 验证

下列既有定向测试均通过（每项约 0.1 秒）：

- `iter_flags_match_local_btree_property_normalization`
- `full_root_leaf_splits_grows_root_and_retries_insert`
- `multi_level_split_preserves_parent_pivot_invariants`
- `btree_roots_round_trip_through_current_journal_entry`
- `replay_restarts_after_a_leaf_split`

全量 workspace 测试与格式检查留在 Check 阶段复跑，避免把审计证据与最终 gate 混同。
