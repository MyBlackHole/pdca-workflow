---
schema: pdca.test-suite/v3
suite_id: null
revision: null
node_id: null
scene: null
contract_ref: null
case_refs: []
mutation_refs: []
defaults_ref: null
coverage: []
required_cases: []
repair_budget: null
acceptance_scope: node_scene_artifact
protocol_revision: 3.4.11
test_layer: null
input_contract: null
local_binding_refs: []
frozen_contract_suite_ref: null
regression_extension_refs: []
---

# 当前节点任务单元测试套件草稿

不是测试结果。进入Do前，TEST-01/CASE-01所有必需字段必须具体。

## 被测边界和固定输入

节点/定义版本；直接孩子真实接口与可用stub边界；环境/fixture及真实摘要；禁止访问的生产对象。

## 公共执行设置

实际tool/entry、构建/运行方式、独立sandbox、初始状态、成功/失败清理、测试器正负控制、输出/状态观测、随机seed与并发时序。案例继承defaults时保留有效展开摘要。

## 约束覆盖矩阵

| 约束ID | 正例 | 反例 | 边界/故障/组合 | 已知错误实现及击杀例 | 不适用理由/真实审核 |
|---|---|---|---|---|---|

## 预先承诺的判定

必须/可选分类，所有必须案例同交付版本pass；error/blocked/not_run/flaky不能冒充通过；mutation invalid不算killed。本套件仅包含当前node_id/scene负责的回归与组合；受影响祖先/其他节点列入rework计划，不作为本套件通过前置。

## 预算与停止

有限Do修复次数、同症状重复上限、资源预算、必需回归预算；超限转真实失败判定/新attempt。不得写“无限直到成功”。
