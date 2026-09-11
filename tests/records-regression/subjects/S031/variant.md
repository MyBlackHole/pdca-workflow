---
constraints:
- VERSION_BINDING
run:
  artifact:
    ref: artifact-v1.md
    digest: 71c051abe6eaa03b21d11cfa46d6628af35a7c1b10895e9a3ad8cc8949273567
  result: pass
  required_cases:
  - C1
  - C2
claimed_artifact:
  ref: artifact-v2.md
  digest: 851b5985f6d7ac24777e9d4fecec386812e9cd03dda23ae167d84066f0248a7f
---

固定合成对象，不认证任何真实身份或历史事件。
