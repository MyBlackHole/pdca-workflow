# 物理 pointer 派生状态与恢复边界

对于 bcachefs 风格的物理 extent 或内部 btree pointer，主 pointer 更新不能被当作独立
bset 写入完成：transaction trigger 可在同一事务中派生 alloc、backpointer/
stripe-backpointer 以及 accounting/reconcile 更新。反向桶是从主 pointer 派生并供扫描、
校验使用的索引，不是可跳过的独立业务树。

恢复是该链的一部分。若 journal replay 显式使用 `BTREE_TRIGGER_norun`，则不能假定
派生状态已经维护；设计必须规定从主 pointer 重建派生状态，或采用经过证明的受控重放。
未定义该规则前，不应实现 transaction runner。

安全的交付顺序是：先定义单一格式的 physical pointer、alloc/backpointer 主从关系与
恢复合约；再按本地 bcachefs 的 sort-order、多轮追加 update 语义接入 transaction
runner 与 pointer/extent dispatch；最后实现派生更新及 crash/fault 验证。GC 另需
`gc_visited` 和 GC bucket/state 前提，不能作为该链的简化附加项。

来源：T0180，`records/T0180-0802-extent-alloc-btree-backpointer-trigger-audit/conclusion.md`。
