---
schema: pdca.asset/v2
id: ontology:concept/pdca-ai-friendly-confirmation
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.1
summary: 按任务独立交互与真实确认
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-verdict
  - ontology:concept/task-rework
  - ontology:concept/task-control
confirmation_spec:
  kind_phases:
    plan_confirmation:
    - plan
    check_confirmation:
    - check
    clarification:
    - plan
    - do
    - check
    - act
  request_decision_required: true
  identity_fields:
  - task_id
  - attempt
  - request_id
  - kind
  - phase
  - conversation_ref
  - subject_ref
  - subject_digest
  timeout_authority: CONTROL-01
---

# 独立交互、真实来源与确认消费

## CONFIRM-01：一个任务一个明确会话

每task_id/attempt绑定conversation_ref，用户可独立进入。统一界面可以按ID无损路由，不由父Agent理解后代答/批准。任务请求保存control/requests，真实响应保存control/responses，单一宿主请求决策保存control/decisions；响应可来自用户消息或可信宿主回执，不能由执行Agent自行签字。

| kind | 允许phase | 确认对象 | 有效响应 |
|---|---|---|---|
| plan_confirmation | plan | 当前CONTRACT-01冻结基线 | confirmed/rejected/needs_change |
| check_confirmation | check | 当前固定结论包，含suite/verdict | confirmed/rejected/needs_change |
| clarification | plan/do/check/act | 明确事实问题及对象 | clarification_answer |

澄清不批准阶段、不扩大权限、不改变冻结oracle。Check对失败判定的confirmed可使任务进入Act，但不把业务outcome改成成功。拒绝/needs_change保持阶段；必要时按REWORK-01提出返工，不能偷回Do。

## 请求身份、来源与准入谓词

任务请求/响应必须匹配task_id、attempt、request_id、kind、phase、conversation_ref、subject_ref/digest。请求还固定派发已授权的wait_policy_ref/digest、具体化deadline/time_source（explicit_wait明确无截止），生产者、范围/风险。完整基线校验与真实用户确认是两个独立条件。

接纳用户回应先验证真实source_ref、actor、当前对象版本和请求类型；歧义“同意”只能澄清本请求。可一次明确确认多个具名对象及各自摘要，每个对象独立记录相同真实来源；未来对象、未列任务、新attempt不能继承此授权。

实际消息接收不等于消费。由CONTROL-01单一可信事件所有者创建不可变request-decision；Agent引用已消费决策，不重写回应。有效阶段确认必须为匹配对象的consumed/confirmed、当前任务未stopping/interrupted、未被后续取消/替代、授权控制视图仍有效。decision保留source和后端排序依据；摘要固定内容但不认证身份。

## 等待、期限和迟到回应

等待策略、截止时比较、confirmed与expired竞争统一由CONTROL-01定义，不在这里复制另一套时钟。explicit_wait允许持续等待并保留取消；deadline_interrupt到期不批准、不自动授权重试。相同请求只取一个终局；已expired/cancelled/superseded的请求收到迟到回应只记审计，不复活旧任务。

confirmed先消费也不能免于随后真实用户取消，下一阶段提交仍核对控制资格。新的请求必须新request_id；同对象已有有效响应不重复索要。等待只暂停当前任务，不占用无关节点的会话或隐式控制其phase。

## 用户取消与异常接续

真实取消在任何非终态都按CONTROL-01安全停止；取消确认不是第五个方法阶段，也不是替代原Check业务判定。先停止新增动作、对账在途操作、撤销写权，才能记录interrupted和接续条件。Agent不得为绕过Check确认自行取消并派新Agent继续修改。

## 整树确认

TREE-01采用独立工作级tree_confirmation schema，不混入任务请求kind。身份为work/tree/proposal/request/work_conversation/manifest_digest，无task_id/phase；同样需要wait-policy、request-decision和当前发布资格。过期仅阻止该提案冻结，不复活已完成根Agent。其余来源/终局原则相同，节点Plan/Check确认不能代替整树确认。

## 启动批准与阶段批准的边界

用户“开始任务/开始优化”只授权该请求范围内的工作，不是对尚未生成基线、Check包、后继attempt或整树提案的预先签认。相同真实消息可明确列明多个已存在对象；每个消费决策仍绑定自己的task/attempt/request/object摘要。无可核实来源或排序时保持待确认，不由Agent生成一个confirmed作为补偿。

真实消息已明确确认同一对象时复用合法来源，不重复询问。内容改变必须新请求；禁止重写历史响应、替换其摘要或把本次重新核对时间写成原批准时间。
