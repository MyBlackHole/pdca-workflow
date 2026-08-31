---
schema: pdca.asset/v1
id: ontology:domain/skill-research
name: research
summary: Conduct research on domain topics and best practices.
description: Investigate a question against high-trust primary sources and capture findings as a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered.
invocation: model-invoked
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
    - ontology:concept/skill-mechanics
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Research — 模型驱动的领域调研

model-invoked：AI 自动调研领域主题并捕获发现为带引用的 Markdown 文件。

## 触发条件

当用户希望调研某个主题、收集文档或 API 事实时触发。

## 流程

1. 识别 primary sources — official docs, source code, specs, first-party APIs。Follow every claim to the source。
2. Systematic investigation。
3. 写入 `research-report.md`：
    ```markdown
    ## 调研目标
    ## 方法
    ## 发现
    ## 结论与建议
    ## 参考资料
    ```
4. 每条关键结论附至少一条**可复核验证途径**（重跑命令/SQL/复现步骤/可回看的 file:line 引用）；无法给出途径的结论降级为"待验证假设"并标注置信度。
5. Register via `$PDCA_HOME/skills/register-evidence/SKILL.md`。

## Subagent 并行 Burn-down

Research tickets 不再等待单独 session。创建 tickets 后，charting session 对每个 research ticket 触发 `/research` subagent 并行 burn-down。

- 捕获发现到 throwaway `research/<name>` branch
- 在实现问题上留下 context pointer
- Research tickets 是"一个 ticket per session"规则的唯一例外
- Subagent 并行 burn-down 时，每个 research ticket 独立 capture，不互相依赖

## Model-Invoked 行为

model-invoked 模式下，AI 自动执行调研流程：
- 自动识别 primary sources
- 自动 systematic investigation
- 自动生成 research-report.md
- 自动 register evidence

## 本体沉淀决策（Act 门禁）

research 结论在 Check `confirmed/partial` 后，进入 Act 必须做显式的本体沉淀决策，避免高复用知识仅留 `records/`：

1. **分流判定**（满足任一即判定为“应本体化”）：
   - 产出含可复用清单/模型/模式/阈值（如 Checklist、成熟度分级、阈值表、决策树）
   - 结论被 PRD 验收标准或后续任务依赖（跨任务复用）
   - 方法论/规范类研究（非一次性事实收集）
2. **决策记录**：在 `records/<record-id>/conclusion.md` 增设 `## 本体沉淀` 章节，显式声明 `ontology` 或 `records-only` 及理由；`task.json#meta.disposition` 的 `reason` 须包含该决策关键词（`ontology:` 或 `records-only`）。
3. **本体化执行**（判定为 `ontology` 时）：新建或更新 `ontology/<type>/<slug>.md`（`pdca.asset/v1`），`relations` 关联 `ontology:concept/pdca-task` 与来源 record，`attributes[].testable_signal` 可回归验证；信号须符合 `testable-signal-to-test-derivation` 三模式（属性断言/契约测试/收敛验证）结构，经 `ontology-validate` 与 `ontology_graph`（0 islands）校验后方可进入 `archive`。
4. **校验**：运行 `python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/<task>`，漏决策或 `records-only` 无理由即 `RESEARCH_SETTLEMENT_MISSING`；校验 `attributes[].testable_signal` 不含泛化短语（符合 `testable-signal-to-test-derivation` 三模式）。

## Exit

Findings written to research-report.md and registered as evidence. Findings captured on throwaway branch with context pointer. 本体沉淀决策已显式记录且校验通过。

## 已知坑

- 只采信高信任 primary source；二手转述/低信源结论须标注置信度，勿当作事实。
- Subagent 并行 burn-down 时，每个 research ticket 独立 capture，不互相依赖。
- model-invoked 模式下，AI 驱动调研，用户只需验证最终发现。