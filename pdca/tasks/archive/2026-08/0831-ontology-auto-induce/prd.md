# 实现本体自动反哺机制（evidence→ontology）

## 背景

当前 PDCA 本体知识体系（T0414）已实现全流程闭环：创建门禁 AC-1~AC-6、证据锚定、结论锚定、archive 自检、CI/hook 门禁。但存在一个结构性缺口——**本体知识的产生与任务产出之间缺乏自动反馈链路**。

依据 `ontology:concept/self-optimization-loop`，完整闭环应为：记录→分析→决策→受控实施→效果验证。当前 `flow-audit` 记录的问题不会自动触发本体补强任务；Act 阶段的知识沉淀依赖人工判断"哪些该进 ontology"；`ontology_induction.py` 仅有 knowledge-draft adapter，无从 evidence/experience 自动反哺的 adapter。

## 问题

1. **`flow-audit` → 本体补强**：流程问题记录（occurrence）积累到阈值后，不会自动创建 `meta.ontology_fragment` 指向待补强目录的本体补强任务（improvement task）。
2. **Act 证据 → 本体更新**：`evidence/manifest.jsonl` 中的 `test-result`、`convergence-map` 等证据不会自动检查是否有关联本体节点需要更新或新建。
3. **`ontology_induction.py` 覆盖不全**：仅实现 `KnowledgeDraftAdapter`，缺少 `EvidenceAdapter` 和 `ExperienceAdapter`。

## 目标

建立从任务产出（evidence/experience/flow-audit）到本体知识的自动反哺机制，使本体自循环完整度从约 70% 提升至 90%+。

## 方案

### F1 — EvidenceAdapter

在 `scripts/ontology_induction.py` 中新增 `EvidenceAdapter`：
- 读取 `evidence/manifest.jsonl` 中的 `evidence_type_ref` 字段
- 根据 `evidence_type_ref` 查找关联的本体节点（`pdca-evidence` 子类型）
- 生成候选本体节点（若目标节点不存在）
- 输出 PR/diff 供人工审查

### F2 — FlowIssue 自动触发

在 `scripts/aggregate-flow-issues.py` 或新增 `scripts/auto-induce-flow-issues.py` 中：
- 读取 flow-audit occurrence 聚合结果
- 当某类问题的 occurrence 数超过阈值（可配置）时，自动创建 improvement candidate
- improvement candidate 经 `create-improvement-candidate.py` 生成为 `phase=plan` 的正式任务，`meta.ontology_fragment` 指向待补强目录

### F3 — Act 阶段自动检查

在 `scripts/ontology_gate.py` 中新增 `auto_induce_evidence` 函数：
- Act 阶段读取 `evidence/manifest.jsonl`
- 对每条 evidence 检查是否存在关联的本体节点
- 若存在缺口，生成 `ontology-clash-check` 提示或自动创建本体补强候选

## 验收标准

- [ ] `EvidenceAdapter` 在 `ontology_induction.py` 中实现，可运行 `python3 scripts/ontology_induction.py --adapter evidence`
- [ ] `auto_induce_flow_issues` 函数可配置阈值并自动创建 improvement candidate
- [ ] `ontology_gate.py` 新增 `auto_induce_evidence` 函数，Act 阶段调用
- [ ] `ontology-validate.py` 通过（AC-1~AC-6）
- [ ] `ontology_graph.py --format summary` `islands: 0`
- [ ] 新增测试断言覆盖 `EvidenceAdapter` 和 `auto_induce_evidence`

## 关联本体节点

```
ontology:concept/self-optimization-loop
ontology:concept/ontology-induction
ontology:concept/pdca-evidence
ontology:entity/evidence-test-result
ontology:entity/evidence-convergence-map
ontology:entity/evidence-review
ontology:concept/ontology-creation-gate
```

## 风险

- 自动创建的本体节点可能不准确，需保留 HITL 审查
- `evidence_type_ref` 与本体节点的映射关系需预先建立
- `flow-audit` 阈值的设定需避免误触发

## 非目标

- 不修改现有 `ontology-validate.py` 的 AC 检查逻辑
- 不修改现有 `flow-audit` 的 occurrence 存储格式
- 不自动修改权威流程（改进候选仍走正常 Plan/Grill/final confirmation）