---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-ctr
type: concept
layer: Knowledge
status: active
summary: CTR 工作模式（计数器 SM4(K,nonce||ctr)）均并行、无填充、需HMAC 补认证、nonce 不可重用
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: counter_structure
  desc: CTR 计数器结构（keystream = SM4(K, nonce||ctr)，C = P xor keystream）
  constraint: 须含计数器 nonce||ctr、密钥流异或、均并行
  testable_signal: "运行 grep -q 'nonce' ontology/concept/cipher-mode-ctr.md && grep -q 'keystream' ontology/concept/cipher-mode-ctr.md"
- name: nonce_constraint
  desc: nonce 不可重用与需 HMAC
  constraint: 须含 nonce 不可重用（重用=密钥流重用）、无认证需 HMAC
  testable_signal: "运行 grep -q '不可重用' ontology/concept/cipher-mode-ctr.md && grep -q 'HMAC' ontology/concept/cipher-mode-ctr.md"
---

# CTR 工作模式

`CTR`（`Counter`）为计数器流模式，`keystream = SM4(K, nonce||ctr)`，`C = P xor keystream`。

## 不变量

- **均并行**：每块 `ctr` 独立，可随机访问、预计算。
- **无填充**：流式异或，任意长度。
- **nonce 不可重用**：`nonce||ctr` 重用即密钥流重用，明文异或泄露。
- **无认证**：需外加 `HMAC-SM3/SHA512`（`CTR+HMAC` 为 `GCM` 的非一体替代）。

Source: `NIST SP 800-38A`
