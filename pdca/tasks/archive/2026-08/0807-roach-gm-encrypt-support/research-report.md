# 调研报告：gs_roach 国密加密支持

- task: T0228-0807-roach-gm-encrypt-support
- 环境: 10.6.67.38 `/opt/cluster/usr/local/core/app_1da42ed9/bin`
- 工具版本: GaussDB Kernel 505.2.1 build 1da42ed9（2024-12-27，commit 10161）
- 日期: 2026-08-07

## 调研目标

判定 gs_roach 是否支持国密加密（SM2/SM3/SM4），区分两种形式：
1. 存储数据加密
2. TLS 传输加密

## 方法

- 通过 tmux 会话 0:2:0 在远程机器实测：
  - `nm -D` / `strings` / `objdump` 静态符号与字符串分析（gs_roach、backUpAgent、libssl、libcrypto）
  - `ldd` 依赖库确认
  - `gs_roach --help` / `backup --help` / `--version` 命令行能力
  - `openssl version` / `openssl ciphers -v` 底层库国密套件确认
  - `openssl x509` / `openssl pkey` 证书算法确认
  - 环境变量、配置文件、证书目录、密钥文件检查
- 官方文档佐证：GaussDB 安全管理（SSL/国密）、openGauss SSL-TLCP 章节、备份恢复工具说明。

## 发现

### 一、存储数据加密（transparent encryption）

| 事实 | 证据 | 结论 |
|------|------|------|
| 支持存储加密 | `roach_ak_sk.key` AK/SK 文件；查询 `gs_encrypted_columns` 检测加密表；`TRANSPARENT` 状态 | ✅ 支持透明加密 |
| 算法为 AES-128-CBC | `roach_aes128_decrypt`、`DecryptAes128Cbc`、`roach_crypt_decrypt`、`roach_decrypt_aes128`；nm 仅 `EVP_aes_128_cbc` | ✅ AES，非国密 |
| 无 SM4 通路 | `nm -D` 无 `EVP_sm4*`、无 `EVP_get_cipherbyname`、无 `EVP_CIPHER_fetch` | ❌ 无法加载 SM4 |

### 二、TLS 传输加密

| 事实 | 证据 | 结论 |
|------|------|------|
| 支持 TLS 传输加密 | SSL 默认开启，`--disable-ssl` 关闭；roach/xbsa 证书目录 | ✅ 支持 |
| 套件为 AES 系列 | 硬编码 `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-...` + `TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384` | ✅ AES |
| cipher 列表不可外部覆盖 | `Failed to set cipher list to XBSA_BACKUP_CIPHER_LIST`（编译期宏） | 无法运行时切国密 |
| 证书为 RSA | server.crt = RSA + sha256WithRSAEncryption | 非 SM2 |

### 三、底层库差异

- 底层 libssl/libcrypto 3.0.9（2023-05-30）具备国密 TLCP 套件 `ECC-SM4-GCM-SM3`、`ECC-SM4-SM3`、`ECDHE-SM4-GCM-SM3`、`ECDHE-SM4-SM3` 及 SM2/SM3/SM4 算法实现。
- gs_roach 二进制未启用这些能力；`openssl ciphers` 承认 4 个 GMTLS 套件，但工具 cipher 列表是编译期固定 AES 串。
- 官方文档明确：国密 SSL/TLCP（SM2 双证书 + SM4-SM3 套件）**仅支持 gsql/JDBC 客户端与服务端之间**；`roach` 与 `xbsa` 证书仅作普通 SSL 传输证书，无国密参数；gs_roach 证书禁用 PKCS#1_V1.5。

## 结论与建议

**gs_roach（505.2.1 build 1da42ed9）支持加密但不支持国密 SM2/SM4。**

1. TLS 传输加密：支持（AES 套件，SSL 默认开启 / `--disable-ssl` 关闭）；不支持国密 SM4。
2. 存储数据加密：支持（透明加密，AK/SK，AES-128-CBC）；不支持国密 SM4。
3. 底层 libssl 具备国密能力但 gs_roach 未启用；官方文档仅 gsql/JDBC 支持国密。

国密启用建议（需上层方案）：
1. **备份链路前置国密 TLS 网关/隧道**：在备份客户端与 roach 主控之间用独立国密 TLS（SM2 证书 + SM4-SM3）加密传输层，gs_roach 自身 SSL 可关闭或保留 AES 双重叠加。
2. **应用/数据源侧 SM4 加密**：在写入数据库前用 SM4（如 gs_encrypt 的 sm4 模式 / CEK SM4_SM3）加密敏感数据，再由 gs_roach 备份，实现内容级国密。
3. 组合使用 1+2 覆盖传输与存储两侧。

## 参考资料

- GaussDB 安全管理（国密 SSL 认证、ssl_cert_file/ssl_enc_cert_file、roach/xbsa 证书说明）— support.huawei.com EDOC1100543054/489bf77a
- openGauss 文档《用 SSL 进行安全的 TCP/IP 连接》《连接数据库（以 TLCP 方式）》— docs.opengauss.org
- openGauss《备份在恢复》/ Roach 工具说明
- 现场二进制：gs_roach、backUpAgent、libssl.so、libcrypto.so（opencode build 环境记录）