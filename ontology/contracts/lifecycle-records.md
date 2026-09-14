---
schema: pdca.lifecycle-record-contract/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: lifecycle_record_examples
record_shapes:
  task:
    strings:
    - task_id
    - work_id
    - tree_revision
    - node_id
    - scene
    positive_integers:
    - attempt
    references:
    - control_view_ref
    enums:
      phase:
      - plan
      - do
      - check
      - act
      execution_state:
      - blocked_unexecuted
      - blocked
      - awaiting_confirmation
      - stopping
      - interrupted
      - unexecuted
  baseline:
    strings:
    - task_id
    - work_id
    - tree_revision
    - node_id
    - scene
    - baseline_id
    - goal_statement
    positive_integers:
    - attempt
  request:
    strings:
    - task_id
    - request_id
    - kind
    - phase
    - conversation_ref
    positive_integers:
    - attempt
    references:
    - subject_ref
    digests:
    - subject_digest
  response:
    strings:
    - task_id
    - request_id
    - kind
    - phase
    - conversation_ref
    - response
    positive_integers:
    - attempt
    references:
    - subject_ref
    - source_ref
    digests:
    - subject_digest
  request-decision:
    strings:
    - decision_id
    - task_id
    - request_id
    - kind
    - phase
    - conversation_ref
    - terminal_state
    - response
    positive_integers:
    - attempt
    references:
    - subject_ref
    - response_ref
    - source_ref
    digests:
    - request_digest
    - subject_digest
  transition:
    strings:
    - task_id
    - gate_id
    - actor_ref
    lists:
    - inputs
    references:
    - inputs_manifest_ref
    - gate_check_ref
    - writer_grant_ref
    - commit_receipt_ref
    digests:
    - baseline_digest
    - inputs_digest
    - gate_check_digest
    positive_integers:
    - attempt
    - sequence
    - observed_control_revision
    booleans: []
    mappings: []
    enums:
      decision:
      - approved
      from:
      - plan
      - do
      - check
      - act
      to:
      - do
      - check
      - act
      - archive
  gate-check:
    strings:
    - check_id
    - task_id
    - gate_id
    lists:
    - checks
    references:
    - subject_ref
    digests:
    - subject_digest
    positive_integers:
    - attempt
    - observed_control_revision
    booleans: []
    mappings: []
    enums:
      result:
      - ready
      - not_ready
  test-run:
    strings:
    - task_id
    - work_id
    - tree_revision
    - node_id
    - scene
    - run_id
    lists:
    - case_results
    - effective_case_refs
    - raw_evidence_refs
    references:
    - suite_ref
    - artifact_ref
    - checker_ref
    - visible_input_manifest_ref
    - evidence_manifest_ref
    digests:
    - suite_digest
    - artifact_digest
    - checker_digest
    positive_integers:
    - attempt
    booleans:
    - mutation_run
    mappings: []
    enums: {}
  review-package:
    strings:
    - task_id
    - review_id
    - phase
    lists:
    - objects
    references: []
    digests:
    - baseline_digest
    positive_integers: []
    booleans: []
    mappings: []
    enums: {}
  control-state:
    strings:
    - task_id
    positive_integers:
    - attempt
    booleans:
    - execution_allowed
    - stop_pending
  capability-check:
    strings:
    - check_id
    - scope_kind
    - work_id
    - task_id
    - checkpoint
    positive_integers:
    - attempt
    lists:
    - checks
  control-event:
    strings:
    - event_id
    - scope_kind
    - work_id
    - task_id
    - kind
    positive_integers:
    - attempt
    - control_revision
    references:
    - source_ref
    - host_order_receipt_ref
  operation:
    strings:
    - task_id
    - operation_id
    - action
    - status
    positive_integers:
    - attempt
    lists:
    - target_resources
    enums:
      status:
      - prepared
      - submitted
      - completed
      - cancelled_before_effect
      - unknown
      - isolated
  resource-reservation:
    strings:
    - reservation_id
    - owner_task_id
    - slot_ref
    - state
    positive_integers:
    - owner_attempt
    lists:
    - resource_set
    enums:
      state:
      - held
      - revoking
      - released
      - retained
  termination:
    strings:
    - termination_id
    - task_id
    - terminal_reason
    - last_valid_phase
    positive_integers:
    - attempt
    lists:
    - execution_revocation_refs
    references:
    - stop_event_ref
    - record_handoff_ref
  rework:
    strings:
    - issue_id
    - work_id
    - tree_revision
    - node_id
    - scene
    - predecessor_task_id
    - successor_task_id
    references:
    - termination_ref
    - origin_artifact_ref
    digests:
    - origin_artifact_digest
    enums:
      state:
      - open
  dispatch:
    strings:
    - task_id
    - dispatch_request_id
    - agent_id
    - conversation_ref
    positive_integers:
    - attempt
    booleans:
    - handoff_completed
    references:
    - spawn_receipt_ref
    - isolation_evidence_ref
