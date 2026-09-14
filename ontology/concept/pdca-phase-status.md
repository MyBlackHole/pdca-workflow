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
dcterms_modified: '2026-09-14'
summary: STATE-01：当前状态是索引，不是授权
state_spec:
  method_phases: &id001
  - plan
  - do
  - check
  - act
  allowed_phases_by_state:
    running: *id001
    awaiting_confirmation: *id001
    awaiting_input: *id001
    blocked: *id001
    stopping: *id001
    interrupted: *id001
    unexecuted:
    - plan
    blocked_unexecuted:
    - plan
    completed:
    - archive
---

# STATE-01：当前状态是索引，不是授权

phase 编码仍为 plan/do/check/act/archive；方法阶段只有前四个。初始 task.phase=plan 表示当前目标，不表示 Plan 已执行。

| execution_state | plan | do | check | act | archive |
|---|---|---|---|---|---|
| unexecuted | 允许 | 禁止 | 禁止 | 禁止 | 禁止 |
| running | 允许 | 允许 | 允许 | 允许 | 禁止 |
| awaiting_confirmation | 允许 | 允许 | 允许 | 允许 | 禁止 |
| awaiting_input | 允许 | 允许 | 允许 | 允许 | 禁止 |
| blocked | 允许 | 允许 | 允许 | 允许 | 禁止 |
| blocked_unexecuted | 允许 | 禁止 | 禁止 | 禁止 | 禁止 |
| stopping | 允许 | 允许 | 允许 | 允许 | 禁止 |
| interrupted | 允许 | 允许 | 允许 | 允许 | 禁止 |
| completed | 禁止 | 禁止 | 禁止 | 禁止 | 允许 |

初始未批准 Plan 和任何阶段完成后均可等待确认；pending_request_ref指向具体待启动阶段。running必须可回链到当前run的合法phase_start消费及未撤销写权。完成阶段只写phase_completed事件并等待，不自动改变phase。

恢复以不可变事件、请求来源、固定产物及实际未决操作重建task.md；不能相信一项布尔值或mtime。completed仅表示按已授权Act收尾且完整循环有据；业务／本体符合性可为fail或unknown。interrupted保留最后阶段，不补造四阶段。

一个任务等待不阻止其他获准阶段；等待会话是否占执行位由真实宿主能力决定，不由父 Agent 心跳判断。
