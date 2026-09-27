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
dcterms_modified: '2026-09-27'
summary: CONFIRM-01：把真实用户回应绑定到固定对象
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

# CONFIRM-01：用户授权事实

CONFIRM-01 只回答：**一条可核实的用户回应，是否明确授权了某个已经固定的对象/动作。**
它不判断 phase 是否具备启动条件，不写 transition，也不决定 task execution_state。

## 三类记录

授权链只使用现有三类记录：

1. **request**：固定待决定的对象；
2. **response**：保存可核实的原始用户回应及来源；
3. **request-decision**：把 response 与 request 匹配并记录 consumed / rejected / cancelled / superseded。

精确字段只以对应 record-shape 为准，不在本页重复 schema。

## Phase start

Plan / Do / Check / Act 的开始都使用 `kind=phase_start`。
请求必须让用户能知道“批准的到底是什么”，至少固定对应 task/attempt、目标 phase/run、
subject 及其版本/摘要、当前会话和本 phase 需要用户决定的范围。

phase 的具体业务输入由各 `flow-*.md` 定义；CONFIRM 只负责固定待批准对象，不重新定义 Plan/Do/Check/Act 方法。

- `clarification` 只补事实，不授权 phase 或扩大写域；
- `confirmed` 只表示用户明确允许这个固定 phase_start 对象，**不表示 GATE 已通过**；
- 上一阶段完成、PASS、ready、Agent 建议都不能替代新的 phase_start 授权；
- 不允许预批未来 phase、未来 run 或未来模型/产物版本。

如果只有一个未变化的当前待确认对象，用户自然语言“同意”可以匹配它；
有多个对象、对象已变化或语义不唯一时必须澄清，不能猜。

## Work action

task creation、tree freeze、scene start、migration 等不是第五阶段，使用 `kind=work_action`。
它们固定 work/action/subject，不产生 phase_start，也不能预批随后 Plan。

一次真实用户消息可以同时明确批准多个**已经固定且逐项具名**的对象，
但每个对象仍有自己的 request/decision 引用；不能用一个宽泛批准覆盖尚不存在的 future object。

## 来源与消费

只接受可核实的原生用户来源：消息 ID、可恢复 transcript、actor、conversation/routing 事实等。
Agent 总结、父 Agent 转述、`source:user` 标签或内容哈希都不能独立认证“用户已批准”。

decision 是可审计投影，不是签发器。它必须引用真实 response 与可信顺序；
相同 request 消费一次后重复投递幂等返回既有结果，不创建第二个 run。

subject / 目标 / oracle / 固定输入发生变化时，原未消费或已确认对象都不能直接用于新对象；
旧 decision 保留历史，新的固定对象重新请求。是否因此能启动 phase 由 GATE-01 判断。
