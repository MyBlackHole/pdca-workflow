---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-ccm
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cipher-mode-ccm/1.0.0
summary: CCM 工作模式（CBC-MAC + CTR）AEAD 认证串行、需填充、nonce 唯一、可替 GCM
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:concept/cipher-mode-gcm
attributes:
- name: aead_structure
  desc: CCM 的 CBC-MAC 认证 + CTR 加密串行结构
  constraint: 须含 CBC-MAC 认证串行、CTR 加密并行、tag 128b、需填充
  testable_signal: "运行 grep -q 'CBC-MAC' ontology/concept/cipher-mode-ccm.md && grep -q 'AEAD' ontology/concept/cipher-mode-ccm.md"
- name: nonce_constraint
  desc: nonce 唯一性与可替 GCM
  constraint: 须含 nonce 唯一不可重用、可替 GCM 但性能略低
  testable_signal: "运行 grep -q '唯一' ontology/concept/cipher-mode-ccm.md && grep -q '可替.*GCM' ontology/concept/cipher-mode-ccm.md"
---

# CCM 工作模式

`CCM`（`Counter with CBC-MAC`）为 `AEAD` 一体模式，`tag = CBC-MAC(AAD, P)`，`C = CTR(P)`。

## 不变量

- **认证串行**：`CBC-MAC` 需串行计算 `tag`，加密 `CTR` 可并行，整体认证瓶颈。
- **需填充**：`CBC-MAC` 需 `PKCS#7` 填充至块对齐。
- **nonce 唯一**：`nonce` 不可重用，否则 `CBC-MAC` 泄露。
- **可替 GCM**：`ZFS AES-CCM` 已有三套件，`SM4` 若增 `CCM` 复用 `modes/ccm.c`，性能略低于 `GCM` 的 `GHASH` 并行。

Source: `NIST SP 800-38C` + `GB/T 32907-2016`
