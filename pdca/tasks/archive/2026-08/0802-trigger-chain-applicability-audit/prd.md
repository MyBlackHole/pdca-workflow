# T0179 审计 transaction/gc trigger 链对 subvol 独立键模型的适用性

## 问题陈述

- **现状**：subvol 已运行 snapshot atomic trigger，但尚无 bcachefs
  `run_one_trans_trigger()` 的等价 runner，且 `insert_trigger_run` / 
  `overwrite_trigger_run` 未被 transactional runner 消费。普通 API 又只产生
  cookie/deleted 键。
- **目标**：用本地 bcachefs 源码证明当前每个可达键/树路径是否需要
  transactional 或 GC trigger，形成可复核结论，避免遗漏适用的一致性语义或错误
  移植 fs 层逻辑。
- **差距**：现有“runner 缺失”的静态观察没有把 bcachefs 的键类型/node-type/GC
  前提映射到 subvol 实际可达路径，无法判定它是缺陷还是不适用。

## 解决方案

以本地 `fs/btree/commit.c:507-656` 为唯一语义来源，追踪 subvol 对
`KEY_TYPE_cookie`、`KEY_TYPE_deleted`、`KEY_TYPE_snapshot` 及内部 snapshot 相关
update 的生成、排序、提交和 GC 可达性。对每个路径给出“已覆盖 / 不适用 / 确认缺失”
判定及源码锚点。确认缺失时只产出独立 bugfix 任务草案，不修改引擎行为。

## Seam 分析

### 测试接缝

- 以 transaction commit 入口和 snapshot trigger 为观察边界，使用现有 unit test
  或最小确定性 probe 证明键类型和阶段可达性。
- 审计结论必须能由源码定位和测试输出独立复查；不依赖外部 bcachefs 文档或运行时。

### 验收可测性

- 每种当前可达键类型均有明确判定与依据。
- 如声称“缺失”，必须同时证明 bcachefs 前提成立、subvol 可达且缺少相应阶段；否则
  只能标为不适用或待后续扩展。
- 所有新增或运行的 Rust 测试在一分钟内完成。

## 用户故事

作为存储引擎维护者，我希望在引入 transaction/GC trigger 代码前知道它对当前
独立键模型是否真正适用，以便保持事务一致性而不引入不兼容的 fs 层行为。

## 实现决策

- 本任务是 review，不改动 subvol 引擎实现、格式或公开 API。
- 唯一上游依据为本地 bcachefs `fs/btree/commit.c` 及其直接调用的本地代码。
- 结论按“键类型 × trigger 阶段 × 可达路径”记录；GC 还须记录 visited 前提。
- 若存在确认缺口，后续任务必须重新在修改前读取对应 bcachefs 源码，并保持最小范围。

## 测试决策

- 运行已有与 commit/snapshot 相关的定向测试以及完整 workspace 测试基线。
- 仅当当前测试无法观察某个可达路径时，补充最小、确定性的测试；测试断言外部可观察
  行为，不断言实现细节。

## 验收标准

- [ ] AC-1: 已逐段对照本地 bcachefs `fs/btree/commit.c:507-656`，准确记录 atomic、transactional、GC 三阶段的调用条件、排序/重试要求与 GC visited 前提。
- [ ] AC-2: 对 subvol 当前可达的 `KEY_TYPE_cookie`、`KEY_TYPE_deleted`、`KEY_TYPE_snapshot` 以及内部 snapshot update，分别给出生成点、提交点和每一 trigger 阶段的“已覆盖 / 不适用 / 确认缺失”结论及源码锚点。
- [ ] AC-3: 任何“确认缺失”结论同时具备 bcachefs 前提成立、subvol 路径可达、当前阶段未执行三项证据；不能满足时不得列为缺陷。
- [ ] AC-4: GC 结论明确包含 bcachefs `gc_visited()` 前提，并说明当前 subvol 是否存在等价可达状态；不得把 GC runner 缺失单独视为缺陷。
- [ ] AC-5: 产出 review report 和后续处置：无适用缺口则记录不实施依据；有适用缺口则创建一个独立、最小范围的 bugfix PDCA 任务，但不在 T0179 中修改引擎代码。
- [ ] AC-6: 定向测试与 `cargo test --workspace --no-fail-fast` 通过；每个单测在一分钟内完成。

## 范围外

- 直接实现 transaction 或 GC trigger runner。
- bcachefs fs 层 inodes/dirents/extents 的 trigger、完整 GC、VFS 或多格式兼容。
- 已完成的 journal btree key 布局校验（T0178）及无关 btree 完整性问题。

## 备注

- 此审计是 T0168 D3 与 T0178 handoff 的有界后续。
- subvol btree id/type 集合独立的边界遵循项目 AGENTS.md 第 14 条。
