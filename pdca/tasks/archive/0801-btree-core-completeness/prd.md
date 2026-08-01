# T0168 — 分析 subvol btree 核心功能完整性（对照 bcachefs 语义矩阵）

## 问题陈述

- **现状**: subvol 是独立 Rust 存储引擎核心（bcachefs 风格 btree/transaction/journal），`crates/subvol/src/` 已有 btree 12 模块（约 23K 行）与 journal/engine/data/snapshot/sb/lock 等全仓模块及 136 个内嵌测试，但从未做过系统性的"完整性审计"——哪些 bcachefs 核心语义已实现、哪些部分实现、哪些缺失，没有一份可验证的矩阵。
- **目标**: 产出对照 bcachefs 的全仓功能完整性矩阵（双基准：bcachefs 语义为主、项目交付目标为辅），覆盖 btree/journal/engine/data/snapshot/sb/lock 功能模块 + 资源生命周期（空间分配与回收）+ 数据一致性（崩溃处理、事务触发操作、在线 fsck）三个维度，明确完整/部分/缺失状态，附证据与源码行号；对发现的缺陷（已确认存在 checkpoint COW 堆崩溃）给到根因级报告。
- **差距**: 无完整性矩阵、无缺陷根因清单、无后续补全任务的拆解建议；测试套件当前不能全绿（堆崩溃），"完整性"无从判定。

## 解决方案

以本地 `/home/black/Documents/bcachefs-tools`（`fs/btree/`、`fs/journal/`、`fs/alloc/`、`fs/snapshots/` 等 C 源码）为唯一语义对照基准，提炼核心功能矩阵；逐模块对照 subvol 实现，判定 完整/部分/缺失；关键路径（update/commit/checkpoint/恢复/reclaim/trigger）追到函数级并给证据行号。缺陷用 ASAN/valgrind 或代码分析定位根因。产出：矩阵报告（功能矩阵 + 资源生命周期矩阵 + 数据一致性矩阵）+ 缺陷清单 + 后续任务拆解建议。

## Seam 分析

