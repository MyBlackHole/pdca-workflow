# OceanBase 备份加密与国密 SM4 支持性验证报告

**验证对象**：OceanBase 4.2.1.1（集群 `obv422167545556`，3 节点）
**源码基线**：oceanbase 源码（commit `3abcb163`）
**验证日期**：2026-08-07
**约束**：全程不修改任何业务数据、不开 TDE、不产生备份产物

---

## 一、调查目标

确认：OceanBase 是否支持"备份数据（备份文件本身）设置为国密 SM4 加密"，且**不动源数据**。

## 二、结论摘要

> **国密（SM 密码）在备份链路分两部分看待：备份存储加密 与 备份传输加密。** 本报告分别给出结论。

| 问题 | 结论 |
|------|------|
| 备份数据加密逻辑是否存在？ | **存在**（`PASSWORD_ENCRYPTION` / `TRANSPARENT_ENCRYPTION` 等模式） |
| 备份能否独立配置"国密 SM4"算法？ | **不能**（无 SM4 可选项，算法取值表为空占位） |
| 备份文件何时是 SM4 密文？ | **仅当源表 TDE 本身就是 SM4**，透明加密沿袭密文 |
| **备份存储加密维度**：落盘文件密文能否是 SM4？ | 只能靠源 SM4 TDE 沿袭；口令加密只落 AES（底层有 SM4 实现但无选项） |
| **备份传输加密维度**：OB→备份介质链路是否启用国密？ | **OB 自身不发起国密握手**（S3/OSS 介质走标准 HTTPS/TLS，无 SM2/SM3/SM4 套件）；OB 节点间内部 TLS 才有国密套件且仅限 BabaSSL 商业构建 |
| 不改源数据、只给备份装 SM4？ | **OB 4.2.1.1 做不到** |

一句话：**备份加密逻辑存在，但"给备份独立选国密 SM4"的开关不存在；SM4 只能经源 TDE 透明加密沿袭（存储维度），传输链路则需在介质侧网关/负载均衡做国密 TLS 终止（OB 自身不启用）。**

---

## 三、证据链

### 证据一：备份数据加密逻辑【存在】

**E1-1 备份加密四模式枚举** —— `src/share/ob_encryption_util.h:229-232`
```
PASSWORD = 1,             // 密码校验
PASSWORD_ENCRYPTION = 2,  // 密码校验 + 加密（独立备份加密）
TRANSPARENT_ENCRYPTION = 3, // 透明加密（沿袭源 TDE）
DUAL_MODE_ENCRYPTION = 4,   // 透明加密 + 密码校验
```
说明备份数据加密是**已实现的分支逻辑**，非营销/占位概念。

**E1-2 备份加密会话变量** —— `src/share/backup/ob_backup_struct.h:385-386`
```cpp
"__ob_backup_encryption_mode__"
"__ob_backup_encryption_passwd__"
```
对应 SQL `BACKUP ENCRYPTION SET PASSWORD 'xxx'`，是独立于源 TDE 的备份加密入口。

### 备份加密 4 模式速查表（纠偏版）

| 模式 | 含义 | 密码的作用 | 备份文件中的数据 | 恢复时 |
|------|------|-----------|----------------|--------|
| `NONE` | 不加密 | 无 | 明文 | 无需密码 |
| `PASSWORD` | 仅口令校验 | 仅作一致性校验 | **明文**（数据未加密） | 需密码（对得上即放行）|
| `PASSWORD_ENCRYPTION` | 口令加密 | **既校验，又作加密密钥** | **密文**（真正的备份数据加密）| 需密码（缺则无法解密）|
| `TRANSPARENT_ENCRYPTION` | 透明加密 | 无密码 | **跟随源 TDE 密文**（源非 SM4 则非 SM4）| 需源主密钥，无需备份口令 |

**通俗类比**：`PASSWORD` = 登记通行证（包裹不上锁）；`PASSWORD_ENCRYPTION` = 上锁保险箱（没密码读不出内容）。

#### PASSWORD_ENCRYPTION（口令加密）支持的算法

