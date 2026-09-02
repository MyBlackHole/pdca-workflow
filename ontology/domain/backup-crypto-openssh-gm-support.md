---
schema: pdca.asset/v1
id: ontology:domain/backup-crypto-openssh-gm-support
type: domain
layer: Knowledge
status: active
summary: OpenSSH 国密支持面（SM2/SM3/SM4）— openEuler 24.03 SP4
domain:
- ontology:domain/backup-crypto
relations:
  specializes:
  - ontology:domain/backup-crypto
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'openssh-gm' ontology/domain/backup-crypto-openssh-gm-support.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# OpenSSH 国密支持面（SM2/SM3/SM4）— openEuler 24.03 SP4

## 核心结论

openEuler 24.03 SP4 的 `openssh-9.6p1-16.oe2403sp4.src.rpm`（T0248 解压审计）通过补丁完整支持国密算法：

| 算法域 | 支持项 | 算法名 / 标识 | 来源补丁 |
|--------|--------|----------------|----------|
| 密钥 | SM2 密钥 | `KEY_SM2` / `KEY_SM2_CERT`，`ssh-keygen -t sm2`（`sm2-256`，`~/.ssh/id_sm2`） | `feature-add-SMx-support.patch` |
| 密钥交换 | SM2+SM3 KEX | `sm2-sm3`（`KEX_SM2_SM3`，`kexsm2.c`：SM2 KAP + Z 摘要） | 同上 |
| 对称加密 | SM4 | `sm4-ctr`（`EVP_sm4_ctr`） | 同上 |
| 摘要/MAC | SM3 | `SSH_DIGEST_SM3`；`hmac-sm3` | 同上 |
| 协商 | 追加白名单 | `PubkeyAcceptedAlgorithms +sm2,sm2-cert` | 同上 |

## OpenSSL 3.x 适配要点

`adaption-for-feature-sm2-support.patch`（2026-05）修复 OpenSSL 3.0 下 SM2 密钥 EVP 适配：

- `ssh-ecdsa.c`：`EVP_PKEY_is_a(res, "SM2")` 时走 `sm2_pkey_to_ec_key(res)`，否则用已废弃的 `EVP_PKEY_get1_EC_KEY`
- `ssh-keygen.c` / `sshkey.c`：SM2 密钥 OID/NID 识别与恢复兼容

> 规律：OpenSSL 3.x 中 SM2 私钥不能经 `EVP_PKEY_get1_EC_KEY` 直取，须先 `EVP_PKEY_is_a` 判定并走专用转换——移植 SM2 进 OpenSSL 3 生态的通用坑。

## 使用方式

```bash
ssh-keygen -t sm2                       # 生成 SM2 密钥
ssh -o KexAlgorithms=sm2-sm3 \
    -o Ciphers=sm4-ctr \
    -o MACs=hmac-sm3 host               # 国密协商（需对端同样支持）
```

## 边界与限制

- 静态补丁证据，未做运行态协商实测（需真实二进制 + 对端支持）
- 仅限该发行版补丁集；vanilla upstream OpenSSH 不包含国密
- 参考：本知识库 `backup-crypto/gm-support-surfaces.md` 归纳 SM2 在国产 CPU 上多为软件实现（GmSSL 等）

---
source_record: records/T0248-0812-openssh-src-unpack/conclusion.md
