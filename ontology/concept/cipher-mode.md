---
schema: pdca.asset/v2
id: ontology:concept/cipher-mode
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cipher-mode/3.1.0
summary: 分组密码工作模式元概念：ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM 的 chaining 方式抽象
relations:
  relates_to:
  - ontology:domain/encryption-modes
  specializes:
  - ontology:concept/entity
attributes:
- name: mode_abstraction
  desc: 模式抽象（chaining 方式决定并行/认证/随机访问/填充/IV）
  constraint: 须含 ECB(独立)/CBC(链式)/CTR(计数器)/GCM(AEAD) 的抽象区分
  testable_signal: 运行 grep -q 'ECB' ontology/concept/cipher-mode.md && grep -q 'GCM' ontology/concept/cipher-mode.md
    && grep -q 'AEAD' ontology/concept/cipher-mode.md
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# 工作模式元概念

分组密码工作模式定义 `128b 明文块 → 128b 密文块` 的 chaining 方式，正交决定 `并行 / 认证 / 随机访问 / 填充 / IV`。

- **独立**：`ECB` 每块独立 `C=SM4(K,P)`。
- **链式**：`CBC` 前块密文反馈。
- **流**：`CFB/OFB` 密钥流 `SM4(K, feedback)` 异或明文。
- **计数器**：`CTR/GCM` `keystream=SM4(K, nonce||ctr)`。
- **AEAD**：`GCM/CCM` 加密+认证一体，`IV` 不可重用。

特化见 `ontology:concept/cipher-mode-gcm`、`ontology:concept/cipher-mode-cbc` 等。
