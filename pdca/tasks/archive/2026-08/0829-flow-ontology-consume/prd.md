# PRD — T0408 让 Do/Check/Act 流程主动消费本体

## 背景
T0405 把本体接入 PDCA（schema 字段 + ontology-ready 关卡 + flow-plan 声明要求），T0406/T0407 落地使用指南与图谱工具。但审计发现：仅 `flow-plan/SKILL.md:38` 提及本体，`flow-do/check/act` 完全未消费本体——任务在 plan 声明片段后，执行与检查阶段不再对照本体。本任务补齐该缺口，使执行层真正以本体为参照。

## 目标
在 `flows/flow-do/SKILL.md`、`flows/flow-check/SKILL.md`、`flows/flow-act/SKILL.md` 注入"对照 `meta.ontology_fragment` 与 ontology 图谱"的主动步骤；保持与 `flow-plan` 术语一致（`pdca.asset/v1`、`relations`、`ontology-ready`）。

## 范围
- 仅修改三个 flow SKILL 的 Markdown 步骤文本与少量通用小节；不改动脚本、schema、校验器。
- **不**新增 CI 硬失败门禁（该选项已明确排除）。
- 同步更新 `docs/ONTOLOGY_GUIDE.md` 说明三流程现已消费本体，避免文档漂移。

## 非目标
- 不强化 `ontology-ready` 关卡本身（使用级约束属另一排除项）。
- 不新增自动 hook。

## 验收标准
- [ ] AC-1：`flow-do/SKILL.md` 新增"通用：本体消费（Do 阶段）"小节，要求实现前/中对照 `meta.ontology_fragment`：复用既有节点、新增概念以 `pdca.asset/v1` frontmatter + `relations` 落盘到 `ontology/` 对应目录、运行 `scripts/ontology_graph.py` 确认不产生孤岛；`ontology_exempt=true` 或 `ontology_fragment` 为空时跳过。
- [ ] AC-2：`flow-check/SKILL.md` 在 Ch1（回顾实验）与 Ch2（Grill）增加本体对照：development/bugfix 若 `ontology_fragment` 存在，须确认 `ontology-validate` 通过且本体变更已登记证据；Grill 增加"结论是否可被既有 ontology 节点/relations 支撑"追问。
- [ ] AC-3：`flow-act/SKILL.md` 在 Ac2（知识沉淀）与 Ac4（架构改进）增加本体对齐：知识沉淀优先关联既有 ontology 节点而非孤立条目；架构改进若发现本体缺口（缺失节点/关系）则创建补强任务。
- [ ] AC-4：编辑后运行 `python3 scripts/resolve-ai-friendliness-route.py --verify-document`，文档锚点自检通过（无回归/无断裂锚点）。
- [ ] AC-5：`docs/ONTOLOGY_GUIDE.md` 增加"流程如何消费本体"章节，覆盖 plan/do/check/act 各自的消费点，与 flow 文本一致。

## 风险与缓解
- 风险：flow 文本与实际 agent 行为脱节（agent 可能忽略新增步骤）。
  缓解：步骤措辞为可执行指令，并在 `docs/ONTOLOGY_GUIDE.md` 显式列出，作为 agent 可读的权威说明；未来可借 T0406 排除项（CI 守护）进一步固化。
- 风险：过度约束导致普通任务负担。
  缓解：所有步骤以 `ontology_fragment` 存在为前提，空片段/`ontology_exempt` 直接跳过。
