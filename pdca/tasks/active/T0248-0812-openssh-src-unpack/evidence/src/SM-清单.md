# OpenSSH 9.6p1 (16.oe2403sp4) 国密支持清单

来源：`/home/black/Downloads/openssh-9.6p1-src/patches/feature-add-SMx-support.patch`（华为 renmingshuai，2023-07）与 `adaption-for-feature-sm2-support.patch`（zhaoyonghao，2026-05），经 `openssh.spec` `Patch61` 应用，随 openEuler 24.03 SP4 构建默认启用。

## 摘要

| 算法域 | 支持项 | 算法名 / 标识 |
|--------|--------|----------------|
| 密钥生成/签名 | SM2 密钥 | `KEY_SM2` / `KEY_SM2_CERT`，`ssh-keygen` 类型 `sm2`（`sm2-256`）、`sm2-cert` |
| 密钥交换 | SM2 + SM3 KEX | `sm2-sm3`（`KEX_SM2_SM3`，`kexsm2.c` +406 行，SM2 KAP + Z 摘要） |
| 对称加密 | SM4 | `sm4-ctr`（`EVP_sm4_ctr`，16B key/IV） |
| 消息认证/摘要 | SM3 | `SSH_DIGEST_SM3`；`hmac-sm3` |
| 算法协商 | 追加白名单 | `PubkeyAcceptedAlgorithms +sm2,sm2-cert` |

## 详细支撑点

### 1. SM2 密钥（ssh-sm2.c，+381 行）
- 新增 `ssh-sm2.o`、`ssh-sm2.c`，`KEY_SM2`（25 处）、`KEY_SM2_CERT`（9 处）
- `ssh-keygen` 支持生成 `sm2` 类型密钥，私钥路径 `_PATH_SSH_CLIENT_ID_SM2` → `~/.ssh/id_sm2`
- regress 中 `sm2-256` 作为 keytype，`ssh-keygen` 输出 `sm2` 类型

### 2. SM2-SM3 密钥交换（kexsm2.c，+406 行）
- `kex.c` 增加 `KEX_SM2_SM3`（11 处），注册 `kexsm2.o`
- `kexsm2.c` 实现 `sm2_compute_z_digest`（SM2 Z 值）、`sm2_kap_compute_key`、`SM2KAP_compute_key`（`EC_KEY_new_by_curve_name(NID_sm2)` + `EVP_sm3()` 的 SM2 KAP）
- `kexecdh.c` 对 `NID_sm2` 分支走 SM2KAP 而非标准 ECDH

### 3. SM4-CTR 对称加密（cipher.c）
```c
{ "sm4-ctr", 16, 16, 0, 0, 0, EVP_sm4_ctr }
```

### 4. SM3 摘要与 HMAC
```c
{ SSH_DIGEST_SM3, "SM3", 32, EVP_sm3 }        // digest.h SSH_DIGEST_SM3=5
{ "hmac-sm3", SSH_DIGEST, SSH_DIGEST_SM3, 0, 0, 0, 0 }   // mac.c
```

### 5. OpenSSL 3.x 适配（adaption-for-feature-sm2-support.patch，2026-05）
- `ssh-ecdsa.c`：`EVP_PKEY_is_a(res, "SM2")` 时走 `sm2_pkey_to_ec_key(res)`，否则 `EVP_PKEY_get1_EC_KEY`（该函数在 OpenSSL 3 已废弃）
- `ssh-keygen.c` / `sshkey.c`（+75/89 行）：SM2 密钥 OID/NID 识别与恢复兼容

## 调用方式

```bash
# 生成 SM2 密钥
ssh-keygen -t sm2
# 使用国密 KEX（需双方协商）
ssh -o KexAlgorithms=sm2-sm3 -o Ciphers=sm4-ctr -o MACs=hmac-sm3 host
```

## 说明
- 未验证运行态实际协商结果（需真实二进制与对端支持），清单仅依据源码补丁静态证据。
- `.asc` 签名校验因公钥服务器故障未完成（缺公钥 7168B983815A5EEF59A4ADFD2A3F414E736060BA）。