### 测试接缝
- subvol 无集成测试目录，测试内嵌各模块 `#[cfg(test)]`；`cargo test --lib` 为唯一测试入口
- 已确认：`engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 单独运行即 SIGABRT（堆损坏），是审计必须复现/定位的缺陷样本
- 对照基准的验证方式：读 bcachefs C 源码（`fs/btree/{bkey,bset,update,commit,interior,iter,read,write,cache}.c`、`fs/journal/{read,write,reclaim,validate}.c`、`fs/alloc/{buckets,accounting}.c`、`fs/snapshots/*.c`），对照函数不运行（bcachefs-tools 仅作语义依据，非运行时依赖）

### 验收可测性
- 矩阵每项有明确证据（subvol 行号 + bcachefs 对应物路径），pass/fail 独立可判
- 缺陷复现命令可重复执行，根因定位到函数级

## 用户故事

1. 作为存储引擎维护者，我想要一份全仓功能完整性矩阵（功能/资源生命周期/数据一致性三维度），以便知道哪些 bcachefs 语义已覆盖、哪些缺失，决定下一步补什么。
2. 作为维护者，我想要缺陷清单（含复现与根因），以便直接开修复任务。
3. 作为维护者，我想要后续任务拆解建议，以便按优先级排期。

## 实现决策

- 基准：双基准交叉。主基准 = 本地 bcachefs-tools `fs/` 下 btree/journal/alloc/snapshots/data/sb C 源码语义矩阵（约束 1/2/3/4/7）；辅基准 = 项目 AGENTS.md 交付目标（btree 正确性、事务一致性、journal 持久化恢复、崩溃/故障注入、属性测试）。不重合部分单独列出。
- 范围（全仓功能模块）：btree 12 模块（bkey/bset/bset_build/bset_search/bset_update/cache/interior/io/iter/node_iter/types/update）+ journal.rs + engine.rs + data/keylist + snapshot.rs + sb/ + lock/ 全部进功能矩阵；util（rcu/rhashtable/bit_spinlock/eytzinger/jhash/workqueue/log）与 checksum 作为支撑模块仅列 API 面 + 测试覆盖，不进功能矩阵。
- 资源生命周期维度（空间分配与回收）：现有资源路径全查——journal 空间回收（reclaim/reclaim_journal/schedule_reclaim，对照 `fs/journal/reclaim.c`）、btree node 内存分配与释放（cache.rs，对照 `fs/btree/cache.c`）、事务内存分配器（update.rs trans kmalloc/allocator，对照 `fs/btree/update.c`）、checkpoint 页管理（engine.rs COW 页，对照 journal 写入路径）。缺失的 bucket/block 层分配器（`fs/alloc/buckets.c`）在矩阵中标注为"缺失/不在当前交付范围"并附说明。
- 数据一致性维度：三者全查——崩溃处理（journal replay/validate/seq_blacklist，对照 `fs/journal/{read,write,validate}.c`）、事务触发操作（btree_trigger_op/trigger 链，对照 `fs/btree/update.c` trigger 机制）、在线 fsck（subvol `verify()` 对照 `fs/alloc/check.c` 与 `fs/btree/check.c` 语义覆盖）。
- 粒度：关键路径（btree update/commit、checkpoint COW、journal replay/恢复、reclaim、trigger）到函数级；其余模块 API 面 + 测试覆盖统计。
- 豁免：AGENTS.md 第 14 条（btree id 方案、fs 层专用 type 与 trigger 关系）不进入矩阵；bucket 分配器评估仅标注缺失状态，不设计实现。
- 缺陷处置：仅报告不修复；堆崩溃报告到根因级（ASAN/valgrind/代码分析），缺陷清单含复现命令。
- 无代码修改任务内完成；产出文档放任务目录 evidence/。
- 验证手段：`cargo test --lib`（现状）、ASAN build（`RUSTFLAGS=-Zsanitizer=address` 或 valgrind）复现堆崩溃、gdb backtrace。

## 测试决策

- 本任务为 review 类型，不新增功能代码；测试活动限于：复现崩溃（ASAN/valgrind）、收集模块测试覆盖统计（`cargo test --lib` 结果按模块聚合）。
- 测试先例：`cargo test --lib` 全量 + 单测过滤（`--test-threads=1`）已可稳定复现崩溃。

## 验收标准

- [ ] AC-1: 完整性矩阵覆盖全仓功能模块（btree 12 + journal + engine + data/keylist + snapshot + sb + lock），每项标注 完整/部分/缺失 且附 subvol 源码行号与 bcachefs 对应物路径
- [ ] AC-2: 资源生命周期矩阵覆盖 journal reclaim/btree cache/事务 allocator/checkpoint 页管理四项，每项含 bcachefs 对照物与缺失状态说明（含 bucket 层评估）
- [ ] AC-3: 数据一致性矩阵覆盖崩溃处理（replay/validate/seq_blacklist）、事务触发操作（trigger 链）、在线 fsck（verify 语义）三项，每项含对照分析
- [ ] AC-4: 矩阵包含双基准不重合项清单（项目交付目标中 bcachefs 语义未覆盖的项，如属性测试缺失——当前无 proptest/fuzz 依赖）
- [ ] AC-5: checkpoint COW 堆崩溃经 ASAN 或 valgrind 复现并定位到函数级根因，复现命令与根因写入缺陷清单
- [ ] AC-6: 缺陷清单完整罗列审计发现的所有缺陷/缺口（含测试套件状态），每项含证据、影响面、严重度
- [ ] AC-7: 产出后续任务拆解建议（如 checkpoint 修复、缺失功能补全、属性测试引入），每项含理由与优先级
- [ ] AC-8: 全文对照 bcachefs 源码完成核对，矩阵中标注的 bcachefs 对应物路径真实存在（抽查 ≥5 处）

## 范围外

- 不修复任何缺陷（堆崩溃等仅报告）
- 不实现任何缺失功能
- 不写属性测试代码
- 不涉及 bcachefs fs 层兼容（inode/dirent/xattr 等）
- 不评估性能
- 不为 bucket 分配器设计实现方案（仅标注缺失状态）

## 备注

- Triage 已确认事实：`cargo build` 通过（425 warnings）；`cargo test --lib` 堆崩溃复现于 `engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root`（SIGABRT，`free(): invalid next size`）；subvol 无属性测试依赖
- bcachefs-tools 对照目录：`/home/black/Documents/bcachefs-tools/fs/btree/`（bkey/bset/cache/commit/interior/iter/read/sort/update/write/write_buffer/journal_overlay）、`fs/journal/`（read/write/reclaim/validate/seq_blacklist）、`fs/alloc/`（buckets/accounting）、`fs/snapshots/`
- 用户终审修订（2026-08-01）：范围扩大至全仓功能模块；新增资源生命周期（空间分配与回收）与数据一致性（崩溃处理/事务触发操作/在线 fsck）两维度
- 约束提醒：任何结论性断言须对照 bcachefs 源码核实；矩阵引用行号以审计当日代码为准
