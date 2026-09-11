---
schema: pdca.fixture-proposal/v1
fixture_only: true
proposal_id: FIX-candidate-B
library_id: FIX-LIB
definition_id: FIX/Range
base_revision: r1
base_digest:
  algorithm: sha256
  value: f915023b583367b115f3c4b416e2e26e2dcca0b21124e207088a450f63c3749b
base_manifest_digest:
  algorithm: sha256
  value: 6a2b99de554a75bf6059bd14d301ab385022009e4b682e31e1577b3786c65466
candidate_change: 禁止外部读I/O的解释与观测说明
state: candidate
production_authorization: null
---

A/B最初都基于r1。教学中A提交后，B必须重新检查base，不可串行覆盖。具体实际临时文件试验由外部验证器执行；本文件不伪造已发布事件。
