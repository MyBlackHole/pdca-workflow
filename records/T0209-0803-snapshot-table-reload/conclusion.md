# T0209 结论：快照表启动重建

任务：T0209-0803-snapshot-table-reload

## Verdict

**complete**（V-T0209-001）——4 项 AC 全部收敛，测试一次通过，
无修复需求，无遗留。

## AC 收敛状态

| AC | 内容 | 状态 | 证据 |
|----|------|------|------|
| AC-1 | 重开加载（对齐 bch2_snapshots_read 反向扫描重建） | 完成 | check-evidence |
| AC-2 | ancestor 语义与 filter_snapshots 重开真实生效 | 完成 | check-evidence |
| AC-3 | 多层快照树端到端一致性 + 继续写入 + 空表幂等 | 完成 | check-evidence |
| AC-4 | 全量测试 + fmt + diff gate | 完成 | check-evidence |

## 关键结论

1. 快照表生命周期缺口补齐：`bch2_snapshots_read`（snapshot.rs）对齐
   `snapshots/snapshot.c:783-806` 的反向遍历 + `__bch2_mark_snapshot`
   调用形式，挂在 `bch2_journal_replay` 之后（engine.rs
   attach_persistent_journal），重开后表内容与崩溃前（mark 填充）
   逐字段一致。
2. filter_snapshots 六步流程（iter.rs:2062-2152，对齐 iter.c:2808-
   2900）在重开后真实生效：过滤视图 `view=LEFT → [(1,ROOT),(2,LEFT)]`
   崩溃前后一致，LEAF 键被快路径滤除——engine 层 all_snapshots 规避
   场景（engine.rs:2419 注释）消除。
3. mark（事务触发）与加载（反向扫描）两路径共存一致：重开后继续写
   CHILD 快照键，表同步且 is_ancestor 正确。
4. 门禁：248 测试全绿（10.60s）、fmt 干净、diff 仅新增（3302e78）。

## 沉淀建议

- 快照表"mark 实时维护 + 启动反向重建"双路径模式、以及"重开验证
  ancestor 语义需 raw iter + set_snapshot + filter_snapshots"的测试
  手法，登记知识 `knowledge/core/`（快照表生命周期与过滤语义验证）。

## 后续

无遗留项。btree 核心盘点缺口 3（snapshot 遍历语义）闭环；缺口 1
（node_scan 全盘扫描重建）与缺口 2（节点级内容检查器）仍未排期。
