---
schema: pdca.asset/v2
id: ontology:concept/pdca-ai-friendly-confirmation
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: CONFIRM-01：每阶段目标沟通与用户显式启动
confirmation_spec:
  kind_phases:
    phase_start:
    - plan
    - do
    - check
    - act
    clarification:
    - plan
    - do
    - check
    - act
  advance_policy: explicit_user_operation
  future_blanket_approval: false
  work_action_scope: work_not_phase
  work_actions:
  - create_tasks
  - freeze_tree
  - start_scene
  - migrate
---

# CONFIRM-01：每阶段目标沟通与用户显式启动

## 请求与授权

所有 Plan、Do、Check、Act 的**开始**都要有 `kind=phase_start` 请求；`phase` 表示待启动的目标阶段。Plan 入口请求包含问题、目标、范围、非目标、约束和预期产物；Do 包含批准计划和写域；Check 固定产物及验收依据；Act 固定检查结论、处置、发布／知识权限。

请求显示给用户，包含 task/attempt/scene、目标阶段、run_id、原会话、固定输入及 subject_ref/digest。对象摘要由实际字节计算，不能用“待计算”、模板占位或仅标题。首次 Plan 前只做目标沟通和最小能力核验，不能把建模／写业务文件放到所谓准备步骤。

上阶段报告可同时提出下一阶段对象；一个明确回应即可启动，不重复审批。只有一个未变的当前待确认事项时自然语言“同意”可绑定它；多个事项或内容变化必须澄清。可批量批准**已经存在且逐项具名**的不同任务当前对象，不预批未来阶段或未来模型版本。

`clarification` 只补事实，不授权阶段／扩大写域。`confirmed` 表示允许该阶段开始，不表示验收通过。阶段完成且所有检查通过也不产生下一阶段授权。

## 工作级操作不是第五阶段

具名任务创建、整树冻结、场景启动、迁移可复用同一request/response/decision用途，kind=work_action、scope_kind=work，绑定work_id、tree_revision、action和固定对象；task/attempt/phase/run留空。不得拿工作级消息直接批准未来阶段。一次真实消息可同时明确列出当前已固定的工作动作与阶段对象，各自记录引用，不重复盘问。共享发布如属于当前Act，应列入Act的具体处置权限，不另启动隐藏流程。

## 来源与消费

使用原生用户消息 ID／可恢复 transcript、actor、路由会话和原始文本。Agent 可保存引用或抄录，但不得将自己的总结、父 Agent转述、`source:user` 标签当真实来源。哈希只固定内容，不认证发言者。无法核实用户消息就等待，不自动补 signed/consumed。

请求、响应、request-decision 沿用三个现有记录用途。匹配 task/attempt/request/phase/run/subject/conversation；请求终局只有 consumed、rejected、cancelled、superseded。消耗一次后重复消息幂等返回原状态，不能启动新 run。物化 decision 必须引用实际 response 和可信顺序；执行者自填 confirmed 没有原生来源仍无效。

## 等待与变更

阶段结束保存完成事件，execution_state=awaiting_confirmation，当前 phase 保持最后实际阶段。无超时自动批准；取消／撤权优先。输入、目标、验收或计划变化使关联未消费请求失效，新对象重新沟通。已批准但尚未执行的对象变化同样不得运行。

Plan 完成不是 Do 授权；Do 完成不是 Check 授权；Check 完成不是 Act 授权。Act 启动需明确是否仅归档、是否发布或沉淀；用户未授权发布，不从“接受”推断。树冻结、知识发布和新场景另有具名对象，不被阶段批准覆盖。
