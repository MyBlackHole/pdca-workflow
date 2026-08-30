# 补齐 PDCA 本体 AI 提效缺口：文档经济学、失效模式、Phase Boundary、Grounding

## 问题陈述

PDCA 本体在流程刚性、证据链完整性、门禁强制执行方面远超 mattpocock/skills。但在**文档经济学、上下文卫生、token 效率**三个直接影响 AI 使用效率的维度上存在可借鉴的显著差距。T0431 已补充 35 个 Matt Pocock 原则概念节点（writing-for-agents、skill mechanics、grilling methodology、domain modeling、triage、to-tickets），但以下核心概念仍未形式化为本体一等节点：

- 锚定词（leading words）— 用预训练词锚定行为，减少 token 消耗
- 指针措辞（pointer wording）— 指针措辞决定触发可靠性
- no-op 模型相对判定 — "是否改变默认行为"是模型相对的
- 失效模式（failure mode）— 技能设计应回溯到它治的失效模式
- Phase Boundary 决策树 — session 内阶段切换的 5 选项决策树
- Grounding 依赖图 — 概念必须 grounding 后才能被后续块依赖

## 解决方案

### P0：文档经济学概念节点（P0）

1. 添加 `ontology:concept/leading-words` 节点：锚定词定义、token 效率规则、testable_signal
2. 添加 `ontology:concept/pointer-wording` 节点：指针措辞原则、弱措辞=方差 bug、testable_signal
3. 添加 `ontology:concept/no-op-judgment` 节点：no-op 模型相对判定、删除策略、testable_signal
4. 更新 `skills/writing-great-skills/SKILL.md` 的 `relations`，引用新节点

### P1：失效模式驱动设计（P1）

5. 添加 `ontology:concept/failure-mode` 节点：四大失效模式枚举、testable_signal
6. 在 `to-tickets` 和 `triage` 技能 frontmatter 中增加 `failure_mode` 可选字段
7. `ontology-validate` 新增 AC-7：技能节点应声明其针对的失效模式

### P2：Phase Boundary 决策树（P2）

8. 添加 `ontology:concept/phase-boundary-decision-tree` 节点：5 选项决策树、testable_signal
9. 更新 `flow-do` 相关文档，集成 Phase Boundary 决策树引用

### P3：Grounding 依赖图（P3）

10. 添加 `ontology:concept/grounding-dependency` 节点：requires/grounds 关系、testable_signal
11. 更新 `knowledge-provenance` 节点，引入 grounding 方法论

## 验收标准

- [ ] AC-1：`ontology:concept/leading-words` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-2：`ontology:concept/pointer-wording` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-3：`ontology:concept/no-op-judgment` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-4：`ontology:concept/failure-mode` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-5：`ontology:concept/phase-boundary-decision-tree` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-6：`ontology:concept/grounding-dependency` 节点存在，frontmatter 合法，`ontology-validate` 通过
- [ ] AC-7：`writing-great-skills` 引用新节点，`ontology-validate` 通过
- [ ] AC-8：`ontology_graph --format summary` 无孤岛节点
- [ ] AC-9：所有新节点有 `attributes` 含 `testable_signal`

## 关联本体节点

```
ontology:concept/leading-words
ontology:concept/pointer-wording
ontology:concept/no-op-judgment
ontology:concept/failure-mode
ontology:concept/phase-boundary-decision-tree
ontology:concept/grounding-dependency
ontology:concept/writing-for-agents
ontology:concept/skill-mechanics
ontology:concept/two-loads
```

## 范围外

- 不修改已有概念节点的语义
- 不引入新的受控类型词汇
- 不修改 `flow-plan`/`flow-check`/`flow-act` 的核心流程

## 依赖

- T0431（已添加 35 个 Matt Pocock 原则概念节点）
- `skills/writing-great-skills/SKILL.md`（已部分引入锚定词/双负载/指针措辞）
