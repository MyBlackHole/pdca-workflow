---
schema: pdca.asset/v2
id: ontology:pattern/audit/project-review-composition
type: pattern
semantic_kind: individual
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 项目审查组成模式：角色复用与递归展开
asset_role: composition_pattern
authority_basis: 当前用户确认的设计约束；规定性工作契约，不是外部技术事实认证
delivery_kind: repository_asset_snapshot
runtime_publication_proven: false
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:pattern
  relates_to:
  - ontology:concept/audit/project-review
  - ontology:concept/audit/rule-consistency-review
  - ontology:concept/audit/source-claim-review
  - ontology:concept/audit/test-contract-review
  - ontology:concept/task-decomposition
constraints:
- id: CP_COVER
  required: true
  rule: 所有当前授权必需维度有主要交付责任，不通过互相排除遗漏。
- id: CP_RECURSE
  required: true
  rule: 每个实际孩子递归评估；默认角色允许进一步细分，不固定叶子数。
- id: CP_SHARE
  required: true
  rule: 多个角色可只读采用同一知识，不形成第二组成父或写入所有权。
- id: CP_COMBINE
  required: true
  rule: 父集成检查角色接口与跨分片问题，不能只加总PASS。
test_contract_ref: ../../../tests/audit-contracts/project-review-composition/suite.md
---

# 项目审查组成模式：角色复用与递归展开

本节点是可跨工作复用的**规定性实体定义**；采用者绑定具体对象、输入和版本，另建自己的完整PDCA与Agent。本文没有当前work/task/用户会话或实际PASS；本次仓库文件交付不伪称运行时共享发布。

## 必需约束

| ID | 规则 |
|---|---|
| CP_COVER | 所有当前授权必需维度有主要交付责任，不通过互相排除遗漏。 |
| CP_RECURSE | 每个实际孩子递归评估；默认角色允许进一步细分，不固定叶子数。 |
| CP_SHARE | 多个角色可只读采用同一知识，不形成第二组成父或写入所有权。 |
| CP_COMBINE | 父集成检查角色接口与跨分片问题，不能只加总PASS。 |


## 必需角色（参数化，不是当前工作节点）

| role_id | 职责与输出 | 默认定义/输入 | 子分解策略 |
|---|---|---|---|
| rules | 阶段、门禁、取消、返工等规则交叉审查 | rule-consistency-review + 固定协议对象 | assess_recursively |
| structure | 类型、组成、唯一权威、依赖与闭包语义 | rule-consistency-review + ontology-creation-gate | assess_recursively |
| facts | 按领域/实体核验资料事实、适用性与未核范围 | source-claim-review | assess_recursively |
| tests | suite/oracle/负样本/观测和返工覆盖 | test-contract-review | assess_recursively |
| reuse | 复用、发布、采用与错误影响的规则和实际材料 | rule-consistency-review + REUSE/EVOLVE/ADOPT | assess_recursively |

角色清单描述必需责任，实例化可以根据用户范围和证据选择合法不同的拓扑；同一当前节点可承担相关角色，但已经实例化为真实组成节点后不可为省任务而合并/省略。若仍无法有界完成则继续分解。未授权排除facts不能让模式“全部覆盖”；必要时明确范围修订并重新确认。

每个角色先继承自己的定义与适用条件，创建新work occurrence；不得因为空records就新建同义共享类型。根业务采用project-review定义。只读规范可被rules/structure/reuse同时引用，resource owner只管理真实写入对象。

## 场景与组合义务

modeling：固定角色职责、接口、覆盖与直接seed，孩子再生成自己的孙节点；父不等待未来后代才能交付。projection：真实子审查报告完成后父执行跨域遗漏/矛盾检查。verification：新Agent复核同一固定报告闭包。共享模式可被多树采用，但不复制task/确认/run。

## 正例与反例

正例：facts角色按密码/文件系统继续拆分，每个子集合范围可复核，根覆盖账本完整。反例：rules说facts归tests，tests又说“以后采用时核验”，则CP_COVER失败。反例：孩子仅因已标leaf就禁止孙节点，CP_RECURSE失败。已有节点计数不是验收oracle。

递归/复用/覆盖规则案例分别为K01/K07/K09/K11/K12；模式使用自己的CP套件，实际根节点仍采用project-review定义及其套件，不复用任何actual。共享组合最后绑定确切孩子版本时重新固定发布payload，早期角色确认不批准未来补写字节。

## 可复用正反例与三场景

[test contract](../../../tests/audit-contracts/project-review-composition/suite.md)给出三个scene的具名正确/错误样本、判定和返工；案例是固定设计，真实任务必须核对适用条件、绑定工具并记录自己的运行。无论复用本定义还是扩展，均不能省略当前节点的完整PDCA。
