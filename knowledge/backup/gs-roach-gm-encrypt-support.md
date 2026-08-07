# gs_roach 国密加密能力边界

- 来源: records/T0228-0807-roach-gm-encrypt-support/conclusion.md
- 日期: 2026-08-07

## 一句话结论

**gs_roach 备份工具本身不支持国密（备份传输 + 备份集 AK/SK 存储加密均为 AES）；而数据源 gaussdb 引擎（TDE 透明加密）支持国密存储加密（SM4_CTR / SM4_CTR_SM3_HMAC），国密 SSL/TLCP 仅 gsql/JDBC 客户端与服务端之间支持。**

## 分层结论

| 层 | 加密能力 | 国密支持 |
|----|---------|---------|
| gs_roach 备份传输 | SSL 默认开启，套件硬编码 AES（ECDHE-ECDSA-AES128-GCM-SHA256 等 + TLS_AES_128/256_GCM） | 不支持国密 |
| gs_roach 备份集存储 |透明加密 AK/SK（roach_ak_sk.key），AES-128-CBC | 不支持国密 |
| gaussdb 引擎存储 | TDE 表级透明加密：enable_tde + tde_key_info(KMS) + encrypt_algo | 支持 SM4_CTR、SM4_CTR_SM3_HMAC |
| gsql/JDBC 传输 | SUPPORT SSL/TLCP |支持国密（ECC-SM4-* / ECDHE-SM4-*） |

## 关键证据（现场二进制 505.2.1 build 1da42ed9）

- gs_roach 的 `nm -D` 全部 EVP_* 符号中只有 `EVP_aes_128_cbc`；无 `EVP_sm4*`、无 `EVP_get_cipherbyname`、无 `EVP_CIPHER_fetch`（即无法动态加载 SM4）。解密函数族 `roach_aes128_decrypt`/`DecryptAes128Cbc`。
- gs_roach cipher 列表来自编译期宏 `XBSA_BACKUP_CIPHER_LIST`（报错串可佐证），无外部配置入口覆盖；证书为 RSA + SHA256。
- 底层 libssl/libcrypto 3.0.9 具备国密 TLCP 套件（ECC-SM4-GCM-SM3 等）与 SM4 算法，但 gs_roach 未启用。
- gaussdb 引擎 `nm` 有 `EVP_sm4_cbc`/`EVP_sm4_ctr`，算法串含 `sm4_ctr_sm3`，TDE 密钥机制（dek Cipher、CLIENT_MASTER_KEY/CMK、enable_tde）完整。

## 更新版本对比（GaussDB V2.0-8.x / openGauss 7.x）

- 引擎 TDE 新增 `sm4_ctr_sm3_hmac` 完整性校验算法；加密表支持**库表级备份恢复**（V2.0-8.200.0+）。
- gs_roach 备份工具自身：官方文档仍只有 `--disable-ssl`（SSL 默认开启），备份传输与备份集中集加密无双国密参数。
- 全密态列级加密支持 SM4_SM3、国密 CMK/CEK（openGauss 7.x）。

## 可复用要点

1. 区分"备份工具自身加密能力"与"数据源引擎加密能力"两个层面，避免混淆结论。
2. 判定某二进制是否支持国密的快速方法：`nm -D` 查是否有 `EVP_sm*` 与 `EVP_get_cipherbyname`/`EVP_CIPHER_fetch`（无 fetch 即无动态加载 SM4 能力）。
3. 底层 OpenSSL 具备国密算法 ≠ 上层工具已启用；需结合工具 cipher 列表与证书算法判断。
4. gs_roach 的 SSL 默认开启，可用 `--disable-ssl` 关闭。

## 场景建议（如需端到端国密）

- 数据源：用引擎 TDE（encrypt_algo='SM4_CTR'）+ gsql/JDBC 国密 TLS/TLCP 认证。
- 备份链路：gs_roach 自身不可国密，需上层替代——备份链路前置国密 TLS 网关/隧道，或备份集导出后以 SM4 加密归档。