---
schema: pdca.conformance-review/v3
review_task_id: null
work_id: null
tree_revision: null
node_id: null
release_ref: null
subject_artifact_refs: []
child_review_refs: []
subject_conformance: null
review_task_verdict: null
test_run_refs: []
issues: []
protocol_revision: 3.4.10
requirements_basis_ref: null
requirements_basis_digest: null
subject_snapshot_ref: null
definition_refs: []
coverage_ref: null
claim_scope: null
limitations: []
---

# 独立对应审查报告草稿

只能由新的独立节点审查任务产生真实报告。review_task_verdict评价审查任务，subject_conformance评价被审实现，二者不能混淆。

## 定义到实现、实现到定义

| 约束 | 实现位置/固定版本 | 正反例run/原始证据 | 符合性 | 缺失/额外行为/理由 |
|---|---|---|---|---|

## 组合与证据

真实孩子接口/错误传播/整体不变量；测试器控制样本、反例/变体、版本漂移、未知项；孩子PASS不替代父组合审查。

## 缺陷与处置

按 [发现核验](../ontology/process/independent-work-review.md#review-counterevidence)填写既有issues及正文；发现问题不直接修改被审对象。

| issue/主张 | 固定位置与触发 | 支持证据 | 已查反证及适用条件 | 确认／否定／unknown及理由 | 影响、取证或关闭回归 |
|---|---|---|---|---|---|

“否定”只针对该发现；不代表所有必需约束通过。严重性依据可证影响，无法核验的运行或权限前提单列。


## 固定集合与具名断言

claim_scope明确exact_declaration/abstract_contract/layout/behavior或本次具体方法范围。coverage从固定requirements_basis独立展开，正向到实现与观察、反向到遗漏/额外行为；不按报告目录生成分母。缺源代码和配置的事实保持unknown，维护观察不可填写独立任务已完成。


## 结果消费核对

实际来源、当次采用版本、具体违例与证据缺口分开说明。输出前将每项确定差异与本表及subject_conformance反向核对；报告自身完成不改写对象符合性。对历史材料不把缺项直接解释为操作未执行。
