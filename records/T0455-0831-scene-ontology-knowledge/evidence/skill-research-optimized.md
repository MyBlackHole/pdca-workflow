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

## Exit

Findings written to research-report.md and registered as evidence. Findings captured on throwaway branch with context pointer.

## 已知坑

- 只采信高信任 primary source；二手转述/低信源结论须标注置信度，勿当作事实。
- Subagent 并行 burn-down 时，每个 research ticket 独立 capture，不互相依赖。
- model-invoked 模式下，AI 驱动调研，用户只需验证最终发现。