# T0159 Verification

验证时间：2026-07-30 20:27 +08:00  
实现提交：`b5091e7afe26a19e5de6a00e03d77e4231f1aed7`  
cutover：`pdca/improvements/flow-issue-cutover.json`，开始时间为 `2026-07-30T20:27:22+08:00`。

## 执行结果

- `python3 -m unittest discover`：52 passed。
- `python3 scripts/run-flow-issue-fixtures.py --all`：8/8 passed。
- `python3 scripts/generate-skills-index.py --check`：通过。
- `python3 -m py_compile scripts/*.py`、全部 schema JSON 解析、`git diff --check`：通过。

AI 友好度 fixture 明确报告，不外推为真实模型成功率：

- 前后配对：cutover 前阶段中途上报返回 `CUTOVER_MISSING`，cutover 后返回 `created`。
- 稳定错误：路径攻击返回 `PATH_INVALID`。
- 紧凑 list 上下文：603 bytes；按 issue 展开来源事件：1218 bytes。

## 验收映射

| AC | 支持证据 |
|---|---|
| AC-1 | 四类 JSON Schema 与 `test_report_flow_issue_creates_a_schema_valid_immutable_occurrence` |
| AC-2 | `report-flow-issue.py`、六 source/七 category schema、public CLI fixture |
| AC-3 | `test_report_is_idempotent_and_rejects_content_reuse_of_the_same_key`、`test_concurrent_reports_create_one_occurrence_and_one_unchanged_retry` |
| AC-4 | occurrence schema 不含 impact/status，`test_report_flow_issue_creates_a_schema_valid_immutable_occurrence` |
| AC-5 | `test_aggregate_and_query_keep_fingerprint_boundaries_and_output_stable` |
| AC-6 | 稳定重建断言与 `test_aggregate_fails_closed_for_a_corrupt_event_file` |
| AC-7 | compact page/query show 断言与 Flow Issue fixture |
| AC-8 | candidate 默认 dry-run 且不创建 task 的治理测试 |
| AC-9 | 绑定 `user_decision` receipt 的拒绝/通过测试 |
| AC-10 | candidate 的 issue/event/baseline/metric/risk/observation 字段与无 task 副作用断言 |
| AC-11 | `test_candidate_needs_confirmed_decision_before_it_can_create_a_plan_task` 与并发 promotion 测试 |
| AC-12 | `test_effectiveness_verdict_generates_only_the_allowed_follow_up_artifact` |
| AC-13 | `test_cutover_routes_transition_audit_failures_to_new_immutable_events` |
| AC-14 | Flow Issue fixture 的 cutover 前后配对、路径攻击和错误晋级拒绝 |
| AC-15 | Flow Issue fixture 的 `end-to-end-feedback-loop` |
| AC-16 | Flow Issue fixture 的 machine pass/fail、稳定错误与 context bytes 报告 |

## 审查

`code-review.md` 的标准轴与规范轴均为 Blocking 0。`architecture-report.md` 未发现 flows/skills/knowledge/pdca 结构缺失。
