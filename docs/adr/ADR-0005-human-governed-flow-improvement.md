# ADR-0005: Flow Improvement 采用人类治理的评测驱动闭环

日期: 2026-07-30
状态: Accepted

## 背景

T0159 的目标是依据 PDCA 使用过程中记录的问题持续优化流程。LLM 可以聚合轨迹、提出根因假设和生成候选，但无可靠外部反馈时不能稳定地自我判断改动是否正确。流程优化还可能修改 `flows/`、`skills/`、schema 和 gate，具有跨任务影响。

需要在自动化收益、误优化风险和现有用户确认门禁之间确定权责边界。

## 候选方案

### A. AI 自动诊断、修改并部署流程

- 优点：反馈周期最短，人工成本低。
- 缺点：模型可能循环自证、优化错误指标、弱化门禁或放大误判；缺少明确授权和回滚责任。

### B. AI 只记录问题，所有分析与改进均人工完成

- 优点：控制最强，实现简单。
- 缺点：无法利用结构化历史自动聚合和生成候选，自我优化收益有限。

### C. AI 自动观测、聚合和提案；用户授权；外部 evidence 验证

- 优点：自动化高成本的信息处理，同时保留流程变更授权、独立评测和回滚边界。
- 缺点：需要 decision receipt、候选评测、观察窗口和效果 verdict 等控制产物。

## 决策

选择 C：

1. AI 可生成 Flow Issue 投影、triage 建议、根因假设和 dry-run Improvement Candidate。
2. false-positive、accepted-risk、关闭问题、impact 晋级和创建 Improvement Task 必须取得用户确认并生成 Flow Issue Decision。
3. Candidate 不直接修改权威流程；确认后才创建正常 PDCA Improvement Task。
4. Improvement Task 完成只标记 `deployed`，不能立即关闭对应 Flow Issue。
5. 每个 candidate 在实施前冻结 baseline、目标指标、检测规则版本、最小观察机会和最长观察期限。
6. 观察后生成 Effectiveness Verdict：`improved | neutral | regressed`；只有 improved 转为 verified。
7. regressed 生成回滚候选，但回滚仍需用户确认。
8. MVP 使用 shadow backlog，不采用未经历史数据校准的固定次数自动触发规则。

## 影响

- 需要严格 schema：event、decision、candidate、effectiveness verdict。
- 需要确定性聚合器、紧凑查询接口、dry-run candidate 生成器和跨周期验证器。
- 需要配对夹具证明新方案能捕获旧方案遗漏的问题，同时不增加错误晋级。
- 自动化边界清晰，但完成一个优化循环需要至少两个观察窗口。
- T0159 已于 2026-07-30 完成 P6 终审，本 ADR 自该确认起生效。