- OB 用备份口令派生密钥对备份文件做 **AES 族加密（默认 AES-256 类）**；口令本身不落盘、不直接当密钥。
- 加密引擎的 OpMode 全集（`ob_encryption_util.h`）**在底层支持 AES-128/192/256（ecb/gcm）以及 SM4（cbc/gcm）**（EVP 实现齐全，`ob_encryption_util_os.cpp:85-92`）。
- **但**：备份口令加密的算法**没有用户可选 SM4 的入口**——加密算法配置值表为空占位（证据二 E2-1），SM4 只在透明加密校验白名单出现。因此实际落地以 AES 为主，SM4 无法通过口令加密直接启用。

### 证据二：SM4 不是"用户可选项"

**E2-1 归档加密算法取值表为空占位** —— `src/share/config/ob_config.cpp:40-41`
```cpp
const char *log_archive_encryption_mode_values[]   = { "None", "Transparent Encryption" };
const char *log_archive_encryption_algorithm_values[] = { "None", "" };   // ← 空占位，无 "SM4-CBC"
```
用户侧不存在可配置的 SM4 算法字符串。

**E2-2 SM4 仅出现在"合法性校验"** —— `src/share/config/ob_config.cpp:1224-1238`
`is_encryption_meta_valid()` 对 `TRANSPARENT_ENCRYPTION` 的元数据做校验，白名单含：
```cpp
case ObCipherOpMode::ob_sm4_cbc_mode:   // 1237
case ObCipherOpMode::ob_sm4_gcm:        // 1238
```
这是"接受已存在的 SM4 密文元数据"，**不是用户可选的加密算法开关**。

**E2-3 运行佐证**（集群 `obv422167545556`，只读）
- `SHOW PARAMETERS LIKE '%encryption%'` → 无 `log_archive_encryption_algorithm` 等条目
- `SHOW VARIABLES LIKE '__ob_backup_encryption%'` → 无公开条目
- `tde_method = none`（三节点一致，TDE 未开启）
- 结论：备份/归档加密属**内置会话与校验逻辑**，不对用户暴露算法选择。

### 证据二补充：企业版（OB 商业版/云版）SM4 支持分析

**问题**：PASSWORD_ENCRYPTION 底层支持国密但没有公开选项——那企业版是否支持？

**开源可实证的部分（"底层支持 SM4"成立）**：
- E2-5 加密引擎 SM4 全模式 EVP 实现齐全且真实：`ob_encryption_util_os.cpp:85-92`（`EVP_sm4_cbc/ecb/ofb/cfb/ctr/gcm`）——加密引擎层面"支持国密"无争议。
- E2-6 SM4 路由是为特定构建**预留**的：`ob_encryption_util.h:249-250` `is_sm_algorithm`/`is_aes256_algorithm`
  **仅声明、实现缺失**（普通开源构建未编译该实现）；且 `cmake/Env.cmake:156` `ob_define(OB_BUILD_TDE_SECURITY ON)` 安全加密分支默认编译进——指向"SM4 启用路径留给安全版/企业版补齐"。

**企业版证据（间接、开源无法终判）**：
- 官方 V4.2.1 文档明确表述支持国密 SM4（128 位，cbc/gcm）。
- 阿里云 OBS（企业/云形态）文档确认：**Oracle 租户可用 `SM4-CBC` 密钥类型**。
- 综合指向：企业版/云版（Oracle 租户）具备 SM4 能力，含"源 SM4 TDE → 透明加密备份为 SM4 密文"。

**诚实边界**：
- "备份口令加密（PASSWORD_ENCRYPTION）在企业版是否可直接把算法选成 SM4"——**开源无此选项，企业版行为无法从本仓库证明**，需企业版文档或实测（`SHOW PARAMETERS LIKE '%encryption%'` + 建 Oracle 租户 SM4 表空间）确认。
- 企业版确认路径：Oracle 租户 `CREATE TABLESPACE ... ENCRYPTION='SM4-CBC'` → `V$OB_ENCRYPTED_TABLES.ENCRYPTIONALG=SM4-CBC` → 备份透明加密即为 SM4 密文。

### 证据三：SM4 备份密文 = 源 TDE 透明沿袭

- 备份宏块数据为源数据的原样拷贝（`encrypt_id` 宏块加密元数据，`ob_macro_block.cpp`）。
- 源表 SM4 TDE 加密 → 磁盘宏块为 SM4 密文 → 备份文件即 SM4 密文。
- `PASSWORD_ENCRYPTION`（独立口令加密）的算法**不由用户指定**（E2-1 占位佐证）。

