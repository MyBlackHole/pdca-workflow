---
schema: pdca.gate-check/v1
protocol_revision: 3.4.10
check_id: null
task_id: null
attempt: null
gate_id: null
subject_ref: null
subject_digest: null
observed_control_revision: null
checks: []
result: null
limitations: []
requirements_basis_ref: null
requirements_basis_digest: null
---

# 门禁逐谓词核验草稿

GATE-01的核验事实，不新增转换边。checks每项含predicate_id、required、authority_ref、subject/ref/digest、evidence_refs、verification_action、observation_ref和satisfied/unsatisfied/unknown。必需谓词集合取自当前gate，不由执行者随意删减；空集拒绝。

只在全部必需项真实satisfied后result=ready。拒绝/未知记录为诊断，不创建approved转换；无真实confirm来源不能因声明限制而通过。能力、控制与写权在提交前再次核验。


requirements_basis固定适用权威、原请求/seed与当前要求来源；由核验入口独立选定，不能由候选自证。模板空值是草稿，不代表未知项通过。

## 嵌套项与被核验对象

checks的authority_ref必须解析到固定协议中的适用权威；evidence_refs与observation_ref逐项解析并核对摘要。未提供元素级subject时继承顶层subject，显式提供则必须同属当前核验对象。Check门禁不得引用其他task/attempt的review。字段齐全但关系错误仍不ready。


## 结果消费核对

提交时重新读取本次verification_action的结果与输入摘要；检查器异常、过期输出及未支持范围不成为satisfied。失败检查记录可以供诚实收尾使用，不生成业务PASS或真实批准。
