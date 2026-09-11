---
schema: pdca.records-subject/v1
fixture_only: true
family: gate
task:
  task_id: T
  attempt: 1
  conversation_ref: C
  phase: check
target:
  ref: target.md
  digest: f6c0ad9c8b5ea28b7eb0c17c3942b068f31d74aa69dc6ec655eb0aad002ff9cc
request:
  ref: request.md
  digest: 27ed192affd3b2f1eeef79aee7268932cbe3393f0353bee2b6ad02cf85bcc662
response:
  ref: response.md
  digest: 941da5b48788727597bc4c0f8f4b5a7baf1fab34b90c3a775b4c038c5352f543
decision:
  ref: decision.md
  digest: 29d022f30b9e08256ddaf11728b658aee0df12453614122866fc543913e1d04d
control:
  state: running
  writer: fixture-task-T
requested_edge: check_to_act
business_verdict: rejected
---

固定合成对象，不认证任何真实身份或历史事件。
