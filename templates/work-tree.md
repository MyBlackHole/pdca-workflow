---
schema: pdca.work-tree/v3.4
work_id: null
tree_revision: null
root_node_id: null
state: draft
nodes: []
frozen_manifest_ref: null
confirmation_ref: null
supersedes: null
proposal_id: null
freeze_receipt_ref: null
protocol_revision: 3.4.10
dependency_graph_refs: []
dependency_check_refs: []
wait_policy_ref: null
control_view_ref: null
definition_manifest_refs: []
modeling_decision_refs: []
adoption_refs: []
view_kind: mutable_projection
tree_spec_ref: null
tree_spec_digest: null
knowledge_obligations: []
knowledge_status_view_ref: null
readiness_ref: null
work_budget_ref: null
issue_impact_refs: []
release_manifest_ref: null
release_receipt_ref: null
---

# 工作树可变视图草稿

每节点唯一ID/父归属；nodes每项含node_id、parent_node_id、children、固定node_ref/revision/digest、建模task/attempt及suite refs。本文件不是固定清单；使用tree-spec与tree-manifest模板，不能把本视图放进目标签认闭包。

## 用户目标与原始范围

真实需求来源、授权范围、成功/失败边界；根目标不由AI自行扩张。

## 拆分覆盖

| 父要求 | 负责孩子或父组合义务 | 证明/测试 | 漏项或冲突 |
|---|---|---|---|

## 结构与冻结检查

唯一根/唯一父/全可达/无环/parent与children一致；全部必需节点定义、suite/oracle、预算明确；失败/未完成seed不得隐去。写实际检查与证据，草稿不是冻结树。

## 变更影响

旧新节点/定义/套件映射、失效任务和证据、需重新确认对象。新版本不覆盖旧包。


TREE-01工作级tree_confirmation模板是唯一冻结路径。confirmation_ref不能引用task的Plan/Check确认；state只能在闭包、真实响应和冻结回执校验后更新。

冻结前固定DEPENDENCY-01图与检查回执；派发只消费该工作授权快照。图检查与tree_confirmation终局必须与当前提案一致；历史图PASS不证明新候选图。


3.3冻结闭包纳入各节点固定定义manifest、reuse决定、local delta和采用行。ADOPT-01当前公告核对结果在独立冻结/控制回执中绑定，不回写已确认清单；普通新head不切换本树版本。

## 3.4 字段与时点

protocol_baseline_ref固定工作协议闭包，subject_snapshot_ref固定被审对象/输入约定，definition_artifact是业务语义而不是记录路径。definition_refs按REUSE-01；decomposition按DECOMP-01。knowledge_obligations只放固定计划与完成条件，未来publication/终态证据在外部履行记录，不回填本文件。新模板空值只表示草稿，不作为准入或通过。
