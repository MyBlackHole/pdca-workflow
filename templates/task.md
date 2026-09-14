---
schema: pdca.task/v3.2
task_id: null
work_id: null
tree_revision: null
node_id: null
scene: null
attempt: 1
predecessor_task_id: null
rework_issue_ref: null
revision: 0
title: null
phase: plan
execution_state: unexecuted
writer: null
conversation_ref: null
baseline: null
test_suite_ref: null
dependencies: []
parent_node_id: null
last_transition: null
extensions: {}
protocol_revision: 3.4.11
control_view_ref: null
last_control_event: null
terminal_reason: null
termination_ref: null
wait_policy_ref: null
pinned_graph: null
resource_reservation_refs: []
capability_check_refs: []
protocol_baseline_ref: null
work_budget_ref: null
integrity_event_refs: []
---

# 当前节点任务草稿

空白模板不是已执行。真实身份/写权/基线/套件/确认齐备才能进入Do；scene为唯一场景字段。

## 当前节点与职责

目标及来自父seed/用户目标的要求；当前场景、定义版本、接口、写域、禁止事项。不得把别的目标节点并入本任务。

## 四字段执行契约

work_product / required_actions / constraints / testable_signal：分别填写具名产物、必须动作与验证、明确范围和oracle。

## 验收与测试映射

| AC ID | 约束ID | 必须性 | 期望/禁止 | suite/case refs | oracle | 失败处置 |
|---|---|---|---|---|---|---|

## 输入与上下文

| 来源节点/定义 | 版本 | 固定位置/摘要 | 适用约束/导入理由 | 授权依据 |
|---|---|---|---|---|

## 执行步骤与预算

节点内步骤、实际测试绑定、有限repair_iteration上限、同症状重复上限、资源预算、全必需回归成本、停止/升级条件。步骤不替代目标节点任务。

## 当前观测与未决

只填真实进度、失败run/issue和需要用户决定的事项；不复制示例expected到actual。

## 控制与写入资格

按STATE-01矩阵；terminal_reason仅有真实termination后填写。control_view_ref来自宿主实际控制视图，不自造取消/恢复；active只作legacy查询。pinned_graph固定ref/revision/digest/check，不从任务dependencies随手计算真相。

协议版本由实际所选protocol-release快照确定；本模板默认值不是执行证据。schema/资产版本可以不同。派发前绑定记录未知字段不造ID，正式任务主记录仍在records/<task-id>/task.md。
