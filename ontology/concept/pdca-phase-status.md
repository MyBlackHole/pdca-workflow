---
schema: pdca.asset/v2
id: ontology:concept/pdca-phase-status
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 阶段、任务状态与产物结果分离
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:concept/pdca-verdict
  - ontology:concept/pdca-task
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
state_spec:
  phases:
  - plan
  - do
  - check
  - act
  - archive
  method_phases:
  - plan
  - do
  - check
  - act
  execution_states:
  - unexecuted
  - running
  - awaiting_confirmation
  - awaiting_input
  - blocked
  - blocked_unexecuted
  - stopping
  - interrupted
  - completed
  allowed_phases_by_state:
    unexecuted:
    - plan
    running:
    - plan
    - do
    - check
    - act
    awaiting_confirmation:
    - plan
    - check
    awaiting_input:
    - plan
    - do
    - check
    - act
    blocked:
    - plan
    - do
    - check
    - act
    blocked_unexecuted:
    - plan
    stopping:
    - plan
    - do
    - check
    - act
    interrupted:
    - plan
    - do
    - check
    - act
    completed:
    - archive
  active_expression: phase != archive
  active_semantics: legacy_unarchived_query_only
  attempt_terminal_states:
  - completed
  - interrupted
  coordinator_wait_state: suspended_waiting_agent
---

# 阶段、执行控制与业务结果

## STATE-01：唯一状态矩阵

`task.md.phase`保留兼容编码plan/do/check/act/archive；方法阶段只有前四项。archive是正常任务终态；取消不设置phase=interrupted，不新增Plan→Archive或Check→Do边。下面矩阵同时保存在frontmatter.state_spec.allowed_phases_by_state，二者必须一致。

| execution_state | plan | do | check | act | archive |
|---|---|---|---|---|---|
| unexecuted | 允许 | 禁止 | 禁止 | 禁止 | 禁止 |
| running | 允许 | 允许 | 允许 | 允许 | 禁止 |
| awaiting_confirmation | 允许 | 禁止 | 允许 | 禁止 | 禁止 |
| awaiting_input | 允许 | 允许 | 允许 | 允许 | 禁止 |
| blocked | 允许 | 允许 | 允许 | 允许 | 禁止 |
| blocked_unexecuted | 允许 | 禁止 | 禁止 | 禁止 | 禁止 |
| stopping | 允许 | 允许 | 允许 | 允许 | 禁止 |
| interrupted | 允许 | 允许 | 允许 | 允许 | 禁止 |
| completed | 禁止 | 禁止 | 禁止 | 禁止 | 允许 |

## 组合允许不等于事实已成立

- unexecuted/blocked_unexecuted：未开始该任务的Plan工作、无阶段回执。前者尚未执行，后者已识别必需能力/派发前置缺失。开始Plan后缺能力用blocked，不能擦除已经发生的动作。
- running：绑定有效，当前记录写入者合法；具体动作仍需CAP-01/RESOURCE-01准入。普通Plan活动不表示Plan已获批准，阶段确认消费后才允许第一条转换。
- awaiting_confirmation：只对应Plan的plan_confirmation或Check的check_confirmation，必须有当前未决请求。Do/Act的普通事实澄清使用awaiting_input；改变范围/权限不能伪装澄清自动批准。
- blocked：记录blocked_reason、blocked_action、required_evidence及恢复主体。资源或工具不足可只阻断业务动作；在真实记录/确认通道仍可用且无停止事件时，允许按GATE-01诚实失败收尾。不得在能力仍缺失时继续被阻断动作。
- stopping：CONTROL-01已经接受停止事件，禁止新增业务动作和阶段转换；只允许原授权内的停止、对账、证据保全。不能按“取消已发出”直接认定执行者消失。
- interrupted：非archive阶段，终止记录证明旧执行资格已撤销、记录写入权已交回/隔离；未决远端影响逐项结清或可靠隔离。保留terminal_reason和最后合法phase，attempt不复活。隔离资源可以继续被保留，并不允许冲突后继使用。
- completed：当且仅当phase=archive且四条完整无冲突回执有效、正常收尾条件满足。业务结果可以失败。正常封存后任务业务和阶段写入停止；槽与资源释放还需RESOURCE-01的真实交接，不能从completed推断自动释放。

## 查询值与写权分离

`active = phase != archive`只保留为legacy“未正常归档”查询，不写入独立镜像，不用于调度或抢占。`attempt_terminal = execution_state in [completed, interrupted]`表示当前尝试不再继续；不能证明资源可复用。

slot_owner由宿主槽记录决定；resource_owner由规范化实际资源预约决定；record_owner由当前写权/交接回执决定。`writer`记录字段不能自己创造写权。`eligible_to_start`必须按SCHED-01核对旧尝试结清、新授权、依赖快照和新资源准入，不能只看active或phase。

CONTROL-01的可信控制视图优先阻止动作，即使task快照尚未来得及写stopping；有停止事件但快照仍running不能继续执行。终态记录损坏时在独立integrity报告中隔离，不将archive重开成running/blocked。phase终态、控制终态、资源保留和业务verdict是不同维度。

## 正反例与恢复

Plan取消可原phase终止；archive+running、do+unexecuted、无终止依据的interrupted必须拒绝。取消与正常归档竞争按CONTROL-01/TRANSITION-01的真实排序保留已经提交的最后合法边，不补边、不吞掉停止事件。完整组合矩阵及错误控制见[协议回归](../../tests/protocol-regression/README.md)。
