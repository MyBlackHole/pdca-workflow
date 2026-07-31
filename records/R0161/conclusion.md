---
schema: pdca.asset/v1
id: R0161
phase: check
source_ids: [implementation-review, verification-matrix, content-audit, environment-health, convergence-validation]
---

## 上下文

T0161 针对与 mattpocock/skills 对比后确认的两个执行缺口实施：development/bugfix 的 test-first 顺序缺少机器可读约束，skill 的 manual/automatic 调用边和入口 alias 缺少可验证调用图。

## 假设与结果

假设：将执行顺序、最小验证回执语义、入口 alias 和调用权限变成 versioned contract，并由公共 resolver、fixture 和内容审计共同校验，可使 AI 执行路径更可判定、更少依赖自然语言猜测。

结果：在本任务定义的确定性范围内成立。12 项 AC 均有非 convergence-map 证据覆盖；全量 unittest、22/22 fixture、两个 contract document resolver、内容预算、索引、doctor、compile 和 convergence gate 均通过。

## 分析

- execution contract 约束 A/B 两条路径的 Seam → 失败测试 → 最小变更 → 切片验证 → 全量验证 → 双轴审查顺序；schema 和 resolver 均对非 canonical 阶段、非法场景、文档 marker 漂移 fail-closed。
- invocation contract 以 frontmatter 的 name/invocation 为类型事实源，只声明 alias 和调用边；所有显式 skill 路径都经过实际文档交叉校验，flow/automatic 不得指向 manual。
- triage、domain-modeling、handoff 的工作体抽为 automatic worker，manual 入口仍保留；`ask-matt` 的 `/grill` alias 与 contract 一致，旧 `/grill-me` 不再暴露。
- 审查中发现的跨 route contract 漂移、错误 entry document、schema 顺序约束缺失和重复 marker 绕过均已修复并有回归测试。

可靠性追问已覆盖：证据是否支持结论、关键路径是否测试、是否存在安全/性能未暴露风险。当前没有发现阻断项；子代理不可用和外部项目 `PDCA_HOME` 配置已有显式 fallback/doctor 提示。

## 失败原因

不适用。当前结论建议判定为 `confirmed`，但仍需用户 verdict。

## 适用边界

本结论只证明仓库内显式 contract、文档引用、调用权限和生命周期 fixture 的确定性一致性，不证明真实 LLM 的任务成功率、遵循率、token、延迟、成本或多 Agent runner 效果。要证明后者，需固定 runner、保留任务集并进行前后配对实验。

## 下一轮建议

1. 保持当前 contract/resolver/fixture 作为静态回归门禁。
2. 未来真实 runner 可生成稳定切片回执后，再评估是否把 receipt 纳入全局 Do→Check gate。
3. 若要回答“是否真实提升 AI 执行效果”，另建实验任务，记录遵循率、返工率、成功率和成本，不与本任务的 bytes 或 fixture 结果混用。
