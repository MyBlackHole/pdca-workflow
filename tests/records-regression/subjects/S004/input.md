---
schema: pdca.records-subject/v1
fixture_only: true
family: gate
task:
  task_id: T
  attempt: 1
  conversation_ref: C
  phase: plan
target:
  ref: target.md
  digest: 2b3f771d736b51f0c8e1d85ba82bc50f47defcabb3b0c949a453742e6b388b89
request:
  ref: request.md
  digest: b42394b9777867d061f322031decbe49aa7ec6d279b0a74f9a43478afc313ef0
response:
  ref: response.md
  digest: e57e0c4ea11793f047935e1b2ad4fcb044ca7106f729c8509119072be4633903
decision:
  ref: decision.md
  digest: 69911562155072165ad7fbd5339120a0e5651e9b7ffc4ff97f137df0735fd183
control:
  state: running
  writer: fixture-task-T
requested_edge: plan_to_do
business_verdict: null
---

固定合成对象，不认证任何真实身份或历史事件。
