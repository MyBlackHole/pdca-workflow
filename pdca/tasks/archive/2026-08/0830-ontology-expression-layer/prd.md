# T0415 PRD：本体下沉到任务表达层（创建/拆分/计划/文档锚定本体）

- 任务 ID：T0415
- 父任务 / 依赖：T0414（本体全流程闭环 + 硬门禁，已完成）
- 场景类型：development

## 背景与问题

对 PDCA 工作流的审查（对话）确认：本体已牢牢扎根于**流程引擎**（`pdca_context.py` 驱动各阶段/转换/门禁）与**证据闭环**（T0414 使 `register-evidence`/`verdict` 锚定到 `pdca-evidence`/`pdca-verdict` 子类型），但尚未下沉到**任务表达层**。四处缺口：

1. **任务创建表达盲区**：`scripts/task_identity.py` 创建任务时完全不引用 ontology；`task.json` 仅用 `meta.ontology_fragment`（字符串路径）+ `meta.ontology_exempt`（布尔）表达本体，任务类型（`scenario_type`）与本体节点类型（concept/entity/pattern/principle）之间无结构化映射；`ontology-ready` 只校验"路径存在 + `pdca.asset/v1` 结构合法"，不校验片段与任务领域真实相关。
2. **任务拆分本体无感知**：`skills/to-tickets/SKILL.md` 拆 PRD 为子任务时零 ontology 引用；`compute-frontier.py` 只验依赖 DAG，不验本体。可能产生与既有 `ontology` 概念重复、或与本体分类法不对齐的子任务。
3. **计划↔本体缺引用**：`prd.md` 验收标准未要求映射到具体本体节点；Plan 阶段用 `pdca_context.py` 取流程指引，却不把 AC 回链到 ontology 概念。
4. **文档漂移**：`skills/register-evidence/SKILL.md` 未同步 T0414 的证据锚定逻辑（`evidence_type_ref` / `pdca-evidence` 子类型）。

目标：把本体从"流程引擎/证据层"进一步下沉为**任务全生命周期的表达事实源**——创建、拆分、计划、文档四处均显式消费/锚定本体。

## 设计概览

### Part 1 任务创建本体感知（task_identity.py）
- `task_identity.py` 在 `create` 时接受可选的 `--ontology-fragment <path>` 透传到 `meta.ontology_fragment`（沿用既有字段，不新增 schema 字段），并新增轻量校验：若 `--ontology-fragment` 提供，须指向存在的本体目录且非空；若未提供且 `--scenario-type` 非 PDCA 元本体自举类，打印提示建议设置片段（不强制，保持顾问式）。
- 新增 `--ontology-type <concept|entity|pattern|principle|...>`（可选）：写入 `meta.ontology_node_type`，显式声明本任务产出的主体节点类型，使"任务类型 ↔ 本体节点类型"成为结构化关系，供后续拆分/计划引用。
- 不改动既有 ID/record 分配逻辑与"不手工派生 ID"约束。

### Part 2 任务拆分本体感知（to-tickets）
- `to-tickets` 拆解前新增一步：扫描 `ontology/` 已存在的 `concept/entity/pattern/principle` 节点 id，检测 PRD 章节标题/子任务 slug 是否与既有节点**重名**；重名时提示"已有本体节点 X，建议复用而非新建任务"或要求 slug 显式区分。
- 拆解时若父任务 `meta.ontology_fragment` 或 `meta.ontology_node_type` 存在，将值**继承**到子任务（子任务继承父的领域片段与节点类型），保证拆分沿本体边界对齐。
- `compute-frontier.py` 维持只验 DAG（本体一致性以提示形式给出，不阻断拆解）。

### Part 3 计划↔本体（PRD 模板 + Plan 阶段）
- `prd.md` 模板新增可选小节 `## 关联本体节点`，列出本任务直接消费/产出/对齐的本体节点 id 列表（一行一个 `ontology:...`）。
- `flow-plan/SKILL.md` 在 PRD 终稿步骤提示：若 `meta.ontology_fragment` 非空，须在该小节登记相关节点；Do 阶段 `flow-do` 本体消费可据此回链。
- 仅为可选登记，不强制，避免吞吐损失（YAGNI）。

### Part 4 文档同步（register-evidence SKILL）
- `skills/register-evidence/SKILL.md` 补充 T0414 的锚定说明：`--kind` 须为 `pdca-evidence` 子类型短名（命中写 `evidence_type_ref`），未知 kind 报错；既有支持型 kind（document/adr/script…）保留。与 `scripts/register-evidence.py` 实现保持一致。

## 验收条件（AC）

- [ ] AC-1（创建表达）：`task_identity.py` 支持透传 `--ontology-fragment` 与新增可选 `--ontology-node-type`（写入 `meta.ontology_node_type`）；片段存在性轻校验；不破坏既有 ID 分配；新增测试覆盖透传与校验。
- [ ] AC-2（拆分感知）：`to-tickets` 拆解前检测与既有 ontology 节点重名并提示；子任务继承父 `ontology_fragment`/`ontology_node_type`（若父有）；`compute-frontier` 行为不变；新增测试覆盖重名提示与继承。
- [ ] AC-3（计划引用）：`prd.md` 模板含 `## 关联本体节点` 小节；`flow-plan/SKILL.md` 提示登记；现有 PRD/任务不受影响；新增测试或文档自检覆盖模板小节存在。
- [ ] AC-4（文档同步）：`skills/register-evidence/SKILL.md` 同步 T0414 证据锚定说明，与实现一致；新增/更新文档自检或人工复核通过。

## 验收标准

- [ ] AC-1（创建表达）：`task_identity.py` 支持透传 `--ontology-fragment` 与新增可选 `--ontology-node-type`（写入 `meta.ontology_node_type`）；片段存在性轻校验；不破坏既有 ID 分配；新增测试覆盖透传与校验。
- [ ] AC-2（拆分感知）：`to-tickets` 拆解前检测与既有 ontology 节点重名并提示；子任务继承父 `ontology_fragment`/`ontology_node_type`（若父有）；`compute-frontier` 行为不变；新增测试覆盖重名提示与继承。
- [ ] AC-3（计划引用）：`prd.md` 模板含 `## 关联本体节点` 小节；`flow-plan/SKILL.md` 提示登记；现有 PRD/任务不受影响；新增测试或文档自检覆盖模板小节存在。
- [ ] AC-4（文档同步）：`skills/register-evidence/SKILL.md` 同步 T0414 证据锚定说明，与实现一致；新增/更新文档自检或人工复核通过。

## 非目标（范围边界）

- 不把"任务类型 ↔ 本体节点类型"做成强制校验门禁（保持顾问式，避免 YAGNI 与吞吐损失）。
- 不改动 `pdca_context.py`、转换合法性、证据/结论锚定（T0414 已完成）。
- 不要求既有历史任务回填 `ontology_node_type` 或 PRD 关联小节。

## 风险与缓解

- **破坏既有 task_identity 调用**：所有新增参数均可选，默认行为与现有一致；测试覆盖默认路径。
- **to-tickets 重名误报**：仅作提示不改变拆解产出，可显式忽略。
- **schema 兼容性**：`ontology_node_type` 作为 `meta` 新增可选字段须同步 `schemas/task.schema.json`，保持 `additionalProperties` 合规。
