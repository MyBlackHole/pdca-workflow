---
schema: pdca.asset/v2
id: ontology:concept/pdca-acceptance-criterion
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 验收条件与判断层级
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-verdict
---

# 验收条件与判断层级

每项验收条件至少包含稳定 `id`、期望、必须性、验证方法、产物/规则来源与失败判据。通过条件应在 Plan 中明确，不能在看到结果后倒推。

区分三个层级：结构检查验证字段/引用是否存在；行为检查验证真实动作及结果；授权检查验证真实用户/宿主授权。结构通过不能替代行为发生，模型描述不能替代授权。

结果采用 `pass`、`fail`、`unknown`、`not_run`，每项写理由。pass 必须指向真实、与当前基线相关的证据；unknown/not_run 不是 pass。测试全部被跳过、空证据集、只检查自身文字时不得宣布业务通过。

具体字段见任务模板；最终聚合规则由 `pdca-verdict` 定义。

## 任务单元测试绑定

每条必须AC关联NODE-01约束、TEST-01 suite与CASE-01案例、真实run及版本。模板、文字正反例和结构检查不能替代行为测试；对error/blocked聚合unknown，not_run仍未运行。内部组合和根节点同样有自己的必需案例。
