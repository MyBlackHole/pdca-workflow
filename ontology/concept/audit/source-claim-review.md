---
schema: pdca.asset/v2
id: ontology:concept/audit/source-claim-review
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 资料主张核验：版本、证据与适用性
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
- id: CL_ID
  required: true
  rule: 每项主张有固定原文/位置和原始断言，禁止悄悄改写待审主张。
- id: CL_VERSION
  required: true
  rule: 证据的对象、版本、条件和权限与主张匹配；缺证据/不匹配为unknown，不能补造。
- id: CL_ORACLE
  required: true
  rule: 支持或反驳来自可复核独立来源/观测，不使用实现自己的输出或同一错误样例循环自证。
- id: CL_VERDICT
  required: true
  rule: 分开supported/contradicted/unknown和审查任务是否完成；不把来源存在、测试数量或active当事实通过。
test_contract_ref: ../../../tests/audit-contracts/source-claim-review/suite.md
---

# 资料主张核验：版本、证据与适用性

本节点是可跨工作复用的**规定性实体定义**；采用者绑定具体对象、输入和版本，另建自己的完整PDCA与Agent。本文没有当前work/task/用户会话或实际PASS；本次仓库文件交付不伪称运行时共享发布。

## 必需约束

| ID | 规则 |
|---|---|
| CL_ID | 每项主张有固定原文/位置和原始断言，禁止悄悄改写待审主张。 |
| CL_VERSION | 证据的对象、版本、条件和权限与主张匹配；缺证据/不匹配为unknown，不能补造。 |
| CL_ORACLE | 支持或反驳来自可复核独立来源/观测，不使用实现自己的输出或同一错误样例循环自证。 |
| CL_VERDICT | 分开supported/contradicted/unknown和审查任务是否完成；不把来源存在、测试数量或active当事实通过。 |

## 实体接口和判定

输入：固定资料片段、主张ID、涉及对象与版本、预先定义的证据要求和可访问来源。输出：逐主张核验表，source_ref/位置、版本/条件、已核范围、差异和不确定性，问题与重验条件。可为源码、规范、实际观测或用户规定性要求，但这些依据类型不得相互冒充。

同一个字段可由用户定义目标，不要求外部文献证明所有系统必须如此；描述外部技术机制则应核对一手来源的匹配版本。来源不足保留unknown；私有分支不可访问不等于不存在。一个来源支持部分条件，不外推整篇或所有版本。事实发现改变应发新问题/证据记录，不重写原主张使其天然正确。

## 递归与组合

大范围按领域、实体或固定版本集合拆分；不默认每句是一任务。每个叶需能列清主张与证据窗口，父汇总版本/术语差异和未核验覆盖。不能把“以后采用时再核验”当作本次内容审查完成。

## 示例边界

合成来源说“版本A上限8”，待审主张说“A上限16”：应contradicted。只有版本B来源：A主张应unknown，不能以名称相同支持。正例和反例均为教学数值，不是某真实产品的技术事实。

modeling确定主张抽取与来源合同，projection实际取得证据并判定，verification独立核查选择偏差、引用和结论。严重错误需隔离受影响采用，未知不能抬升为通过。

## 可复用正反例与三场景

[test contract](../../../tests/audit-contracts/source-claim-review/suite.md)给出三个scene的具名正确/错误样本、判定和返工；案例是固定设计，真实任务必须核对适用条件、绑定工具并记录自己的运行。无论复用本定义还是扩展，均不能省略当前节点的完整PDCA。
