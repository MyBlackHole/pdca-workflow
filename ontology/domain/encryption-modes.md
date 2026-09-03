---
schema: pdca.asset/v1
id: ontology:domain/encryption-modes
type: domain
layer: Knowledge
status: active
summary: 分组密码工作模式族（ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM）不变量与 AEAD/随机访问/IV 约束
relations:
  specializes:
  - ontology:domain/backup-crypto
  relates_to:
  - ontology:domain/backup-crypto-gm-support-surfaces
attributes:
- name: mode_invariants
  desc: 8 模式不变量（并行/认证/填充/IV/随机访问）正交分类
  constraint: 须覆盖 ECB(并行无认证泄露)/CBC(加密串行无认证)/CTR(均并行无认证)/XTS(盘加密 tweak)/GCM(CCM 为 AEAD，IV 不可重用)
  testable_signal: "运行 grep -q 'GCM.*AEAD.*GHASH' ontology/domain/encryption-modes.md && grep -q 'XTS.*tweak' ontology/domain/encryption-modes.md && grep -q 'ECB.*泄露' ontology/domain/encryption-modes.md"
- name: aead_boundary
  desc: AEAD 一体性边界（GCM/CCM 为唯二 AEAD，IV/nonce 不可重用）
  constraint: 须含 GCM(CTR+GHASH 并行) 与 CCM(CBC-MAC+CTR 串行) 为 AEAD，IV 12B/唯一性约束
  testable_signal: "运行 grep -q 'AEAD' ontology/domain/encryption-modes.md && grep -q '不可重用' ontology/domain/encryption-modes.md && grep -q 'GCM.*CTR.*GHASH' ontology/domain/encryption-modes.md"
- name: storage_adaptation
  desc: 存储适配约束（随机访问/盘加密/流）
  constraint: 须含 ECB(禁用)/CTR(最佳并行)/XTS(盘加密窃取法) 的存储适配判定
  testable_signal: "运行 grep -q '随机访问' ontology/domain/encryption-modes.md && grep -q '盘加密' ontology/domain/encryption-modes.md"
---

# 分组密码工作模式族

分组密码（如 `SM4/AES 128b`）的工作模式定义 `明文块→密文块` 的 chaining 方式，决定 `并行 / 认证 / 随机访问 / 填充 / IV` 五力权衡。

## 1. 模式不变量

| 模式 | 原理 | 并行 | 认证 | 填充 | IV/tweak | 随机访问 |
|------|------|------|------|------|----------|----------|
| ECB | 独立 `C=SM4(K,P)` | 均并行 | 无 | 需 | 无 | ✓ |
| CBC | 链式 `C_i=SM4(K,P_i xor C_{i-1})` `C_0=IV` | 加密串行 | 无 | 需 | 随机 | × |
| CFB | 流 `keystream=SM4(K,C_{i-1})` | 解密并行 | 无 | 无 | 随机 | △ |
| OFB | 流 `O_i=SM4(K,O_{i-1})` | 均串行 | 无 | 无 | 不可重用 | ✓预计算 |
| CTR | 计数器 `keystream=SM4(K,nonce||ctr)` | 均并行 | 无 | 无 | 不可重用 | **✓最佳** |
| XTS | `C=P xor E(K2,tweak) → SM4(K1) → xor` `tweak=LBA` | 均并行 | 无 | 窃取法 | tweak | ✓ |
| **GCM** | `CTR+GHASH` `tag=GHASH(AAD,C) xor SM4(K,0)` | 均并行 | **AEAD** | 无 | 12B不可重用 | ✓ |
| CCM | `CBC-MAC+CTR` | 认证串行 | **AEAD** | 需 | 唯一 | ✓ |

`ECB` 因同明文同密文泄露相等性，存储中禁用；`CBC/CFB/OFB/CTR/XTS` 无认证，需外加 `HMAC`；`GCM/CCM` 为唯二 `AEAD` 一体。

## 2. AEAD 一体性

`GCM`（`CTR` 加密 + `GHASH GF(2^128)` 认证并行交错）与 `CCM`（`CBC-MAC` 认证串行 + `CTR` 加密）为 `AEAD` 唯二，`IV/nonce` 绝不可重用（`GCM` 重用泄露 `GHASH` 密钥）。

## 3. 存储适配

- **随机访问**：`CTR/GCM/XTS` 均并行最佳，`CBC` 加密串行不适大块。
- **盘加密**：`XTS` 以 `tweak=LBA` 使同扇区同明文不同密文，无额外存储，窃取法免填充，为 `FDE` 专用。
- **流/文件名**：`CFB/CTS` 流无填充适小块。

## 4. 门禁

- `grep -q 'GCM.*AEAD.*GHASH' ontology/domain/encryption-modes.md && grep -q 'XTS.*tweak' ontology/domain/encryption-modes.md && grep -q 'ECB.*泄露' ontology/domain/encryption-modes.md`
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues
