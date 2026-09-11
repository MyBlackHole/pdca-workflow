---
schema: pdca.asset/v2
id: ontology:concept/audit/rule-consistency-review
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 规则一致性审查：适用条件与跨文件冲突
asset_role: reusable_work_definition
authority_basis: 当前用户确认的设计约束；规定性工作契约，不是外部技术事实认证
delivery_kind: repository_asset_snapshot
runtime_publication_proven: false
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-decomposition
  - ontology:concept/ontology-reuse
  - ontology:concept/task-unit-test
  - ontology:process/independent-work-review
constraints:
- id: RC_SOURCE
  required: true
  rule: 逐规则固定权威来源、原文、适用条件与协议/对象版本。
- id: RC_SCOPE
  required: true
  rule: 区分组成、继承、依赖、授权与运行状态；按共同前置条件比较规则，不混用不同scene。
- id: RC_COUNTEREXAMPLE
  required: true
  rule: 冲突须有能同时满足前置的具体事件/状态轨迹；可能风险与已发生故障分开。
- id: RC_BIDIRECTION
  required: true
  rule: 既识别真实冲突，也排除不同适用域产生的伪冲突；未观察到错误不等于验证完成。
test_contract_ref: ../../../tests/audit-contracts/rule-consistency-review/suite.md
---

# 规则一致性审查：适用条件与跨文件冲突

本节点是可跨工作复用的**规定性实体定义**；采用者绑定具体对象、输入和版本，另建自己的完整PDCA与Agent。本文没有当前work/task/用户会话或实际PASS；本次仓库文件交付不伪称运行时共享发布。

## 必需约束

| ID | 规则 |
|---|---|
| RC_SOURCE | 逐规则固定权威来源、原文、适用条件与协议/对象版本。 |
| RC_SCOPE | 区分组成、继承、依赖、授权与运行状态；按共同前置条件比较规则，不混用不同scene。 |
| RC_COUNTEREXAMPLE | 冲突须有能同时满足前置的具体事件/状态轨迹；可能风险与已发生故障分开。 |
| RC_BIDIRECTION | 既识别真实冲突，也排除不同适用域产生的伪冲突；未观察到错误不等于验证完成。 |

## 实体接口

输入：固定的规则集合、规则ID→原文范围映射、场景/条件/事件约定，以及需检查的规则问题。输出：逐项一致、冲突、遗漏或未知判定，最小可复核轨迹，涉及原文与修复建议。目录计数和grep只作定位，不能证明取消、返工、写权和确认的语义正确。

## 工作方法与可拆边界

从单条规则的前置/动作/结果开始，检查共享状态和接口的成对/多条组合。数据依赖图与资源等待图分开；方法阶段与执行状态分开。跨文件没有明确顺序时登记歧义，不能说真实系统一定死锁。范围大可按状态机、资源控制、版本/发布划分子实体，但跨分片交接约束必须留给组合父。

## 已知正反样本

“孩子本地完成即可交付”与“工作缺陷等祖先复核才关闭”不冲突；把交付条件误写成必须先关闭工作缺陷，会与父等待孩子可用产生循环。两个规则有不同scene前置，不应无条件合并为冲突；同场景同输入允许和禁止同一动作，则须给出具体轨迹。

modeling固定比较对象和oracle；projection实际核对文本与构造轨迹；verification独立重放与检查误报/漏报。修复方案不是已实施修复；若用户要求修改，另建明确节点任务和新基线。

## 可复用正反例与三场景

[test contract](../../../tests/audit-contracts/rule-consistency-review/suite.md)给出三个scene的具名正确/错误样本、判定和返工；案例是固定设计，真实任务必须核对适用条件、绑定工具并记录自己的运行。无论复用本定义还是扩展，均不能省略当前节点的完整PDCA。
