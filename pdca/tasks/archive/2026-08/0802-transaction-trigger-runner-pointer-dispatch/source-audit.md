# T0182 本地 bcachefs 源码对照审计

审计时间：2026-08-02（Asia/Shanghai）

| PRD 验收项 | 本地唯一依据 | 对照结果 |
| --- | --- | --- |
| AC-1 / AC-3 | `fs/btree/commit.c:560-647`、`fs/btree/types.h:1363-1373` | `run_one_trans_trigger()` 的 insert/overwrite 状态与 `bch2_trans_commit_run_triggers()` 的 sort-order 多轮、norun 跳过已对应到 `btree/update.rs`；未启用 GC runner。 |
| AC-2 | `fs/sb/members.h:399-435`、`fs/alloc/buckets.c:785-892` | member-live、online、bucket geometry 与 pointer admission 的错误边界对应到 `trigger_pointer_validate()`；持久化打开时以 members-v2 建立 dev 0 online。 |
| AC-4 | `fs/data/extents.h:419-446`、`fs/alloc/buckets.c:894-931`、`fs/alloc/backpointers.h:170-220` | extent、btree_ptr、btree_ptr_v2 共用 extent trigger；旧 pointer 先移除、再加入新 pointer；interior level 使用固定 btree node sectors。 |
| AC-4 / AC-5 | `fs/btree/interior.c:844-907,939-1142,1267-1304` | physical interior publication 遵循 old trigger + overwrite journal、new trigger + btree/root journal；新节点先写，split restart 中保留待发布状态，旧节点延后处理。 |
| AC-5 | `fs/init/recovery.c` 的 journal replay/recovery pass 边界 | journal replay 使用 norun；`StorageEngine::recover()` 与 persistent reopen 之后才清空并按 primary scan 重建 alloc/backpointer。 |

本任务没有引用网络资料或外部 bcachefs 版本；上述路径均位于
`/home/black/Documents/bcachefs-tools`。
