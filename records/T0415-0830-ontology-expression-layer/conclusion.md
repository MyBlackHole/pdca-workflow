---
schema: pdca.asset/v1
id: T0415-0830-ontology-expression-layer
phase: check
source_ids: [ac1-identity, ac1-tests, ac2-clash, ac3-prd, ac4-register, convergence-map]
---

# T0415 结论：本体下沉到任务表达层

## 上下文

审查确认本体已扎根于流程引擎（`pdca_context.py`）与证据闭环（T0414），但未下沉到任务表达层。T0415 在 `task_identity.py` 创建、`to-tickets` 拆分、`prd.md` 模板、`register-evidence` 文档四处补上本体感知，使本体成为任务全生命周期的表达事实源。

## 假设与结果

- 假设：在任务创建/拆分/计划/文档四处显式消费或锚定本体，可消除"任务表达盲区"且不引入强门禁负担。
- 结果：四处均加入顾问式本体感知（可选字段 + 提示），既有任务不受影响，新增单测与文档自检覆盖。

## 分析

- **AC-1** ✅ `task_identity.py` 支持透传 `--ontology-fragment` 与新增可选 `--ontology-node-type`（写入 `meta.ontology_node_type`）；片段存在性轻校验；自动继承父任务片段/节点类型；新增单测覆盖（ac1-identity / ac1-tests）
- **AC-2** ✅ `to-tickets` 拆解前经 `ontology-clash-check.py` 检测与既有本体节点重名并提示；子任务继承父 `ontology_fragment`/`ontology_node_type`；`compute-frontier` 行为不变；新增 `test_ontology_clash.py` 覆盖（ac2-clash / ac1-tests）
- **AC-3** ✅ `templates/to-spec/SPEC.md` 新增 `## 关联本体节点` 小节；`flow-plan/SKILL.md` P1 提示登记；新增 `test_prd_template_ontology_section.py` 自检模板小节存在（ac3-prd）
- **AC-4** ✅ `skills/register-evidence/SKILL.md` 同步 T0414 证据锚定（`--kind` 须为 `pdca-evidence` 子类型短名、命中写 `evidence_type_ref`、未知报错）；与 `scripts/register-evidence.py` 实现一致（ac4-register）

收敛校验：`validate-convergence` 返回 `valid: true`，convergence-map 已锚定 `ontology:entity/evidence-convergence-map`。

## 适用边界

- 本体感知均为顾问式（可选字段 + 提示），不构成强门禁，与 YAGNI 一致；历史任务无需回填。
- 关系树驱动 WBS 拆分（README §1 宣称）**未**在本任务实现，仅做到重名提示 + 字段继承，属后续独立任务。

## 下一轮建议

- 缺口 B：实现"specializes/composed_of 关系树驱动 to-tickets 拆分"，兑现 README §1 的承诺。
- 缺口 A 深化：让 `ontology:concept/pdca-task` 元概念节点真正驱动任务表达校验（当前未被消费）。

## Verdict（建议，待用户确认固化）

- 建议 `outcome: confirmed`：四处本体感知均落地且有测试/文档自检支撑，AC-1~AC-4 全 ✅。
- 此区块由用户 `check_confirmation` 确认后，由门禁写入 `task.json` `meta.verdict`（outcome/reason/verdict_id/at），AI 不代签。
