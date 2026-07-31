---
schema: pdca.asset/v1
id: knowledge:information-architecture.task-fingerprint-reranking
layer: knowledge
summary: 用任务指纹、不可变推荐回执和封存反馈实现可解释且抗污染的上下文重排
tags: [context-retrieval, task-fingerprint, reranking, feedback]
scenarios: [default]
phases: [plan, do, check]
applies_when: [AI 需要从结构化资产中选择与当前任务最相关的上下文]
excludes_when: [用户明确禁止读取历史上下文]
source_ids: [experience:T0015--07-26-实现任务指纹与上下文相关性重排]
confidence: high
status: active
---
# 任务指纹与上下文重排

## 决策规则

1. 指纹必须包含任务身份与目标、scenario、phase、PRD digest、query、tags 和显式 signals；时间戳不得进入稳定 digest。
2. 召回默认限于 active Knowledge 与 Skill，只有显式请求才展开 Experience，Evidence 不进入推荐。
3. 排序同时考虑词法候选位置、scenario、phase、tag、applies_when、confidence 和相似指纹反馈，并输出每项分数。
4. `excludes_when` 是硬门禁，但只与结构化 tags/signals 匹配；自由 query 只用于召回和软相关性，避免模糊排除误杀。
5. 每次推荐生成不可变 receipt，绑定 ranker version、fingerprint、asset ID 与 content digest。反馈只能引用回执中真实出现的同版本资产。
6. used/helpful/misleading 是观察事件，不是知识。只有 task meta 中存在 Context seal、且 feedback→receipt→asset 引用链完整的闭环记录才能影响其他任务。
7. 相似反馈要求 scenario、phase 相同且 query/tag/signal token 集合达到兼容阈值；同一来源指纹对同一资产的贡献必须封顶。

## 安全门禁

- 推荐与反馈只操作当前活跃任务，并与生命周期状态共用协调锁。
- Do 可记录 used；Check 可记录 helpful/misleading；Act 已封存，不再生成回执或追加反馈。
- JSONL 严格拒绝未知字段、损坏行、重复冲突 key、符号链接、超量事件和超大文件。
- 资产内容 digest 变化时旧反馈失效，不允许同 ID 的新版本继承旧评价。
- `task learn` 封存 Context digest，archive 必须复验；未封存 record 不参与反馈迁移。

## 检索层级

任务指纹负责“与当前任务是否相关”，四层来源链负责“为何可信”。排序不能替代 provenance 校验，provenance 也不能替代 applicability 判断。
