---
schema: pdca.asset/v1
id: ontology:domain/gm-algorithm-suite
type: domain
layer: Knowledge
status: active
summary: 国密算法体系 SM1-SM9 本体与 SM4 模式族（ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM）及指令分解
relations:
  specializes:
  - ontology:domain/backup-crypto
  relates_to:
  - ontology:domain/zfs-crypto
  - ontology:domain/backup-crypto-gm-support-surfaces
attributes:
- name: algorithm_coverage
  desc: SM1-SM9 算法本体覆盖（标准/类型/参数/作用）
  constraint: 须覆盖 SM1(分组未公开)/SM2(GB/T 32918 256b 椭圆曲线)/SM3(GB/T 32905 512→256 杂凑)/SM4(GB/T 32907 128/128 32轮 Feistel) 及 SM7/SM9
  testable_signal: "运行 grep -q 'SM4E' ontology/domain/gm-algorithm-suite.md 且 grep -q 'SM4_GCM' ontology/domain/gm-algorithm-suite.md 且 grep -q 'GB/T 32907' ontology/domain/gm-algorithm-suite.md"
- name: mode_coverage
  desc: SM4 对称模式族覆盖（ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM）及 AEAD/随机访问/IV约束
  constraint: 须覆盖 ECB(泄露)/CBC(串行需HMAC)/CFB/OFB(流)/CTR(并行)/XTS(盘加密)/GCM(CCM 为 AEAD，ZFS仅GCM)
  testable_signal: "运行 grep -q 'GCM.*AEAD' ontology/domain/gm-algorithm-suite.md 且 grep -q 'XTS.*盘加密' ontology/domain/gm-algorithm-suite.md"
- name: instruction_decomposition
  desc: SM4E/SM4EKEY 指令分解与 SM4-GCM = SM4+CTR+GHASH 映射
  constraint: 须含 SM4E(Vd=4Round)/SM4EKEY(下4轮密钥) 及 PMULL 的 GHASH 加速，8×SM4E 完成32轮
  testable_signal: "运行 grep -q 'SM4E' ontology/domain/gm-algorithm-suite.md 且 grep -q 'GHASH.*PMULL' ontology/domain/gm-algorithm-suite.md"
---

# 国密算法体系与 SM4 模式族

> 来源：`records/T0539-0903-research-zfs-pcie-sm4/evidence/research-report.md:§0.4 + §2.1`（`GM/T 32907/32905/32918 + GB/T 38636/2020 + GM/T 0018-2012/2023`）

## 1. 算法本体（SM1-SM9）

| 算法 | 标准 | 类型 | 参数 | 作用 | 存储/传输定位 |
|------|------|------|------|------|---------------|
| SM1 | `GM/T` 分组（未公开） | 对称 128/128，**卡内** | 轮数未公开，`SDF SGD_SM1_*`，密钥不出卡 | 分组加解密 | 派科卡 `SM1-CBC` 主力，`ZFS` 无 `SM1` 套件 |
| SM2 | `GB/T 32918-2016` | 椭圆曲线 `256b` `y²=x³+ax+b` | 密钥 `256b`，签名/加密/密钥交换 | 签名、密钥协商 | `ZFS` 的 `SDF ECC` 密钥管理（`SDF_GenerateKeyPair_ECC`），非数据面 |
| SM3 | `GB/T 32905-2016` | 杂凑 `512→256` `Merkle-Damgård` 64轮 | `IV 256b` | 摘要、HMAC、KDF | `ZFS HKDF-SHA512` 对标，`HMAC-SM3` 为 `B系列内核` 形态 |
| **SM4** | **`GB/T 32907-2016`** | **分组 `128/128` 32轮 `Feistel`** `S-box 256 + L/L'` | `FK[4]/CK[32]` `X_{i+4}=X_i xor T(X_{i+1} xor X_{i+2} xor X_{i+3} xor CK)` | 分组加解密 | **`ZFS` 唯一 `SM4-GCM`**（`sm4.c:13`） |
| SM7/SM9 | `GM/T` | 标识/IBE | `IBE` 无证书 | 标识加密 | 卡可选，`ZFS` 无 |

