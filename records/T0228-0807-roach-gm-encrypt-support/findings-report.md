# gs_roach 国密加密支持与存储引擎国密加密调研报告

| 项 | 值 |
|----|----|
| 任务 | T0228-0807-roach-gm-encrypt-support |
| 环境 | 10.6.67.38 `/opt/cluster/usr/local/core/app_1da42ed9/bin` |
| 现场版本 | GaussDB Kernel 505.2.1 build 1da42ed9（2024-12-27, commit 10161） |
| 调研日期 | 2026-08-07 |
| 调研方式 | tmux 会话 0:2:0 现场静态/运行时分析 + 官方文档联网佐证 |

---

## 一、调研目标

判定 gs_roach 是否支持国密加密（SM2/SM3/SM4），并厘清两个层面：
1. **gs_roach 备份工具自身**：备份传输加密、备份集存储加密是否支持国密。
2. **存储引擎（gaussdb）层面**：源数据加密存储是否支持国密，以及备份后数据的加密形态。

## 二、方法

- **静态分析**：`nm -D` / `strings` / `objdump` 检查 gs_roach、backUpAgent、libssl.so、libcrypto.so、gaussdb 的加密符号与算法串。
- **运行时验证**：`gs_roach --version/--help`、`openssl version`、`openssl ciphers -v`、`openssl x509` 证书算法、环境变量与配置文件检查。
- **官方文档佐证**：GaussDB V2.0-8.x 安全管理/透明加密、openGauss SSL-TLCP、备份恢复工具文档。

---

## 三、结论摘要（一句话）

> **gs_roach 备份工具本身不支持国密（备份传输 + 备份集存储均为 AES）；数据源 gaussdb 引擎支持国密存储加密（TDE：SM4_CTR / SM4_CTR_SM3_HMAC）；国密 SSL/TLCP 仅 gsql/JDBC 客户端与服务端之间支持。**物理备份能保留引擎 TDE 产生的 SM4 密文。

---

## 四、分层结论详表

| 层 | 加密能力 | 国密支持 | 证据 |
|----|---------|---------|------|
| gs_roach 备份传输 | SSL 默认开启，套件硬编码 AES（`ECDHE-ECDSA-AES128-GCM-SHA256` 等 + `TLS_AES_128/256_GCM_*`），证书 RSA+SHA256 | ❌ 不支持国密 | strings/nm；cert RSA |
| gs_roach 备份集存储 | 透明加密 AK/SK（`roach_ak_sk.key`），AES-128-CBC | ❌ 不支持国密 | nm 仅 `EVP_aes_128_cbc`；`roach_aes128_decrypt`/`DecryptAes128Cbc` |
| gaussdb 引擎存储 | TDE 表级透明加密：`enable_tde`+`tde_key_info`+`encrypt_algo` | ✅ 支持 SM4_CTR、SM4_CTR_SM3_HMAC | gaussdb nm 有 `EVP_sm4_cbc`/`EVP_sm4_ctr`；算法串 `sm4_ctr_sm3` |
| gsql/JDBC 传输 | SSL / TLCP | ✅ 支持国密 `ECC-SM4-SM3`、`ECDHE-SM4-SM3`、`ECC-SM4-GCM-SM3`、`ECDHE-SM4-GCM-SM3` | GaussDB 安全管理文档 |

---

## 五、关键判定证据（现场二进制）

### 5.1 gs_roach 自身不支持国密

```bash
# EVP 符号：只有 AES，无任何 SM
nm -D gs_roach | grep -iE 'EVP|CIPHER' 
#   U EVP_aes_128_cbc     ← 唯一对称算法
#   U SSL_CIPHER_get_name
#   U SSL_CTX_set_ciphersuites
#   U SSL_set_ciphersuites

# 决定性：无动态加载 SM4 的能力
nm -D gs_roach | grep -icE 'EVP_sm|EVP_get_cipher|EVP_CIPHER_fetch'   # = 0

# TLS 套件硬编码（strings）
# ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:...
# TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384

# cipher 列表来自编译期宏，无外部覆盖入口
# "Failed to set cipher list to XBSA_BACKUP_CIPHER_LIST."
```

