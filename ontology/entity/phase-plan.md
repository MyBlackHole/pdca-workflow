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

- **科学方法内核**：Plan 是"**提出可证伪的预测/假说与试验设计**"——明确"若做出变更 X，预期在 Do 中观测到结果 Y（以及为何如此）"，连同可观测的指标与对比基线。预测越具体，Check 越能判定（对应经典 PDCA 的"plan a predicted change"）。
- **目的**：澄清目标与范围，确立可验证的验收标准，分解工作。
- **进入条件**：任务已创建且 `meta.phase=plan`，无未解决的阻塞分诊问题。
- **关键活动**：triage 分诊 → Grill 追问对齐 → 方向确认 → 写 PRD（含 `## 验收标准` 与 `- [ ] AC-x:` 复选框）→ 拆解 `implement.jsonl` → 取得 `final_confirmation`。
- **退出**：PRD 经用户 `final_confirmation`，`meta.phase` → `do`。
- **对应流程**：`ontology/process/flow-{plan,do,check,act}.md`。

