---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-gcm
type: concept
layer: Knowledge
status: active
summary: GCM 工作模式（CTR 加密 + GHASH 认证）AEAD 一体、并行、IV 12B 不可重用
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:concept/cipher-mode
attributes:
- name: aead_structure
  desc: GCM 的 CTR+GHASH AEAD 结构（GHASH GF(2^128) + CTR 密钥流）
  constraint: 须含 CTR 加密与 GHASH 认证并行交错、tag=GHASH(AAD,C) xor SM4(K,0)、IV 12B 不可重用
  testable_signal: "运行 grep -q 'GHASH' ontology/concept/cipher-mode-gcm.md && grep -q 'CTR' ontology/concept/cipher-mode-gcm.md && grep -q '不可重用' ontology/concept/cipher-mode-gcm.md"
- name: sm4_acceleration
  desc: SM4-GCM 的 SM4E/SM4EKEY + PMULL 硬件分解
  constraint: 须含 SM4E(4轮/次,8次32轮) 加速 CTR 的 SM4，PMULL 加速 GHASH，sm4-ce-gcm 400 优先级
  testable_signal: "运行 grep -q 'SM4E' ontology/concept/cipher-mode-gcm.md && grep -q 'PMULL' ontology/concept/cipher-mode-gcm.md"
---

# GCM 工作模式

`GCM`（`Galois/Counter Mode`）为 `NIST SP 800-38D` 标准化的 `AEAD` 一体模式，`SM4-GCM` 与 `AES-GCM` 同构。

## 结构

`GCM = CTR 加密 + GHASH 认证` 并行交错。`CTR` 段 `keystream = SM4(K, nonce||ctr)` 生成密钥流异或明文；`GHASH` 段 `tag = GHASH(AAD, C) xor SM4(K, 0)` 在 `GF(2^128)` 上多项式哈希 `AAD` 与密文，`tag 128b` 存 `cksum`。

## 不变量

- **AEAD 一体**：加密与认证一次完成，无需外加 `HMAC`。
- **均并行**：`CTR` 与 `GHASH` 均可 `4-8` 路并行，`sm4-ce-gcm-core.S` 交错流水达 `1.7 GB/s`。
- **无填充**：流式 `CTR`，任意长度。
- **IV 12B 不可重用**：`nonce 96b` 重用泄露 `GHASH` 密钥，`ZFS` 为 `ZIO_DATA_IV_LEN 12B` 约束（`zfs/module/os/linux/zfs/zio_crypt.c:752`）。

## 硬件分解

`SM4E Vd=SM4_4Round(Vn,Vm)`（`4` 轮/次，`8` 次 `32` 轮）加速 `CTR` 的 `SM4`，`PMULL` 加速 `GHASH`，`arch/arm64/crypto/sm4-ce-gcm` 以 `400` 优先级自动择优。

Source: `NIST SP 800-38D` + `GB/T 32907-2016` + `arch/arm64/crypto/sm4-ce-gcm-core.S:741`
