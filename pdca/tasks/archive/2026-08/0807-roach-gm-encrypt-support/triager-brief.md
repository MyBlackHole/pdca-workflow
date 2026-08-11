# Triager Brief

- task: T0228-0807-roach-gm-encrypt-support
- 日期: 2026-08-07
- 分类: enhancement / research

## 需求描述

使用 tmux 会话 0:2:0（远程机器 10.6.67.38，路径 /opt/cluster/usr/local/core/app_1da42ed9/bin）分析 gs_roach 是否支持国密加密，两种形式：
1. 存储数据加密
2. TLS 传输加密

## 分类依据

"分析 X 是否支持 Y" → enhancement / research。

## 查重结果

- `pdca/tasks/` 无同主题任务。
- knowledge 命中仅共享背景：T0148（NBU 传输加密调研，对象为 NBU 非 roach）、T0164（GM TLS 基准测试，对象为 GMSSL 库性能），均非 gs_roach 国密支持分析，无直接重复。

## Claim 验证

### 环境确认
- gs_roach 版本：`Roach (GaussDB Kernel 505.2.1 build 1da42ed9) compiled 2024-12-27 commit 10161`
- 链接库：自有 `libssl.so`、`libcrypto.so`（OpenSSL 3.0.9，2023-05-30）
- 环境变量已设 PGSSLROOTCERT/PGSSLCERT/PGSSLKEY/OPENSSL_CONF（指向 share/sslcert）

### 静态 + 运行时证据（tmux 会话实测）

| 维度 | 证据 | 结论 |
|------|------|------|
| 底层 libssl 国密套件 | strings 含 `ECC-SM4-GCM-SM3`/`ECC-SM4-SM3`/`ECDHE-SM4-GCM-SM3`/`ECDHE-SM4-SM3`/SM2KEP | ✅ 底层库具备国密 TLCP 能力 |
| 底层 libcrypto 国密算法 | strings 含 SM2/SM3/SM4 全系列 | ✅ 底层库具备 SM 算法 |
| openssl ciphers | `ECC-SM4-GCM-SM3` 等 4 个 GMTLS 套件在列 | ✅ OpenSSL 3.0.9 承认国密套件 |
| gs_roach 自身 TLS 套件 | strings 硬编码 AES 系列 + `TLS_AES_128/256_GCM_*`；nm 无 SM/EVP_sm 符号 | ❌ gs_roach 自身不配置国密套件 |
| gs_roach 存储加密算法 | nm/strings 仅 `EVP_aes_128_cbc`、`roach_aes128_decrypt`、`DecryptAes128Cbc` | ❌ 存储加密通路 AES-128-CBC |
| 透明加密 | `roach_get_ak_sk_for_trans_encrypt`、`gs_encrypted_columns` 查询、AK/SK 校验 | ✅ 支持透明加密（AK/SK），算法为 AES |
| cipher list 可覆盖 | `Failed to set cipher list to XBSA_BACKUP_CIPHER_LIST`（编译期宏），无外部入口 | ❌ 无法运行时覆盖为国密 |
| 证书 | roach sslcert 下 server.crt/client.crt = RSA + sha256WithRSAEncryption | ❌ 当前证书 RSA，非 SM2；无 server_enc.crt |
| backUpAgent | nm/strings 无 SM 符号，仅 EVP_aes_128_cbc | ❌ 与 gs_roach 一致 |

### 官方文档佐证（GaussDB / openGauss）
- 国密 SSL/TLCP（SM2 双证书 + SM4-SM3 套件）**仅支持 gsql/JDBC 客户端与服务端之间**，需 `ssl_enc_cert_file`/`PGSSLENCCERT`/`sslgmcipher`(ECC_SM4_SM3|ECDHE_SM4_SM3)、`ssl_use_tlcp`。
- SSL 预置证书表中 `roach`（gs_roach master 与 agent 通信）与 `xbsa`（gs_roach 与 backUpAgent 通信）仅作为普通 SSL 传输证书，文档未提供 gs_roach 侧国密参数；且 gs_roach 证书禁用 PKCS#1_V1.5。
- gs_roach SSL 认证默认开启，可用 `--disable-ssl` 关闭。
- openGauss 自 2.0 起 SM3 认证 + SM4 加解密（gs_encrypt/gs_decrypt 支持 aes128/sm4），列级 CEK 支持 SM4_SM3。

### 初步结论
gs_roach（505.2.1 build 1da42ed9）**自身不支持国密加密**：
- TLS 传输：二进制硬编码 AES 套件、无国密开关；底层 libssl 3.0.9 具备国密套件但未被工具启用；官方明确国密仅限 gsql/JDBC。
- 存储加密：透明加密（AK/SK）+ 备份数据走 AES-128-CBC，无 SM4 通路。
- 需国密时，只能通过上层替代方案。

## 信息缺口
- 结论产出形式已确认（结论文档 + knowledge 条目）。
- 是否实测国密握手：当前环境无 SM2 证书且工具无国密入口，实测价值低，默认不做；如需可另行任务。

## 下一步
补充 P3 PRD 验收标准，进入 P6 终审。