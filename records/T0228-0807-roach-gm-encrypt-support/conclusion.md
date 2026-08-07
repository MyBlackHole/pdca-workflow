---
schema: pdca.asset/v1
id: T0228-0807-roach-gm-encrypt-support
phase: check
source_ids: [research-report-v2, convergence-map-v2]
---

## 上下文

用户询问 gs_roach（GaussDB Kernel 505.2.1 build 1da42ed9）是否支持国密加密。分两种形式：存储数据加密、TLS 传输加密。通过 tmux 会话 0:2:0 在远程机器 10.6.67.38 的 `/opt/cluster/usr/local/core/app_1da42ed9/bin` 现场分析。

## 假设与结果

| 假设 | 验证结果 | 证据 |
|------|---------|------|
| gs_roach 支持存储数据加密 | ✅ 支持透明加密（AK/SK + gs_encrypted_columns） | research-report nm/strings 符号 |
| gs_roach 存储加密算法为国密 SM4 | ❌ gs_roach 自身走 AES-128-CBC | nm 仅 EVP_aes_128_cbc，解密函数 roach_aes128_decrypt 等 |
| gaussdb 引擎（源数据）支持加密存储 | ✅ TDE 表级加密，enable_tde+tde_key_info+encrypt_algo | nm EVP_sm4_cbc/EVP_sm4_ctr；算法串 sm4_ctr_sm3 |
| gaussdb 引擎支持国密存储加密 | ✅ TDE 支持 SM4_CTR / SM4_CTR_SM3_HMAC（encrypt_algo='SM4_CTR'） | nm 符号 + GaussDB 透明数据加密文档 |
| gs_roach 支持 TLS 传输加密 | ✅ 支持（SSL 默认开启，--disable-ssl 可关） | --help、ssl 证书目录 |
| TLS 用国密套件 | ❌ 硬编码 AES 套件 | strings ECDHE-ECDSA-AES128-GCM..., TLS_AES_128/256_GCM |
| 底层库具备国密能力 | ✅ libssl/libcrypto 3.0.9 有 SM2/SM3/SM4/TLCP | strings/openssl ciphers |
| 工具二进制启用国密 | ❌ 无 EVP_sm，无 EVP_get_cipherbyname/fetch | nm -D SM_REF_COUNT=0 |
| 官方支持 gs_roach 国密 | ❌ 国密仅 gsql/JDBC 客户端与服务端之间 | GaussDB 安全管理文档 |

## 分析

1. gs_roach（备份工具）支持加密但不支持国密：
   - TLS 传输：SSL 默认开启，套件硬编码 AES 系列，cipher 列表为编译期宏（XBSA_BACKUP_CIPHER_LIST），无外部覆盖入口，证书为 RSA。
   - 存储：透明加密（AK/SK，roach_ak_sk.key），解密函数族 roach_aes128_decrypt/DecryptAes128Cbc（AES-128-CBC）；无 SM4（nm 无 EVP_sm4、无 EVP_get_cipherbyname/fetch）。
2. gaussdb 引擎（数据库本体/源数据）支持国密存储加密：
   - TDE 透明数据加密（表级），enable_tde on + tde_key_info（外部 KMS）+ encrypt_algo。
   - 支持算法：AES_128_CTR（默认）、SM4_CTR（国密）、AES_128_CTR_SHA256_HMAC、SM4_CTR_SM3_HMAC、AES_128_GCM。
   - nm 证据：EVP_sm4_cbc、EVP_sm4_ctr、g_sm4；算法串 sm4_ctr_sm3；密钥机制 dek_cipher、CLIENT_MASTER_KEY/CMK。
   - 官方文档：GaussDB 透明数据加密、openGauss 设置透明数据加密 TDE。
3. gs_roach 备份加密表时，数据本身已由引擎 TDE 加密；备份工具另以 AK/SK 透明加密（AES）与传输 SSL（AES）保障备份链路自身保密性。
4. 底层 libssl 3.0.9 具备国密 TLCP 套件与 SM2/SM3/SM4，但 gs_roach 二进制未启用；官方明确国密 SSL/TLCP 仅 gsql/JDBC 客户端与服务端之间，roach/xbsa 证书仅作普通 SSL 传输证书。

## 适用边界

- 适用于 GaussDB Kernel 505.2.1 build 1da42ed9（2024-12-27，现场实测结论）。
- 更新版本（GaussDB V2.0-8.x、openGauss 7.x）结论见"更新版本对比"；不适用于未来可能加入国密支持的版本；不能类推出 gsql/JDBC 的场景（那些已支持国密）。

## 更新版本对比（联网核实，2026-08-07）

| 维度 | 现场 505.x | 更新版本 GaussDB V2.0-8.x / openGauss 7.x |
|------|-----------|------------------------------------------|
| 引擎 TDE 国密存储加密 | SM4_CTR / SM4_CTR_SM3_HMAC | 新增 sm4_ctr_sm3_hmac 完整性校验算法；加密表库表级备份恢复（V2.0-8.200.0+） |
| gs_roach 备份工具自身传输 | SSL 默认开启，AES 套件，无国密 | 仍仅 --disable-ssl，SSL 默认开启，AES；备份工具传输无双国密参数 |
| gs_roach 备份 AK/SK 存储加密 | AES-128-CBC | 无文档表明 gs_roach 密钥通道改国密 |
| gsql/JDBC 国密 TLS/TLCP | 不支持（仅 JDBC 支持） | gsql(server)+JDBC 支持（SSL_PCIPH 国密套件） |
| 全密态列级 SM4/G用户 | 列级 CEK 支持 SM4_SM3（openGauss 5.0） | SMNA4_SM3、加密表、ALTER ... ENCRYPTED（openGauss 7.x 全密态） |

**更新版本结论**：国密能力的主增强在 **数据源（gaussdb 引擎 TDE 存储加密、gsql/晋JDBC 传输加密、全密态列级加密）**，这些均明确支持国密 SM2/SM3/SM4；而 **gs_roach 备份工具自身的备份传输/备份集 AK-SK 加密**，即使更新版本官方文档仍无国密参数（仅 AES + SSL 默认开启 + --disable-ssl）。

## 下一轮建议

- 如需端到端国密：应用侧/数据源充分利用引擎 TDE(SM4_CTR) + gsql/JDBC 国密传输；备份工具本身用上层替代方案——备份链路前置国密 TLS 网关/隧道，或备份集导出后 SM4 加密归档。
- 可作为后续"国密合规备份方案设计"任务输入。

## 结论

**gs_roach 备份工具（505.2.1 build 1da42ed9）本身支持存储数据加密（透明加密 AES-128-CBC）与 TLS 传输加密（AES 套件），但不支持国密 SM2/SM4；其底层 libssl 具备国密能力但工具未启用，官方国密 SSL/TLCP 仅 gsql/JDBC 支持。而数据源 gaussdb 引擎本身支持国密存储加密（TDE：enable_tde + encrypt_algo='SM4_CTR'/SM4_CTR_SM3_HMAC）。**