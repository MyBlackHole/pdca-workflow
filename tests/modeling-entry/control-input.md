---
schema: pdca.modeling-entry-control/v1
fixture_only: true
original_request:
  goal: 审查现有规则与测试资料
  requirements:
  - id: R_RULES
    required: true
  - id: R_TESTS
    required: true
parent_seed:
  policy: assess_recursively
  required:
  - R_RULES
  - R_TESTS
  scope:
  - rules
  - tests
reusable_definition:
  id: FIX-REVIEW
  revision: 1
  constraints:
  - KEEP_SCOPE
  - KEEP_EVIDENCE
  allowed_input: fixed_project_snapshot
resource_budget:
  unit: fixture-context-unit
  max_simultaneous: 100
  required_regression_reserve: 20
note: 预算是固定夹具前提，不是实际模型容量。
---

# 通用入口的固定控制输入

已确认的实际用户请求或父seed在本地Plan另行绑定，不能以本夹具替代。source需求与判据先固定；可按各case指定差异构造受控候选，保存其实际字节和观测。
