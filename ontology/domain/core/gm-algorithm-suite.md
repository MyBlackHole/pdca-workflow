---
schema: pdca.asset/v1
id: ontology:domain/gm-algorithm-suite
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/gm-algorithm-suite/1.0.0
summary: 国密算法体系（SM1-SM4/SM7/SM9）本体与 SM4 分组结构及对称模式族不变量
relations:
  specializes:
  - ontology:domain/backup-crypto
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:domain/zfs-crypto
  - ontology:domain/backup-crypto-gm-support-surfaces
attributes:
- name: algorithm_family
  desc: 国密算法族划分（对称 SM1/SM4、非对称 SM2、杂凑 SM3、标识 SM7/SM9）及标准归属
  constraint: 须区分 SM1(未公开分组,卡内)/SM2(GB/T 32918 256b 椭圆曲线)/SM3(GB/T 32905 512→256 杂凑)/SM4(GB/T 32907 128/128 Feistel) 及 SM7/SM9
  testable_signal: "运行 grep -q 'GB/T 32907' ontology/domain/gm-algorithm-suite.md 且 grep -q 'GB/T 32905' ontology/domain/gm-algorithm-suite.md 且 grep -q 'GB/T 32918' ontology/domain/gm-algorithm-suite.md"
- name: sm4_structure
  desc: SM4 分组结构（S-box/L/Feistel 32轮）与密钥调度
  constraint: 须含 S-box 256项、L/L' 线性变换、FK[4]/CK[32]、X_{i+4}=X_i xor T(...) 32轮 Feistel
  testable_signal: "运行 grep -q 'S-box' ontology/domain/gm-algorithm-suite.md 且 grep -q 'Feistel' ontology/domain/gm-algorithm-suite.md && grep -q '32轮' ontology/domain/gm-algorithm-suite.md"
- name: sm4_instruction_decomposition
  desc: SM4E/SM4EKEY 指令分解与 SM4-GCM 的 CTR+GHASH 映射
  constraint: 须含 SM4E(Vd=4Round,8次完成32轮)/SM4EKEY 及 PMULL 的 GHASH，8×SM4E 完成32轮
  testable_signal: "运行 grep -q 'SM4E' ontology/domain/gm-algorithm-suite.md && grep -q 'GHASH' ontology/domain/gm-algorithm-suite.md && grep -q 'PMULL' ontology/domain/gm-algorithm-suite.md"
---

# 国密算法体系与 SM4 结构

## 1. 算法族

国密算法按功能正交划分为对称、非对称、杂凑、标识四族，标准族为 `GB/T 32907/32905/32918` 与 `GM/T`。

| 算法 | 标准 | 类型 | 密钥/参数 | 功能 |
|------|------|------|-----------|------|
| SM1 | `GM/T` 分组（未公开） | 对称 128/128，卡内 | 轮数未公开，`SGD_SM1_*` | 分组加解密 |
| SM2 | `GB/T 32918-2016` | 椭圆曲线 `256b` `y²=x³+ax+b` | 曲线 `256b`，签名/加密/密钥交换 | 签名、密钥协商 |
| SM3 | `GB/T 32905-2016` | 杂凑 `512→256` `Merkle-Damgård` 64轮 | `IV 256b` | 摘要、HMAC、KDF |
| **SM4** | **`GB/T 32907-2016`** | **分组 `128/128` 32轮 `Feistel`** | `FK[4]/CK[32]` | 分组加解密 |
| SM7/SM9 | `GM/T` | 标识/IBE | `IBE` 无证书 | 标识加密 |

`SM1/SM4` 为对称加解密，`SM2` 为非对称，`SM3` 为杂凑，三者经 `SM2-ECDH + SM3-KDF + SM4-AEAD` 组合为全栈。

## 2. SM4 分组结构

`SM4` 为 `32` 轮 `Feistel`，每轮 `X_{i+4}=X_i xor T(X_{i+1} xor X_{i+2} xor X_{i+3} xor CK_i)`，`T = L ∘ τ`，`τ` 为 `S-box`（`256` 项 `8b` 置换）按字节查表，`L(B)=B xor ROTL(B,2) xor ROTL(B,10) xor ROTL(B,18) xor ROTL(B,24)`，`L'(B)=B xor ROTL(B,13) xor ROTL(B,23)` 用于密钥调度。密钥调度由 `FK[4]` 与 `CK[32]` 生成 `32` 轮密钥 `RK[32]`。

## 3. 对称模式族（独立域）

对称模式族详见独立域 `ontology:domain/encryption-modes`（`ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM` 按 `认证/并行/随机访问/填充/IV` 正交分类）。本域仅保留与国密的交集：`GM/T 0018-2012` `SDF` 仅 `ECB/CBC/CFB/OFB/MAC`，`2023` 新增 `GCM/CCM/XTS/CTR`。

## 4. 指令分解

`SM4E Vd=SM4_4Round(Vn,Vm)` 对 `Vn(128b)` 用 `Vm(轮密钥)` 做 `4` 轮 `SM4`（`S-box+L`），`8` 次完成 `32` 轮；`SM4EKEY Vd=NextKey(Vn,Vm)` 由 `Vn`+`Vm(CK)` 生成下 `4` 轮轮密钥。`GCM = CTR 加密 + GHASH 认证`：`CTR` 的 `SM4` 由 `SM4E/SM4EKEY` 加速（`8×SM4E` 并行 `4-8` 路），`GHASH(tag=GHASH(AAD,C) xor SM4(K,0))` 由 `PMULL`（`GF(2^128)`）加速，`sm4-ce-gcm` 将两者交错流水。

Source: `GM/T 32907-2016` + `GB/T 32905-2016` + `GB/T 32918-2016` + `GM/T 0018-2012/2023` + `arch/arm64/crypto/sm4-ce-gcm-core.S`
