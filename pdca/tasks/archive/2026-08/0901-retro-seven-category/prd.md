# 补齐 retro 7分类回顾能力

## 背景

mattpocock/skills HEAD 6654f6b 新增 `skills/in-progress/retro/SKILL.md`（7分类回顾），本地完全缺失（`ontology/concept/retrospective.md` 不存在）。7分类中的 `Information access` 是本地 `self-optimization-loop` 未覆盖的维度，直接补强 Act 阶段的自我优化能力。T0459 复审已将其列为 P1 最优先。

## 目标

新增 `retrospective` 本体能力，使 Act 阶段的回顾从"自由文本"变为"7分类检查表"，并与 `self-optimization-loop` 的5步模型衔接。

## 验收标准

- [ ] AC-1 新增 `ontology/concept/retrospective.md`（`type: concept`，`specializes: pdca-continuous-improvement`，`relates_to: self-optimization-loop`），含7分类定义（Navigation/Automated checks/Coding standards/Global AGENTS.md/Tool economy/No-ops/Information access）与适用边界
- [ ] AC-2 扩展 `ontology/concept/self-optimization-loop.md`，在"最小反馈模型"或新增小节中引用 `retrospective` 的7分类作为 Act 回顾检查清单
- [ ] AC-3 `ontology-validate.py --ontology-dir ontology` 通过且 `ontology_graph --format summary` islands:0
- [ ] AC-4 新增 `ontology/domain/skill-retrospective.md`（`type: domain`，`specializes: pdca-task`，`relates_to: retrospective`），描述 skill 的触发条件与 7 分类候选呈现流程（与远端 SKILL.md 对齐，但不照搬 prompt 措辞）

## 非目标

- 不实现 retro 的自动化扫描脚本（仅本体与 skill 文档）
- 不改动 `implement-spec` 相关内容（另任务观察）

## 关联本体节点

```
ontology:concept/self-optimization-loop
ontology:concept/pdca-continuous-improvement
ontology:concept/retrospective
ontology:domain/skill-retrospective
```

## 风险

- 7分类描述需与远端对齐但不照搬，避免措辞漂移；以本体 `attributes.testable_signal` 约束可验证性
