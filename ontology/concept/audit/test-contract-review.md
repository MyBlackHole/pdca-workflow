---
schema: pdca.asset/v2
id: ontology:concept/audit/test-contract-review
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.1
summary: 任务单元测试审查：反例、判定器与返工覆盖
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
- id: TC_RESOLVE
  required: true
  rule: case在本node/suite/revision内唯一可解析，输入/expected/oracle及必要观测完整，not_defined不得当not_run。
- id: TC_NEGATIVE
  required: true
  rule: 实际运行固定正确和错误样本；没有出现违例不算已拒绝错误样本。
- id: TC_ORACLE
  required: true
  rule: always-pass/always-fail/关键词误报等错误判定器应被识别；真实判定依据独立且与实体约束一致。
- id: TC_REGRESSION
  required: true
  rule: 失败不可覆盖，修复版本须跑全部必需本地回归及对应组合/独立复核；旧PASS不拼接新版本。
test_contract_ref: ../../../tests/audit-contracts/test-contract-review/suite.md
---

# 任务单元测试审查：反例、判定器与返工覆盖

本节点是可跨工作复用的**规定性实体定义**；采用者绑定具体对象、输入和版本，另建自己的完整PDCA与Agent。本文没有当前work/task/用户会话或实际PASS；本次仓库文件交付不伪称运行时共享发布。

## 必需约束

| ID | 规则 |
|---|---|
| TC_RESOLVE | case在本node/suite/revision内唯一可解析，输入/expected/oracle及必要观测完整，not_defined不得当not_run。 |
| TC_NEGATIVE | 实际运行固定正确和错误样本；没有出现违例不算已拒绝错误样本。 |
| TC_ORACLE | always-pass/always-fail/关键词误报等错误判定器应被识别；真实判定依据独立且与实体约束一致。 |
| TC_REGRESSION | 失败不可覆盖，修复版本须跑全部必需本地回归及对应组合/独立复核；旧PASS不拼接新版本。 |

## 输入输出

输入：实体约束、套件/case/fixture/oracle、实际run/产物版本、失败与返工记录。输出：约束覆盖矩阵、未定义/未运行/运行失败/环境错误清单，误报与漏报控制结果，版本有效性和必需回归缺口。suite文件存在不代表测试正确。

## 两层判定

错误候选违反实体应被判fail；审查器成功发现该错误时其自身对应案例可pass。实际输入错误样本并保存actual，不能在正确草稿上写“无错误→反例通过”。同理不能用始终拒绝的检查器把所有负例变绿；必须提供符合约束但包含“不得声称孩子已实现”等否定文本的正例。

## 分解边界

可按suite完整性/判定依据/观测能力/返工版本拆分；父保留跨场景映射和总覆盖。与资料事实审查共享只读定义合法，测试组不应自称独占所有oracle规则。自定义测试绑定可以用人工或AI，但应有固定输入和具体判断、证据；结构化参考模型不证明任意文本判读能力。

modeling设计审查方法及固定样本；projection对实际项目suite/run审查；verification独立复核发现和错误检查器识别结果。缺必要原始观测时记录unknown，而非补填实际运行。

## 可复用正反例与三场景

[test contract](../../../tests/audit-contracts/test-contract-review/suite.md)给出三个scene的具名正确/错误样本、判定和返工；案例是固定设计，真实任务必须核对适用条件、绑定工具并记录自己的运行。无论复用本定义还是扩展，均不能省略当前节点的完整PDCA。

## 从测试记录提取事实

除既有结构套件外，采用[真实材料回归](../../../tests/records-regression/README.md)中相关原文/版本样本，并按CASE-01作当前绑定。逐项比较suite计划、实际subject/变体差异、oracle、checker、run与交付版本，验证负例到底击穿什么约束。

重点拒绝：删约束行冒充旧PASS错配测试；oracle未删除却声称验证缺oracle；subject内直接给出本例答案；只保留最终PASS；/tmp原证据已清除；已发现根必需反例缺失却没有阻断issue。报告须列原文位置、影响范围与unknown，不能只输出facts=true。
