---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-gcm
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-07
owl_versionIRI: http://pdca.local/ontology/cipher-mode-gcm/1.0.0
summary: GCM 工作模式（CTR 加密 + GHASH 认证）AEAD 一体、并行、IV 12B 不可重用
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:concept/cipher-mode
attributes:
- name: aead_structure
  desc: GCM 的 CTR+GHASH AEAD 结构（GHASH GF(2^128) + CTR 密钥流），分组密码 E 典型为 AES，国密实例为 SM4
  constraint: 须含 CTR 加密与 GHASH 认证并行交错、tag=GHASH(AAD,C) xor E(K,0^128)、IV 96位推荐不可重用；SM4 仅可作为 E 的实例出现，不得写死为主公式
  testable_signal: "运行 grep -q 'GHASH' ontology/concept/cipher-mode-gcm.md && grep -q 'CTR' ontology/concept/cipher-mode-gcm.md && grep -q '不可重用' ontology/concept/cipher-mode-gcm.md"
- name: hardware_acceleration
  desc: GCM 通用硬件分解：CTR 侧分组密码指令 + GHASH 侧有限域乘法指令
  constraint: 须含 AES-NI 加速 CTR 与 PCLMULQDQ 加速 GHASH；SM4 实例为 SM4E(4轮/次,8次32轮)+PMULL（如 arm64 sm4-ce-gcm 400 优先级），仅可作为实例出现
  testable_signal: "运行 grep -q 'AES-NI' ontology/concept/cipher-mode-gcm.md && grep -q 'PCLMULQDQ' ontology/concept/cipher-mode-gcm.md"
---

# GCM 工作模式

`GCM`（`Galois/Counter Mode`）为 `NIST SP 800-38D` 标准化的 `AEAD` 一体模式，分组密码 `E` 典型为 `AES`（即 `AES-GCM`），国密实例为 `SM4`（即 `SM4-GCM`，见 `GB/T 32907-2016`），二者同构。

## 结构

`GCM = CTR 加密 + GHASH 认证` 并行交错。`CTR` 段 `keystream = E(K, nonce||ctr)` 生成密钥流异或明文；`GHASH` 段 `tag = GHASH(AAD, C) xor E(K, 0^128)` 在 `GF(2^128)` 上多项式哈希 `AAD` 与密文，全长 `tag 128b`，标准允许截断至 `32–128b`（截断直接降低伪造界）。`AAD` 明文传输但纳入认证，改动即验签失败。

## 不变量

- **AEAD 一体**：加密与认证一次完成，无需外加 `HMAC`。
- **均并行**：`CTR` 与 `GHASH` 均可多路并行。
- **无填充**：流式 `CTR`，任意长度。
- **IV 96位推荐不可重用**：`nonce 96b` 为推荐长度（其他长度经 `GHASH` 压缩派生，性能与安全次之）；同一 `key` 下 nonce 重用双后果——`CTR` 密钥流重用泄露明文异或，`GHASH` 子密钥 `H` 可恢复致任意伪造。`ZFS` 取 `12B` 约束为实例（`zfs/module/os/linux/zfs/zio_crypt.c:752` 的 `ZIO_DATA_IV_LEN`）。
- **单 IV 加密上限约 64GB**：`32` 位计数器耗尽即须换 `IV`。
- **验签失败整体丢弃**：解密 `Final` 重算比对，不一致不得区分错因、不得降级放行（防预言机；NBU `mangle` 解密 `Final` 失败丢弃即此规则实例）。

## 硬件分解

通用分解：`AES-NI`（`AESENC`）加速 `CTR` 的分组密码，`PCLMULQDQ` 加速 `GHASH` 的有限域乘法。SM4 实例：`SM4E Vd=SM4_4Round(Vn,Vm)`（`4` 轮/次，`8` 次 `32` 轮）加速 `CTR`，`PMULL` 加速 `GHASH`，`arch/arm64/crypto/sm4-ce-gcm` 以 `400` 优先级自动择优为例。

Source: `NIST SP 800-38D` + `GB/T 32907-2016` + `arch/arm64/crypto/sm4-ce-gcm-core.S:741` + `T2071 evidence/21-tag-iv-asm.txt`（NBU 每调随机 12B IV、16B Tag 实例）