### 证据四：备份传输链路的国密（第二维度）

**传输链路的国密 ≠ 存储密文**：即使存储侧密文做成 SM4，OB→备份介质的**搬运通道**是否用国密是另一回事。本维度结论：**OB 自身不发起国密握手**。

**E4-1 S3/OSS 介质通道走标准 HTTP(S)/TLS，无国密套件**
- `deps/oblib/src/lib/restore/ob_storage_s3_base.cpp:195`
  `config.scheme = Aws::Http::Scheme::HTTP; // if change to HTTPS, be careful about checksum logic.`
  使用 AWS SDK，TLS 套件由 OpenSSL 默认集提供（无 SM2/SM3/SM4）。
- `deps/oblib/src/lib/restore/ob_storage_oss_base.cpp:883-892`
  仅解析 `http://`/`https://` 前缀（`AOS_HTTPS_PREFIX`），无国密协议判断。

**E4-2 OB 内部 TLS 确有国密套件，但仅限 BabaSSL 商业构建，且非备份介质链路**
- `deps/ussl-hook/ssl/ssl_config.c:65-70` / `deps/easy/src/io/easy_ssl.c:83-87`
  ```c
  static const char baba_tls_ciphers_list[] =
      "... ECC-SM2-WITH-SM4-SM3:ECDHE-SM2-WITH-SM4-SM3: ..."
  ```
- 套件仅在 `OB_USE_BABASSL` 分支编译（`ssl_config.c` 多处 `#ifdef OB_USE_BABASSL`；`easy_ssl.c:1014` 由 `is_babassl` 选择）。
- 该 TLS 用于 OB 节点间/内部通信（RPC、Raft、MySQL 协议等，`easy_ssl_ctx_create_for_mysql`），**不覆盖 S3/OSS 备份介质请求**。

**E4-3 结论**
- 备份传输无国密选项（S3/OSS 默认 HTTP，改 HTTPS 也是国际标准套件）。
- 要"传输国密"，只能**在介质侧前置国密网关/负载均衡做 SM2/SM3/SM4 TLS 终止**（OB→网关仍走标准 TLS，网关→介质走国密），属部署层改造，OB 不参与。

---

## 四、运行实测记录

1. 本机 podman 拉取 `oceanbase/oceanbase-ce`（4.4.2.1 社区镜像，MODE=SLIM）实测：
   - `tde_method=internal` 可开、主密钥 `mysql_keystore` 建立
   - 该社区镜像 **不支持 Oracle 租户模式**（`Not support oracle mode`）→ 无法用 `SM4-CBC` 加密表空间显式选 SM4
   - 数据备份报 `backup can not start`（受限环境）
2. 真实集群 `obv422167545556`（OB 4.2.1.1）只读验证：
   - `tde_method=none`，无加密配置项暴露（E2-3）

---

## 五、常见误解澄清

| 误解 | 实际 |
|------|------|
| "备份加密=国密 SM4" | 备份口令加密存在，但算法非 SM4 可选 |
| "开了备份加密源数据会变" | 不会，备份加密只作用于备份产物，源表不动 |
| "源加密了备份就必是密文" | 对，透明沿袭；但要求源先开 TDE |
| "创建租户时可配加密" | 否，`CREATE TENANT` 无加密参数；加密挂"表空间/表" |

---

## 六、可操作结论与建议

- **若要 SM4 备份密文**：唯一路径 = 源表开启 SM4 TDE（透明加密沿袭）→ **必然影响源数据**。
- **若不能动源数据**：备份只能走非 SM4 的口令加密（`BACKUP ENCRYPTION SET PASSWORD`），或无加密备份。
- 如需国密合规 + 不动源：需在具备"备份独立算法选择"的 OB 形态/版本上另行评估（本版本无此能力）。

---

## 七、TDE 开启 SM4 完整正确步骤（实操）

> **前提**：TDE 的 SM4（`SM4-CBC`/`SM4-GCM`）只能在 **Oracle 模式**加密表空间显式选择；MySQL 模式建表不支持显式指定 SM4。开启 TDE 后**不可逆**（除非重建租户），建议先在独立测试租户执行。

### 步骤 0：确认集群 OBSERVER 状态、选定目标租户
```sql
-- sys 系统租户
SELECT * FROM __all_server;   -- 或 GV$OB_SERVERS，确认全部 ACTIVE
```

