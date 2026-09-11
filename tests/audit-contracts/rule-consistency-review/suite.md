---
schema: pdca.audit-contract-suite/v1
suite_id: audit-rule-consistency-review-v1
revision: 1.0.0
definition_id: ontology:concept/audit/rule-consistency-review
fixture_only: true
runtime_result: not_run
scene_coverage:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
constraints:
- RC_SOURCE
- RC_SCOPE
- RC_COUNTEREXAMPLE
- RC_BIDIRECTION
cases:
- case_id: M-P
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids:
  - RC_SOURCE
  - RC_SCOPE
  - RC_COUNTEREXAMPLE
  - RC_BIDIRECTION
  category: positive
  purpose: 完整合成样本应被正确接受；subject可有被准确报告的缺陷。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-M-P
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: true
    violated_constraint_ids: []
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: M-N1
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids: &id001
  - RC_SOURCE
  category: negative_sample
  purpose: 故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-M-N1
    facts:
      source_pinned: false
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id001
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: M-N2
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids: &id002
  - RC_SCOPE
  category: negative_sample
  purpose: 故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-M-N2
    facts:
      source_pinned: true
      conditions_aligned: false
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id002
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: M-N3
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids: &id003
  - RC_COUNTEREXAMPLE
  category: negative_sample
  purpose: 故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-M-N3
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: false
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id003
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: M-N4
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids: &id004
  - RC_BIDIRECTION
  category: negative_sample
  purpose: 故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-M-N4
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id004
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: E-P
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids:
  - RC_SOURCE
  - RC_SCOPE
  - RC_COUNTEREXAMPLE
  - RC_BIDIRECTION
  category: positive
  purpose: 完整合成样本应被正确接受；subject可有被准确报告的缺陷。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-E-P
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: true
    violated_constraint_ids: []
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: E-N1
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids: &id005
  - RC_SOURCE
  category: negative_sample
  purpose: 故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-E-N1
    facts:
      source_pinned: false
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id005
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: E-N2
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids: &id006
  - RC_SCOPE
  category: negative_sample
  purpose: 故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-E-N2
    facts:
      source_pinned: true
      conditions_aligned: false
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id006
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: E-N3
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids: &id007
  - RC_COUNTEREXAMPLE
  category: negative_sample
  purpose: 故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-E-N3
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: false
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id007
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: E-N4
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids: &id008
  - RC_BIDIRECTION
  category: negative_sample
  purpose: 故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-E-N4
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id008
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: V-P
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids:
  - RC_SOURCE
  - RC_SCOPE
  - RC_COUNTEREXAMPLE
  - RC_BIDIRECTION
  category: positive
  purpose: 完整合成样本应被正确接受；subject可有被准确报告的缺陷。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-V-P
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: true
    violated_constraint_ids: []
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: V-N1
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids: &id009
  - RC_SOURCE
  category: negative_sample
  purpose: 故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-V-N1
    facts:
      source_pinned: false
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id009
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: V-N2
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids: &id010
  - RC_SCOPE
  category: negative_sample
  purpose: 故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-V-N2
    facts:
      source_pinned: true
      conditions_aligned: false
      witness_present: true
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id010
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: V-N3
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids: &id011
  - RC_COUNTEREXAMPLE
  category: negative_sample
  purpose: 故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-V-N3
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: false
      false_conflicts_rejected: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id011
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
- case_id: V-N4
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids: &id012
  - RC_BIDIRECTION
  category: negative_sample
  purpose: 故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-rule-consistency-review-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-rule-consistency-review-V-N4
    facts:
      source_pinned: true
      conditions_aligned: true
      witness_present: true
      false_conflicts_rejected: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids: *id012
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/concept/audit/rule-consistency-review.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保留原fail→最小复现→检查oracle是否误读/遗漏→合同不变Do内有限修复否则新attempt/Agent→重跑本套件全部15例及相关组合→新证据关闭本地问题，不伪造旧PASS。
  actual: null
  runtime_result: not_run
---

# 规则一致性审查：适用条件与跨文件冲突：可复用三场景套件

15个案例是具名且字段完整的**合成契约测试**：每场景1正例+4逐项破坏的反例。字段fact仅表示模型输入，不是对实际项目的自证；真实任务须给每项fact可复核的原文和来源/观测。运行这些谓词不等于已经完成任何实际项目审查。

每个案例拥有完整输入、动作、expected、oracle、观测、失败和返工。使用前固定本suite字节及当前绑定，把case身份解析为(node,suite,revision,scene,case)；不从别的suite拿同名M-P填空。

## 正误判定器控制

always-pass须被所有N样本识别；always-fail须被P样本识别；omit-one-obligation须被其对应N1—N4识别。将约束存在性检查错当事实判断也不合格。下方case索引不填真实actual：

- `ontology_modeling/M-P`：完整合成样本应被正确接受；subject可有被准确报告的缺陷。
- `ontology_modeling/M-N1`：故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
- `ontology_modeling/M-N2`：故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
- `ontology_modeling/M-N3`：故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
- `ontology_modeling/M-N4`：故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。
- `ontology_projection/E-P`：完整合成样本应被正确接受；subject可有被准确报告的缺陷。
- `ontology_projection/E-N1`：故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
- `ontology_projection/E-N2`：故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
- `ontology_projection/E-N3`：故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
- `ontology_projection/E-N4`：故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。
- `ontology_conformance_verification/V-P`：完整合成样本应被正确接受；subject可有被准确报告的缺陷。
- `ontology_conformance_verification/V-N1`：故意破坏 RC_SOURCE；不能仍称相应审查产物合格。
- `ontology_conformance_verification/V-N2`：故意破坏 RC_SCOPE；不能仍称相应审查产物合格。
- `ontology_conformance_verification/V-N3`：故意破坏 RC_COUNTEREXAMPLE；不能仍称相应审查产物合格。
- `ontology_conformance_verification/V-N4`：故意破坏 RC_BIDIRECTION；不能仍称相应审查产物合格。

## 实际使用的场景区别

modeling验证当前范围、方法、测试与分解设计；projection核对实际执行报告/证据；verification独立复核报告。实际项目的真实输入和tools在各任务Plan固定，不能修改这里的约束来适配错误结果。泛化到其他项目必须先检查适用性；不要求自由建模长成唯一参考树。
