---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# 能力核验：记录格式

本契约只保存 CAP-01 的宿主能力证据，不记录 task 创建结果。
null/空列表/not_run 表示事实尚未取得，不得升级为“支持”。

## 示例

```markdown
---
schema: pdca.capability-check/v4
protocol_revision: 4.0.0-rc.4
task_id: null
attempt: null
environment_ref: null
scope: environment_or_invocation
required_capabilities: []
evidence_refs: []
result: not_run
limitations: []
---

# 能力核验

记录真实宿主/工具/配置及 CAP-01 所需能力的证据、适用范围和 limitation。
环境级证据只在相关版本/配置未变化且范围相同时复用；本次 dispatch 的真实 request/receipt/identity
仍写入 dispatch record，不由 capability-check 代替。

静态脚本、工具名称、Agent 自述或一个 ID 都不能单独升级 fresh / communicate / continue / isolation 结论。
```
