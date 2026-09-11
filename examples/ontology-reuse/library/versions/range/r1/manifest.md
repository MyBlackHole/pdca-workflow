---
schema: pdca.fixture-manifest/v1
fixture_only: true
library_id: FIX-LIB
definition_id: FIX/Range
revision: r1
payload:
  kind: definition
  ref: library/versions/range/r1/definition.md
  digest:
    algorithm: sha256
    value: f915023b583367b115f3c4b416e2e26e2dcca0b21124e207088a450f63c3749b
closure:
- kind: term
  ref: library/terms/byte-r1.md
  digest:
    algorithm: sha256
    value: 2e476a16340f06debf495433b9056925b2b003b38fba229de7a97d0e06e2f01f
- kind: case-suite
  ref: library/cases/range-s1.md
  digest:
    algorithm: sha256
    value: 1fd3dc6df37db0faf3e05743a02de0d90e27524c737ddb2dfc17f79942e7efd5
publication_receipt: null
---

没有实际发布回执。只有字节/闭包fixture，用baseline_snapshot作为教学绑定；真实published_release必须有EVOLVE-01来源。
