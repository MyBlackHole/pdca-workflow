---
schema: pdca.asset/v2
id: ontology:concept/pdca-transition
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: TRANSITION-01：记录 task phase 的不可变事件链
transition_protocol:
  events:
  - phase_started
  - phase_completed
  - archived
  normal_order:
  - plan
  - do
  - check
  - act
  sequence_allocator: task_writer_monotonic
---

# TRANSITION-01：阶段事件链

TRANSITION-01 只定义**已经发生的阶段事实如何顺序记录**。
它不生成用户授权，不判断 Gate，也不把事件链本身当 task 当前状态。

## 事件

- `phase_started`：GATE-01 已对同一 task/attempt/phase/run/subject 判定 ready 后，记录该 run 实际开始；
- `phase_completed`：同一 run/Agent 已固定真实结果包后，记录该 phase 实际完成；
- `archived`：已授权 Act 完成后的终态封存事件，不是第五阶段。

正常阶段顺序是 Plan→Do→Check→Act。Check→Do 返工只有在 REWORK-01 + 新 Do phase_start + GATE 成立时，
才能记录新的 Do run；事件链不自动生成返工或下一阶段。

## 链与幂等

每个 task/attempt 使用单调 `sequence`，每条 receipt 通过 previous ref/digest 指向前一完整 receipt。
控制事件和业务 operation_id 不占用这个 sequence。

- `phase_started` 必须引用本 run 实际使用的 confirmation decision 与固定输入；
- `phase_completed` 必须引用同 run 的真实 result/evidence；
- 相同 request/run 的重复交付只返回既有事实，不追加第二次同义事件；
- 分叉、截断、未知 writer、身份不匹配或前驱缺失时阻断后续追加，不按文件 mtime/“最新文件”猜链。

事件 receipt 的精确字段只以 transition record-shape 为准。

## 事件不是授权或 exactly-once

写入 `phase_completed` 只说明该 run 已结束，不授权下一 phase。
`archived` 只说明 Act 已按其授权处置完成，不启动新 scene/task/attempt。

事件链也不是业务副作用的事务/CAS/exactly-once 保证。
缺 receipt 不证明副作用没发生；未知业务操作先按 operation/RESOURCE 对账，不能靠补写 transition 重放非幂等动作。

STATE-01 从完整 transition/control/request 事实派生当前 task 索引；
transition 本身不维护 `execution_state`。
