# 样本节点补 domain/docType/tags（AC-4）

以下现有节点已追加可选人读字段；仅追加，未改动 `type`/`id`/`relations`，故 `ontology-validate` 仍通过（`type==目录名` 等约束不变）。

| 节点 | domain | docType | tags |
|------|--------|---------|------|
| `ontology/entity/x509-certificate.md` | TLS/mTLS | Entity | [x509, cert] |
| `ontology/concept/pdca.md` | PDCA | Concept | [pdca, meta-ontology] |
| `ontology/pattern/mtls-handshake-enum-unify.md` | TLS/mTLS | Pattern | [mtls, enum] |
| `ontology/principle/structured-mtls-failure-diagnostics.md` | TLS/mTLS | Principle | [mtls, diagnostics] |

验证见 `validation.md`（`ontology-validate` OK + 既有测试无回归）。
