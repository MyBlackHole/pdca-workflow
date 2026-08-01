# T0180 跟进：审计 extent/alloc/btree/backpointer trigger 依赖链

## 问题陈述

- **现状**：subvol 有 extents iterator、range update 与内部 btree pointer 格式，
  但 transaction commit 只运行 snapshot atomic trigger；没有 bcachefs 式
  transactional trigger runner，也没有 extent、alloc 或 backpointer 的派生维护。
- **目标**：以本地 bcachefs 为唯一依据，确定 extent、alloc、btree pointer、
  backpointer/stripe-backpointer、accounting/reconcile、journal/recovery 和 GC
  之间的依赖与当前实现缺口，输出可拆分、可实现的最小后续任务。
- **差距**：没有这份依赖图即移植 runner，会遗漏其创建的 update、回合排序、
  backpointer 一致性和 GC 前提；只看公开 cookie API 又会漏掉 btree core 路径。

## 解决方案

从 bcachefs `commit.c` 的三阶段 runner 出发，分别追踪 extent 和 btree pointer
的 `bch2_trigger_extent()`、alloc 的 `bch2_trigger_alloc()`、以及
`bch2_bucket_backpointer_mod()` 产生的写入。对每条边标注执行阶段、是否可追加
transaction update、持久化/恢复顺序、GC 前提及 subvol 当前状态。根据证据创建
独立的最小 follow-up task；本任务不改动引擎行为。

## Seam 分析

### 测试接缝

- 以 raw transaction commit、extents iterator/update、内部 btree split/grow 和
  journal replay 为观察边界。
- 若已有最小测试可以证明可达性则复用；若没有，只添加确定性 probe，不实现
  trigger 逻辑。

### 验收可测性

- 每一张依赖边都具有本地 bcachefs 和 subvol 两侧的源码锚点。
- “确认缺失”必须同时满足：上游存在语义、subvol 对应生产路径可达、当前没有等价
  更新/恢复处理。
- 任何建议实现项都须有独立、最小范围与可验证验收标准。

## 用户故事

作为存储引擎维护者，我希望在支持范围 key 或空间分配前完整理解它们对 btree
pointer、alloc、backpointer、accounting 与恢复的连锁影响，以便事务不会留下不可恢复
或不可校验的派生状态。

## 实现决策

- 本任务为审计，不添加 extent/alloc/backpointer 的产品实现。
- 不把 bcachefs fs 层 btree-id 编号直接施加到 subvol；只保留由本地源码证明的
  语义依赖，遵守项目 AGENTS.md 的独立 btree-id 边界。
- GC 单独记录 `gc_visited()` 和 GC state 前提；缺少完整 GC 模型时不得把 GC
  trigger 单独移植。

## 测试决策

- 运行现有 btree split/grow、extent iterator/update、journal root/replay 与全量
  workspace 测试。
- 新 probe 只验证路径可达性和当前缺失，不修改产品语义；每项测试在一分钟内完成。

## 验收标准

- [ ] AC-1: 逐段对照本地 bcachefs `commit.c` transactional/GC runner 与 `types.h` trigger mask，记录多轮 sort-order、insert/overwrite 状态和 `gc_visited()` 前提。
- [ ] AC-2: 完整绘制 `extent / btree pointer -> alloc -> backpointer / stripe-backpointer -> accounting / reconcile -> journal / recovery / GC` 依赖图；每条边均有本地 bcachefs 源码锚点。
- [ ] AC-3: 对 subvol 的 extents iterator/range update、内部 btree pointer、journal root/replay、alloc/backpointer key 类型和 `bch_fs` 状态逐项标注可达性与当前实现状态。
- [ ] AC-4: 每个“确认缺失”项均证明上游语义、subvol 可达生产路径和当前缺少等价维护三项；没有三项证据的项目列为不适用或待扩展。
- [ ] AC-5: 为每个确认缺失的最小独立实现范围创建 follow-up PDCA task；任务不得混合 extent、alloc、backpointer、GC 等无法独立验证的范围。
- [ ] AC-6: 定向测试与 `cargo test --workspace --no-fail-fast` 通过；所有单测在一分钟内完成。

## 范围外

- 直接实现 transactional/GC runner、extent I/O、设备分配器、完整 GC 或完整 fsck。
- 完整 VFS、inode、目录、xattr、多格式迁移和运行时 bcachefs 依赖。

## 备注

- 本任务源自 T0179 partial verdict 的范围修正。
