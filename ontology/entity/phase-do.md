---
schema: pdca.asset/v1
id: ontology:entity/phase-do
type: entity
layer: Knowledge
summary: PDCA do 阶段
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-do

PDCA 的执行阶段：按 PRD 验收标准实现，并登记可复核证据。

- **目的**：以最小可逆变更产出满足 AC 的增量，保留 digest 可复核证据。
- **进入条件**：`meta.phase=do`、PRD 含验收标准、`ontology-ready` 门禁通过（development/bugfix 须 `meta.ontology_fragment` 合法，或 `ontology_exempt=true`）。
- **关键活动**：按 `meta.scenario_type` 路由到路径 A–F → 测试优先实现 → 变更后运行 `scripts/ontology_graph.py` 孤岛自检（若涉及本体）→ 双轴代码审查 → 登记 evidence → 生成并登记 `convergence-map` → 提交（如有变更）。
- **退出**：`meta.phase` → `check`，且 evidence 与收敛映射齐备。
- **对应流程**：`flows/flow-do/SKILL.md`。

