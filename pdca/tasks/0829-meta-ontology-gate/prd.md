# T0412 PRD：建 meta-ontology 为本体创建门禁提供权威依据

## 背景
T0411 后用户提问"PDCA 本体是否满足规范、本体创建是否有规范门禁"。结论：本体本身合规，但**门禁的权威依据目前是文档/脚本**——`ontology/README.md` 的散文、`skills/ontology-check` 的步骤、`scripts/ontology-validate.py` 的硬编码 AC-1~AC-6，均非本体节点。用户要求"建本体的本体来给本体创建提供门禁的权威依据"，即把门禁及其规则建模为一套 meta-ontology（本体的本体）节点，使门禁的权威来源从文档上升为本体自身（自描述）。

范围经用户确认为 **A（权威依据型）**：建模节点 + 用 `relations` 表达"门禁 → 依据规则 → 由校验器执行"的权威链；`ontology-check` 与 `README` 改为引用这些节点；`ontology-validate.py` 行为不变（不改成运行时读取规则，B 方案留待后续）。

## 验收标准
- [ ] AC-1 新建 `ontology/concept/meta-ontology.md`（id `ontology:concept/meta-ontology`）：本体的本体根概念，定义其目的为"建模本体资产、创建门禁与校验规则，使门禁权威来自本体"。frontmatter 合规（`pdca.asset/v1`、type=concept、无非法 relations）。
- [ ] AC-2 新建 `ontology-asset.md`、`ontology-creation-gate.md`、`ontology-validate.md`、`ontology-rule.md` 四个概念节点，均 `specializes: ontology:concept/meta-ontology`。
- [ ] AC-3 新建 6 个规则节点 `ontology-rule-type-controlled` / `ontology-rule-non-dangling` / `ontology-rule-acyclic` / `ontology-rule-attr-testable` / `ontology-rule-richness` / `ontology-rule-guides-range`，均 `specializes: ontology:concept/ontology-rule`，正文分别对应 AC-1~AC-6。
- [ ] AC-4 用 `relations` 表达权威链：`ontology-creation-gate` `configured_by: [ontology-validate]` 且 `relates_to: [6 个规则节点]`；`ontology-validate` `relates_to: [ontology-creation-gate]`；`ontology-asset` `relates_to: [ontology-creation-gate]`；各规则节点 `relates_to: [ontology-creation-gate]`。全图无 DANGLING_REF、无环、无孤岛。
- [ ] AC-5 `ontology/README.md` §9 门禁段与 `skills/ontology-check` 增加引用：门禁的权威依据为 `ontology:concept/ontology-creation-gate` 及其规则节点（`ontology-rule-*`）。
- [ ] AC-6 新增 `docs/adr/ADR-0034-meta-ontology-gate.md`（架构级硬决策：以 meta-ontology 承载门禁权威）；`tests/test_meta_ontology.py` 断言上述节点存在且权威链正确；`ontology-validate` 通过、`pytest` 全绿。

## 范围与边界
- 仅新增 meta-ontology 节点 + 文档/指南引用 + ADR + 测试；**不改 `ontology-validate.py` 逻辑**，不实现"validator 读取规则节点"（属 B 方案，另立任务）。
- 不使用非受控关系键触发 DANGLING 校验：仅用 `specializes`/`configured_by`/`relates_to`（均在受控词表内）。
- 不改动既有 `pdca-*` 元本体与 T0411 成果。
