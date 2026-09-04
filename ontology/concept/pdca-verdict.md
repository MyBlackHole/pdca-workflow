---
schema: pdca.asset/v1
id: ontology:concept/pdca-verdict
type: concept
layer: Knowledge
summary: PDCA 结论元概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-verdict/1.0.0
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-verdict

Check 阶段产出的结论判定元概念。

- **取值与含义**：
  - `confirmed`：结论成立，进入 Act 完成知识沉淀与归档。
  - `rejected`：结论不成立，仍进入 Act 做失败处置（提取教训，不沉淀知识）。
  - `partial`：部分成立，进入 Act 沉淀有效部分并创建跟进任务。
- **理由**：rejected / partial 也必须进入 Act，不从 Check 退回 Plan——失败经验同样要被归档与处置。

## 决策背景（原 ADR-0036：结论锚定）
- 决策：新增 verdict-rejected / verdict-partial 与 verdict-confirmed 构成完整三态；check/act/archive 校验 meta.verdict.outcome 映射的 verdict-<outcome> 节点必须存在，缺失则阻断转换。
