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
  digest: 3eb4e8c14524bb8815d152d5b8d593661b0755d41742c2eb6c5a30a3c3495d7a
decision:
  ref: decision.md
  digest: d03fcb258a53aa2ae7212cc8bf7496048a52c2df973d89735cccb70145807b35
control:
  state: running
  writer: fixture-task-T
requested_edge: plan_to_do
business_verdict: null
---

固定合成对象，不认证任何真实身份或历史事件。
