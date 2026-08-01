---
schema: pdca.asset/v1
id: T0180-0802-extent-alloc-btree-backpointer-trigger-audit
phase: check
source_ids: [evt-001, evt-002, evt-003]
---

## 上下文

T0179 曾仅审计 cookie/deleted 和 snapshot，用户要求补足空间分配、范围 key、内部
btree pointer、审计记录/反向桶 btree 的 trigger 依赖。本任务不改产品行为，只对照本地
bcachefs 与 subvol 的可达路径。

## 假设与结果

| 假设 | 结果 | 证据 |
| --- | --- | --- |
| range/extent 与物理 pointer 不需要 transaction trigger | 不成立；上游绑定 `bch2_trigger_extent()`，并要求多轮 transaction runner | evt-001 |
| 内部 btree pointer 不属于该链 | 不成立；`BKEY_TYPE_btree` 在 transaction mask，`btree_ptr`/`v2` 使用 extent trigger | evt-001 |
| backpointer 是独立触发源 | 不成立；它是 pointer 变更在同一事务中写入的派生 btree | evt-001 |
| 当前公开 cookie API 已因此损坏 | 未证实；公开写入强制 `not_extents`，当前无真实 physical bucket 模型 | evt-001、evt-003 |

## 分析

成立的完整边界是：extent leaf key 或内部 btree pointer 的 transaction trigger 可创建
alloc、backpointer/stripe-backpointer、accounting/reconcile 等派生 update；runner 必须按
sort-order 和多轮追加语义处理。journal replay 当前显式 `BTREE_TRIGGER_norun`，所以未来
派生状态需要预先规定重建或受控 replay，不能默认重放后已一致。

subvol 的 raw extent iterator/update 与 split pointer 构造提供了延展接缝，但 alloc、
backpointer、accounting、GC state 和相应 trigger runner 都不存在。GC 还额外依赖
`gc_visited` 与 GC bucket 状态，不能作为孤立事务功能移植。

## 失败原因

不适用：这是审计任务，没有失败的实现尝试。原先 T0179 的“无缺口”结论范围过窄，已被
partial verdict 和本任务的依赖图纠正。

## 适用边界

结论适用于 subvol 未来引入真实 physical extent/btree pointer、空间分配或反向桶索引的
情形；不把 bcachefs fs 层 btree-id 编号移植到 subvol。它不宣称当前 cookie/deleted
公开 API 已有 alloc/backpointer 数据损坏，也不授权不完整 GC 实现。

## 下一轮建议

建议顺序为：T0181 先固定最小 physical pointer/派生状态/恢复合约；T0182 再实现
transaction runner 与 pointer/extent dispatch；T0183 最后实现同事务 alloc/backpointer
维护和 crash recovery 验证。三个任务均已创建为 Plan，尚未开始 Do。
