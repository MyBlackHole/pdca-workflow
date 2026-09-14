---
schema: pdca.rework/v3.2
issue_id: null
work_id: null
tree_revision: null
node_id: null
scene: null
origin_task_id: null
origin_run_id: null
case_ids: []
state: open
root_cause_class: null
confidence: null
predecessor_task_id: null
successor_task_id: null
affected_nodes: []
stale_refs: []
regression_case_ids: []
close_evidence: []
local_delivery_refs: []
affected_regression_refs: []
review_refs: []
protocol_revision: 3.4.11
successor_route: null
termination_ref: null
old_slot_release_ref: null
resource_settlement_refs: []
successor_authorization_ref: null
origin_artifact_ref: null
origin_artifact_digest: null
violated_constraint_ids: []
blocking_scopes: []
regression_extension_refs: []
work_budget_ref: null
integrity_event_ref: null
---

# 失败复现、返工与回归单

## 失败现场

旧定义/套件/实现及孩子版本；精确输入、expected/actual、失败断言、原始证据和副作用；未复现写未复现。

## 测试器检查与最小复现

已知正确/错误控制样本、测试环境是否可信；原输入到最小样本的缩减链、seed/时序、复现实际run。

## 根因假设与修复方案

已证事实/推断/unknown分开；机制与最小修复、应改变的案例、不应改变的行为、不能修改的oracle/权限。

## 路径和预算

Do内同任务有限修复还是新attempt/newAgent；Check以后不得回Do。预算/重复上限、停止与升级条件。

## 回归计划

原失败→同约束边界→全部必需suite→受影响孩子输入/组合祖先→新的独立审查。每层列具体case/node/ref，不能只写“回归通过”。

## 修复与关闭证据

新实现版本/差异、每次run/失败、全必需聚合、影响分析、独立审查。缺任何必需证据不得closed；旧issue/失败不能改写成pass。


## 作用域与唯一更新者

local_delivery_refs保存各节点可供组合的本地交付；affected_regression_refs和review_refs保存后续工作级回归。只有这些证据都匹配当前版本才更新closed，执行Agent不能自签整树关闭。宿主工作索引唯一写入者执行记录更新；该记录不要求孩子等待祖先才能正常归档。

## 后继准入

successor_route为normal_archive或authorized_interrupt；后者必须真实终止/撤权/资源结清，原phase不伪归档。successor_authorization与取消来源分开；unknown远端资源保留时禁止冲突后继。

有限维护profile及fixture边界见[生命周期记录契约](../ontology/contracts/lifecycle-records.md)。字段和摘要通过不认证真实宿主能力；不得把示例复制成执行事实。
