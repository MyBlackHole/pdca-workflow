---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-ofb
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cipher-mode-ofb/1.0.0
summary: OFB 工作模式（流 O_{i-1} 反馈）均串行、预计算、IV 不可重用、错误不扩散
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: feedback_structure
  desc: OFB 反馈结构（O_i = SM4(K, O_{i-1})，C = P xor O_i，O_0=IV）
  constraint: 须含 O_{i-1} 反馈、均串行、预计算
  testable_signal: "运行 grep -q 'O_{i-1}' ontology/concept/cipher-mode-ofb.md && grep -q '均串行' ontology/concept/cipher-mode-ofb.md"
- name: iv_constraint
  desc: IV 不可重用与错误特性（预计算、1位错误仅影响1位）
  constraint: 须含 IV 不可重用（重用=密钥流重用）、预计算、错误不扩散
  testable_signal: "运行 grep -q '不可重用' ontology/concept/cipher-mode-ofb.md && grep -q '预计算' ontology/concept/cipher-mode-ofb.md"
---

# OFB 工作模式

`OFB`（`Output Feedback`）为流反馈模式，`O_i = SM4(K, O_{i-1})`，`C = P xor O_i`，`O_0 = IV`。

## 不变量

- **均串行**：`O_i` 依赖 `O_{i-1}`，加密解密均串行。
- **预计算**：`keystream` 可在 `P` 到达前预计算。
- **IV 不可重用**：`IV` 重用即密钥流重用，`C1 xor C2 = P1 xor P2` 灾难。
- **错误不扩散**：1 位密文错误仅影响 1 位明文（对比 `CBC` 的 1 块）。

Source: `NIST SP 800-38A`
