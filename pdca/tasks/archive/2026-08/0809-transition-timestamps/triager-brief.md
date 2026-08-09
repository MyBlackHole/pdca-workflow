# T0239 Triage Brief — transition 自动补写 states.plan 时间戳

## 来源
T0238 conclusion 直接标注的下一步：plan→do 转换要求 states.plan 已打时间戳，
但初始创建（task.json）时无 plan 时间戳，需人工对齐 final_confirmation 时刻。

## Claim 验证（P0）
- transition-phase.py L77-79：`now = isoformat(timespec="seconds")`，
  写 `states[args.to]`；**无 plan 补写逻辑** ✅
- gate_issues（L71）在转换前校验，STATE_TIMESTAMP_MISSING 会拒绝
  plan→do（当 states.plan 为 null）✅
- confirmation_time_issues（pdca_core.py L110-138）：要求
  `created_at ≤ final_confirmation.at ≤ transition_moment` ✅
- transition-phase 无 final_confirmation 读取逻辑（需新增）✅
- 现有测试 test_operations.py::test_transition_is_adjacent_and_idempotent
  的 fixture 手工设置了 plan 时间戳 ✅

## 方案
在 transition-phase.py 的 plan→do 转换中：
1. 读取 clarifications.jsonl 的 final_confirmation.at
2. 若 states.plan 为 null，用 final_confirmation.at 补写（该时刻 = Plan 真实完成时刻，
   满足 created_at ≤ confirmed_at ≤ now）
3. 统一时间戳格式：确认 created_at/plan/do 等全部用 timespec="seconds"
   （消除微秒/无微秒漂移）
4. 新增测试：初始无 plan 时间戳的任务 plan→do 成功，plan = confirmation 时刻

## 后续
P2 Grill → P3 PRD → P3.5 seam → P4 → P5 → P6 → Do
