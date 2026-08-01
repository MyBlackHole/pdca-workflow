# T0173 journal reclaim 压力属性测试

## 问题

T0169 修复的原始 bug 是 reclaim 裁剪（`last_seq` 推进、closed 记录修剪）后
journal-only 恢复丢键。T0168 矩阵 A1 显示 reclaim 实现路径（reclaim_journal/
request_reclaim/后台 worker）与 bcachefs reclaim.c 对齐「完整」，但现有 4 个
属性测试（random/crash/fault-injection/multi-snapshot/journal 损坏）中
**没有任何一个主动触发 reclaim**：journal 区 8MB、属性测试 ops 量（~120 组）
远不足以到达 high watermark 触发后台回收。reclaim 裁剪后恢复路径在属性层面
是冷路径，T0169 修复无持续回归保障。

## 目标

新增属性测试：随机操作序列 + 周期性显式 `reclaim_journal()` + 崩溃恢复，
验证 reclaim 裁剪（`last_seq` 推进、旧记录回收）后设备路径恢复不丢键、
与模型完全一致，持续回归 T0169 修复场景。

## 用户故事

作为存储引擎开发者，我希望在随机操作流中周期性触发 journal reclaim 并崩溃
恢复，以便验证：reclaim 裁剪后的数据在任何崩溃窗口下都不丢失、不重复、
与内存模型一致（bcachefs 语义：设备 btree + last_seq 之后 journal 窗口重放，
对齐 read_btree_roots + bch2_journal_read）。

## 方案

复用 `crash_recovery_restores_sync_point_state`（btree_proptest.rs:254）模式，
新增第 5 个 proptest：

- 参数：`ops`（op_group_strategy，1..=MAX_OPS）+ `reclaim_every in 3usize..=6`
  （每 N 组触发一次 reclaim）+ `crash_every in 9usize..=17`（复用既有窗口）
- 每步：apply_group + apply_model（同现有框架）
- reclaim 步骤（`step % reclaim_every == reclaim_every - 1`）：
  1. reclaim 前取 `metrics()` 快照（`journal_last_sequence_ondisk` 基线）
  2. `engine.reclaim_journal()`
  3. 断言 `metrics().journal_last_sequence_ondisk >= 基线`（裁剪生效/单调）
- crash 步骤（`step % crash_every == crash_every - 1`）：
  `sync` → drop → `open_persistent` → `assert_model`（同现有框架）
- 收尾：最终 sync + drop + open_persistent + assert_model

**reclaim 路径选择（用户已确认）**：直接路径 `reclaim_journal()`（checkpoint_locked，
同步完成，确定性最强）；后台 worker 路径已有既有单测覆盖
（reclaim_background_once），属性测试聚焦裁剪后恢复正确性。

## 实现决策

| 决策 | 选择 | 依据 |
|------|------|------|
| reclaim 触发 | 直接路径 reclaim_journal() | 同步、确定性；用户已确认 |
| 裁剪断言 | metrics().journal_last_sequence_ondisk 单调 | engine.rs:204-205 公开字段；durability_point() 不含 last_seq |
| 断言强度 | >=（容忍无新数据时不变）+ 恢复模型一致（隐含裁剪正确性） | reclaim 无覆盖数据时不推进 |
| 触发频率 | reclaim_every 3..=6，crash_every 9..=17 | reclaim 比 crash 更频繁，保证多数 crash 前已发生过 reclaim |
| 约束 12/13 | 无自有逻辑；全部复用既有公开 API 与 bcachefs 语义锚点 | reclaim.c:1047/1184 |

## 验收标准

- [ ] AC-1: reclaim 步骤断言 `journal_last_sequence_ondisk` 单调不倒退
- [ ] AC-2: 每次 crash 恢复后 `assert_model` 通过（不丢键、不重复）
- [ ] AC-3: 最终恢复后 `assert_model` 通过
- [ ] AC-4: 与既有 4 个属性测试共存，全量回归绿（lib 173 + 集成全部）+ fmt 干净
- [ ] AC-5: 连续 8 轮 proptest 稳定通过

## 范围外

- 后台 worker 路径属性级覆盖（既有单测已覆盖）
- wait_for_reclaim/request_reclaim 语义（既有单测已覆盖）
- seq 环回/黑名单（D2）、interior split（T0168 P1 排期项）
- 任何引擎实现修改（纯测试任务）

## 备注

- 提交：feature-commit-format（【F-T0173】engine: 新增 journal reclaim 压力属性测试…，0.1.0 -> 0.1.0）
- 单一格式版本，无兼容性影响
