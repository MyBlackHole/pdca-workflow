---
schema: pdca.records-subject/v1
fixture_only: true
family: coverage
constraints:
- id: CP_RECURSE
  field: child_policy
  allowed: assess_recursively
  positive: &id001
    ref: positive.md
    digest: d7db131f9f404579ef78a2b4b4ef3d102911fafa8d1a3e4a7c1bf15963096235
  negative:
    ref: sample-1.md
    digest: 727b5f562dbd46fa485a1671d4c67af6a0d7fbf8a5397f8df4c227be18630b18
- id: CP_SHARE
  field: knowledge_policy
  allowed: shared_read_only
  positive: *id001
  negative: null
---

固定合成对象，不认证任何真实身份或历史事件。
