---
schema: pdca.regression-extension/v1
protocol_revision: 3.4.11
extension_id: null
issue_ref: null
frozen_contract_suite_ref: null
frozen_contract_suite_digest: null
existing_constraint_refs: []
added_case_refs: []
old_failure_evidence_refs: []
semantic_change: null
adoption_authorization_ref: null
applicable_attempt_refs: []
---

# 不覆盖冻结合同的回归增补

TEST-01/REWORK-01：逐新增案例绑定版本、摘要、原有禁止谓词和固定expected。semantic_change必须经过明确比对，不自填false。允许行为改变则新树；仅加强旧约束检测才作为增补。

后继Plan/实际run须固定基准+增补的完整effective_case_refs，保留每个原必需案例及相同期望。旧suite/node/历史run保持原字节。旧版本未能复现时披露，不能声称先红后绿；授权不能从发现缺陷推导。
