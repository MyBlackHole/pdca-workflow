# T0175 验证记录

时间：2026-08-01（最终回归轮）
环境：`cargo test -p subvol --lib` + `cargo test -p subvol --test btree_proptest`。

## AC-1 T0174 split_stress_preserves_model 通过

- 修复后 `Transaction(-12)` 不再出现：本轮 256 cases 全绿（10.12s lib /
  100.14s 集成），此前多轮 78.95-95.02s 同样 10/10。
- 修复内容（e1 diff：214 行）：
  1. engine.rs `flags[0] = 8<<12`（512B → 4KB 节点，根因 1：512B 节点在
     split 压力下 2000 键必然触发第 4 级分裂越界 BTREE_MAX_DEPTH=4 → -12）
  2. engine.rs commit 循环：`-12 && trans.restarted != 0` 纳入 restart 重试
     （对齐 commit.c:1319-1320，ENOMEM 与 transaction_restart 同级重试）；
     新增失败诊断日志（restarted/req/mem_bytes/nr_updates）
  3. update.rs `__bch2_trans_kmalloc`：mem 已存在需扩容时设置
     `trans.restarted = 5`（BCH_ERR_transaction_restart_mem_realloced，
     对齐 iter.c:3798-3800）
  4. update.rs `bch2_trans_subbuf_reserve`：subbuf alloc 失败且 restarted
     已设置 → 返回 -4（restart 传播，对齐 commit.c:1319-1320）；真 OOM 保持 -12
  5. iter.rs `bch2_trans_begin`：restarted==5 时消费 realloc_bytes_required
     扩容 trans mem（realloc，失败降级 BTREE_TRANS_MEM_MAX，再失败保留原
     mem 重试；对齐 iter.c:3913-3933）
  6. journal.rs `bch2_journal_res_get`：direct reclaim 未推进时等待重试
     （update_last_seq + 10s deadline + 1ms sleep，对齐 journal.c
     res_get_slowpath() total_wait=max(max_dev_latency*2, HZ*10)），消除
     split 压力下并行 reclaim 偶发 Journal(-9)
  7. update.rs `__btree_node_flush` 三分支语义（0=已写完/-1=保留
     unflushed/-5=写盘失败，对齐 fs/bset/commit.c:254 与
     __btree_node_flush() 失败 break 语义）——journal 回收不丢 pin

## AC-2 全量回归绿 + fmt

```
$ cargo test -p subvol --lib
test result: ok. 173 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 10.12s

$ cargo test -p subvol --test btree_proptest
test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 100.14s

$ cargo fmt --check -p subvol
（无输出，通过）
```

- lib 173 含关键回归锚点 `direct_reclaim_keeps_btree_pin_unflushed_after_write_error`
  （journal.rs:2767/2772 断言：写盘失败后 pin 保留 unflushed 列表），验证
  flush0 语义修改未破坏既有行为。

## AC-3 trans 扩容仅在 restart 时发生

- 扩容唯一入口：`bch2_trans_begin` 中 `restarted == 5` 分支消费
  `realloc_bytes_required`；`__bch2_trans_kmalloc` 仅在 mem 已存在且不足时
  设置该字段并返回 restart。正常运行路径（mem_bytes==0 首分配、空间充足）
  不触发扩容。无运行时回归。

## AC-4 多轮稳定

- 多轮全量验证：95.02s / 88.51s / 87.22s / 78.95s / 100.14s 均 10/10 通过
  （proptest）+ lib 173/173；含 `-- --test-threads=4` 并行轮。
- 修复后无 Journal(-9)、无 Transaction(-12)、无 flush pin 丢失。

## AC-5 bcachefs 语义对齐

| 修复点 | bcachefs 锚点 |
|--------|--------------|
| restarted=5（mem_realloced） | fs/btree/iter.c:3798-3800 `__bch2_trans_kmalloc` |
| trans_begin 消费扩容 | fs/btree/iter.c:3913-3933 `bch2_trans_begin` |
| -12 纳入 restart 重试 | fs/btree/commit.c:1319-1320 `bch2_trans_commit` |
| subbuf 失败传播 restart | commit.c:1319-1320（restart 统一 -4 表达） |
| res_get 等待重试（10s） | fs/journal/journal.c:958-986 `res_get_slowpath()` |
| flush 三分支语义 | fs/bset/commit.c:254 `__btree_node_flush()` |
| 节点 4KB 几何 | bcachefs_format.h:1223 `BCH_SB_BTREE_NODE_SIZE`（位域 12-27） |
