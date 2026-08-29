# ADR-0034: 以 meta-ontology 承载本体创建门禁的权威依据

日期: 2026-08-29
状态: Accepted

## 背景

T0411 后回顾"本体创建是否有规范门禁"时指出：本工作流确实存在门禁（`skills/ontology-check` + `scripts/ontology-validate.py` 的 AC-1~AC-6），但这些规则只存在于 `ontology/README.md` 的散文、skill 的步骤与脚本的硬编码逻辑中——**门禁的权威依据是文档/脚本，而非本体自身**。这导致"为什么这些规则是门禁"无法从本体内部得到回答，且规则变更缺乏本体级的可追溯性。

用户提出：应"建本体的本体来给本体创建提供门禁的权威依据"，即把门禁及其规则建模为一套 meta-ontology（本体的本体）节点。经范围确认采用 **A（权威依据型）**：建模节点并用 `relations` 表达权威链，使门禁依据本体；`ontology-validate.py` 行为不变（不改为运行时读取规则，属 B 方案留待后续）。

## 决策

1. **新增 meta-ontology 节点（均 `type: concept`，`specializes: ontology:concept/meta-ontology` 或 `ontology:concept/ontology-rule`）**：
   - `ontology:concept/meta-ontology`：本体的本体根，定义其目的为"使门禁权威来自本体"。
   - `ontology:concept/ontology-asset`：本体资产（受门禁约束的对象）。
   - `ontology:concept/ontology-creation-gate`：本体创建门禁。
   - `ontology:concept/ontology-validate`：校验器（对应 `scripts/ontology-validate.py`）。
   - `ontology:concept/ontology-rule`：规则类节点。
   - 六条规则实例：`ontology-rule-type-controlled`(AC-1)、`ontology-rule-non-dangling`(AC-2)、`ontology-rule-acyclic`(AC-3)、`ontology-rule-attr-testable`(AC-4)、`ontology-rule-richness`(AC-5)、`ontology-rule-guides-range`(AC-6)。
2. **权威链表达（仅用受控关系键 `specializes`/`relates_to`，且全部单向指向根以避免环）**：
   - `ontology-creation-gate` `relates_to` `ontology-validate` 与六条规则节点（门禁由校验器执行、依据规则）。
   - 各规则节点 `specializes` `ontology-rule` → `ontology-rule` `specializes` `meta-ontology`。
   - `ontology-asset` `specializes` `meta-ontology` 且 `relates_to` `ontology-creation-gate`。
   - `meta-ontology` 作为根**不向外指**，所有边单向汇入根，确保 `ontology-validate` 的 AC-3（无环）通过、`ontology_graph` 无孤岛。
3. **门禁权威上移**：`ontology/README.md` §9 与 `skills/ontology-check` 改为声明——门禁由 `ontology-creation-gate` 承载、规则即 `ontology-rule-*` 节点、执行者为 `ontology-validate`。修改规则须先动对应 `ontology-rule-*` 节点。
4. **范围边界（本 ADR 不含 B 方案）**：`ontology-validate.py` 仍按其现有硬编码 AC-1~AC-6 执行，不改为运行时读取 `ontology-rule-*` 节点（避免自举/循环依赖，且 validator 自身须先过校验的鸡生蛋问题）。若未来需要"规则本体驱动校验器"，另行立任务。

## 影响

- 本体创建门禁的权威依据从"文档/脚本"变为"本体节点"，可在图谱中追溯"门禁→规则→执行者"关系。
- `ontology-check` 与 README 的 AC 清单成为 `ontology-rule-*` 节点的镜像，二者应保持同步。
- 新增 12 个 meta-ontology 节点，已通过 `ontology-validate`（无环、无孤岛、无空悬）。
- 风险：若 `ontology-rule-*` 节点与脚本实际 AC 实现漂移，需在评审中人工对齐（B 方案的"validator 读规则"可从根本上消除此漂移，但代价是自举复杂度）。
- 衔接 T0411/T0412：本 ADR 是 T0412 的落地授权。
