---
schema: pdca.transition-receipt/v3.2
task_id: LC08-OLD
sequence: 1
from: plan
to: do
previous_receipt_digest: null
baseline_digest: bc0db796124d10145875ae2cf74274815612fee2d27828cf6d407b1fd3e206fc
gate_id: plan_to_do
inputs:
- ref: baseline.md
  digest: bc0db796124d10145875ae2cf74274815612fee2d27828cf6d407b1fd3e206fc
confirmation_refs:
- ref: plan_response.md
  digest: 27b688481c78533e0a07c8ecd1a6755f7ebaf839b79c74ac25f164bb64443157
test_run_refs: []
result_package_refs: []
decision: approved
actor_ref: fixture:old-agent
recorded_at: fixture-order:10
protocol_revision: 3.4.4
attempt: 1
inputs_digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
confirmation_decision_refs:
- ref: plan_decision.md
  digest: d6ddca3f81fb775ca4b2c07b76cbe9dec0e782c0e47570f9846bc9bf7bee27f3
writer_grant_ref:
  ref: source.md
  digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
observed_control_revision: 1
commit_receipt_ref:
  ref: commit.md
  digest: 2ac6ad621b2f8f88469bdfb2d63f3a4e056326f6a4a3be8f8f16d4d9cadcb882
state_spec_ref: ontology:concept/pdca-phase-status
inputs_manifest_ref:
  ref: source.md
  digest: 8498ef449cab9edf4fdafd420ea94e56aa6da1a0b93cf923de8aa1231f67e790
gate_check_ref: gate.md
gate_check_digest: 825921732de58238364153f2487f58f527d69d97b500e832da5f4acfff9787e1
---

合成生命周期测试记录（fixture）。没有实际派发、真实用户批准、执行撤权、写权交回或生产I/O；不作为生产证据。
