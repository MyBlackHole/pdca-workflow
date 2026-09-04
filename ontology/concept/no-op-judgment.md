---
schema: pdca.asset/v1
id: ontology:concept/no-op-judgment
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/no-op-judgment/1.0.0
summary: no-op 的模型相对判定：是否改变默认行为取决于模型本身
relations:
  specializes:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有文档中判断某句是否 no-op 的场景
  constraint: 见正文
  testable_signal: 检查文档中是否存在弱词 no-op（如 be thorough）；失败时是否删整句而非删词
---

# No-op 的模型相对判定

"无操作不写"（极简原则 2）的判定是**模型相对**的："这行是否改变默认行为"取决于模型本身，不取决于读者。两人争论一句是否 no-op，实为争论默认行为——用运行文档解决，不用辩论。

## 原则

- 太弱的词是 no-op：`_be thorough_` 当模型本就 thorough-ish → 换更强词（`_relentless_`），不是换技巧
- 失败时删整句，不删词——残句仍花 load 说无用的话
- 用运行文档解决默认行为争议，不用辩论

## 边界

no-op 的判定依赖模型族——不同模型对同一词的默认行为理解不同，需本地验证。