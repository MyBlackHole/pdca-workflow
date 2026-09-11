---
schema: pdca.asset/v2
id: ontology:concept/pdca-gate
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.7
summary: 任务自主阶段门禁与测试判据
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/pdca-transition
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:process/independent-work-review
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/work-dependency-graph
  - ontology:concept/pdca-phase-status
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/ontology-evolution
  - ontology:concept/task-decomposition
gate_ids:
- plan_to_do
- do_to_check
- check_to_act
- act_to_archive
gate_predicate_ids:
  plan_to_do:
  - identity_and_input
  - graph
  - fixed_baseline_tests_budget
  - capability
  - resource
  - confirmation
  - control
  do_to_check:
  - case_observations
  - fixed_artifacts
  - side_effects
  - record_control
  - integrity
  check_to_act:
  - ac_verdict_issues
  - subject_conformance_if_review
  - confirmation
  - control
  act_to_archive:
  - knowledge_and_rework
  - honest_delivery
  - no_pending_requests
  - side_effects_settled
  - recoverable_chain
  - control
---

# 当前节点的自主门禁

## GATE-01：结构合法、授权有效与业务成功分开

门禁由当前绑定Agent依据事实判断；不存在父Agent阶段放行。四条正常边不变，提交再核对STATE-01/CONTROL-01有效资格，资源准入来自真实宿主，不从文字推导锁。

| gate_id | 边 | 必须事实 |
|---|---|---|
| plan_to_do | plan→do | TREE/NODE身份和SCHED输入就绪；DEPENDENCY快照/检查对应当前授权版本；基线/AC/全部必需suite/oracle/预算固定且结构完整；CAP当前必需执行/观测能力真实可用；RESOURCE记录区及业务写域资格已取得；CONFIRM存在匹配当前task/attempt/request/kind=plan_confirmation/phase=plan/conversation/subject_digest的真实consumed/confirmed决策；当前控制无停止/撤权 |
| do_to_check | do→check | 每条必须AC/案例有真实pass/fail/error/blocked/not_run及依据；产物/结果包版本固定；副作用可解释且当前记录/控制资格允许失败收尾；Agent完成完整性检查。不要求全部pass、不要求父审查回执 |
| check_to_act | check→act | AC/suite/verdict/缺陷与证据回链明确，审查scene有subject_conformance；匹配当前task/attempt/request/kind=check_confirmation/phase=check/conversation/结论包摘要的真实consumed/confirmed；仍有控制资格。用户可认可失败，不改业务结果 |
| act_to_archive | act→archive | 知识处置及理由、失败issue/影响/后继计划完整；交付可用性诚实；无pending请求；正常业务动作已停、未知副作用不悬而未决；状态/链可恢复，无停止事件抢先生效。第4回执/快照写完才交回记录写权 |

基线完整性检查不等于用户确认。澄清、旧请求、过期/取消/替代决策不能充当批准。当前控制事件抢先取消时走CONTROL停止而非下一阶段。

必需测试能力在Plan前就缺失，不能开Do后用全blocked伪装实施。能力在Do期间真实丢失而记录/确认仍安全可用时，可固定全部error/blocked并诚实进入Check；它不会让suite、本地业务、delivery或release成功。外部作用未知需先RECOVERY核查，不借失败收尾丢弃风险。

TEST-01聚合只覆盖当前节点职责，祖先回归不阻止孩子正常结束；VERDICT-01区分node_local_pass/delivery_usable/work_issue_closed/release_approved。仅full交付，不放行失败实现；有效审查任务报告subject失败不等于报告自身不合格。no_new_knowledge合法。

## 采用谓词附加到既有门禁

Plan→Do：建模需要REUSE-01检索/决定与输入适用性完整；其他scene需要固定definition_refs/effective_contract及ADOPT采用检查。必需事实未知或当前可信公告阻断时不执行。Do→Check允许把实际采用失败/未知如实收尾，不能将“不适用资料”标业务成功。

Act→Archive仍允许candidate_only/confirm_existing；未发布共享候选不阻断本地正常完成，前提是本地义务已独立核验。共享发布另按EVOLVE-01核对真实授权、base、目录代数与提交，不能将归档等同于全球发布。

## 建模质量与真实准入的补充判据

GATE-01不允许draft绕过已有身份、资源、能力和确认门禁。formal Plan→Do 的当前suite是固定的通用建模验收，不是待生成的三个suite本身。Do→Check可诚实报告定义/测试不足，不能据此称业务通过。

modeling node_local_pass额外核对：NODE的双逻辑产物与引用用途、REUSE知识去向、DECOMP实际分解依据，以及当前节点三个scene的suite语义已定义（运行可not_run，设计不可not_defined）。这不要求孩子未来产物在父本地任务结束前存在。知识必需发布未完成阻止工作知识目标通过，不反向阻止已满足本地合同的正常结束；真实发布依EVOLVE。

## 逐谓词取证，不以限制说明替代准入

使用[gate-check](../../templates/gate-check.md)逐项记录本表**全部**必需谓词、当前对象、证据ref/digest、核验动作、实际观测和satisfied/unsatisfied/unknown；证据清单与门禁适用项必须双向覆盖，漏项按unknown。`decision=approved`只允许全部必需谓词satisfied；文件齐全、自述“已检查”、手填布尔值均不构成观测。失败核验另存诊断，不消耗四条边的sequence。

“无独立确认通道”“任务内正常推进”“不是范围变更”“不伪造确认”都不豁免CONFIRM-01。批准启动、根seed批准、整树批准不得代替当前Plan/Check批准。缺必需能力停在相应边界；候选材料可保留，但不能声明正式Do、正常archive或delivery_usable。

用户认可失败结论不改变失败事实。审查者发现别的节点缺陷可以本地合格；被影响对象的采用/冻结是否阻断由REWORK-01按issue的**实际影响范围**判断，不把所有open issue变成全局停机，也不把“发现者通过”当“被审者通过”。


`gate_predicate_ids` 将上表已有必需事实按类别稳定定位；不替代类别内部的完整条款。机械检查只验证这些类别与证据绑定，不认证真实能力/确认。


## 结果消费的最小核验顺序

按已有谓词执行，不新增审批者或转换边：固定要求及被核验对象 → 实际执行verification_action → 核对本次结果来源、退出状态、输入版本和方法范围 → 展开全部必需观察 → 计算判定及limitations。核验成功不读取报告的“100%”作为oracle；旧输入、新产物、漏要求、未支持检查或检查器异常均不能使相应谓词satisfied。

确定差异必须传入subject_conformance/对应AC；缺证据保持unknown，不推断操作未发生。失败材料可以进入诚实Check，真实确认可以认可失败；不得把阻止业务PASS误写成禁止正常失败收尾。工具仅验证维护子集时，其pass不满足范围更大的宿主、布局或发布谓词。最后提交仍按既有CONTROL/RESOURCE/CONFIRM核对真实资格，维护脚本不授予资格。