**要点**：无 `EVP_sm4*`、无 `EVP_get_cipherbyname`、无 `EVP_CIPHER_fetch` → gs_roach **不具备**加载 SM4 的能力，只能编译期绑定 AES-128-CBC。

### 5.2 存储引擎（gaussdb）支持国密

```bash
nm -D gaussdb | grep -iE 'EVP_sm|SM4|TDE'
#   U EVP_sm3
#   U EVP_sm4_cbc
#   U EVP_sm4_ctr
#   B g_sm4

# TDE 机制完整
strings gaussdb | grep -iE 'enable_tde|tde_key_info|dek_cipher|sm4_ctr'
# sm4_ctr_sm3   ← 国密算法串
# enable_tde / tde_key_info / dek_cipher / CLIENT_MASTER_KEY ...
```

### 5.3 底层库具备国密（但工具未启用）

```bash
openssl version   # OpenSSL 3.0.9 30 May 2023
openssl ciphers -v | grep SM4
# ECC-SM4-GCM-SM3  | GMTLS  Kx=unknown
# ECDHE-SM4-GCM-SM3| GMTLS  Kx=SM2DH
# ECC-SM4-SM3      | GMTLS
# ECDHE-SM4-SM3    | GMTLS  Kx=SM2DH
```

---

## 六、备份是否会带出国密密文？

**是，但需分清两层。**

- **引擎 TDE（SM4_CTR）**：数据页写盘前加密、读盘后解密。gs_roach 是**物理备份**（直接拷贝数据文件），拷出的是磁盘上的 **SM4 密文** → 物理备份集的数据正文保留国密密文 ✅。
- **gs_roach 备份集自身加密**（AK/SK 透明加密）为 **AES-128-CBC**：若启用，会在 SM4 密文外层**再叠一层 AES**，形成"引擎页级国密 + 备份集级国际"双层。

| 场景 | 备份集数据形态 |
|------|--------------|
| 源表 `enable_tde=on, encrypt_algo=sm4_ctr` + gs_roach 物理备份（不开 AK/SK） | 数据=SM4 密文（国密） |
| 同上 + gs_roach AK/SK 透明加密 | 数据=SM4(AES(AES)) 双层密文 |
| 逻辑导出（gs_dump / SQL 导出） | 读到引擎解密后的**明文**，非国密 |

**边界**：TDE 默认只加密行存表数据文件；xlog/undo 是否加密取决于 `tde_encrypt_config.log_algorithm`（可设 `sm4_ctr`），未设时 xlog 为明文。

---

## 七、存储引擎国密加密配置步骤

### 前置条件
- 引擎版本 ≥ GaussDB V2.0-3.300（支持 TDE）；当前 505.2.1 可用。
- 需可访问的外部 **KMS 密钥服务**（保护 DEK；GaussDB 支持华为云 DEW/KMS 及兼容 KMS）。
- 仅支持行存表；不支持列存/物化视图/系统表加密。指定算法后不可更改。

### 配置流程

**1) 配置 GUC（gs_guc set）**

```bash
# 开启透明加密（重启生效）
gs_guc set -Z datanode -D <datadir> -c "enable_tde = on"

# 配置外部 KMS 访问信息
gs_guc set -Z datanode -D <datadir> -c "tde_key_info = 'keyType=huawei_kms,iamUrl=<IAM地址>,iamUser=<用户>,iamPassword=<密码>,iamDomain=<账号>,kmsProject=<项目>,ak=<AK>,sk=<SK>,kmsCaCert=<KMS CA证书路径>'"

# （可选）表数据/日志默认算法设为国密
gs_guc set -Z datanode -D <datadir> -c "tde_encrypt_config = 'table_algorithm=sm4_ctr_sm3_hmac'"
```

