---
schema: pdca.asset/v1
id: ontology:entity/phase-plan
type: entity
layer: Knowledge
summary: PDCA plan 阶段
status: active
relations:
  specializes:
  - ontology:concept/pdca-phase
---
# phase-plan

PDCA 的第一阶段：把模糊输入转为结构化、可执行的任务合约。

- **目的**：澄清目标与范围，确立可验证的验收标准，分解工作。
- **进入条件**：任务已创建且 `meta.phase=plan`，无未解决的阻塞分诊问题。
- **关键活动**：triage 分诊 → Grill 追问对齐 → 方向确认 → 写 PRD（含 `## 验收标准` 与 `- [ ] AC-x:` 复选框）→ 拆解 `implement.jsonl` → 取得 `final_confirmation`。
- **退出**：PRD 经用户 `final_confirmation`，`meta.phase` → `do`。
- **对应流程**：`flows/flow-plan/SKILL.md`。

