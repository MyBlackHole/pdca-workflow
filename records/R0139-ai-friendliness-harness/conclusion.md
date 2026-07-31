---
schema: pdca.asset/v1
id: R0139-ai-friendliness-harness
phase: check
source_ids: [fixture-results, fixture-inputs]
---

## 上下文

检查六类场景基准能否为后续流程或 skill 改动提供相同输入、机器判定的配对基线。

## 假设与结果

- development、bugfix、research、documentation、design、review 各有正常与故障夹具：通过。
- 12 个夹具均产生确定错误码或路由结果：12/12 通过。
- 相同输入重复执行结果稳定：通过自动测试。

## 分析

故障覆盖拒绝确认、缺 PRD、断链、非法场景、未来状态和归档矛盾。输入文件与结果均以 SHA-256 登记，可用于同版本配对比较。没有真实 runner 的 Agent trial 资产已删除，避免产生虚假实验结论。

## 适用边界

该 harness 是模型无关的流程基准，不测量真实 LLM 成功率、延迟或跨模型差异。

## 下一轮建议

只在出现真实故障或可执行 runner 时扩充场景，避免为了数量增加无判别力夹具。
