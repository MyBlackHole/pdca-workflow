---
schema: pdca.test-run/v3
run_id: null
task_id: null
work_id: null
tree_revision: null
node_id: null
scene: null
attempt: null
repair_iteration: 0
suite_ref: null
suite_digest: null
artifact_ref: null
artifact_digest: null
child_artifacts: []
environment_ref: null
started_at: null
time_source: null
case_results: []
mutation_run: false
mutant_id: null
raw_evidence_refs: []
protocol_revision: 3.4.10
effective_case_refs: []
regression_extension_refs: []
checker_ref: null
checker_digest: null
visible_input_manifest_ref: null
fixture_validation_refs: []
previous_run_ref: null
repair_kind: null
repair_diff_ref: null
evidence_manifest_ref: null
retention_check_ref: null
assertion_results: []
requirements_basis_ref: null
requirements_basis_digest: null
---

# 实际测试运行记录草稿

未运行时不得填写真实run_id、假时间、假摘要或pass。每次实现/环境/套件变化新建run；保留前次失败。

## 环境和执行

实际命令/工具/参数、工作目录、工具版本、fixture/seed/时序、真实退出状态、环境限制；敏感值脱敏但保留可复现方式。

## 逐案例观测

| case_id/revision | actual输入与状态 | expected摘要 | actual返回/状态 | 失败断言/差异 | result | 原始证据/摘要 | cleanup |
|---|---|---|---|---|---|---|---|

result只用TEST-01取值。跨运行不稳定另标flaky并保留所有运行；不能只保留最后成功。

## 覆盖/聚合

必须总数、实际执行数、缺失/跳过/error/blocked、过期证据、变体killed/survived/invalid与理由；不混合不同artifact摘要统计“全绿”。

## 下一步

关联issue、复现/修复迭代与回归范围；正确实现run和mutation run分开。

## 分层结果与注入核验

case_results逐项绑定完整(node,suite,suite_revision,case,case_revision)、effective_case_digest、subject/fixture/oracle摘要、observation_ref、subject_verdict、checker_case_result和checker_mutation_result。result保持TEST-01原枚举；无错误检查器运行时mutation字段为空，不把正常拒绝样本汇总为killed。

visible_input_manifest明确检查器实际看到的文件/提示，不含本例expected答案。fixture_validation保留计划注入与真实diff及不变量比较；未命中记error/invalid。临时目录清理前核对evidence_manifest内样本、方法和实际观测可重新读取；retention_check不是仅一句“已保留”。

## 观测归属与保留集合

逐案例观测固定task/attempt/run_id、scene、有效case/产物/检查器/可见输入摘要。引用其他运行的材料需具名复用绑定，不得冒充本次新观测。run之外的可见输入与证据清单同样核对身份、成员及固定摘要，不能仅验证清单文件自身摘要。

维护程序的结构/关系pass不能升级为语义或输入隔离pass；未执行项目分别保留not_run/unsupported。辅助集合的有限维护profile见[关系边界](../ontology/contracts/record-relations.md)。


## 固定集合与具名断言

assertion_results逐条固定assertion_id、完整case身份、expected/oracle引用、observation_ref/digest和实际result。case数与assertion数分别从有效集合计算；套件外诊断不计入必需覆盖。
