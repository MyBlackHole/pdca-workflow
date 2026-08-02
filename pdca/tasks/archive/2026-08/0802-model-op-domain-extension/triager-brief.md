# T0202 Triage Brief：属性测试模型 op 域扩展

## 任务概述

现有两个属性测试模型各自覆盖单一 op 域：
- `btree_proptest.rs`（tests/）：btree 域 put/delete（+事务批量、
  split、multi-snapshot、journal corruption、崩溃恢复 sync 点），
  不含 alloc 域 op。
- `engine.rs:4063 open_bucket_discard_model_protects_open_from_reuse`
  （T0197 注入守卫）：alloc 域 op（queue_discard/reclaim/allocate/
  reopen/open/close/set_device_rw + alloc 树投影 + open/queued 影子
  状态），不含 btree put/delete。

两个域从未在单一随机序列中组合：**同一个持久化引擎上，btree 内容
与桶生命周期 op 交错执行，崩溃恢复后两者必须同时精确等于模型**。
这正是 T0200/T0201 disposition 的"模型 op 域扩展（属性测试模型加
op）"。

## 上游锚点（初步核对）

- allocate/reclaim/discard 语义：foreground.c / discard.c / alloc 树
  （T0187/T0188/T0190 已锚定，T0192 open-bucket-lifecycle 知识）
- alloc 树投影对照：T0197 模型既有 scan_raw_locked(4) 模式
- 崩溃恢复 sync 点：crash_recovery_restores_sync_point_state 既有
  模式（快照 = sync 点，恢复后 scan 精确等于模型）
- 最终一致原则：组合场景若含并发注入才放宽为最终一致；本任务
  单线程顺序序列，断言精确对照（对齐 T0199 原则的边界）

## 方案（草案，待 Grill 确认）

1. btree_proptest.rs 新增组合属性测试：随机序列 op 域 =
   Put/Delete（DEFAULT 树）× AllocateBucket/ReclaimBucket/
   QueueDiscardBucket/RunDiscardWorkerOnce（桶生命周期）×
   FlushJournal（sync 点）。
2. 模型状态：BTreeMap<KeyPosition, Vec<u64>>（DEFAULT 树）+ bucket
   影子状态数组（free/btree-owned/need-discard）+ queued 集合。
3. 断言：每步或期末 verify_all + open_bucket_count==0 +
   discard_queue_empty + discover_discard_buckets 对照 + scan 精确
   等于模型；崩溃恢复后同样断言。

## 风险

- 组合 op 的模型复杂度（bucket 状态机 × btree 内容）反例定位困难，
  但 proptest-regressions 已有最小反例机制。
- 随机 allocate/reclaim 需要固定几何（8 桶、free 集 4..=7），
  与 T0197 模型一致。
- 超时：新增 proptest 用例需 ≤1min（AC-6），CASES 需控制。

## 建议

按上述方案立项；AC-1 锚点、AC-2 组合 op 域、AC-3 崩溃恢复组合、
AC-4 影子状态一致性、AC-5 零生产改动、AC-6 门禁。
