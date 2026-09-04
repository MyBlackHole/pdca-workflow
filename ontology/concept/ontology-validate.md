---
schema: pdca.asset/v1
id: ontology:concept/ontology-validate
type: concept
layer: Knowledge
summary: 本体校验器——执行 ontology-creation-gate 的自动化工具（scripts/ontology-validate.py）
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-validate/1.0.0
relations:
  specializes:
  - ontology:concept/meta-ontology
---
# ontology-validate

本体校验器：执行 `ontology-creation-gate` 门禁的自动化工具，对应 `scripts/ontology-validate.py`。

- **角色**：`ontology-creation-gate` 的自动执行者（`ontology-creation-gate` 通过 `configured_by` 引用本节点）。
- **覆盖规则**：实现 AC-1~AC-6，与 `ontology-rule-*` 规则节点一一对应（当前为脚本硬编码逻辑；将其改为"运行时读取规则节点"属范围 B，留待后续任务）。
- **退出语义**：0 issue 通过；非零 issue 应阻断写入/提交（CI 或 add 知识流程应调用它作为强制门禁）。

## 决策背景（原 ADR-0035：校验器运行时读取 rule_spec）
- 背景：ontology-rule-* 节点曾只是脚本硬编码常量的镜像，改节点不意味改校验行为，存在漂移风险。
- 决策：ontology-validate 启动时加载 6 个 ontology-rule-* 的 rule_spec 作为检查参数唯一来源；节点缺失或非法直接报错退出，不静默回退。
