---
schema: pdca.asset/v2
id: ontology:concept/audit/project-review
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.1
summary: 本体项目审查：固定对象、责任覆盖与证据汇聚
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
- id: PR_TARGET
  required: true
  rule: 保持用户审查目标，固定被审对象/版本，不能变成建设同名系统。
- id: PR_COVERAGE
  required: true
  rule: 必需审查范围有唯一主要交付负责人；允许多个验证参与者，不因scope切分遗漏事实或规则交叉审查。
- id: PR_EVIDENCE
  required: true
  rule: 每项结论可追溯固定原文、方法、覆盖及证据；unknown/not_run不提升为已验证。
- id: PR_AGGREGATE
  required: true
  rule: 根检查跨分片遗漏、矛盾及当前闭包；孩子全通过不代替根整体判断。
test_contract_ref: ../../../tests/audit-contracts/project-review/suite.md
---

# 本体项目审查：固定对象、责任覆盖与证据汇聚

本节点是可跨工作复用的**规定性实体定义**；采用者绑定具体对象、输入和版本，另建自己的完整PDCA与Agent。本文没有当前work/task/用户会话或实际PASS；本次仓库文件交付不伪称运行时共享发布。

## 必需约束

| ID | 规则 |
|---|---|
| PR_TARGET | 保持用户审查目标，固定被审对象/版本，不能变成建设同名系统。 |
| PR_COVERAGE | 必需审查范围有唯一主要交付负责人；允许多个验证参与者，不因scope切分遗漏事实或规则交叉审查。 |
| PR_EVIDENCE | 每项结论可追溯固定原文、方法、覆盖及证据；unknown/not_run不提升为已验证。 |
| PR_AGGREGATE | 根检查跨分片遗漏、矛盾及当前闭包；孩子全通过不代替根整体判断。 |

## 实体、范围与参数

输入：用户目标和明确排除项、subject文件清单/固定版本、协议基线、选择的审查维度和风险。输出：逐项覆盖账本、问题清单（原文、位置、依据、后果、修复与反例）、原始证据索引、分层结论及复核包。目标是审查现有项目，不实施未授权修复，不代签发布，不声称未运行的宿主行为。

固定范围维度包括协议行为规则、结构/类型语义、资料事实、测试/返工有效性、采用与发布机制；用户明确限定范围时记录限制，不自行扩展成全库认证。结构计数不等于语义、事实或宿主验证；每一层分别说明审查覆盖与缺口。

## 组成角色与递归

按[组合模式](../../pattern/audit/project-review-composition.md)实例化职责，不强制一种命名或拓扑。每个必需维度必须有负责人；资料事实量大时继续按领域/实体/固定版本拆分。根保留跨维度的一致性检查，输入为直接孩子固定报告和必要原证据而非所有活动对话。

## 三场景交付

modeling：建立本项目的审查实体/实例、直接子角色、覆盖与三场景测试；不宣称被审项目已通过。projection：实际执行审查（产物可为文档和证据，不必写代码）。verification：独立复核报告的依据、覆盖和错误定位。审查发现被审对象错误时，审查任务自身仍可合格；未完成事实必须保留。

## 组合反例

结构孩子称“资料事实由证据孩子负责”，证据孩子又排除实际事实核验：PR_COVERAGE失败。所有孩子输出PASS但根清单少一个必须文件：PR_AGGREGATE失败。根不能用多加一句总PASS弥补。

## 可复用正反例与三场景

[test contract](../../../tests/audit-contracts/project-review/suite.md)给出三个scene的具名正确/错误样本、判定和返工；案例是固定设计，真实任务必须核对适用条件、绑定工具并记录自己的运行。无论复用本定义还是扩展，均不能省略当前节点的完整PDCA。

## 项目目标与审查运行分开

subject_snapshot是原项目对象；review_run是本次审查执行证据。两者可都审，但分别报告范围、覆盖和缺陷，不能用运行记录合格替代项目适用。AI适用性使用原材料场景验证：缺确认时正确阻断、缺证据不放行、否定句不误报、父缺陷返工、预算内完整覆盖与安全接续。固定文本控制只能证明所列样本，不宣称任意模型都可靠。
