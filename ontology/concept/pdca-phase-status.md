---
schema: pdca.asset/v2
id: ontology:concept/pdca-phase-status
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: STATE-01：task 当前状态是事件事实的派生索引
---

# STATE-01：派生状态，不负责授权

STATE-01 只回答：**根据已保存的 transition、control、pending request 与未决 operation，task 当前应显示什么状态。**
`phase` / `execution_state` 是导航索引，不是 permission matrix；能否开始某 phase 只由 GATE-01 判断。

方法 phase 仍为 `plan/do/check/act`，终态索引可使用 `archive`。

## execution_state 的含义

| execution_state | 派生事实 |
|---|---|
| unexecuted | task 已创建但没有任何 `phase_started`；`phase=plan` 只是首个目标 |
| blocked_unexecuted | 首个 Plan 尚未开始，且创建后存在能力/身份/输入等阻断事实 |
| running | 存在当前 run 的 `phase_started`，尚无匹配 `phase_completed` 或生效的停止事实 |
| awaiting_input | 当前 run 未完成，并有 clarification / 必要外部输入等待 |
| awaiting_confirmation | 最近实际 phase 已完成，当前没有运行中的 run，等待新的用户对象决定；也可有 pending request |
| blocked | 已有执行历史，但当前 continuation/start 所需事实存在 unresolved/unknown 阻断 |
| stopping | CONTROL-01 的停止/撤权已生效，正在结清或隔离实际副作用/资源 |
| interrupted | 原 run/attempt 已停止且未正常完成，保留最后实际 phase 和未决事实 |
| completed | Act 已完成且存在匹配 `archived` receipt；`phase=archive` |

`completed` 只表示这个 task/attempt 的流程封存，不表示业务对象一定 PASS；
subject conformance / delivery usability 仍由 VERDICT-01 表达。

## 投影规则

- task 初始 `phase=plan` 不表示 Plan 已授权或启动；
- `phase_started(P)` 后投影 `phase=P, execution_state=running`；
- run 内等待 clarification 可投影 awaiting_input，但 run/phase 身份不变；
- `phase_completed(P)` 后保持 `phase=P`，投影 awaiting_confirmation；不要自动改成下一 phase；
- 有 cancel/revoke 时优先投影 stopping/interrupted，不能被普通 completion 文件覆盖；
- `archived` 后投影 `phase=archive, execution_state=completed`。

task.md 的状态索引必须能回链到最后完整 transition、control、request/decision 与未决 operation。
恢复时重新派生；不能相信布尔值、mtime、目录数量或 Agent 自述。

STATE 不判断“下一 phase 允许不允许”。pending request 也只表示有待用户决定的固定对象；
只有 CONFIRM 产生匹配授权且 GATE 当前仍 ready，才可能随后记录新的 `phase_started`。
