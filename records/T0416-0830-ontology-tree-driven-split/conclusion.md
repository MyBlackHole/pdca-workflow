---
schema: pdca.asset/v1
id: T0416-0830-ontology-tree-driven-split
phase: check
source_ids: [pytest-t0416, cli-demo-t0416, convergence-map]
---

# T0416 结论：本体关系树驱动任务拆分（to-tickets WBS 生成）

## 上下文

T0415 让 `to-tickets` 具备了本体重名检查与 `ontology_fragment`/`ontology_node_type` 字段继承，但拆分逻辑仍由 PRD 章节**人工划分**，未兑现 `ontology/README.md` §1 承诺的"specializes/composed_of 关系树自底向上驱动 WBS 拆分"。本任务新增 `scripts/ontology_tree_split.py`，使本体关系树真正驱动子任务边界与 `ontology_node_type` 自动推导。

## 假设与结果

- 假设：在 PRD 显式声明"章节→节点"拆分映射后，据此结合本体关系树可自底向上生成 WBS 候选，且**仅输出候选不自动落盘**（顾问式）。
- 结果：脚本解析关系树与映射，输出候选（含 `ontology_node_type` 与依赖边）；映射节点不存在、关系图成环、空映射均抛出明确错误且不生成错误骨架。

## 分析

- **AC-1** ✅ `ontology_tree_split.py` 读取本体目录构建 `specializes`/`composed_of` 图，解析 PRD 拆分映射，输出候选子任务（含 `ontology_node_type` 与依赖边）（pytest-t0416 / test_generate_builds_wbs_with_node_type_and_deps）
- **AC-2** ✅ 映射节点不存在、`composed_of`/`specializes` 成环、空映射均抛出明确 `ValueError` 且不生成错误骨架（pytest-t0416 / test_missing_node_raises, test_cycle_raises, test_empty_map_raises）
- **AC-3** ✅ `to-tickets` 在声明 `## 拆分映射` 时调用 `ontology_tree_split` 生成候选（不自动落盘）；未声明则原行为不变；SKILL 文档已同步调用说明（pytest-t0416 / test_to_tickets_skill_mentions_tree_split, cli-demo-t0416）
- **AC-4** ✅ `SPEC.md` 含 `## 拆分映射` 小节、`flow-plan` P4 提示；新增两套测试覆盖解析/校验/生成（pytest-t0416 / test_spec_template_has_split_map_section, test_to_tickets_skill_mentions_tree_split）

收敛校验：`validate-convergence` 返回 `valid: true`，convergence-map 已锚定 `ontology:entity/evidence-convergence-map`。

## 适用边界

- 拆分映射需作者**显式声明**（章节↔节点），工具不猜测对齐，避免误对齐。
- 保持顾问式：仅输出候选，落盘仍走 `task_identity` 人工确认，未改变"P6 前禁止调度"约束。
- 不改 `compute-frontier.py` DAG 语义（依赖边仍由其校验）。

## 下一轮建议

- 可进一步增强：从"显式映射"演进为"PRD 章节自动对齐本体节点"（需对齐规则/LLM，风险更高），作为后续独立任务。
- 与 T0415 字段继承协同：候选子任务的 `ontology_node_type` 已由关系树自动推导，无需人工传参。

## Verdict（建议，待用户确认固化）

- 建议 `outcome: confirmed`：四处实现均落地，测试覆盖解析/校验/集成，AC-1~AC-4 全 ✅。
- 此区块由用户 `check_confirmation` 确认后，由门禁写入 `task.json` `meta.verdict`（outcome/reason/verdict_id/at），AI 不代签。
