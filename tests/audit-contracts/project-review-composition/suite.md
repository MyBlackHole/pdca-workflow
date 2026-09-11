---
schema: pdca.audit-contract-suite/v1
suite_id: audit-project-review-composition-v1
revision: 1.0.0
definition_id: ontology:pattern/audit/project-review-composition
fixture_only: true
runtime_result: not_run
scene_coverage:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
constraints: &id001
- CP_COVER
- CP_RECURSE
- CP_SHARE
- CP_COMBINE
cases:
- case_id: M-P
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids: *id001
  category: positive
  purpose: 角色模式完整采用应接受
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-M-P
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
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
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: M-N1
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids:
  - CP_COVER
  category: negative_sample
  purpose: 逐项破坏CP_COVER必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-M-N1
    facts:
      role_coverage_complete: false
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COVER
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: M-N2
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids:
  - CP_RECURSE
  category: negative_sample
  purpose: 逐项破坏CP_RECURSE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-M-N2
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: false
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_RECURSE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: M-N3
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids:
  - CP_SHARE
  category: negative_sample
  purpose: 逐项破坏CP_SHARE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-M-N3
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: false
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_SHARE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: M-N4
  revision: 1.0.0
  scene: ontology_modeling
  required: true
  constraint_ids:
  - CP_COMBINE
  category: negative_sample
  purpose: 逐项破坏CP_COMBINE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-M-N4
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COMBINE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: E-P
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids: *id001
  category: positive
  purpose: 角色模式完整采用应接受
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-E-P
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
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
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: E-N1
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids:
  - CP_COVER
  category: negative_sample
  purpose: 逐项破坏CP_COVER必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-E-N1
    facts:
      role_coverage_complete: false
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COVER
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: E-N2
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids:
  - CP_RECURSE
  category: negative_sample
  purpose: 逐项破坏CP_RECURSE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-E-N2
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: false
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_RECURSE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: E-N3
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids:
  - CP_SHARE
  category: negative_sample
  purpose: 逐项破坏CP_SHARE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-E-N3
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: false
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_SHARE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: E-N4
  revision: 1.0.0
  scene: ontology_projection
  required: true
  constraint_ids:
  - CP_COMBINE
  category: negative_sample
  purpose: 逐项破坏CP_COMBINE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-E-N4
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COMBINE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: V-P
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids: *id001
  category: positive
  purpose: 角色模式完整采用应接受
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-V-P
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
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
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: V-N1
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids:
  - CP_COVER
  category: negative_sample
  purpose: 逐项破坏CP_COVER必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-V-N1
    facts:
      role_coverage_complete: false
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COVER
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: V-N2
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids:
  - CP_RECURSE
  category: negative_sample
  purpose: 逐项破坏CP_RECURSE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-V-N2
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: false
      readonly_sharing_allowed: true
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_RECURSE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: V-N3
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids:
  - CP_SHARE
  category: negative_sample
  purpose: 逐项破坏CP_SHARE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-V-N3
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: false
      parent_combination_checked: true
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_SHARE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
- case_id: V-N4
  revision: 1.0.0
  scene: ontology_conformance_verification
  required: true
  constraint_ids:
  - CP_COMBINE
  category: negative_sample
  purpose: 逐项破坏CP_COMBINE必须拒绝
  preconditions:
    isolated_fixture: true
    definition_revision: 3.4.0
    suite_id: audit-project-review-composition-v1
    production_authorization: false
  inputs:
    subject_label: synthetic-pattern-V-N4
    facts:
      role_coverage_complete: true
      recursive_assessment_allowed: true
      readonly_sharing_allowed: true
      parent_combination_checked: false
    facts_origin: 固定夹具，非模型自报的生产事实
    subject_issues_may_exist: true
  action: 把该固定结构及其原文问题交给当前scene检查方法，逐约束核对；结构参考模型只评价facts谓词，真实AI/来源核对另行运行。
  expected:
    contract_qualified: false
    violated_constraint_ids:
    - CP_COMBINE
  forbidden:
  - 把subject本身失败等同审查任务失败
  - 把未知证据标通过
  - 读取expected作为实际观测
  oracle:
    source: ../../../ontology/pattern/audit/project-review-composition.md
    method: 各必需谓词独立断言，失败项集合精确等于expected；真实文本判定须给原文/版本/可复核依据。
    model_scope: synthetic_structured_predicates_only
  observation:
  - 固定inputs摘要
  - 实际逐约束判断
  - 缺证或失败项
  - 运行者/环境与范围
  failure_signature: 漏掉任一应失败约束或误拒完整正样本为判定错误；夹具读不到/工具异常为error。
  cleanup: 先保留所有证据，再清除本次隔离副本；不改共享定义或原expected。
  rework: 保存不合格角色映射→不改变用户scope→修复遗漏、递归策略或父组合→必要时新tree/attempt→本套件15例及K07/K09/K11/K12/K20全部回归。共享发布与实际节点任务单独验证。
  actual: null
  runtime_result: not_run
---

# 组成模式三场景测试契约

15个固定结构样本覆盖CP_COVER/CP_RECURSE/CP_SHARE/CP_COMBINE，每scene有完整正例与四个单约束破坏样本。只是模型输入，不是实际任务结论；真实采用需要角色原文、分解证据、逐节点任务和父组合实际结果。

正例允许多角色只读同一知识，各实际节点独立完整PDCA。反例覆盖漏掉facts、父强迫孩子叶化、禁止只读共享、仅汇总孩子PASS。判定器应准确接受正样本并拒绝相应负样本；always-pass/always-fail/漏一项义务须被识别。

输入/动作/oracle/观测/清理/返工逐case写在frontmatter。案例引用使用suite/scene/case/revision全身份；不得从根suite借同名例充当CP覆盖。真实host结果全部not_run；与K回归联合验证，但不声称结构模型具备通用语义审查能力。
