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
  digest: 008cccba8788a9ba5f83d42809f09fccb96524349d150850001d9657419c3957
response:
  ref: response.md
  digest: 2e02f424003ba21f2c7bf616c876d9a7aa4201993550c677a00f0de758f20b02
decision:
  ref: decision.md
  digest: 5d5570b16c1d00a5c70abf2d0433c5458890b574c75403c63e4d1265c5f458bd
control:
  state: running
  writer: fixture-task-T
requested_edge: plan_to_do
business_verdict: null
---

固定合成对象，不认证任何真实身份或历史事件。
