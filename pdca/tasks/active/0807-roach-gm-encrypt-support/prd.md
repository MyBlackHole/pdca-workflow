# PRD

- task: T0228-0807-roach-gm-encrypt-support

## 问题

用户询问：gs_roach（GaussDB Kernel 505.2.1 build 1da42ed9）是否支持国密加密，分两种形式：存储数据加密与 TLS 传输加密。

## 背景与范围

- 对象：远程机器 10.6.67.38 上 `/opt/cluster/usr/local/core/app_1da42ed9/bin/gs_roach`。
- 通过 tmux 会话 0:2:0 现场静态（nm/strings/objdump/ldd）+ 运行时（help/ciphers/证书）分析。
- 佐证：GaussDB / openGauss 官方文档。

## 调研结论（已验证）

### 存储数据加密
- gs_roach **支持存储数据加密**（透明加密）：读取 `roach_ak_sk.key` 的 AK/SK，查询 `gs_encrypted_columns` 检测加密表。
- **算法为 AES-128-CBC**，非国密。解密函数族：`DecryptAes128Cbc`、`roach_aes128_decrypt`、`roach_crypt_decrypt`、`roach_decrypt_aes128`。
- 无 SM4：`nm -D` 无 `EVP_sm*`、无 `EVP_get_cipherbyname`、无 `EVP_CIPHER_fetch`（无法动态加载 SM4）。

### TLS 传输加密
- 支持 TLS 传输加密：SSL 默认开启，可用 `--disable-ssl` 关闭；使用 roach/xbsa 证书目录。
- 算法=AES 系列：硬编码 `ECDHE-ECDSA-AES128-GCM-SHA256:...` + `TLS_AES_128/256_GCM_*`；cipher 列表来自编译期宏 `XBSA_BACKUP_CIPHER_LIST`，无外部覆盖入口。
- 证书为 RSA + SHA256，非 SM2。

### 底层库同工具差异
- 底层 libssl/libcrypto 3.0.9 具备国密 TLCP 套件（ECC-SM4-GCM-SM3 等）与 SM2/SM3/SM4 算法实现，但 gs_roach 二进制未启用。
- 官方文档明确：国密 SSL/TLCP（SM2 双证书 + SM4-SM3 套件）**仅支持 gsql/JDBC 客户端与服务端之间**；roach 与 xbsa 证书仅作普通 SSL 传输证书，无国密参数。

## 结论

gs_roach（505.2.1 build 1da42ed9）**支持加密但不支持国密**：
1. TLS 传输加密：支持（AES），不支持国密 SM4 套件。
2. 存储数据加密：支持（透明加密 AK/SK，AES-128-CBC），不支持国密 SM4。
3. 如需国密，需上层替代方案（如备份链路前端国密 TLS 网关/隧道，或在应用/数据端用 SM4 加密后入库）。

## 用户故事 / 验收

作为数据库管理员，我希望确认 gs_roach 的国密能力边界，用于合规与安全方案选型。

## 实现/测试决策

- 纯调研，无代码改动。
- 验证手段：tmux 会话现场抓取 nm/strings/OID/证书/openssl ciphers 输出。
- 官方文档佐证：GaussDB 安全管理 / openGauss SSL-TLCP 章节。

## 范围外

- 不构造国密握手实测（环境无 SM2 证书且工具无入口，工作量/价值不平衡）。
- 不评估上层国密网关实现细节（仅给方向）。

## 验收标准

- [ ] AC-1: 明确给出 gs_roach TLS 传输加密的国密支持结论（不支持国密，支持 AES），并给出符号级证据
- [ ] AC-2: 明确给出 gs_roach 存储数据加密的国密支持结论（透明加密 AES-128-CBC，非 SM4），并给出符号级证据
- [ ] AC-3: 说明底层库(libssl 3.0.9)与工具二进制的差异及实际启用边界（国密仅 gsql/JDBC）
- [ ] AC-4: 给出至少一条可行的国密启用路径建议
- [ ] AC-5: 产出结论文档并归档到 knowledge 条目