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
  digest: b1a8c97c87dd0b7b01fed23648cb4d59d78bc32e90d3306acd80fe1ed6c5b113
response:
  ref: response.md
  digest: d0a5508f3c70a5de1ae101b0d2947a922e8ea8fa4b5ded349ead5d230e6cb815
decision:
  ref: decision.md
  digest: 4328c77bf5fb759a472c9aebf7f127403d19b6952fadd8d3e67e64cb2e773f25
control:
  state: running
  writer: fixture-task-T
requested_edge: plan_to_do
business_verdict: null
---

固定合成对象，不认证任何真实身份或历史事件。
