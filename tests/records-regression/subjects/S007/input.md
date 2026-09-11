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
  digest: 3d40d09f4a672f1bd49c862c99fa34be260f113ce9d9ec1c24e2b397f156f1aa
decision:
  ref: decision.md
  digest: e410869e16c6595af758ae8fb3990584d8994fc284781e7d3ce1b0f38a1ccc4d
control:
  state: running
  writer: fixture-task-T
requested_edge: plan_to_do
business_verdict: null
---

固定合成对象，不认证任何真实身份或历史事件。
