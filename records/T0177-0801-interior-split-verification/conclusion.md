# T0177 验证 interior split 多级分裂语义对齐与异步 btree_update 框架不适用性 — 结论

## 任务

T0168 review-report P1 行（0801-btree-core-completeness/evidence/
review-report.md:114）声称 interior split_interior/异步 update_start
语义「部分模块未对齐」（矩阵三：interior.rs 缺异步 btree_update 框架/
split_interior/merge）。本任务对照本地 bcachefs interior.c 全文（3853
行）细分验证：多级分裂语义是否已存在、异步框架是否适用、merge 是否
属交付门槛，并补测试锁定。

## 收敛结论

**结论：通过**（convergence valid=true，5/5 AC 全达标）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 多级分裂测试（深度 ≥2 级联，verify+scan）| 通过（新增测试 ok）| e1（diff）/ e2 |
| AC-2 失败路径 -8/-10/-12 对照（可达分支有覆盖）| 通过（-8 retry 测试既有；-10/-12 不可达，代码对照一致）| e1 / e2 |
| AC-3 conclusion 沉淀（异步不适用 + merge 范围外 + P1 修正）| 通过（本 conclusion）| e3（本文件）|
| AC-4 全量回归绿 + fmt + <60s | 通过（lib 176/176、集成 10/10、37s、fmt 干净）| e1 / e2 |
| AC-5 bcachefs 语义对齐 | 通过（interior.c:1962/2095/2191/2271/534/1404/2327）| e2 |

## 验证记录

- 新增 `multi_level_split_preserves_parent_pivot_invariants`
  （interior.rs:1514，+168 行）：512B 节点深度 2 树连续插入触发
  leaf→parent→root 级联分裂至 root level≥2，递归 verify_subtree 断言
  键序/child pivot/区间连续/键完备（offset 1..=208 全量）。
- 回归套件修复（不改引擎行为）：fault_injection 注入-消费竞态（后台
  reclaim worker 抢消费 fault）改循环收敛；split_stress 规模压缩使全量
  <60s（约束 9，open_persistent 逐键 replay 为 recovery.c 对齐语义）。
- 测试 eprintln 全部迁移到日志 API（`subvol::rewrite_log_debug!`，
  SUBVOL_LOG 控制；lib.rs 公开重导出 + log.rs 宏路径为纯可见性调整）。

## 关键结论（review-report P1 修正）

1. **多级分裂语义已存在且对齐**：subvol `bch2_btree_split_leaf`
   （interior.rs:380）同步 loop 模型——leaf 分裂后 parent 放不下则
   继续分裂 parent（parent_keys + pivot 扫描 + formats，interior.rs:
   990-1030 区域），直至新建 root（interior.rs:780 区域）。与 bcachefs
   `btree_split`（interior.c:1962）+ `bch2_btree_insert_node` 递归
   parent_keys（interior.c:2191）+ `__btree_root_alloc`（interior.c:2095）
   控制流逐段对应。**多级分裂是 btree_split 递归语义，不是"靠重试
   爬升"**：-8（parent key 缺失 → interior.c:2271 split_race restart）
   /-10（锁升级失败）/ -12（BTREE_MAX_DEPTH，interior.c:534）均为
   restart/错误分支，仅用于竞争、锁、深度边界，非分裂主路径。
2. **异步 btree_update 框架不适用**：bcachefs `bch2_btree_update_start`
   （interior.c:1404）的 mempool/closure/gc.lock/interior_updates
   list/write_blocked/异步节点写盘管线，根因是 bcachefs 节点写盘
   异步后台化；subvol 为 journal 先行持久化（事务 commit 时 journal
   一次落盘即原子持久化，engine.rs:731 注释），无独立写盘管线——
   与 T0176 seq_blacklist 结论同类：机制因架构差异不适用（约束 12，
   不为不存在的场景添加逻辑路径）。review-report「未对齐」表述修正为
   「同步模型已对齐，异步框架因架构差异不适用」。
3. **merge 范围外**：`bch2_foreground_maybe_merge`（interior.c:2327
   附近）为分裂后相邻节点合并的性能优化，非 btree 操作正确性/持久性
   语义；T0168 未将其列为交付门槛，本任务不实现。

## 语义锚点

- fs/btree/interior.c:1962（btree_split）、2095（__btree_root_alloc）、
  2191（bch2_btree_insert_node parent 递归）、2271（split_race
  restart）、534（BTREE_MAX_DEPTH）、1404（bch2_btree_update_start）、
  2327（bch2_foreground_maybe_merge）
- 项目：interior.rs:380（split_leaf 同步 loop）、780（root 增深）、
  990-1030（parent 分裂/pivot）、863/1167（-8）、883/909（-10）、
  162（-12）；engine.rs:731（journal 先行持久化注释）
- 约束 10：本任务实现前对照 interior.c 全文（3853 行），关键函数
  逐段比对，无凭记忆改动

## 备注

- 提交：【F-T0177】engine: 新增多级分裂 pivot 不变量测试锁定 btree_split
  递归语义并修复 fault 注入竞态, 0.1.0 -> 0.1.0
- 纯测试 + 文档任务，无引擎行为修改；日志宏可见性调整为基础设施
- 单一格式版本，无兼容性影响