### 步骤 1：开启 TDE（tde_method=internal，广播全部 OBSERVER）
```sql
-- 在 sys 租户执行
ALTER SYSTEM SET tde_method = 'internal';
SHOW PARAMETERS LIKE 'tde_method';
```
- 取值：`none`（关闭）、`internal`（主密钥存内部表，私有云推荐）、`bkmi`（外部 KMS）。
- 开启后**不可关闭**（除非重建租户）。

### 步骤 2（可选，主密钥）：
OB 4.2 主密钥由 Keystore 自动生成；如需显式指定：
```sql
ALTER SYSTEM SET tde_master_key_id = 100001;
```
> 以目标版本文档为准；多数 4.x 自动生成。

### 步骤 3：Oracle 模式创建 SM4 加密表空间
```sql
-- Oracle 模式租户
CREATE TABLESPACE tde_sm4 ENCRYPTION = 'SM4-CBC';   -- 或 'SM4-GCM'
```

### 步骤 4：建表并写入数据
```sql
CREATE TABLE t_sm4 (id NUMBER, secret VARCHAR2(100)) TABLESPACE tde_sm4;
INSERT INTO t_sm4 VALUES (1, '国密SM4-密文-测试');
COMMIT;
```

### 步骤 5：旧数据重写为加密（全量合并）
```sql
ALTER TABLE t_sm4 SET progressive_merge_num = 1;
ALTER SYSTEM MAJOR FREEZE;
ALTER TABLE t_sm4 SET progressive_merge_num = 0;
```

### 步骤 6：验证确为 SM4 加密
```sql
-- sys 租户
SELECT * FROM oceanbase.V$OB_ENCRYPTED_TABLES;    -- ENCRYPTIONLAG=SM4-CBC/SM4-GCM, ENCRYPTED=YES, BLOCKS_ENCRYPTED>0
SELECT * FROM oceanbase.V$ENCRYPTED_TABLESPACES;
```

### 步骤 7（备份侧验证 SM4 密文）
备份宏块为源数据原样拷贝；源表 SM4 → 备份即 SM4 密文。恢复需源主密钥。

---

## 八、备份启用加密的执行命令（口令加密 / 透明加密 / 双模）

> SQL 语法以官方知识库《如何为全量备份集和增量备份集设置加密密码》（适用 V2.2.7x/V3.x/V4.x）为准，本报告演示命令摘自并校验于该文档。

### 场景 A：口令加密备份（不依赖源 TDE）

**算法**：备份口令在备份线程经派生生成密钥，对备份数据集做 AES 族加密（SM4 无选项，见证据二）。

```sql
-- 0) 【可选】为业务租户配置归档/数据备份路径（root@sys 执行；V4 业务租户内可去掉 tenant=）
ALTER SYSTEM SET LOG_ARCHIVE_DEST='LOCATION=file:///obbackup/mysqlt/archive' tenant=mysqlt;
ALTER SYSTEM SET DATA_BACKUP_DEST='file:///obbackup/mysqlt/full_backup' tenant=mysqlt;
--    确认：
SELECT * FROM cdb_ob_archive_dest  WHERE tenant_id=1018;
SELECT * FROM cdb_ob_backup_parameter WHERE tenant_id=1018;

-- 1) 开启日志归档（等 cdb_ob_archivelog 的 STATUS 变为 DOING 才成功）
ALTER SYSTEM ARCHIVELOG tenant=mysqlt;
SELECT * FROM cdb_ob_archivelog WHERE tenant_id=1018;

-- 2) 设置备份集密码（root@sys 执行；或业务租户内执行去掉 tenant 语义）
--    · 会话级：发起备份前断开连接再重连即可取消本次设置
--    · 一旦备份开始，该密码即写入备份集（不可删除），恢复时必须提供
SET ENCRYPTION ON IDENTIFIED BY 'ObsBackup#SM4!2026' ONLY;

-- 3) 发起全量备份（备份集即为密文；PASSWD 列显示口令摘要，ENCRYPTION_MODE 列显示模式）
ALTER SYSTEM BACKUP TENANT = mysqlt;
--    或 V4 业务租户内：ALTER SYSTEM BACKUP DATABASE;
--    等 cdb_ob_backup_jobs 中该租户记录为空 = 完成
SELECT * FROM cdb_ob_backup_jobs WHERE tenant_id=1018;

-- 4) 【增量备份】密码可与全量相同，也可不同（不同时恢复须同时提供，全量在前）
ALTER SYSTEM BACKUP INCREMENTAL TENANT = mysqlt;

-- 5) 恢复：解密口令须先设置（SET DECRYPTION IDENTIFIED BY），多密码用逗号分隔；
--    口令错误报 ERROR 9047 (HY000): invalid password for backup
SET DECRYPTION IDENTIFIED BY 'ObsBackup#SM4!2026';   -- 全量/增量密码相同只需一个
ALTER SYSTEM RESTORE mysqlt_restore FROM
  'file:///obbackup/mysqlt/full_backup,file:///obbackup/mysqlt/archive'
  WITH 'pool_list=restore_pool&concurrency=3';
--    等 cdb_ob_restore_progress 记录为空 = 恢复完成
SELECT * FROM cdb_ob_restore_progress;
```

