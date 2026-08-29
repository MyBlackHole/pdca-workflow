---
schema: pdca.asset/v1
id: ontology:concept/pdca-verdict
type: concept
layer: Knowledge
summary: PDCA 结论元概念
status: active
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