---

# 停止、失败及异常接续：有限记录检查契约

本附件归属现有 STATE-01、CONTROL-01、RESOURCE-01、SCHED-01、CONTRACT-01、REWORK-01，不增加状态、方法阶段、批准角色或执行器。按需读取；只用正式 templates 字段，辅助证据明确为 fixture。这里定义有限维护 profile，不认证宿主事实。

## 适用性和两个结果

`lifecycle_record_examples`核对blocked_unexecuted、blocked、awaiting_confirmation、stopping、interrupted及后继准入的固定材料关系。合法停止可得到record_consistency=pass，但business_completed、delivery_eligible、release_eligible都为false。未实施项仍incomplete，不能把检查器退出码0当成PDCA完成。没有停止来源且仅缺能力时仍blocked；已接到停止但撤权/在途影响未知时保持stopping。

`fixed_formal_record_example`仍检查正常四边；正常completed的业务结果可以rejected/partial。诚实失败收尾保留真实确认与四条边，不伪造通过、不强迫删除失败run；不得把正常失败改用interrupted逃避已有门禁。后者的失败控制在独立维护挑战中实际构造，不复制一整套预置成功材料。

## 独立验收和阶段前缀

basis由检查入口固定，列明案例身份、预期状态/阶段、必需能力、已存在操作及资源、旧产物摘要。被审记录不能删除整个操作或资源来自证完整。检查实际目录中全部转换与basis列出的前缀一致；Plan零条、Do一条、Check两条、Act三条。每条已存在边核验身份、基线、前驱、门禁、固定证据及适用确认；停止前已经提交的边保留，停止后不新增边。不会为停止记录补齐四边。序列测试使用具名fixture宿主序列，不是壁钟，也不是生产排序证明。

## 终止和资源

interrupted必须绑定真实来源相应的typed记录：当前task/attempt的执行撤销、原writer向封存者的交接、所有在途操作及每项settled或isolated证据。unknown不是settled。操作隔离必须覆盖完整影响资源并说明阻止旧写者；相应资源retained而不是released。终止资源集合必须分区完整且互斥；释放证据核对owner及epoch；控制视图的retained集合与termination一致。仅删除锁文件、超时、心跳丢失不属于这些证明。

本维护profile只比较已由basis列明的规范化whole_object键；不实现别名发现、范围重叠或资源侧fencing。不同资源字符串不证明生产中无冲突。辅助fixture被写成native来源时也不会获得生产资格。

## 后继

异常后继须原尝试interrupted、新task/new attempt/new Agent、独立后继授权、原失败产物的不可变引用、旧写域结清或无冲突保留域、累计预算继承。stop来源不是新任务授权。冲突资源仍retained则后继blocked_unexecuted，不派发；释放或具名无冲突候选只通过维护准入关系检查，仍要真实派发和自己的Plan确认。旧artifact不能在同一版本名下被重写；旧确认不传给新attempt。

## 字段范围

frontmatter.record_shapes为本profile对正式模板的字段投影；只在选中profile时读取。不改变正常完成profile，不将completed-only要求强加给合法停止。profile未覆盖真实授权、真实新Agent、原子控制及自然语言判定；检查结果必须逐项列出这些未执行范围。
