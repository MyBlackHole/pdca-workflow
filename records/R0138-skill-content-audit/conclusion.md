---
schema: pdca.asset/v1
id: R0138-skill-content-audit
phase: check
source_ids: [content-audit, flow-plan-pairing, rubric-review]
---

## 上下文

检查 skill 内容成本审查是否能用可复现信号支持精简决策，并避免以缩短文本冒充 AI 提升。

## 假设与结果

- 41 个 flow/skill 均有 bytes、结构、重复和引用指标：通过。
- 自动指标与认知 rubric 分离：通过。
- 接受的精简达到最小效果量且既定夹具无回归：通过，`flow-plan` 从 5503 降至 3535 bytes，下降 35.76%。

## 分析

实测 tokenizer 与 UTF-8 bytes 给出相同 Pareto 候选，字符数会漏掉 `flow-plan`。因此删除 `tiktoken` 和字符指标，保留零依赖 bytes。`flow-do`、`flow-check` 未找到能确定达到 15% 且保持边界的方案，故终止精简。

## 适用边界

bytes 是当前候选排序的成本代理，不是模型真实 token。零回归仅针对配对时 10 个确定性测试；当前扩展后的 15 个测试也通过，但仍不能外推到所有真实 Agent 任务。

## 下一轮建议

只有具备真实独立 Agent runner 时才重新评估模型 token 或行为成本，不预建空协议。
