---
schema: pdca.asset/v1
id: ontology:concept/ghash
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-07
dcterms_modified: 2026-09-07
owl_versionIRI: http://pdca.local/ontology/ghash/1.0.0
summary: GHASH 有限域多项式认证哈希（GF(2^128) Horner 求值，密钥 H=E(K,0)，ε-AXU 不可伪造界）
relations:
  relates_to:
  - ontology:concept/cipher-mode-gcm
  - ontology:domain/encryption-modes
attributes:
- name: poly_structure
  desc: GHASH 的 Horner 多项式结构（GF(2^128)，约化多项式 x^128+x^7+x^2+x+1，末尾长度块）
  constraint: 须含 Horner 求值、GF(2^128)、H=E(K,0^128)、len(AAD)||len(C) 长度块
  testable_signal: "运行 grep -q 'Horner' ontology/concept/ghash.md && grep -q 'GF(2^128)' ontology/concept/ghash.md && grep -q '长度块' ontology/concept/ghash.md"
- name: unforgeability_bound
  desc: GHASH 的 ε-AXU 不可伪造界（q 次伪造、l 块长度下约 q·l/2^128，截断 Tag 直接降界）
  constraint: 须含 AXU、伪造界 q·l/2^128、截断代价
  testable_signal: "运行 grep -q 'AXU' ontology/concept/ghash.md && grep -q '伪造' ontology/concept/ghash.md && grep -q '截断' ontology/concept/ghash.md"
- name: reuse_collapse
  desc: Nonce 重用致 H 可解的崩塌条件与弱密钥 H=0
  constraint: 须含重用解 H（禁断攻击）、H=0 弱密钥、与 CTR 密钥流重用的双后果区分
  testable_signal: "运行 grep -q '禁断' ontology/concept/ghash.md && grep -q 'H=0' ontology/concept/ghash.md && grep -q '重用' ontology/concept/ghash.md"
---

# GHASH 认证哈希

`GHASH` 是 `GCM` 的认证半壁：把 `AAD` 与密文 `C` 按 `16B` 切块 `X1…Xn`（末尾追加 `len(AAD)||len(C)` 长度块），以子密钥 `H = E(K, 0^128)` 为求值点，在 `GF(2^128)`（约化多项式 `x^128+x^7+x^2+x+1`）上做 `Horner` 求值 `Y = X1·H^n + … + Xn·H`，最终 `Tag = Y xor E(K, J0)`。

## 安全性在哪里

三层，缺一即崩：

1. **`H` 机密 → AXU 不可伪造界**：`H` 由分组密码在固定输入下导出，对无密钥者伪随机。`GHASH` 是 `ε-AXU`（近异或泛哈希）族：不同输入在未知 `H` 下碰撞/伪造概率 `≤ l/2^128`（`l` 为块数）；`q` 次在线伪造总界约 `q·l/2^128`。这就是 Tag `128b` 对应 `2^-128` 伪造概率的来源；Tag 截断到 `t` 位则界直接降到约 `q·2^-t`。
2. **掩码一次一密**：`E(K, J0)` 对哈希值做一次一密式遮蔽，同一 `(AAD,C)` 在不同 `nonce` 下 Tag 不同；掩码流 `CTR` 与哈希可并行是 GCM 高速的原因。
3. **归约到底层与 nonce 唯一**：以上两条分别归约到分组密码是伪随机置换（`H` 与掩码不可区分于随机）与同一 `key` 下 `nonce` 永不重用。

## 崩塌条件

- **Nonce 重用（禁断攻击）**：同一 `nonce` 下两组 `(C,T)` 联立即得关于 `H` 的线性方程，可解出 `H`，之后任意伪造。这是 GCM 最严重的失败模式，与 `CTR` 密钥流重用泄明文异或是两个独立后果。
- **弱密钥 `H=0`**：此时 `GHASH` 恒为零，认证完全消失（概率极低但标准明确保留该 caveat）。
- **单 IV 约 64GB**：`32` 位计数器耗尽则 `CTR` 回绕，等同重用。

## 硬件分解

`GHASH` 即大数乘累加，`PCLMULQDQ`（`x86`）/`PMULL`（`arm64`）一条指令完成 `GF(2^128)` 乘法；与 `AES-NI/SM4E` 的 `CTR` 部分交错流水即 `GCM` 高速实现。

Source: `NIST SP 800-38D` + `T2071 evidence/21-tag-iv-asm.txt`（NBU `Final` 验签即重算比对实例）
