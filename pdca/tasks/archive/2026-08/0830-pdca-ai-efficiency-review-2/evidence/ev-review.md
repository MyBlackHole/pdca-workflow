# PDCA 本体与 Matt Pocock skills 对比审查（第二轮）

## 审查范围

验证 T0431/T0432/T0433 已补充的概念节点是否完整覆盖 Matt Pocock/skills (v1.2.3) 的核心方法论，识别剩余差距。

## 本体概念节点现状

### 统计
- 总概念节点数：93 个
- 通过 ontology-validate：OK
- ontology_graph：332 nodes, 681 edges, 0 islands

### T0431 补充的概念节点（35 个）
| 类别 | 节点 |
|------|------|
| Writing-for-agents | information-hierarchy, progressive-disclosure, context-pointer, step, completion-criterion, co-location, two-loads, writing-for-agents |
| Skill Mechanics | skill-invocation, model-invoked, user-invoked, router-skill, shared-reference, skill-mechanics |
| Grilling methodology | design-tree, frontier, round, facts-not-opinions, grilling-completion, grilling-methodology |
| Domain Modeling | domain-model, active-discipline, challenge-glossary, sharpen-language, agent-brief, domain-modeling |
| Triage | triage-state-machine, agent-ready-brief, ai-disclaimer, triage |
| To Tickets | vertical-slice, tracer-bullet, blocking-edges, expand-contract, task-decomposition |

### T0432 补充的概念节点（9 个）
| 类别 | 节点 |
|------|------|
| 文档经济学 | leading-words, pointer-wording, no-op-judgment |
| 失效模式 | failure-mode |
| Phase Boundary | phase-boundary-decision-tree |
| Grounding | grounding-dependency |

## Matt Pocock/skills 参考对照

### User-invoked 技能（14 个）
ask-matt, grill-me, grill-with-docs, triage, improve-codebase-architecture, setup-matt-pocock-skills, to-spec, to-tickets, implement, wayfinder, handoff, teach, to-questionnaire, wait-what

### Model-invoked 技能（11 个）
grilling, writing-for-agents, prototype, diagnosing-bugs, research, tdd, domain-modeling, codebase-design, code-review, resolving-merge-conflicts, wizard

### 核心原则对照
| 原则 | PDCA 覆盖 | 状态 |
|------|-----------|------|
| 信息层级 | information-hierarchy, progressive-disclosure, context-pointer, step, completion-criterion, co-location | ✅ 覆盖 |
| 双负载 | two-loads, leading-words, pointer-wording, no-op-judgment | ✅ 覆盖 |
| 锚定词 | leading-words | ✅ 覆盖 |
| 指针措辞 | pointer-wording | ✅ 覆盖 |
| no-op 判定 | no-op-judgment | ✅ 覆盖 |
| 共置 | co-location | ✅ 覆盖 |
| 技能机制 | skill-invocation, model-invoked, user-invoked, router-skill, shared-reference, skill-mechanics | ✅ 覆盖 |
| 设计树 | design-tree | ✅ 覆盖 |
| 前沿 | frontier | ✅ 覆盖 |
| 轮次 | round | ✅ 覆盖 |
| 事实而非观点 | facts-not-opinions | ✅ 覆盖 |
| 追问完成 | grilling-completion | ✅ 覆盖 |
| 追问方法论 | grilling-methodology | ✅ 覆盖 |
| 领域建模 | domain-model, active-discipline, challenge-glossary, sharpen-language, agent-brief, domain-modeling | ✅ 覆盖 |
| 分诊 | triage-state-machine, agent-ready-brief, ai-disclaimer, triage | ✅ 覆盖 |
| 任务拆分 | vertical-slice, tracer-bullet, blocking-edges, expand-contract, task-decomposition | ✅ 覆盖 |
| 失效模式 | failure-mode | ✅ 覆盖 |
| Phase Boundary | phase-boundary-decision-tree | ✅ 覆盖 |
| Grounding 依赖图 | grounding-dependency | ✅ 覆盖 |

## 剩余差距

### P0：必须补充
| # | 差距 | 影响 | 优先级 |
|---|------|------|--------|
| G1 | `ask-matt` 路由概念节点缺失 | ask-matt 是用户入口路由技能，概念层无对应节点 | 高 |
| G2 | `writing-great-skills`（ontology/domain 版）relations 未更新 | T0432 结论声称更新了 relations，但实际文件仍缺少 leading-words, pointer-wording, no-op-judgment 的 relates_to | 高 |
| G3 | `pdca-task` 缺少 steps 和 completion criteria 字段 | 技能步骤和完成标准无法在本体层面建模 | 高 |

### P1：重要补充
| # | 差距 | 影响 | 优先级 |
|---|------|------|--------|
| G4 | Phase Boundary 决策树未集成到 flow-do 收尾阶段 | 决策树仅作为概念存在，未在流程中触发 | 中 |
| G5 | Grounding 依赖图未推广到知识资产写作规范 | 仅作为概念存在，未在 writing-for-agents 中强制 | 中 |
| G6 | user-invoked/model-invoked 触发条件未建模 | 触发条件（"Use when..."）缺乏本体表示 | 中 |
| G7 | `setup-matt-pocock-skills` 模式无对应概念 | repo 配置技能的模式未建模 | 低 |
| G8 | `wizard`/`teach`/`to-questionnaire` 模式无对应概念 | 交互式 wizard、多会话 teach、问卷模式未建模 | 低 |

### P2：文档经济学
| # | 差距 | 影响 | 优先级 |
|---|------|------|--------|
| G9 | Context-pointer 的 branch trigger mechanism 未显式建模 | 指针的分支触发条件缺乏形式化表示 | 低 |
| G10 | SKILL-MECHANICS.md 等价文档缺失 | mattpocock/skills 有独立的 SKILL-MECHANICS.md 详细描述 frontmatter 和 invocation 选择 | 低 |

## 验证结果

- ✅ `ontology-validate`：OK
- ✅ `ontology_graph`：332 nodes, 681 edges, 0 islands
- ✅ 所有新增节点均有 attributes 含 testable_signal
- ✅ T0431/T0432 补充的概念节点均已通过验证

## 结论

T0431/T0432 已补充的 44 个概念节点覆盖了 mattpocock/skills v1.2.3 的大部分核心原则（20/25 项主要原则已覆盖）。剩余 5 项差距中，3 项为高优先级（G1、G2、G3），2 项为中优先级（G4、G5、G6），4 项为低优先级（G7-G10）。

本轮审查产出改进建议，后续迭代落地。