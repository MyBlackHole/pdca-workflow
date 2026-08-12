# Do 阶段执行说明 — T0248

## 执行摘要

- 解压 src.rpm：`/home/black/Downloads/openssh-9.6p1-src/` 根级文件 + 114 个补丁移入 `patches/`
- 源码树：`src/openssh-9.6p1/`（configure/README/ssh.c 存在）
- `.asc` 签名校验：尝试 keyserver.ubuntu.com 与 pgp.mit.edu，均"服务器故障"；缺公钥 `7168B983815A5EEF59A4ADFD2A3F414E736060BA`，校验未完成（PRD 允许失败不阻塞）
- 国密证据：基于 `feature-add-SMx-support.patch` 与 `adaption-for-feature-sm2-support.patch` 静态内容

## AC 映射

| AC | 状态 | 证据 |
|----|------|------|
| AC-1 | 完成 | rpm-manifest-count.txt（134 包内条目 / 114 patches 计数）+ 目标目录存在 |
| AC-2 | 完成 | patches/ 含 feature-add-SMx-support.patch、adaption-for-feature-sm2-support.patch |
| AC-3 | 完成 | src/openssh-9.6p1/ 含 configure/README/ssh.c |
| AC-4 | 完成（记录失败） | gpg 校验记录：缺公钥，keyserver 故障 |
| AC-5 | 完成 | SM-清单.md 覆盖 SM2 密钥/KEX、SM3 摘要/MAC、SM4-CTR |

## 国密结论

OpenSSH 9.6p1 (oe2403sp4) 支持：SM2 密钥（`ssh-keygen -t sm2`）、`sm2-sm3` KEX、`sm4-ctr` cipher、`hmac-sm3`/SM3 摘要；含 OpenSSL 3.x SM2 EVP 适配。详细见 SM-清单.md。