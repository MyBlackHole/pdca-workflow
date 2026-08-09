# PRD — transition 自动补写 states.plan 时间戳 + 时间戳格式统一

## 背景

Plan→Do 转换要求 `states.plan` 已打时间戳。但任务初始创建（task.json）时
`states.plan = null`，此前需人工在对齐 final_confirmation 时刻后手工补写，
产生真实摩擦。T0238 conclusion 将其标注为下一步。

## 需求

### R1 transition 自动补写 plan 时间戳
`scripts/transition-phase.py` 的 plan→do 转换中：
- 若 `states.plan is None`，读取 `clarifications.jsonl` 的 `final_confirmation.at`
  作为 plan 完成时刻写入 `states.plan`
- 若无 final_confirmation 记录（gate 已保证存在，此分支仅健壮性兜底），
  用当前 `now` 补写

### R2 时间戳格式统一
transition 写入的 states 时间戳统一 `timespec="seconds"`（无微秒），
消除微秒/无微秒漂移。仅限 states，不强制 created_at。

### R3 测试
新增测试覆盖：
- 初始无 plan 时间戳的任务 plan→do 成功，plan = confirmation 时刻
- 缺失 confirmation 时兜底用 now
- 已存在 plan 时间戳时不覆盖

## 验收标准

- [ ] AC-1: 无 plan 时间戳 + 有 final_confirmation 的任务 plan→do，
      states.plan == final_confirmation.at
- [ ] AC-2: 无 final_confirmation 时兜底用 now，转换成功
- [ ] AC-3: states.plan 已存在时不覆盖原值
- [ ] AC-4: 现有测试（test_transition_is_adjacent_and_idempotent）仍通过
- [ ] AC-5: 全部测试套件通过（137 + 新增）

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 语义门禁（created_at ≤ confirmed_at ≤ now）不被破坏