**GUC 参数**
| GUC | 作用 | 取值 |
|-----|------|------|
| `enable_tde` | 透明加密开关 | on/off |
| `tde_key_info` | 外部 KMS 访问信息 | keyType=...,iamUrl=...,ak=...,sk=...,kmsCaCert=... |
| `tde_encrypt_config.table_algorithm` | 表数据算法 | `aes_128_ctr`、`sm4_ctr`、`sm4_ctr_sm3_hmac`、`aes_128_gcm` |
| `tde_encrypt_config.log_algorithm` | xlog/undo 算法 | `aes_128_ctr`、`sm4_ctr` |

> 注意：`enable_tde` 需重启数据库；确保 KMS 可访问，否则数据库无法启动。

**2) 重启数据库**
```bash
gs_om -t stop && gs_om -t start   # 或 gs_ctl restart -D <datadir>
```

**3) 创建国密加密表**
```sql
-- 国密 SM4_CTR
CREATE TABLE tde_sm4 (id INT, data TEXT)
  WITH (orientation = row, storage_type = row_outer_store, enable_tde = on, encrypt_algo = 'sm4_ctr');

-- 国密 + 完整性校验（GaussDB 8.x+）
CREATE TABLE tde_sm4_hmac (id INT, data TEXT)
  WITH (enable_tde = on, encrypt_algo = 'sm4_ctr_sm3_hmac');
```

**4) 密钥轮转（可选）**
```sql
ALTER TABLE tde_sm4 ENCRYPTION KEY ROTATION;
```

**5) 验证**
```sql
SELECT relname, reloptions FROM pg_class WHERE relname = 'tde_sm4';
-- reloptions 应含 enable_tde=on, encrypt_algo=SM4_CTR, dek_cipher=...
```

---

## 八、更新版本对比（联网核实）

| 维度 | 现场 505.x | GaussDB V2.0-8.x / openGauss 7.x |
|------|-----------|----------------------------------|
| 引擎 TDE 国密 | SM4_CTR / SM4_CTR_SM3_HMAC | 新增 `sm4_ctr_sm3_hmac` 完整性校验；加密表**库表级备份恢复**（V2.0-8.200.0+ 有效） |
| gs_roach 自身传输 | SSL 默认开启 AES，无国密 | 仍仅 `--disable-ssl`，无国密参数 |
| gs_roach 备份集存储 | AES-128-CBC | 文档未见国密改动 |
| gsql/JDBC 国密 | gsql 服务端支持国密 TLS/TLCP | + 全密态列级 SM4_SM3（openGauss 7.x） |

**要点**：版本更新带来的国密增强集中在**数据源侧**（引擎 TDE、gsql/JDBC、全密态），gs_roach 备份工具本身仍未提供国密参数。

---

## 九、国密启用建议（端到端）

1. **数据源**：引擎 TDE（`encrypt_algo='sm4_ctr'`）+ gsql/JDBC 国密 TLS/TLCP 认证。
2. **备份链路**：gs_roach 自身不可国密，采用上层替代：
   - 备份链路上前置国密 TLS 网关/隧道（SM2 证书 + SM4-SM3）；
   - 或备份集导出后以 SM4 加密归档。
3. 备份集双层形态（引擎 SM4 + roach AES）可满足"数据正文国密"诉求，若需全链路纯净国密则用网关方案。

---

## 十、适用范围与限制

- 结论基于现场 505.2.1 build 1da42ed9 二进制与 GaussDB/openGauss 官方文档（2026-08 查询）。
- 不适用于未来新增国密支持版本；gsql/JDBC 国密能力不能类推到 gs_roach。
- 现场未实际执行 TDE 建表/KMS 对接实验（需 KMS 服务与数据库实例权限），配置步骤以官方文档为据。

## 附：参考资料
- GaussDB 安全管理（SSL/国密认证、roach/xbsa 证书）— support.huawei.com EDOC1100543054/489bf77a
- GaussDB 透明数据加密（TDE）— support.huaweicloud.com（集中式/分布式 V2.0-8.x）
- GaussDB 备份恢复工具（gs_roach、--disable-ssl）— support.huawei.com EDOC1100519995
- openGauss 《用 SSL 进行安全的 TCP/IP 连接》《连接数据库（以 TLCP 方式）》
- openGauss 设置透明数据加密 TDE（5.0.0）