## 2. SM4 模式族（8 模式）

| 模式 | 原理 | 并行 | 认证 | 填充 | IV 要求 | 随机访问 | ZFS 结论 |
|------|------|------|------|------|---------|----------|----------|
| ECB | 独立块 | 均并行 | 无 | 需 | 无 | ✓ | **禁用**：泄露相等性 |
| CBC | 链式 `P xor C_{i-1}` | 加密串行 | 无 | 需 | IV随机 | × | 需 `HMAC`，`B系列` 内核 `CBC-HMAC` 即此 |
| CFB | 流 `C_{i-1}` 反馈 | 解密并行 | 无 | 无 | IV随机 | △ | 小文件/文件名 |
| OFB | 流 `O_{i-1}` 反馈 | 均串行 | 无 | 无 | IV不可重用 | ✓预计算 | 不适 |
| CTR | 计数器 `SM4(K,nonce)` | 均并行 | 无 | 无 | nonce不可重用 | **✓最佳** | 需 `HMAC` |
| XTS | `tweak` 扇区号 | 均并行 | 无 | 窃取法 | tweak=LBA | ✓ | 全盘优选（`fscrypt` 用） |
| **GCM** | `CTR+GHASH` | 均并行 | **AEAD** | 无 | IV 12B不可重用 | ✓ | **ZFS现选** |
| CCM | `CBC-MAC+CTR` | 认证串行 | **AEAD** | 需 | nonce唯一 | ✓ | 可替 `GCM` |

`GM/T 0018-2012` 仅 `ECB/CBC/CFB/OFB/MAC`，`2023` 新增 `GCM/CCM/XTS/CTR`；`ZFS` 仅 `GCM`（`sm4.c:13 GCM-only`），存量卡 `ECB/CBC` 对 `ZFS GCM` 零收益。

## 3. 指令分解：SM4E/SM4EKEY 与 `SM4-GCM = SM4 + CTR + GHASH`

- **SM4E `Vd=SM4_4Round(Vn,Vm)`**：对 `Vn(128b 数据)` 用 `Vm(轮密钥)` 做 4 轮 `SM4`（`S-box+L`），8 次完成 32 轮；**SM4EKEY `Vd=NextKey(Vn,Vm)`** 由 `Vn`+`Vm(CK)` 生成下 4 轮轮密钥（`arch/arm64/crypto/sm4-ce-gcm-core.S:741`）。
- **GCM 分解**：`GCM = CTR 加密 + GHASH 认证`，`CTR` 的 `SM4` 由 `SM4E/SM4EKEY` 加速（`8×SM4E` 并行 4-8 路），`GHASH(tag=GHASH(AAD,C) xor SM4(K,0))` 由 `PMULL/PMULL2` (`GF(2^128)`) 加速，`sm4-ce-gcm 400` 交错流水达 `1.7-1.9 GB/s`（`kernel_shangmi`）。
- **ZFS 映射**：`zfs/module/icp/io/sm4.c:33` `gcm_mode_encrypt` 即 `SM4(CTR)+GHASH`，`generic` 查表 `S-box`，`ce-gcm 400` 替换为 `SM4E+PMULL`；`qat_crypt.c:170` 拦截因 `QAT` 无 `SM4E` 硬件。

## 4. 门禁

- `grep -q 'SM4E' ontology/domain/gm-algorithm-suite.md && grep -q 'GCM.*AEAD' ontology/domain/gm-algorithm-suite.md && grep -q 'GB/T 32907' ontology/domain/gm-algorithm-suite.md`
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues
- `grep -q 'gm-algorithm-suite' ontology/domain/zfs-crypto.md`（可选关联）

Source: `records/T0539-0903-research-zfs-pcie-sm4/evidence/research-report.md:§0.4 + §2.1` + `zfs/module/icp/io/sm4.c:13,33` + `arch/arm64/crypto/sm4-ce-gcm-core.S:741` + `GM/T 32907/32905/32918`
