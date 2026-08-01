---
schema: pdca.asset/v1
id: T0168-0801-btree-core-completeness
phase: check
source_ids: [review-report, checkpoint-cow-heap-rootcause, convergence-map, convergence-validation]
---

## 上下文

T0168 对 `/home/black/Documents/subvol`（bcachefs 风格 Rust 存储引擎核心）做 btree 核心功能完整性审计：以本地 `/home/black/Documents/bcachefs-tools` 源码为唯一对照基准，双基准交叉（bcachefs 语义为主 + 项目交付目标为辅），对全仓功能模块（btree 12 模块 + journal + engine + data/keylist + snapshot + sb + lock）产出一致性矩阵、资源生命周期矩阵、数据一致性矩阵、双基准不重合项清单、缺陷清单与后续任务拆解。缺陷仅报告不修复。

## 假设与结果

假设：subvol btree 核心（bkey/bset/迭代器/缓存/事务/checkpoint/恢复）与 bcachefs 逐函数语义对齐，主要缺口集中在明确不在交付范围的部分（bucket 分配器、快照写操作、sb 多版本），核心链路无严重偏离。

结果：**总体成立，但发现 1 个 CRITICAL 缺陷**。24 个功能项 15 完整 / 7 部分 / 2 缺失；缺失项均符合 AGENTS.md 范围声明。D1：`bch2_trans_commit` 空间检查未累加同 leaf 多 update 占用（bcachefs commit.c:1083-1097 有 `u64s += i->k->k.u64s`），且缺少 bcachefs commit.c:189-195 的剩余空间 EBUG_ON 防御 → 堆越界写（ASAN 复现：`checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 崩溃于 `bch2_bset_insert` copy_nonoverlapping），影响 btree 写路径与 checkpoint 持久化。修复前不满足"btree 操作正确性 + 崩溃一致性"交付门槛。

## 分析

- **AC-1 功能矩阵**：btree 12 模块 10 完整 / 2 部分（interior.rs 缺异步 btree_update/split/merge；update.rs 含 D1 + trigger 链简化），journal/engine 及辅助模块 5 完整 / 4 部分 / 2 缺失。测试覆盖 136 内嵌 + 17 engine 集成（含进程级崩溃恢复）。
- **AC-2 资源生命周期**：journal reclaim、btree cache、事务 allocator 三链路完整对齐（reclaim.c / cache.c / iter.c 对应）；checkpoint COW 页为架构代理（部分）；bucket 层缺失但属范围声明。
- **AC-3 数据一致性**：写入/恢复路径完整（含 27 个崩溃相关测试）；seq_blacklist 缺失（强连续性校验替代，seq 达上限硬失败）；trans/gc trigger 链缺失；在线 verify 仅排序 + 单节点拓扑。
- **AC-4 双基准不重合项**：属性测试（proptest/fuzz）为零、write_buffer 未成形、interior 异步框架未对齐、seq 环回机制缺失。
- **AC-5 根因级**：D1 已到函数级根因（update.rs:1953-1975 独立判空检查 → 越界写），ASAN + 调用链 + bcachefs 对照三重确认。
- **AC-6 缺陷清单**：D1 CRITICAL / D2 seq 上限 / D3 trigger 链 / D4 verify 覆盖 / D5 校验部分 / D6 测试薄弱。
- **AC-7 任务拆解**：P0 修 D1；P1 seq 环回、interior split；P2 属性测试、trigger 链、递归 fsck；P3 测试补充、逐 key 校验。
- **AC-8 抽查**：12 个 bcachefs 对照路径全部真实存在，5 个关键符号验证通过。

## 遗留风险

- D1 修复须对齐 commit.c 累加语义并补 EBUG_ON 与回归测试，修复后全量重跑 `cargo test --lib` 确认全绿（当前 1 个崩溃测试 + 其他全部通过）。
- 属性测试为零与 AGENTS.md 交付重点的差距待后续任务补足。
