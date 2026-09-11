# 全流程派发／前沿调度回归 · agent-dispatch.1

本套件检查归一化的有限事件关系，不认证真实Agent、用户、资源后端，也不是完整PDCA合规检查。
独立basis由固定目标/授权图/真实能力选择；不得由trace删除要求。每例保留basis、原始payload、序号、摘要、观测与结果。

维护附件 `run_dispatch_tests.py` 先固定全部输入和预期，再调用只读审查器。所有坏样本（除专门测试摘要损坏者）同步重算来源与basis摘要，不能用无关hash失败算命中。

| Case | 输入/行为 | 有限预期 | 必须命中的诊断 |
|---|---|---|---|
| AD-P01 | two independent accepted before waiting | pass | 无诊断；生产资格未证明 |
| AD-P02 | honest capacity one | pass | 无诊断；生产资格未证明 |
| AD-P03 | refill without batch barrier | pass | 无诊断；生产资格未证明 |
| AD-P04 | A waits confirmation while B completes | pass | 无诊断；生产资格未证明 |
| AD-P05 | only conflicting writers serialize | pass | 无诊断；生产资格未证明 |
| AD-P06 | unknown creation reserves only its slot | pass | 无诊断；生产资格未证明 |
| AD-P07 | parent local delivery before children | pass | 无诊断；生产资格未证明 |
| AD-P08 | honest failed completion remains unusable | pass | 无诊断；生产资格未证明 |
| AD-P09 | cancel and safe interrupted release | pass | 无诊断；生产资格未证明 |
| AD-P10 | valid in-flight prefix not business completion | pass | 无诊断；生产资格未证明 |
| AD-P11 | fresh successor attempt preserves historical identities | pass | 无诊断；生产资格未证明 |
| AD-P12 | no formal spawn when full-PDCA capability missing | pass | 无诊断；生产资格未证明 |
| AD-P13 | cancellation scoped to one candidate | pass | 无诊断；生产资格未证明 |
| AD-P14 | unknown query resolves same request | pass | 无诊断；生产资格未证明 |
| AD-P15 | external reservation respected | pass | 无诊断；生产资格未证明 |
| AD-N01 | host executes child Plan | fail | stage_actor |
| AD-N02 | Do-only task marked completed | fail | incomplete_pdca_completion |
| AD-N03 | reuse Agent identity across tasks | fail | fresh_agent_identity |
| AD-N04 | reuse conversation across tasks | fail | fresh_agent_identity |
| AD-N05 | inherit active parent context | fail | full_pdca_isolation |
| AD-N06 | draft delivery alias | fail | draft_delivery_alias |
| AD-N07 | children before parent seed | fail | dispatch_not_eligible |
| AD-N08 | spawn A wait terminal then B | fail | idle_ready_capacity |
| AD-N09 | batch barrier leaves idle slot | fail | idle_ready_capacity |
| AD-N10 | A confirmation creates global barrier | fail | idle_ready_capacity |
| AD-N11 | resource head-of-line blocks independent C | fail | idle_ready_capacity |
| AD-N12 | dispatch exceeds capacity | fail | dispatch_not_eligible |
| AD-N13 | blind respawn unknown attempt | fail | duplicate_attempt_spawn |
| AD-N14 | forget unknown slot reservation | fail | dispatch_not_eligible |
| AD-N15 | omit candidate from opportunity | fail | candidate_coverage |
| AD-N16 | candidate changes independent basis | fail | basis_digest |
| AD-N17 | missing Agent identity | fail | fresh_agent_identity |
| AD-N18 | child resets target directory | fail | received_input_binding |
| AD-N19 | child shares sibling record scope | fail | writer_handoff |
| AD-N20 | cross-task confirmation | fail | confirmation_source |
| AD-N21 | confirm wrong object | fail | confirmation_subject_or_phase |
| AD-N22 | Agent self-signs user response | fail | confirmation_source |
| AD-N23 | no actual test run | fail | missing_actual_run |
| AD-N24 | old attempt run evidence | fail | attempt_mismatch |
| AD-N25 | phase proceeds after cancel | fail | action_not_active_or_cancelled |
| AD-N26 | release without completed or interrupted terminal | fail | unsafe_release |
| AD-N27 | missing raw source | incomplete | source_missing_or_mismatch |
| AD-N28 | event sequence gap | incomplete | event_gap |
| AD-N29 | empty trace is unknown not pass | incomplete | trace_empty |
| AD-N30 | unmapped event incomplete | incomplete | unsupported_event |
| AD-N31 | baseline silently changes | fail | pin_changed |
| AD-N32 | invalid phase order | fail | phase_order |
| AD-N33 | wrong assignment received | fail | received_input_binding |
| AD-N34 | wrong input snapshot received | fail | received_input_binding |
| AD-N35 | failed run sold as usable | fail | unusable_delivery_claim |
| AD-N36 | boolean attempt | fail | task_identity_required |
| AD-N37 | boolean capacity | fail | capacity_type |
| AD-N38 | dependency cycle cannot self-ready | fail | dependency_cycle |
| AD-N39 | task claims whole record root | fail | private_scope |
| AD-N40 | duplicate same request accepted twice | fail | accept_without_request |
| AD-N41 | partial export not complete proof | incomplete | trace_incomplete |
| AD-N42 | reusing historic Agent | fail | fresh_agent_identity |
| AD-N43 | wrong request accepted | fail | accept_without_request |
| AD-N44 | parallel claimed without async capacity | fail | dispatch_not_eligible |

## 真实宿主的另行验收

本套件的phase事件只检查责任与顺序，不能代替正式四条转换原件、确认来源认证、真实ME与业务案例。必须现场证明新Agent输入隔离、全流程恢复、真实消息路由、私有写域以及在途接受句柄。原生异步能力缺失时不得伪造；实际容量1正确受限不算2路并行通过。

实例见[并发测试步骤](../../examples/parallel-pdca.md)，权威见[TASK](../../ontology/concept/pdca-task.md)、[SCHED](../../ontology/concept/work-tree-scheduling.md)、[CAP](../../ontology/concept/capability-protocol.md)。当前真实宿主验收状态为NOT_RUN；离线/进程实验结果由独立附件记录。
