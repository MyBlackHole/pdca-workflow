# PRD — T0166 流程文件时间线一致性加固（终版）

## 1. 问题陈述

- **现状**: 今日审查发现 T0164 存在确凿的流程违规与回填痕迹：plan→do receipt（16:47:04）早于 final_confirmation（17:15:00）28 分钟；`states.do`（16:47:04）晚于 `states.plan`（17:15:00）与 `created`（17:00:00）；`task.json.bak`（转换快照）内含未来时间；`implement.jsonl` do 执行（17:10）早于确认（17:15）；`meta.convergence` 为 record ID 占位符而非收敛条件。
- **目标**: 从机制上杜绝"先转换/执行、后补确认、再回填流程文件"的路径；存量任务可一键体检发现同类问题。
- **差距**: `transition-phase.py` 只校验"final_confirmation 存在"，不校验"确认时间 ≤ 转换时刻"；`pdca-doctor.py` 不检测 states 时间单调性、receipt 与确认/状态的交叉一致性。现有 `FINAL_CONFIRMATION_TIME_ORDER` 只挡"确认早于任务创建"，`FUTURE_STATE_SET` 只挡未来时间——T0164 的违规模式恰好从两条校验的缝隙穿过。

## 2. 解决方案

三个修复（用户已确认方向，且每项通过 AI 价值 × AI 友好性审核）：

### R1 登记 T0164 违规为 Flow Issue Occurrence
- 用 `report-flow-issue.py`（T0159 已建的 ADR-0004 机制）登记两条 occurrence：
  - **O-1**（`conformance-deviation`）：plan→do 转换早于 final_confirmation，issue-code `PLAN_TO_DO_BEFORE_FINAL_CONFIRMATION`，evidence 引用 receipt/clarifications
  - **O-2**（`ai-usability`）：convergence 占位符（record ID 而非收敛条件），issue-code `CONVERGENCE_PLACEHOLDER`——按 R4 决策登记为已知缺陷，不修
- **AI 价值**: 违规成为不可变事实源，供聚合器重建 backlog、供未来 Improvement 决策引用，AI 不依赖会话记忆
- **AI 友好性**: 单 CLI 命令、schema 校验、幂等 key、确定输出；无新认知负担

### R2 transition-phase.py 门禁加固（fail-closed）
- plan→do 转换时新增校验：**所有 `final_confirmation.at` 不得晚于转换执行时刻**（超过容差即拒绝，issue code `FINAL_CONFIRMATION_AFTER_TRANSITION`）
- 转换前同时校验 `states` 时间单调性（`created ≤ plan ≤ do`）——转换时刻不得出现 states 时间在未来
- 错误输出沿用现有 JSON 格式（`{"status":"rejected","issues":[...]}`），每条含修复指引
- **AI 价值**: 直接堵住 T0164 的绕过路径——"先干活后补确认"在门禁处即失败，AI 被迫按正确顺序操作
- **AI 友好性**: 复用既有 fail-closed 模式与错误码约定；`transition-phase.py` 是唯一合法推进入口，AI 无歧义

### R3 pdca-doctor.py 存量体检（非阻断 warning）
- 新增检查项（对所有任务，含存量）：
  - **states 单调性**: `created ≤ plan ≤ do ≤ check ≤ act ≤ archive`（已设值之间）
  - **确认 ≤ 转换**: `final_confirmation.at` 不晚于 plan→do receipt 的 `at`（两者都存在时）
  - **receipt 一致性**: `plan-to-do.json.at == task.json.states.do`（转换 receipt 与状态时间戳交叉校验）
  - **快照兼容性**: `task.json.bak` 中 `states.<to>` 应为 null 且 phase 为转换前阶段（存在 bak 时）
- 输出并入 `pdca-doctor.py --json` 的检查结果区，`valid` 字段不受影响（非阻断）
- **AI 价值**: 存量任务（如 T0164/T0165）也能被发现；AI 自查成本低
- **AI 友好性**: 已有 `--json` 机器可读输出；只读不改；T0164 已回填的坏数据不会被误修

### 明确不做（YAGNI / 用户决策）
- 不修改 `task.schema.json` 收紧 convergence（R4：价值低、波及历史任务）
- 不回滚 T0164、不修正其已登记证据（工作真实完成，check 时向用户说明）
- 不新增"文件不可变哈希链"类重机制（T0159 已定 receipt digest 方案，够用）

## 3. Seam 分析

### 测试接缝
- `pdca_core.gate_issues`（纯函数）：`transition-phase.py` 复用其门禁；测试直接调用 `gate_issues` 断言新 issue code
- `transition-phase.py`（CLI seam）：临时仓库构造"确认时间晚于转换时刻"的任务 → 断言 `status=rejected` + `FINAL_CONFIRMATION_AFTER_TRANSITION`
- `pdca-doctor.py --json`（CLI seam）：构造 states 乱序/确认晚于 receipt 的任务 → 断言新检查项出现在结果中且 `valid=true`

### 验收可测性
- 每个新检查项都有确定性 fixtures（临时仓库，不依赖真实任务数据）
- 现有 `tests/test_state_contract.py`、`tests/test_operations.py` 回归不破坏
- doctor 检查项对正常任务零噪音（已有任务体检通过）

## 4. 用户故事

1. 作为执行 PDCA 的 AI，我希望转换门禁拒绝"确认晚于转换时刻"，以便我无法用回填掩盖流程顺序。
2. 作为流程维护者，我希望 doctor 能体检存量任务的时间线矛盾，以便发现并治理既有违规。
3. 作为用户，我希望 T0164 的违规以不可变 occurrence 留痕，以便 Check 阶段能基于事实确认 verdict。
4. 作为 AI，我希望错误输出含 issue code 与修复指引，以便不猜测如何纠正。

## 5. 实现决策

- 修改模块：`scripts/pdca_core.py`（门禁/体检逻辑）、`scripts/transition-phase.py`（调用门禁，无需改）、`scripts/pdca-doctor.py`（新检查项接入）
- `gate_issues` 增加 plan 阶段校验：确认时间 ≤ 当前时间（当前时间由调用方注入，测试可固定）
- 新增 doctor 检查函数（与 `gate_issues` 解耦，只读扫描 `pdca/tasks/active/**`）
- issue code 前缀遵循现有约定（`FINAL_CONFIRMATION_*`、`STATE_*`）

## 6. 测试决策

- 测试放 `tests/`（已有 `test_state_contract.py`、`test_operations.py` 先例，pytest + 临时仓库 fixture）
- 仅测外部行为：CLI 退出码/JSON 输出、`gate_issues` 返回的 issue code 集合
- 回归：`python3 -m pytest tests/ -x` 全量通过

## 验收标准

- [ ] AC-1: 两条 occurrence 登记成功（O-1 conformance-deviation / O-2 ai-usability），`aggregate-flow-issues.py` 可重建
- [ ] AC-2: 构造"确认 at=17:15、转换时刻=16:47"的任务 → `transition-phase.py` 返回 `status=rejected` 且含 `FINAL_CONFIRMATION_AFTER_TRANSITION`
- [ ] AC-3: 构造 states 乱序任务 → doctor `--json` 输出含新检查项且 `valid=true`（非阻断）
- [ ] AC-4: 构造确认晚于 receipt 的存量任务 → doctor 检出
- [ ] AC-5: 现有全量测试通过（无回归）
- [ ] AC-6: 正常任务（T0165、T0166 自身）doctor 体检零噪音

## 8. 范围外

- T0165 证据登记（属 T0165 自身 do 收尾，本任务只提醒）
- schema 收紧 convergence、T0164 回滚、文件哈希链机制
