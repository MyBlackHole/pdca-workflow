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

## 决策背景（原 ADR-0033 / 0034 / 0036）
- ADR-0033：采纳 ONTOLOGY_GUIDE 为兼容吸收方案，指南置于 docs/（不放入 ontology/，以免破坏 ontology-validate 扫描）；pdca.asset/v1 frontmatter + relations 仍为唯一事实源。
- ADR-0034：本体创建门禁的权威依据从"文档/脚本"升级为本体节点（meta-ontology / ontology-creation-gate / ontology-rule-*），使门禁可图谱追溯。
- ADR-0036：补齐全流程闭环——证据锚定 pdca-evidence 子类型、结论锚定 pdca-verdict 三态、archive 前跑 ontology-validate + 孤岛检查、提交级 pre-commit/CI 硬门禁。
