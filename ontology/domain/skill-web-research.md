---
schema: pdca.asset/v1
id: ontology:domain/skill-web-research
name: web-research
summary: Conduct web research on domain topics and best practices.
description: 网络资料调研辅助技能。当实验阶段的场景为网络调研时，提供问题拆解、搜索策略、信息整理和结论输出的结构化指导。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
---

---
name: web-research
description: 网络资料调研辅助技能。当实验阶段的场景为网络调研时，提供问题拆解、搜索策略、信息整理和结论输出的结构化指导。
---

# Web Research（网络资料调研）

## 问题拆解
- 将调研问题分解为 3-5 个可搜索的子问题
- 为每个子问题定义中英文搜索关键词
- 以 `prd.md` 中的假设和 Goal 为调研起点
- 记录到当前会话工作目录（如 `workspace/{task-slug}/search-plan.md`）

## 搜索策略
- 对每个子问题至少搜索 2 个独立来源
- 优先官方文档、权威来源
- 使用工具: `websearch`（关键词搜索）、`webfetch`（页面抓取）、`context7`（库文档查询）

## 信息整理
- 对比多方来源，标注可信度（高/中/低）
- 记录关键发现到 `workspace/{task-slug}/findings.md`
- 标注与原始假设一致或矛盾的发现

## 结论输出
- 总结调研结果，回答原始问题
- 对照 `prd.md` 验收标准逐项确认
- 列出引用来源（URL + 标题）
- 标注未确认/待验证的结论
- 输出到 `workspace/{task-slug}/research-conclusion.md`

## 已知坑

- 仅实验阶段场景为网络调研时加载；记录每条结论的来源链接，勿凭记忆引用。
