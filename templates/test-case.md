---
schema: pdca.test-case/v3
case_id: null
revision: null
node_id: null
scene: null
suite_ref: null
constraint_ids: []
ac_ids: []
category: null
required: true
defaults_ref: null
preconditions: null
inputs: null
action: null
expected: null
forbidden: null
oracle: null
observation: null
failure_signature: null
cleanup: null
kills: []
regression_issue: null
protocol_revision: 3.4.10
test_layer: null
subject_ref: null
oracle_ref: null
fault_model: null
injection_invariants: []
source_binding_ref: null
assertions: []
---

# 一条可复现正例或反例

## 为什么测

解释该输入为何区分这条规则；不是写“验证正确性”。所有frontmatter空字段在用于运行前必须具体或通过固定defaults解析完整。

## 输入与动作

列精确输入/状态/顺序/故障注入点；给真实工具绑定。非法输入本身不是测试失败，正确拒绝才是预期。

## 独立判定

明确返回、错误类别/优先级、输出/状态/禁止副作用、比较方式/容差及来源。不得用实现输出生成自己的expected。

## 证据和失败定位

应保存哪些前后快照/输出/日志；断言失败与测试环境error如何区别；清理不能抹掉证据。actual放test-run，不覆盖本案例。


## 固定集合与具名断言

每项具名断言写assertion_id、constraint_ids、expected、forbidden、oracle、observation；断言清单不能由运行结果倒推。
