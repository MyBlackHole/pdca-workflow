---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-ecb
type: concept
layer: Knowledge
status: active
summary: ECB 工作模式（独立块 C=SM4(K,P)）均并行、无IV、泄露相等性、存储禁用
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: independence_leakage
  desc: ECB 独立块与相等性泄露（同明文同密文）
  constraint: 须含独立块 C=SM4(K,P)、泄露相等性、存储中禁用
  testable_signal: "运行 grep -q '泄露.*相等性' ontology/concept/cipher-mode-ecb.md && grep -q '禁用' ontology/concept/cipher-mode-ecb.md"
---

# ECB 工作模式

`ECB`（`Electronic Codebook`）为独立分组模式，每块 `C = SM4(K, P)` 独立加密。

## 不变量

- **均并行**：块间无依赖。
- **泄露相等性**：同明文块得同密文块，泄露明文相等性（`P1=P2 → C1=C2`）。
- **存储禁用**：任何多块存储场景禁用，仅测速/填充对比用。

Source: `NIST SP 800-38A`
