---
schema: pdca.asset/v1
id: ontology:entity/phase-check
type: entity
layer: Knowledge
summary: PDCA check 阶段
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-check

PDCA 的检查阶段：从执行结果到结论的对比分析。

- **目的**：对照 PRD 与证据验证假设，得出可信结论并封存 verdict。
- **进入条件**：`meta.phase=check`，`evidence/manifest.jsonl` 与 exactly one `convergence-map` 齐备，`validate-convergence` 通过。
- **关键活动**：回顾实验（git diff / 证据）→ Grill 追问可靠性（含"结论是否被 ontology 节点/relations 支撑"）→ 验证收敛 → 写 `conclusion.md`（每 AC 行可 grep 到证据 ID）→ 获取用户 verdict（confirmed / rejected / partial）。
- **退出**：`meta.phase` → `act`，verdict 已落 `meta.verdict`。
- **对应流程**：`flows/flow-check/SKILL.md`。

