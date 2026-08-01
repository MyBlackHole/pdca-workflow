# T0173 journal reclaim 压力属性测试 — 结论

## 任务

在 btree_proptest.rs 新增第 5 个属性测试 `reclaim_after_checkpoint_preserves_model`：
随机操作流中周期性显式 `reclaim_journal()`（直接路径 checkpoint）叠加崩溃恢复，
验证 reclaim 裁剪（`last_seq` 推进）后设备路径恢复不丢键（T0169 回归保障）。

## 收敛结论

**结论：通过**（convergence valid=true，5/5 AC 全达标）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 last_seq_ondisk 单调 | 通过（测试内 `after >= before` 断言） | e1（diff:49 行，含断言） |
| AC-2 crash 恢复模型一致 | 通过（每 crash 点 assert_model） | e1 |
| AC-3 最终恢复模型一致 | 通过（收尾 assert_model） | e1 |
| AC-4 全量回归绿 + fmt | 通过（lib 173/173、集成 9/9、fmt 干净） | e2 |
| AC-5 8 轮稳定 | 通过（8 轮各 64 cases 全绿） | e2 |

## 验证记录

- 新增测试单独运行：1.11s/64 cases 通过
- 8 轮稳定性：每轮 1.05-1.27s 全绿
- 全量回归：lib 173/173；集成 btree_proptest 9/9（原 8 + 新 1）
- `cargo fmt --check -p subvol` 干净
- 与既有 4 个属性测试无命名/参数冲突

## 语义锚点

- bcachefs：recovery.c:763 `journal_replay_seq_start = last_seq`（重放起点）；
  reclaim.c:1047/1184（direct/background 双路径）
- 引擎：engine.rs:596 `reclaim_journal()` = `checkpoint_locked`（flush pins →
  推进 last_seq）；engine.rs:66（恢复重放 last_seq 之后窗口）；engine.rs:204
  `journal_last_sequence_ondisk` 公开字段
- 约束 12/13：测试仅使用既有公开 API（create/open_persistent/reclaim_journal/
  metrics/sync），无自有逻辑、无新结构体

## 备注

- 本任务纯测试，无引擎实现修改、无格式变更（单一版本，无兼容性影响）
- 后台 worker 路径（request_reclaim/wait_for_reclaim）与 reclaim_background_once
  由既有单测覆盖，不在本任务范围（PRD 范围外已声明）
