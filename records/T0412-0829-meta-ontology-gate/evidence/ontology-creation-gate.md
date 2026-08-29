---
schema: pdca.asset/v1
id: ontology:concept/ontology-creation-gate
type: concept
layer: Knowledge
summary: 本体创建门禁——新本体资产写入前的强制校验点，其权威依据来自本 meta-ontology 的规则节点
status: active
relations:
  specializes:
  - ontology:concept/meta-ontology
  relates_to:
  - ontology:concept/ontology-validate
  - ontology:concept/ontology-rule-type-controlled
  - ontology:concept/ontology-rule-non-dangling
  - ontology:concept/ontology-rule-acyclic
  - ontology:concept/ontology-rule-attr-testable
  - ontology:concept/ontology-rule-richness
  - ontology:concept/ontology-rule-guides-range
---
# ontology-creation-gate

本体创建门禁：新 `ontology/<type>/<slug>.md` 资产写入前/后的强制校验点。

- **权威依据（关键）**：本门禁不是由脚本自由定义的，而是由本 meta-ontology 承载——它**依据**（`relates_to`）下列规则节点，并**由**（`configured_by`）`ontology-validate` 执行：
  - `ontology-rule-type-controlled`（AC-1）
  - `ontology-rule-non-dangling`（AC-2）
  - `ontology-rule-acyclic`（AC-3）
  - `ontology-rule-attr-testable`（AC-4）
  - `ontology-rule-richness`（AC-5）
  - `ontology-rule-guides-range`（AC-6）
- **人工入口**：`skills/ontology-check` 是本门禁的人工/流程入口；其 AC 清单即上述规则节点的镜像。
- **自动执行者**：`scripts/ontology-validate.py`（`ontology-validate`）。
- **受检对象**：`ontology-asset`。
