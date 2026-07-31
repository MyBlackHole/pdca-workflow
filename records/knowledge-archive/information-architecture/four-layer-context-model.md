---
schema: pdca.asset/v1
id: knowledge:information-architecture.four-layer-context-model
layer: knowledge
summary: 用 Evidence、Experience、Knowledge、Skill 四层派生链组织 AI 上下文
tags: [information-architecture, provenance, context-retrieval]
scenarios: [default]
phases: [plan, do, check, act]
applies_when: [AI 需要从历史任务中选择可信且相关的上下文]
excludes_when: [无需留存和复用的一次性对话]
source_ids: [experience:T0014--07-26-组织证据经验知识与技能四层模型]
confidence: high
status: active
---
# 四层 AI 上下文模型

## 决策规则

- Evidence 保存原始事实，内容寻址且不可变；搜索只暴露人工摘要。
- Experience 保存一次任务的上下文、行动、结果和适用边界，并引用 Evidence ID。
- Knowledge 保存跨任务成立、允许修订的结论，通过 projection receipt 引用 Experience。
- Skill 把 Knowledge 转换成可执行步骤，通过 front matter 引用 Knowledge ID。

四层之间只传递摘要、稳定 ID 和 digest，不复制上游全文。

## 检索顺序

1. 从当前任务提取 query、scenario、phase 和 tag。
2. 默认检索 active Knowledge 与 Skill。
3. 决策不确定、存在冲突或需要反例时，沿 source ID 展开 Experience。
4. 只有需要核验事实时才读取 Evidence 摘要；原始 blob 需显式打开。

## 门禁

- 不存在的 source ID、错误的来源方向和未经 manifest 验证的 Knowledge 来源必须拒绝。
- `applies_when` 与当前任务不匹配，或命中 `excludes_when` 时，不应注入上下文。
- Deprecated 资产默认不参与搜索。