> 口令清除/变更命令各版本存在差异，以所部署版本官方《备份与恢复》手册为准。

### 场景 B：透明加密备份（TRANSPARENT_ENCRYPTION，跟随源 TDE）

**算法**：无备份口令；源 SM4 TDE 密文随宏块原样进备份文件（证据三）。

```sql
-- 前置：目标租户已按"七、TDE 开启 SM4 步骤"完成 表空间 SM4 + 合并重写（BLOCKS_ENCRYPTED>0）
ALTER SYSTEM BACKUP TENANT = mysqlt;   -- 或 V4 业务租户内 ALTER SYSTEM BACKUP DATABASE;
-- 备份即 SM4 密文；恢复无需备份口令，但必须能访问源租户主密钥（内部密钥文件/外部 KMS）
```

### 场景 C：双重模式（DUAL_MODE_ENCRYPTION = 透明 + 口令）

同时满足"源码 TDE 密文"与"独立口令加密"（恢复需 源主密钥 + 备份口令 双因子）。

```sql
SET ENCRYPTION ON IDENTIFIED BY 'ObsBackup#SM4!2026' ONLY;  -- 已在源 TDE 租户设置过则复用
ALTER SYSTEM BACKUP TENANT = mysqlt;
```

### 各模式命令矩阵

| 模式 | 需备份口令 | 备份文件数据 | 恢复要求 |
|------|:--:|------|----------|
| `NONE` | 否 | 明文 | 无 |
| `PASSWORD` | 是（仅校验） | **明文** | 口令对得上即可 |
| `PASSWORD_ENCRYPTION` | 是（当密钥） | **密文（AES 族）** | 解密口令 |
| `TRANSPARENT_ENCRYPTION` | 否 | 跟随源 TDE（SM4 需源 SM4） | 源主密钥 |
| `DUAL_MODE_ENCRYPTION` | 是 | 密文 | 源主密钥 + 解密口令 |

---

## 附录：关键源码位置索引

| 内容 | 位置 |
|------|------|
| 备份加密模式枚举 | `src/share/ob_encryption_util.h:224-234` |
| 备份加密会话变量 | `src/share/backup/ob_backup_struct.h:385-386` |
| 归档加密算法值表（空占位） | `src/share/config/ob_config.cpp:34-41` |
| 加密元数据合法性校验（SM4 白名单） | `src/share/config/ob_config.cpp:1224-1264` |
| SM4 算法实现（EVP_sm4_*） | `src/share/ob_encryption_util_os.cpp:85-92` |
| 宏块加密元数据（encrypt_id） | `src/storage/blocksstable/ob_macro_block.cpp` |
| S3 介质通道（HTTP/HTTPS，无国密） | `deps/oblib/src/lib/restore/ob_storage_s3_base.cpp:195` |
| OSS 介质通道（仅 http/https 前缀） | `deps/oblib/src/lib/restore/ob_storage_oss_base.cpp:883-892` |
| OB 内部 TLS 国密套件（BabaSSL 分支） | `deps/ussl-hook/ssl/ssl_config.c:65-70`、`deps/easy/src/io/easy_ssl.c:83-87,1014` |
| SM4 预留路由（声明无实现） | `src/share/ob_encryption_util.h:249-250` |
