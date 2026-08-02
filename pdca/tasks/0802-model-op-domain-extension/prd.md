# T0202 属性测试模型 op 域扩展：btree × alloc 组合与崩溃恢复对照

## 问题陈述

现有两个属性测试模型各自覆盖单一 op 域：`btree_proptest.rs`
（tests/）只做 btree put/delete（+事务批量、split、multi-snapshot、
journal corruption、崩溃恢复 sync 点）；`engine.rs:4063`
`open_bucket_discard_model_protects_open_from_reuse`（T0197）只做
alloc 域桶生命周期（queue_discard/reclaim/allocate/reopen/open/
close/set_device_rw + alloc 树投影），不含 btree put/delete。

两个域从未在单一随机序列中组合：**同一个持久化引擎上 btree 内容
与桶生命周期 op 交错执行，崩溃恢复后两者必须同时精确等于模型**。
T0200/T0201 disposition 均指向"模型 op 域扩展（属性测试模型加
op）"，本任务补齐该组合验证缺口。

## 目标

在 `crates/subvol/tests/btree_proptest.rs` 新增组合属性测试：随机
序列 op 域 = btree put/delete × alloc 生命周期（allocate_bucket /
reclaim_bucket / queue_discard_bucket / run_discard_worker_once）×
flush sync 点；模型三态对照（DEFAULT 树内容 + bucket 影子状态 +
queued 集合）；崩溃恢复后精确断言（scan 精确等于模型 + alloc 影子
状态精确 + verify_all + 无泄漏 + 队列排空）。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：alloc 域 op 语义（allocate/
      reclaim/discard 的上游对应与 T0192/T0197 知识）、T0197 模型
      结构（op 0..8 与影子状态）、crash_recovery_restores_sync_point_
      state 既有 sync 点模式（btree_proptest.rs:294-326）。
- [ ] AC-2: 组合 op 域模型：随机序列（op 域 = Put/Delete ×
      AllocateBucket/ReclaimBucket/QueueDiscardBucket/
      RunDiscardWorkerOnce × Flush sync 点）在持久化引擎上执行，
      模型三态（DEFAULT 树 BTreeMap + bucket 影子数组 free/btree/
      need-discard + queued 集合）与引擎实际状态逐步对照。
- [ ] AC-3: 崩溃恢复组合：sync 点丢弃引擎重建（open_persistent），
      恢复后 btree scan 精确等于模型 + alloc 影子状态精确
      （discover_discard_buckets 对照 need-discard 集合、
      open_bucket_count==0、discard_queue_empty）+ verify_all 通过。
- [ ] AC-4: 影子状态一致性：每步（或周期）alloc 树投影与模型
      bucket 影子数组一致（对齐 T0197 scan_raw_locked(4) 模式）；
      非法/边界 op（空间不足、重复 queue）期望与实现裁决一致。
- [ ] AC-5: 生产代码零改动（仅测试新增）；不新增公开 API。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过；新增 proptest
      用例单项 ≤1min（含现有 btree_proptest 37s 余量）。

## 实现决策

- 位置：`tests/btree_proptest.rs`（复用既有 key/value/op 策略、
  unique_tmp_dir、ModelEngine 模式与 proptest-regressions 机制）。
- 几何：固定 8 桶（JOURNAL 几何，nbuckets=8、first_bucket=0），
  free 集 4..=7（对齐 T0197/T0201 模式，allocate 确定性可分配）。
- op 语义对齐：
  - allocate_bucket(0)：成功返回 free 桶（影子 0→1 btree-owned）；
    空间不足/不可用时 Err。
  - reclaim_bucket(position)：btree-owned→need-discard（影子 1→2），
    非法（非 btree-owned）报对应错误。
  - queue_discard_bucket：need-discard→queued；重复 queue 报 -17。
  - run_discard_worker_once：queued 且可回收→free（影子 2→0）；
    队列空返回 Ok（-11 语义按实现）。
- 崩溃恢复：对齐 crash_recovery_restores_sync_point_state——flush
  sync 点 + drop + open_persistent + 精确断言。
- 断言不依赖顺序：单线程顺序序列无注入，模型对照精确（非最终
  一致放宽）。

## 范围外

open_bucket/close_open_bucket/set_device_rw（T0197 已覆盖守卫
语义）、并发注入（T0199/T0201 已覆盖）、多镜像、真实磁盘故障。

## 备注

前置：T0192（open bucket 生命周期知识）、T0197（模型守卫注入，
op 域 0..8）、T0199（并发注入+最终一致）、T0201（确定性崩溃点）。
生产代码零改动约束同 T0197/T0201。
