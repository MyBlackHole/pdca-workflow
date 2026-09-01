---
schema: pdca.asset/v1
id: ontology:entity/ontology-deep-integration-split
type: entity
layer: Knowledge
status: active
summary: 拆分门禁硬化（本体默认对齐，冲突阻断，关系树驱动拆分为默认路径）
relations:
  specializes:
    - ontology:concept/domain-entity
---

# 拆分门禁硬化

叶子实体1：使本体从顾问式变为默认路径。

- 任务侧：`meta.ontology_fragment` 非空为默认（`ontology_exempt` 需显式理由），PRD 无 `## 拆分映射` 时告警
- 门禁侧：`scripts/ontology-clash-check.py` 阻断保持；`scripts/ontology_tree_split.py` 由可选变为 Plan 默认执行（有 fragment 即跑）
- 继承：`task_identity.py` 已支持 fragment/node_type 自动继承，保持拆分沿本体边界对齐
