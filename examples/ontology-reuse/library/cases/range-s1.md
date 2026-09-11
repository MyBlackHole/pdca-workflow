---
schema: pdca.fixture-suite/v1
fixture_only: true
suite_id: FIX/RANGE
revision: s1
cases:
- case_id: P-END
  input:
    N: 16
    offset: 15
    length: 1
  expected:
    allow: true
    code: OK
- case_id: N-END
  input:
    N: 16
    offset: 15
    length: 2
  expected:
    allow: false
    code: E_BOUNDS
- case_id: N-LOWER
  input:
    N: 16
    offset: -1
    length: 1
  expected:
    allow: false
    code: E_DOMAIN
host_result: NOT_RUN
---

只用于演示固定案例规范如何引用，非完整范围suite。真实范围基准仍在examples/range-task。actual不可从expected复制。
