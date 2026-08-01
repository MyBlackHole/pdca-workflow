---
schema: pdca.asset/v1
id: T0169-0801-btree-commit-space-check-fix
phase: check
source_ids: [fix-commits, test-result, convergence-map]
---

## 上下文

T0169 修复 T0168 审计报告的 D1 CRITICAL 缺陷：`bch2_trans_commit` 空间检查未累加同一 leaf 多个 update 的累计占用（bcachefs commit.c:1083-1097 有 `u64s += i->k->k.u64s`），单事务连续键写满 512B 初始节点时 `bch2_bset_insert` 的 `copy_nonoverlapping` 越过 bset 尾部写坏堆（ASAN：heap-buffer-overflow WRITE of size 40）。范围限定 update.rs（commit 空间检查）+ bset_update.rs（断言）+ 回归测试，行为对齐 bcachefs commit.c，禁止自有逻辑。

## 假设与结果

假设：按 PRD 三个修复方向（同 leaf 累加、写入前 EBUG_ON 等价断言、超容量序列回归测试）修复后可消除越界写，且不引入 bcachefs 没有的逻辑分支。

结果：**成立，5/5 AC 验收通过**。三项修复全部落地：累加判空 + split/restart（`702c2a6`，对齐 commit.c:1083-1097 same_leaf_as_prev 语义）；写入前断言（`6701bf8`，位于 `bch2_btree_bset_insert_key_inlined` commit 写路径、`bch2_bset_insert` 调用前，对齐 commit.c:189-195 原位）；回归测试（`6701bf8`，单事务 32 键 ≈ 288 u64s 超 64 u64s 容量）。`cargo test --lib` 173 passed（~2.2s，约束 9 内），ASAN 运行回归测试无报告。

## 分析

- **AC-1**：update.rs `acc_u64s` 按相邻 update 的同一节点累加后调用 `bch2_btree_node_insert_fits`，语义对齐 commit.c:1083-1097（subvol 以 `last_leaf != b` 判同叶，bcachefs 以 `same_leaf_as_prev` 判相邻同 path/level，等价）。
- **AC-2**：放不下走既有 `bch2_btree_split_leaf` + `btree_trans_restart` 同步模型（PRD 指定复用路径）；173 测试全绿覆盖并发/崩溃/持久化，无死循环无丢失。
- **AC-3**：断言位于 commit 写路径（commit.c:194 `bch2_btree_bset_insert_key_inlined` 对应位置），debug 触发即 panic；刻意未放入 `bch2_bset_insert` 入口，避免误伤直接构造 fake 节点的既有单测（已验证 173 全绿）。
- **AC-4**：回归测试 32 键超容量序列直接覆盖原崩溃窗口（第 8+ 次插入时节点已满），commit 成功 + scan=32 + verify 通过；即使累加逻辑被回退，AC-3 断言也会先于越界拦截。
- **AC-5**：`cargo test --lib` 173 passed × 稳定；`-Zsanitizer=address` nightly 运行回归测试无报告。PRD 现象中的原崩溃测试（checkpoint COW 路径）随 checkpoint 迁移移除，其写路径由新回归测试等价覆盖。
- **范围约束**：仅改 update.rs + engine.rs（测试）；split 扩容（interior.rs/update.rs）为 512B 小节点容纳超容量序列的必要部分，随 `702c2a6` 提交；未引入 bcachefs 不存在的结构或控制流（约束 12/13）。

## 遗留风险

- ASAN 全量（非单测）未跑；原崩溃测试已移除，ASAN 验证以新回归测试为准，风险低。
- D2-D6（seq 环回、trigger 链、verify 覆盖、测试薄弱）不在本任务范围，已在 T0168 review-report 任务拆解中排期。
