---
schema: pdca.asset/v1
id: T0248-0812-openssh-src-unpack
phase: check
source_ids: [sm-support-list, rpm-manifest, do-notes]
---

## 上下文

用户请求按 PDCA 流程解压 `/home/black/Downloads/openssh-9.6p1-16.oe2403sp4.src.rpm`，并在过程中提出"openssh 是否支持国密"。经方向确认，任务范围扩展为：解压源码包 + 产出国密（SM2/SM3/SM4）支持清单。用户批准 PRD 全案（final_confirmation confirmed），验收标准 AC-1~AC-5。

## 假设与结果

| 假设 | 结果 |
|------|------|
| src.rpm 可完整解压 | ✅ 解压成功，根级文件 + 114 个补丁 + 源码 tar |
| 目标目录组织为 src/ + patches/ | ✅ 补丁入 patches/（114），源码树入 src/openssh-9.6p1/ |
| .asc 签名校验可完成 | ⚠️ 未完成：keyserver（ubuntu/mit）均服务器故障，缺公钥 7168B983815A5EEF59A4ADFD2A3F414E736060BA；按 PRD 约定失败不阻塞 |
| 国密支持清单可依据补丁生成 | ✅ SM2 密钥/KEX、SM3 摘要/MAC、SM4-CTR 均有补丁内静态证据 |

## 分析

### AC 达成情况
- **AC-1** ✅：`/home/black/Downloads/openssh-9.6p1-src/` 含 `openssh-9.6p1.tar.gz`、`openssh.spec`、114 个补丁；与 rpm 包内清单一致（evidence: rpm-manifest）
- **AC-2** ✅：`patches/feature-add-SMx-support.patch`、`patches/adaption-for-feature-sm2-support.patch` 可定位
- **AC-3** ✅：`src/openssh-9.6p1/` 含 configure/README/ssh.c
- **AC-4** ✅（记录为未完成）：gpg 校验因 keyserver 故障+缺公钥未完成，已在 do-notes 记录
- **AC-5** ✅：SM-清单.md 覆盖 sm2-sm3 KEX、sm4-ctr cipher、hmac-sm3/SM3、sm2/sm2-cert 密钥

### 国密支持结论
OpenSSH 9.6p1 (16.oe2403sp4) **支持国密**：
- **密钥**: SM2（`ssh-keygen -t sm2`，KEY_SM2/KEY_SM2_CERT，id_sm2）
- **KEX**: `sm2-sm3`（kexsm2.c，SM2 KAP + Z 摘要 + SM3）
- **Cipher**: `sm4-ctr`（EVP_sm4_ctr）
- **MAC/摘要**: `hmac-sm3`、SSH_DIGEST_SM3
- **OpenSSL 3.x 适配**: `EVP_PKEY_is_a(res,"SM2")` + `sm2_pkey_to_ec_key()`（adaption 补丁，2026-05）

## 失败原因（仅 rejected/partial）

不适用 — 结论 confirmed。

## 适用边界

- 国密结论基于**补丁静态内容**，未验证运行态协商（需真实二进制+对端支持）
- `.asc` 签名未验证，tarball 完整性依赖 rpm 官方签名链路
- 清单针对 16.oe2403sp4 发行版补丁集，不适用于上游 vanilla OpenSSH

## 下一轮建议

- 如需运行态验证：解出 rpm 二进制或用 spec 构建源码，实测 `ssh -Q kex/cipher/mac` 与 SM2 握手
- 如需补丁深度审计：对 feature-add-SMx-support.patch 逐文件评审（kexsm2.c/ssh-sm2.c 安全实现）
