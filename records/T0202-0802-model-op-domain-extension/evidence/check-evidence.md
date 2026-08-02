# T0202 check 阶段：AC 验收证据

## 实现清单

- subvol `f9df169`：engine.rs +86/-54（add_free_bucket 提升）+ btree_proptest.rs +295
  - `add_free_bucket` 从 mod tests 提升为 `StorageEngine` 公开方法（逻辑零变化，43
    处调用点机械改写；锚点 fs/alloc/background.c:1113 alloc_freespace_pos +
    bch2_btree_bit_mod）
  - `combined_alloc_discard_and_btree_ops_match_model`：组合 proptest（crash_every
    9..=17）——op 域 = Put/Delete × AllocateBucket/ReclaimBucket/QueueDiscardBucket/
    RunDiscardWorkerOnce；模型 = btree BTreeMap + BucketModel（state[4] 三态 +
    queued[4] + VecDeque 队列），崩溃点三态同时精确断言
  - 崩溃点重建：rebuild_bucket_state（scan alloc 树解析 data_type，bch_alloc_v4
    布局 value[1]>>48）+ discover_discard_buckets 重新入队同步 + 队列清空断言
    （open_persistent 不自动入队）+ need_discard 树位计数对照
  - 4 个确定性边界用例：空间耗尽 -28 / 重复 queue -17 / worker 空队与回旋 / 
    reclaim→discover→worker 全链路回 free

## 上游锚点（AC-1）

见 ac1-source-anchors.md（alloc op 语义上游对应表 / background.c:1113 freespace
位维护 / T0197 模型结构 / crash sync 点模式 / 组合模型设计推导）。

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | ac1-source-anchors.md：alloc 域 5 个 op 上游对应（foreground.c 候选规则 / background.c 回收 / discard.c:643 darray / fast_work 单桶 / need_discard 树扫描）、alloc 键与 freespace 位维护、T0197 模型结构、crash sync 点模式（btree_proptest.rs:294-326） |
| AC-2 | 组合 op 域模型 | combined_alloc_discard_and_btree_ops_match_model：随机序列 2:1:1:1:1 混合策略；每步引擎调用 + 模型同步 + 前置/后置断言（allocate 返回最小 free 桶、reclaim 恒成功 toggle、queue 重复 -17、once 回旋语义） |
| AC-3 | 崩溃恢复组合 | sync 点 drop + open_persistent：btree assert_model 精确 + rebuild_bucket_state == 模型 state 精确 + discover 树位计数 == need-discard 桶数 + discard_queue_empty（open_persistent 不自动入队）+ verify_all（assert_model 内）；最终收尾同断言 |
| AC-4 | 影子状态一致性 | 崩溃点 alloc 树投影与模型 state 逐项一致（解析 bch_alloc_v4 data_type）；确定性边界：4 桶全占 allocate -28、重复 queue -17、空队 -11、非 need-discard 队首回旋 -11、reclaim→discover→worker 全链路后桶回 free 可再 allocate |
| AC-5 | 生产代码零改动 | **部分偏离**：生产行为零改动（引擎逻辑零变化），但 add_free_bucket 从 mod tests 提升为公开方法（新增公开 API 面）。偏离理由：btree 模块私有（mod btree 不导出），集成测试无法访问 trigger_update_value/bch2_btree_bit_mod/scan_raw_locked 等内部符号，无法在测试文件初始化桶状态；替代方案（feature gate）增加构建复杂度且 lib.rs 需 re-export。提升为"仅供属性测试初始化的测试设施"（doc 注释明确非运行时路径），需 verdict 确认 |
| AC-6 | 全量门禁 | 229 lib + 15 btree_proptest（44.46s ≤1min，--test-threads=4）+ 5 cli 全绿；fmt 通过。备注：默认 16 线程全并行下 split_stress 偶发 >60s（stash 原版同样复现，既有环境问题非本次引入，与并发度相关），验证基线 --test-threads=4 |

## 结论

待 verdict 确认（AC-5 偏离需裁决）。
