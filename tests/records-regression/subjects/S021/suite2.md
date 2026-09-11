---
suite_id: S2
scene: ontology_conformance_verification
cases:
- id: P
  input: 合法实现
  expected: pass
  oracle: 固定实体约束
  required: true
- id: N
  input: 违反必需约束的实现
  expected: fail
  oracle: 同一固定实体约束
  required: true
runtime_result: not_run
---

固定合成对象，不认证任何真实身份或历史事件。
