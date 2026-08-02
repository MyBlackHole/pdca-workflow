# 组合 op 域模型：btree × alloc 属性测试设计（T0202）

## 适用场景

同一持久化引擎上 btree 内容与桶生命周期 op 交错执行、崩溃恢复后
两者必须同时精确等于模型的属性测试设计。

## 关键事实（引擎语义）

1. **btree 数据全走 journal**：`sync()` 只 flush journal
   （engine.rs:1352），btree 节点不写桶 → 数据桶状态仅由 alloc op
   驱动，无 backpointer 干扰（reclaim 的 -16 守卫恒不触发）。
2. **discover_discard_buckets 是恢复入口**（engine.rs:1309）：扫描
   need_discard 树位并**重新入队**（insert + push_back + 计数返回），
   不只是统计。崩溃恢复后队列重建必须以它为权威（T0197 op4 模式）。
3. **need_discard 树 = 持久队列，fast_discard = 内存工作集**：
   open_persistent 不自动恢复 discard 队列（darray 内存态，
   discard.c:643）；树位保留（discover 可见）。
4. **组合域守卫全不触发**：无 open 桶、dev 恒 rw、无 backpointer、
   无脏/缓存扇区、journal_seq_empty 恒 0 → reclaim 恒成功（0↔2
   toggle）、discard 恒成功（队首 state==2）。
5. **bch_alloc_v4 data_type 字节偏移**：repr(C) 布局 bch_val(0B) +
   journal_seq_nonempty u64@0 + flags u32@8 + gen u8@12 + oldest_gen
   u8@13 + data_type u8@14 → 编码进 value[1]>>48（scan 解码后）。
   常量：FREE=0、BTREE=3、NEED_DISCARD=9。

## 模型结构

- btree 模型：BTreeMap<KeyPosition, Vec<u64>>（既有 apply_model/
  assert_model）。
- BucketModel：state[4]（0=free/1=btree-owned/2=need-discard）+
  queued[4] + queue VecDeque<usize>（与引擎 discard_inflight.0 严格
  同构：同 push/pop 序列）。
- op 策略混合 2:1:1:1:1（btree:allocate:reclaim:queue:once）。
- 崩溃点断言：assert_model + rebuild_bucket_state（alloc 树投影）==
  模型 state + discover 计数 == need-discard 桶数 + 模型队列重建
  （discover 入队顺序 = 树扫描键序 = offset 升序）。
- allocate 断言：返回最小 free 桶（freespace 位 ∩ FREE 升序第一个）；
  空间耗尽唯一失败路径 -28。

## 陷阱

- **崩溃后勿清空模型队列**：discover 已入队，模型必须同步重建
  （首跑即捕获此失配：模型空 vs 引擎 discover 入队）。
- T0197 的 reopen 重建模式（queued=true + push_back）是正确参照，
  不是缺陷。
- 队列断言顺序：open_persistent 后先断言 discard_queue_empty（验证
  darray 内存态），再 discover（重建入口），再断言计数。

## 上游锚点

- allocate：foreground.c free-bucket 候选规则
- reclaim：background.c 空桶回收（gen/oldest_gen 递增 + 双树位）
- queue/worker：discard.c:643 bch2_fast_discard_bucket_add（darray）
- discover：discard.c for_each_btree_key 扫描 need_discard 树
- freespace 位：background.c:1113 alloc_freespace_pos +
  bch2_btree_bit_mod_iter

## 测试设施模式

add_free_bucket（桶初始化）从 mod tests 提升为 StorageEngine 公开
方法（T0202 AC-5 偏离，用户裁决确认）：btree 模块私有致集成测试
无法访问 trigger_update_value/bch2_btree_bit_mod 等内部符号；公开
测试设施（doc 注释明确非运行时路径）优于 feature gate（构建复杂度）。
