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
dcterms_modified: '2026-09-14'
summary: TRANSITION-01：用户驱动的阶段事件链
transition_protocol:
  events:
  - phase_started
  - phase_completed
  - archived
  initial_phase: plan
  normal_order:
  - plan
  - do
  - check
  - act
  rework_edges:
  - - check
    - do
  start_requires_user: true
  phase_completion_auto_advances: false
  sequence_allocator: task_writer_monotonic
  terminal_phase: archive
---


# TRANSITION-01：用户驱动的阶段事件链

4.x不再以固定1/2/3/4四条自动边代表完整流程。沿用transitions目录，顺序记录phase_started、phase_completed、archived事件；sequence由当前合法任务writer递增，previous_ref/digest关联实际前项。控制事件、业务operation_id不共用此序号。

正常顺序Plan→Do→Check→Act。每个phase_started都引用新的phase_start请求、真实响应消费和run_id，固定输入与写域。phase_completed只能由同run／同Agent在固定结果后产生；随后等待。Act完成后的archived是本次已批准处置内的封存，不再索要第五阶段确认，也不启动新工作。

用户要求在Check后修复：目标／oracle不变时，可明确批准新的Do run，然后重新批准Check及Act；原失败报告和所有run不可覆盖。新结果使旧Check／Act输入过期。目标、oracle或Agent必须变化则安全结束原attempt，用户决定新attempt并从Plan开始；不能悄改基线。

提交前核对原绑定、当前phase、最近完整链、用户授权、固定对象及CONTROL／RESOURCE资格。完整回执重读后更新task索引；相同请求／run重复投递不再执行。链分叉、截断、未知写者与身份不匹配阻断，不按最新文件选一条。

事件链不是跨文件事务、CAS或exactly-once。没有回执不代表业务没做；结果未知先对账原operation，不重放非幂等动作。没有受信原子控制边界时如实标合作式保证。
