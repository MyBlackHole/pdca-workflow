---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
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
protocol_revision: 4.0.0-rc.5
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

## 物理归属

环境级核验（`task_id: null`）必须依附于一个已授权、已登记的 project/workspace 绑定，保存在：

```text
PDCA_ROOT/records/projects/<project_id>/workspaces/<workspace_id>/capability-checks/<record-ref>.md
```

`<record-ref>` 只是稳定文件引用，不编码“已通过”、宿主版本或环境身份，也不能从文件名推导能力结论。
同一环境事实发生影响适用性的版本/配置变化时创建新的 check record，并让后续引用指向新记录；已经被 task/dispatch
引用的旧记录保留原字节，不就地改写成新结论。

本次正式 task / invocation 的能力核验如果需要保存实例级 request/receipt/identity 相关限制，则放在该 task 已固定的
`record_dir` 内，并由 `dispatch.capability_check_ref` 引用精确记录。环境级 check 不能代替本次 dispatch receipt，
invocation 级 check 也不能反向改写 project/workspace 的历史环境证据。

尚未建立 project/workspace 绑定时，可以先只读完成能力探测并保留获准的私有原始证据，但不得自行发明
`records/capabilities/` 等平行根；先按 PROJECT binding 契约完成绑定与记录写入授权，再持久化环境级 capability-check。
```
