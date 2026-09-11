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
    digest: 6605aec8fa8d46d6775cc698eb46d90143d8676e104934aaaffd5efcec80b7af
- id: CP_SHARE
  field: knowledge_policy
  allowed: shared_read_only
  positive: *id001
  negative:
    ref: sample-2.md
    digest: a845f8a06aee8b98f4adab09f3a7492607769897d14d50e74fcf7cd4543f36f8
---

固定合成对象，不认证任何真实身份或历史事件。
