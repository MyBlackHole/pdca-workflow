---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-cbc
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cipher-mode-cbc/1.0.0
summary: CBC 工作模式（链式 P xor C_{i-1}）加密串行、无认证、IV 随机、需 HMAC 补认证
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: chaining_structure
  desc: CBC 链式结构（C_i = SM4(K, P_i xor C_{i-1})，C_0=IV）
  constraint: 须含链式 xor、前块密文反馈、C_0=IV，加密串行/解密并行
  testable_signal: "运行 grep -q '链式' ontology/concept/cipher-mode-cbc.md && grep -q '串行' ontology/concept/cipher-mode-cbc.md"
- name: iv_and_auth
  desc: IV 随机性与无认证需 HMAC
  constraint: 须含 IV 随机不可预测、无认证需外加 HMAC-SM3/SHA512
  testable_signal: "运行 grep -q 'IV.*随机' ontology/concept/cipher-mode-cbc.md && grep -q 'HMAC' ontology/concept/cipher-mode-cbc.md"
---

# CBC 工作模式

`CBC`（`Cipher Block Chaining`）为链式分组模式，每块 `C_i = SM4(K, P_i xor C_{i-1})`，`C_0 = IV`。

## 不变量

- **加密串行**：`C_i` 依赖 `C_{i-1}`，不可并行；解密 `P_i = SM4^{-1}(K, C_i) xor C_{i-1}` 可并行。
- **IV 随机**：`IV` 需密码学随机且不可预测，否则首块泄露相等性。
- **无认证**：需外加 `HMAC-SM3/SHA512`（`GM/T B系列` 内核 `CBC-HMAC-SM3` 即此组合）。
- **需填充**：`PKCS#7` 填充至 `128b` 对齐。

## 后果

隐藏 `ECB` 的相等性泄露，但加密串行不适大块并行；`IV` 管理成本高于 `CTR/GCM` 的计数器。

Source: `NIST SP 800-38A` + `GB/T 32907-2016`
