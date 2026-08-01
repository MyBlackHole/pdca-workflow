# T0175 事务 commit 循环 ENOMEM restart 修复 — 结论

## 任务

修复 T0174 暴露的缺陷：split 路径大事务内存（subbuf）需求使
`Transaction(-12)` 硬失败，而 bcachefs 对 ENOMEM 执行 transaction restart。
修复并进一步定位出分裂路径三个独立缺陷：节点 512B 容量配置、trans
扩容未纳入 restart、journal reclaim 偶发 -9。

## 收敛结论

**结论：通过**（convergence valid=true，5/5 AC 全达标）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 split_stress 通过（不再 Transaction(-12)） | 通过（256 cases 全绿，多轮 10/10） | e1（diff:214 行）/ e2 |
| AC-2 全量回归绿 + fmt | 通过（lib 173/173、集成 10/10、fmt 干净） | e1 / e2 |
| AC-3 扩容仅 restart 时发生 | 通过（唯一入口 trans_begin restarted==5 分支） | e2 |
| AC-4 多轮稳定 | 通过（5 轮 10/10 + lib 173/173，含并行轮） | e2 |
| AC-5 bcachefs 语义对齐 | 通过（iter.c:3798-3800/3913-3933、commit.c:1319-1320、journal.c res_get_slowpath、commit.c:254） | e2 |

## 验证记录

- 修复后：无 Transaction(-12)、无 Journal(-9)、无 flush pin 丢失
- 关键回归锚点：lib 测试 `direct_reclaim_keeps_btree_pin_unflushed_after_write_error`
  （journal.rs:2767/2772，写盘失败后 pin 保留 unflushed）
- 5 轮全量：95.02s / 88.51s / 87.22s / 78.95s / 100.14s 均 10/10 全绿
- `cargo fmt --check -p subvol` 干净

## 根因与修复

1. **节点容量配置（根因 1）**：engine.rs `flags[0] = 1<<12`（512B）→
   `8<<12`（4KB）。512B 节点在 2000 键压力下必然触发第 4 级分裂越界
   `BTREE_MAX_DEPTH=4` → -12。对齐 bcachefs_format.h:1223 位域 12-27。
2. **trans 扩容未纳入 restart（PRD 根因）**：`__bch2_trans_kmalloc` mem
   不足时设置 `restarted=5`（mem_realloced，iter.c:3798-3800）；subbuf
   失败传播 -4（commit.c:1319-1320）；`bch2_trans_begin` 消费
   realloc_bytes_required 扩容（iter.c:3913-3933）；commit 循环
   `-12 && restarted!=0` 纳入重试，真 OOM 保持硬失败。
3. **journal reclaim 偶发 -9（并行路径）**：`bch2_journal_res_get`
   direct reclaim 未推进时等待重试（update_last_seq + 10s deadline +
   1ms sleep，对齐 journal.c res_get_slowpath()）；`__btree_node_flush`
   三分支语义修正（0=已写完 / -1=保留 unflushed / -5=写盘失败，
   对齐 commit.c:254），回收不丢 pin。

## 语义锚点

- fs/btree/iter.c:3798-3800（kmalloc 扩容 restart）、3913-3933（trans_begin
  消费扩容）
- fs/btree/commit.c:1319-1320（ENOMEM 与 restart 同级重试）
- fs/journal/journal.c:958-986（res_get_slowpath 10s 等待）
- fs/bset/commit.c:254（__btree_node_flush 已写完返回 0）
- 约束 12/13：所有控制流均可在上述 bcachefs 源码找到对应，无自有逻辑；
  无新结构体（BTREE_TRANS_MEM_MAX 改为 pub(crate) 仅形式调整）

## 备注

- 提交：bug-commit-format（【B-T0175】…，0.1.0 -> 0.1.0）
- 真 ENOMEM（超 BTREE_TRANS_MEM_MAX）路径保持硬失败（bcachefs 同，
  PRD 范围外声明）
- 本任务修复覆盖 T0174 暴露的三类缺陷（节点几何/trans restart/journal
  语义），PRD 方案中"不改动 commit 循环"因实际需要扩大为
  `-12 && restarted!=0` 兜底（仍以 -4 为统一 restart 表达）
