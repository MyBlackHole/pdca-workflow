---
schema: pdca.asset/v1
id: ontology:process/flow-act
type: process
layer: Knowledge
status: active
summary: Act 阶段流程实体：知识投影、自我优化闭环、ID 不变量、时间线一致性与运行时协调
relations:
  specializes:
  - ontology:concept/process
  part_of:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:entity/phase-act
  - ontology:concept/pdca-continuous-improvement
  - ontology:concept/knowledge-provenance
  - ontology:concept/self-optimization-loop
  - ontology:concept/task-record-identity
  - ontology:concept/timeline-integrity-gate
  - ontology:concept/pdca-provable-skill-increments
---

# PDCA Act 流程（flow-act）

Act 阶段处置知识、完成自我优化闭环，是 PDCA 周期中"学习并固化"的环节，之后进入 archive。

## 阶段步骤（权威描述）

1. **知识处置**：显式投影 `ontology/domain/<topic>-<slug>.md`，记来源 record/摘要/理由/连续 revision；相同内容与理由重试须幂等。`research` 场景须按 `ontology:domain/skill-research` 的“本体沉淀决策”做分流判定与记录（`conclusion.md##本体沉淀` + `meta.disposition` 显式关键词）。
2. **disposition 与 journal**：写入 `meta.disposition`（`research` 须含 `ontology:` 或 `records-only` 决策词），更新 journal。
3. **门禁**：通过 `pdca-gate`、archive 本体自检（ontology-validate + 孤岛检查）与 `check-research-ontology-settlement`（research 场景）后，经 `transition-phase.py` 进入 archive。

## 关键决策（已迁移自外部知识）

- **知识来源封存**（详 `ontology:concept/knowledge-provenance`）：`records/<id>/evidence/` 存内容寻址原始事实，`experience.md` 存情境化经验，进入 Act 前同时封存两者摘要；`ontology/domain/` 是跨任务演进知识而非实验副本；默认检索优先 ontology/domain/skill，需解释经 manifest 来源边回 experience，需核验只展开 Evidence 摘要。
- **自我优化闭环**（详 `ontology:concept/self-optimization-loop` 与 `ontology:concept/pdca-provable-skill-increments`）：完整闭环为 记录→分析→决策→受控实施→效果验证；改进候选仍走正常 Plan/Grill/final confirmation，不得由审计器直接改权威流程；效果是后续周期判定而非候选自证；可证明优先——每个机制配硬指标与测试断言。
- **ID 不变量与撞车重分配**（详 `ontology:concept/task-record-identity`）：`task.id` 分配须处仓库级临界区；创建入口统一（triage/to-tickets/Act follow-up 复用 `task_identity.py create`）；record identity 创建时生成且不可变；occurrence 目录 identity 须等于 payload `record_id`；历史归并仅由 immutable relocation/alias receipt 表达。撞车重分配按"被引用为主干/格式规范/创建早"判定主流方，引用归属按 slug 特征词区分任务树，先引用扫描后重命名，flow-events 内 `record_id`/`task_id` 同步。
- **时间线一致性**（详 `ontology:concept/timeline-integrity-gate`）：`final_confirmation.at` 取自执行时刻不可编造；`states` 须单调 `created≤plan≤do≤check≤act≤archive`；阶段推进仅经 `transition-phase.py`，其 `receipt.at` 须等于 `states.<target>`；先干后补确认属违规；plan 时间戳由转换自动补写（`clarifications.jsonl` 的 confirmation.at 优先）。
- **运行时协调**（详 `ontology:concept/runtime-transition-coordinator`）：自动阶段推进须是基于 Evidence 快照的单阶段 CAS，非观察事件后递归调用；协调锁同时覆盖事实写入者与状态写入者；重试成功须绑定 Scenario digest 的 transition receipt；Check→Act 不能仅凭 Validator pass 自动宣称"已学习"。

## 来源

- `（原知识层）record-knowledge-provenance.md`
- `（原知识层）self-optimization-loop.md`
- `（原知识层）task-record-identity-invariants.md`
- `（原知识层）id-collision-remediation.md`
- `（原知识层）timeline-integrity-gates.md`
- `（原知识层）runtime-transition-coordinator.md`
- `（原知识层）provable-skill-increments.md`
