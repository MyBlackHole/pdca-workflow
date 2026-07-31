# NBU 备份传输加密逻辑调研 — 完整报告

> 调研时间：2026-07-31
> 目标主机：10.6.67.187 (nbusvr103)
> NBU 版本：NetBackup 10.3.0.1 (Build 0042, 2023-12-31)
> OS：CentOS Linux release 7.9.2009 (Core)

## 1. NBU 整体工具架构

### 1.1 进程架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     Web UI 层                                     │
│   Tomcat (Java) ── nbwebsvc ── /usr/openv/wmc/webserver/         │
│   RabbitMQ (消息队列) ── /usr/openv/mqbroker/                    │
├──────────────────────────────────────────────────────────────────┤
│                     CORBA 服务层                                  │
│                                                                  │
│  nbemm  ── 企业介质管理 (EMM)       nbrb  ── 资源代理           │
│  nbjm   ── 作业管理器 (Job Manager)  nbpem ── 策略执行管理器    │
│  nbrmms ── 远程介质&存储管理         nbstserv ── 存储服务       │
│  nbsl   ── 服务层                   nbproxy ── CORBA 代理       │
├──────────────────────────────────────────────────────────────────┤
│                     控制层                                        │
│                                                                  │
│  bprd(13720)  ── 备份请求守护进程    bpdbm ── 备份数据库管理器  │
│  bpjobd       ── 作业守护进程        bpcd(13782) ── 客户端守护  │
│  bpbrm        ── 备份恢复管理器      bprd_parent/child           │
│  bpdbm_parent/child                                             │
├──────────────────────────────────────────────────────────────────┤
│                     安全层                                        │
│                                                                  │
│  vnetd(13724) ── 网络认证+代理守护   nbatd ── 认证令牌守护      │
│  nbcertcmd    ── 证书管理 CLI        nbcryptocmd ── 加解密工具  │
│  nbaudit      ── 审计日志            nbazd ── 访问控制         │
│  bpclntcmd    ── 凭据缓存管理        bpkeyfile/bpkeyutil ── 密钥│
├──────────────────────────────────────────────────────────────────┤
│                     数据层                                        │
│                                                                  │
│  bptm  ── 磁带管理 (数据读写)        bpdm ── 磁盘管理           │
│  ltid  ── 卷/驱动器管理              PDDE ── MSDP 重删存储      │
│  nbfsd/nbfsd_irp ── 文件服务                                     │
├──────────────────────────────────────────────────────────────────┤
│                     客户端层                                      │
│                                                                  │
│  bpbackup ── 备份客户端     bprestore ── 恢复客户端              │
│  bpbkar ── 备份归档读取     bplist ── 文件列表                  │
│  bparchive ── 归档客户端    bpclntcmd ── 客户端连接              │
├──────────────────────────────────────────────────────────────────┤
│                     基础设施                                      │
│                                                                  │
│  PostgreSQL(13785) ── NBDB     pgBouncer ── 连接池              │
│  nbdisco ── 发现服务           nbim ── 库存管理                  │
│  nbanomaly* ── 异常检测       nbtelemetry ── 遥测               │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 端口监听

| 端口 | 进程 | 用途 |
|------|------|------|
| 13720 | bprd | 备份请求 |
| 13724 | vnetd | 网络认证/代理 |
| 13782 | bpcd | 客户端守护 |
| 13785 | postgres | NBDB 数据库 |
| 1556 | pbx_exchange | PBX 通信 |
| 443 | vnetd | HTTPS 隧道 |

### 1.3 二进制大小与角色

| 二进制 | 大小 | 角色 |
|--------|------|------|
| bpdbm | 12.7 MB | 备份数据库管理器 |
| bprd | 13.8 MB | 备份请求守护进程 |
| bptm | 9.3 MB | 磁带/数据管理 |
| bpbrm | 6.7 MB | 备份恢复管理器 |
| bpdm | 6.5 MB | 磁盘管理器 |
| nbproxy | 5.8 MB | CORBA 代理 |
| bpjobd | 3.8 MB | 作业守护 |
| bpcd | 2.1 MB | 客户端守护 |
| nbcryptocmd | 1.6 MB | 加解密工具 |
| nbcertcmd | 1.3 MB | 证书管理 |
| vnetd | 163 KB | 网络认证代理 |
| bpbackup | 82 KB | 备份客户端 CLI |

### 1.4 架构哲学：为什么需要这么多工具和服务

NBU 的工具/服务数量多（~50 个管理工具 + ~31 个守护进程），根源于以下设计决策：

#### 1.4.1 CORBA 分布式架构

NBU 使用 CORBA（ACE/TAO）作为 IPC 框架，而不是共享库或线程内通信。

```
线程模型 vs 进程模型的差异：
┌──────────────────────────────────────┐
│  单进程多线程（如 MySQL）              │
│  ├─ 线程 A: 网络 I/O                  │
│  ├─ 线程 B: SQL 查询                  │
│  └─ 线程 C: 备份引擎                  │
│  优点：管理简单，共享内存              │
│  缺点：一个线程崩溃全进程挂            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  NBU CORBA 多进程模型                 │
│  ├─ 进程1: bprd  (备份请求)           │
│  ├─ 进程2: bpdbm (DB 管理器)          │
│  ├─ 进程3: nbjm  (作业管理器)         │
│  ├─ 进程4: bptm  (数据读写)           │
│  └─ 进程5: bpcd  (客户端)             │
│  优点：进程隔离，独立崩溃              │
│  缺点：需要网络通信，管理复杂          │
└──────────────────────────────────────┘
```

每个服务通过 CORBA IDL 接口暴露功能，其他服务通过 CORBA 名称服务（nbemm 承担此角色）发现对方。这种设计带来了大量独立进程。

#### 1.4.2 分层隔离（Separation of Concerns）

NBU 将功能拆成 5 层，每层独立部署：

```
         ┌────────────────────────────────┐
         │  Web UI 层 (Java/Tomcat)        │
         │  nbwebsvc, mqbroker             │
         ├────────────────────────────────┤
         │  CORBA 服务层 (C++)             │
         │  nbemm, nbjm, nbpem, nbrb      │
         ├────────────────────────────────┤
         │  控制层 (C++)                    │
         │  bprd, bpdbm, bpjobd, bpbrm    │
         ├────────────────────────────────┤
         │  安全层 (C++)                    │
         │  vnetd, nbatd, nbaudit          │
         ├────────────────────────────────┤
         │  数据层 (C++/专用)               │
         │  bptm, bpdm, ltid, PDDE        │
         └────────────────────────────────┘
```

每层之间通过固定 TCP 端口通信，不能直接调用下层内部函数。例如备份请求必须经过：
`bprd(13720) → vnetd认证(13724) → nbjm(作业调度) → bptm(数据读写)`

#### 1.4.3 Unix 传统：单一职责原则

每个 CLI 工具只做一件事，由 init.d/systemd 统一管理：

```
管理命令         │ 用途                  │ 所属角色
─────────────────┼──────────────────────┼─────────────
bpbackup/bprestore │ 客户端备份/恢复       │ 用户交互
bplist            │ 文件列表              │ 文件查询
bperror           │ 错误报告              │ 诊断
bpconfig/bpsetconfig │ 配置管理             │ 系统管理
bppllist/bpplinfo │ 策略管理              │ 策略管理
bpmedia/bpmedialist │ 介质管理              │ 存储管理
nbemmcmd          │ EMM 服务管理          │ CORBA 管理
nbjmreq           │ 作业请求              │ 作业管理
bpdbjobs          │ 作业查询              │ 监控
```

如果在现代架构中重新设计，这些可以合并为 `nb backup/restore/list/config/policy/media/job` 等子命令（类似 kubectl），但 NBU 始于 1990 年代，继承了 Unix 工具的 CLI 风格。

#### 1.4.4 历史演进（版本累加）

NBU 每个大版本都会新增功能，新增功能以**新增服务**而非重构现有服务的方式实现：

| 年代 | 版本 | 新增服务 | 原因 |
|------|------|---------|------|
| 1990s | NBU 1.x | bprd, bpdbm, bptm, bpcd | 基础架构 |
| 2000s | NBU 5.x | vnetd, nbatd | 安全增强 |
| 2010s | NBU 7.x | nbjm, nbpem | CORBA 化重构 |
| 2015+ | NBU 8.x | nbkms, nbseccmd | 证书/加密 |
| 2020+ | NBU 10.x | nbanomaly*, nbtelemetry | AI/遥测 |

nbseccmd 本身就是一个典型例子：在 8.x 之前 DTE 配置散布在 bp.conf 和策略中，后来新增了专门的 nbseccmd 统一管理安全配置（含 DTE），但旧接口（bpconfig、bp.conf）仍然保留兼容。

#### 1.4.5 安全隔离

安全相关功能被拆为独立进程，即使被攻破也局限于该进程：
- vnetd：网络入口，即使被攻破也不暴露 NBDB
- nbatd：令牌服务，与数据路径隔离
- nbaudit：只写审计日志，不参与业务
- nbkms：密钥管理，密钥材料不离开此进程

#### 1.4.6 总结

NBU 多服务/多工具的根因：

| 原因 | 占比 | 说明 |
|------|------|------|
| CORBA 进程模型 | 40% | 每个服务独立进程，IPC 需网络通信 |
| 分层隔离 | 25% | 5 层不能越级调用 |
| 单一职责 | 20% | 每个 CLI 工具只做一件事 |
| 历史累积 | 10% | 30 年版本迭代只增不减 |
| 安全隔离 | 5% | 敏感功能独立进程 |

如果今天从零设计 NBU，一个合理的方案可能是：
- 控制面：3~4 个微服务（API Gateway、Policy、Job、Storage）
- 数据面：1 个流式数据传输服务
- CLI：合并为 `nbctl backup/restore/config/policy/job` 子命令体系
- 安全：内置于服务网格（mTLS），无需独立代理层

但 NBU 的庞大服务数量是 30 年产品演进的自然结果，每个服务都有其历史必要性。

## 2. NBU DTE (Data-in-Transit Encryption) 架构

### 2.1 配置层级 (4 层)

```
全局 DTE 模式（域级别）
  ├── Preferred Off  （首选关闭）
  ├── Preferred On   （首选开启，10.0+ 全新安装默认）
  └── Enforced       （强制加密，不支持则作业失败）

客户端 DTE 模式（主机级别）
  ├── Off  （关闭）
  ├── On   （开启）
  └── Auto （自动，10.0+ 默认）

介质服务器 DTE 模式（主机级别）
  ├── Off  （关闭）
  └── On   （开启，默认）

映像 DTE 模式（作业/备份集级别）
  ├── Off
  └── On
```

### 2.2 DTE 决策逻辑（bpbrm 实现）

bpbrm 中 `g_dte_mode` 全局变量驱动决策：

```
g_dte_mode 枚举值:
  DTE_MODE_OFF      = 0
  DTE_MODE_ON       = 1
  DTE_MODE_ENFORCED = 2 (对应全局 Enforced)

决策流程:
  1. 读取全局 DTE 模式
  2. 跳过条件：Catalog 恢复/import/verify/skip_dte_processing
  3. 获取客户端版本和 DTE 能力
  4. 检查客户端 DTE 模式开关
  5. 检查介质服务器 DTE 模式开关
  6. NAT 客户端特殊处理（忽略介质服务器设置）
  7. SAN 光纤传输不支持 DTE
  8. XBSA 快照不需要 IN-APP-TLS
  9. 最终结果写入 image/作业记录

错误场景:
  - Enforced + 客户端 DTE=Off      → 作业失败
  - Enforced + 客户端不支持 DTE    → 作业失败
  - Enforced + 介质服务器 DTE=Off  → 作业失败
  - 映像 DTE=On + 客户端不支持     → 作业失败
```

### 2.3 两条加密路径

| 特性 | IN-APP-TLS | vnetd-proxy |
|------|-----------|-------------|
| 实现 | 直接 TLS 握手 | 通过 vnetd 代理转发 |
| 适用条件 | 双方版本 ≥ DTE_INAPP_SUPPORT_RELEASE_NUM | 低版本/不支持 IN-APP-TLS |
| 性能 | 高（直连） | 中（代理转发） |
| 安全 | 端到端加密 | 代理节点可观测 |
| 触发条件 | `DTE In-app-TLS is supported for client type: %d` | `using vnet proxy for DTE` |

vnetd 代理模式:
- `inbound_proxy` — 入站代理
- `outbound_proxy` — 出站代理
- `http_pbx_tunnel` — HTTP PBX 隧道
- `http_api_tunnel` — HTTP API 隧道

### 2.4 DTE 决策状态机

bpbrm 的 DTE 决策逻辑是一个层次化的状态机，从全局配置向下覆盖到作业级别：

```
                    ┌──────────────────────┐
                    │  全局 DTE 模式        │
                    │  -dteglobalmode       │
                    │  0=Off 1=On 2=Enforce │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  跳过条件检查         │
                    │  Catalog 备份?  → 跳过│
                    │  Import/Verify? → 跳过│
                    │  skip_dte_processing?│
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  检查对端版本          │
                    │  vnet_is_peer_dte_    │
                    │  capable()            │
                    └──┬───────────────┬───┘
                       │ 支持          │ 不支持
                       ▼              ▼
              ┌────────────────┐  ┌──────────────┐
              │ 客户端 DTE 模式 │  │ Enforced?    │
              │ Off/On/Auto    │  │ 是→作业失败   │
              └──┬──────────┬──┘  │ 否→vnetd-proxy│
                 │ Auto     │固定  └──────────────┘
                 ▼          ▼
         ┌──────────────┐  ┌──────────────┐
         │ 跟随全局配置  │  │ 使用固定值   │
         │ 全局 On→On   │  │ DTE_MODE_ON  │
         │ 全局 Off→Off │  │ 或 OFF       │
         └──────┬───────┘  └──────┬───────┘
                │                 │
                ▼                 ▼
         ┌─────────────────────────────┐
         │ 介质服务器 DTE 模式检查      │
         │ emmlib_QueryMediaDTESetting │
         │ Off→按介质服务器配置         │
         │ On→允许                     │
         └──────────┬──────────────────┘
                    │
         ┌──────────▼──────────────────┐
         │ 特殊处理                     │
         │ NAT 客户端?→忽略介质服务器   │
         │ SAN 传输?→DTE 不支持        │
         │ XBSA 快照?→无需 IN-APP-TLS  │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │ 最终 DTE 模式确定             │
         │ ┌───────┬────────┬─────────┐ │
         │ │ 结果  │ IN-APP │ vnetd-  │ │
         │ │       │ -TLS  │ proxy   │ │
         │ ├───────┼────────┼─────────┤ │
         │ │ OFF   │  否    │  否     │ │
         │ │ ON    │  是    │  否     │ │
         │ │ N/A   │  否    │  是     │ │
         │ └───────┴────────┴─────────┘ │
         │ 写入作业记录 DTEMode=On/Off   │
         └──────────────────────────────┘
```

关键全局变量（bpbrm 中定义的 C/C++ 标识符）：
```
g_dte_mode              ← DTE_MODE_OFF(0)/ON(1)/ENFORCED(2)
g_dte_mode_value        ← 最终确定的 DTE 模式值
dte_global_mode_str     ← DTE 模式字符串表示
is_media_server_dte_disabled  ← 介质服务器 DTE 禁用位
disable_separate_comm_sock_for_dte  ← 通信套接字控制
enable_proxy_for_dte    ← 代理使能标志
is_data_channel_encrypted  ← 数据通道加密状态
```

## 3. 加密组件深入分析

### 3.1 加密库栈

```
应用层: bpbrm/bptm/bpbackup/bpcd
           │
           ▼
libnbssl.so (3.3 MB) ─── NBU SSL 封装 (NB_101_* API, 基于 OpenSSL 1.0.2k)
  ├── NB_101_SSL_CTX_new/SSL_new/SSL_do_handshake
  ├── NB_101_EVP_CipherInit/CipherUpdate/CipherFinal
  ├── NB_101_AES_cbc_encrypt / AES_set_encrypt_key
  ├── NB_101_DES_ecb_encrypt / DES_xcbc_encrypt
  └── NB_101_DTLSv1_method/client/server
           │
           ▼
libnbtls.so (32 KB) ─── NBU TLS 轻量封装
  ├── nbtls_lib_init/fin ─── 库初始化
  ├── nbtls_config_init/set_int/set_str/set_ssl_options
  ├── nbtls_ctx_init/fin ─── TLS 上下文
  ├── nbtls_handshake ─── 握手
  └── nbtls_io ─── 读写
           │
           ▼
libnbcertmgmt.so (1.6 MB) ─── 证书管理
libcmncrypto.so ─── 通用加密
libcmncryptocore.so (534 KB) ─── 核心加密 (mangle 加解密)
libcredhelperMT.so ─── 凭据管理 (passphrase 加解密)
libvxVxSSIOPST.so ─── VxSS 安全身份 (CORBA TLS)
```

### 3.2 二进制加密职责

| 二进制 | 加密相关符号 | 职责 |
|--------|-------------|------|
| **bpbrm** | `g_dte_mode`, `JOB_DTE_MODE`, `DTE_MEDIA_MODE`, `emmlib_QueryMediaDTESetting`, `update_dte_mode_for_job_to_jm`, `vnet_set_dte_mode_in_tss`, `bpcr_adjust_connect_options`, `BRMJobDteModeMsg` | DTE 模式决策、作业级加密策略传递、连接选项调整 |
| **bptm** | `check_dte_support`, `dte_context_initializer`, `determine_dte_mode_by_image`, `Encrypting data-in-transit`, `establish_decryption_key`, `get_encryption_key`, `kmsDecryptKey`, `DRIVE_ENCRYPTION_ACTIVE`, `manage_drive_encryption`, `scsi_report_encryption_capabilities` | 数据面加密、密钥获取、SCSI 驱动器加密控制 |
| **bpbackup** | `libnbsslST.so`, `deployCertSource`, `deployUseExistingCerts`, `VNET_PROXY_HINT_DTE_CAPABLE`, `-unix_eca_cert_path` | 证书部署、DTE 能力标记 |

### 3.3 密码套件

`/usr/openv/share/ciphers.txt`:
```
AES-128-CFB    BF-CFB        DES-EDE-CFB
AES-256-CFB    AES-192-CFB
```

系统 OpenSSL: 1.0.2k-fips

**不支持任何国密算法（SM2/SM3/SM4）**。等保三级在 NBU 上无法使用国密 TLS。

### 3.4 加密算法参考（libcmncryptocore.so）

libcmncryptocore 导出符号:
- `mangle_aes_256_gcm_encrypt_with_rand_iv` / `mangle_aes_256_gcm_decrypt`
- `mangleEncrypt` / `mangleDecrypt` / `mangle_derive_key`
- `mangleGenerateRSAKeys` / `mangleCreateSignatureKeys`
- `cmncrypto_generatePrivateKey` / `cmncrypto_releasePrivateKey`
- `is_private_key_file_encrypted_c`

## 4. 证书与身份体系

### 4.1 证书拓扑

```
NBU CA ── /CN=nbatd/OU=root@nbusvr103/O=vx
  ├── RSA 2048, SHA-256
  ├── 有效期: 2025-10-23 ~ 2045-10-18 (20年)
  ├── CA 证书: /usr/openv/var/webtruststore/cacert.pem
  │
  ├── broker 中间 ── /CN=broker/OU=root@nbusvr103/O=vx
  │     └── 主机证书 ── /CN=nbusvr103/OU=NBU_Machines@nbusvr103/O=vx
  │           ├── RSA 2048, 有效期 2 年
  │           ├── SAN: nbusvr103
  │           ├── HostID: c44f05de-b410-4584-9438-59ca72fc10c5
  │           ├── 公钥: .../keystore/PubKeyFile-2048.pem
  │           └── 私钥: .../keystore/PrivKeyFile-2048.pem
  │
  └── 主机证书 (host ID 格式)
        └── /CN=c44f05de-.../OU=NBU_HOSTS/O=vx
```

### 4.2 证书管理命令 nbcertcmd

| 操作 | 说明 |
|------|------|
| `-createCertRequest` | 生成 CSR |
| `-deployCertificate` | 部署证书到本地信任库 |
| `-getCertificate` | 从 CA 获取证书 |
| `-signCertificate` | CA 签名 CSR |
| `-renewCertificate` | 续期证书 |
| `-revokeCertificate` | 吊销证书 |
| `-listAllCertificates` | 列出所有本地证书 |
| `-listCACertDetails` | CA 详情 |
| `-hostSelfCheck` | 主机自检（证书/CRL） |
| `-getSecConfig` | 安全配置（CA 使用策略/部署级别） |
| `-setSecConfig` | 设置安全配置 |
| `-getNBKeysize` | 密钥大小 |

CA 使用策略返回 `NBCA:ON ECA:OFF` —— 仅使用内置 NBU CA。

### 4.3 私钥存储保护

```
私钥存储路径:

/usr/openv/var/vxss/at/root/.VRTSat/profile/certstore/keystore/
  ├── PrivKeyFile-2048.pem  ── RSA 私钥 (PEM, 未加密)  600 root
  ├── PubKeyFile-2048.pem   ── RSA 公钥 (PEM)          644 root
  ├── 3f5h4z38413o4f1tx694v6g6g35344.fips  ── FIPS 标记
  └── KeyStore.lock

其他 keystore 路径:
  /usr/openv/var/vxss/credentials/keystore/c44f05de-...-key.pem
  /usr/openv/var/global/vxss/{nbcertservice,websvccreds,tomcatcreds}/.../keystore/
```

**关键事实**：私钥存储在**未加密的 PEM 文件**中（`-----BEGIN RSA PRIVATE KEY-----`），保护完全依赖文件系统权限（`600` root/nbwebsvc）。

凭据密钥库（`.bcfks`）由 `credjkskey`（64 位 hex 密钥）派生密钥加密，使用 AES-256-GCM。

### 4.4 安全架构全景图

NBU 安全体系由以下 6 个功能域组成，每域有独立的守护进程和管理命令：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NBU 安全架构                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌── ① 身份认证 ──────────────────────────────────────────────┐     │
│  │  nbatd ── EAB 认证令牌守护 (OID:18)                        │     │
│  │    ├── 颁发短寿命令牌（用于服务间通信）                     │     │
│  │    ├── 验证客户端令牌                                       │     │
│  │    └── 集成 vnetd 认证流程                                 │     │
│  │  nbazd ── 访问控制决策                                     │     │
│  │  bpclntcmd ── 凭据缓存管理                                  │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ② 网络访问 ──────────────────────────────────────────────┐     │
│  │  vnetd(13724) ── 单一网络入口点                              │     │
│  │    ├── inbound_proxy   ── 入站代理（接收外部连接）           │     │
│  │    ├── outbound_proxy  ── 出站代理（连接到外部）             │     │
│  │    ├── http_pbx_tunnel ── HTTP PBX 隧道                      │     │
│  │    └── http_api_tunnel ── HTTP API 隧道（HTTPS:443）         │     │
│  │  bpcd(13782) ── 客户端守护，通过 vnetd 认证                  │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ③ 传输加密 ──────────────────────────────────────────────┐     │
│  │  nbseccmd ── 安全配置管理（DTE + KMS）                      │     │
│  │    ├── -dteglobalmode <0/1/2>    ── DTE 域级配置            │     │
│  │    ├── -dtemediamode <off/on>    ── 介质服务器配置           │     │
│  │    ├── -insecurecommunication    ── 8.0 以下兼容             │     │
│  │    └── -nbcaMigrate              ── CA 迁移                  │     │
│  │  bpbrm ── 作业级加密决策                                      │     │
│  │    ├── emmlib_QueryMediaDTESetting()                         │     │
│  │    ├── vnet_is_peer_dte_capable()                            │     │
│  │    └── bpcr_adjust_connect_options()                         │     │
│  │  bptm ── 数据面加密（libnbtls 调用者）                        │     │
│  │    ├── nbtls_handshake() / nbtls_io()                        │     │
│  │    ├── nbdte_psk_get() / nbdte_psk_put()                    │     │
│  │    └── manage_drive_encryption()  ── 磁带加密                │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ④ 证书与密钥 ────────────────────────────────────────────┐     │
│  │  nbcertcmd ── 证书管理 CLI                                     │     │
│  │    ├── -configure     ── 初始配置（CA 自签名 + 主机证书）     │     │
│  │    ├── -authenticate  ── 获取主机证书                          │     │
│  │    └── -renewKeyPair  ── 密钥对续期                            │     │
│  │  nbcertconfig ── 证书配置                                      │     │
│  │  nbhostidentity ── 主机身份导入                                 │     │
│  │  nbcertmgmt.so ── 证书管理库                                    │     │
│  │  nbkms ── 密钥管理服务 (OID:286)                               │     │
│  │    └── get_encryption_key()  ── 获取数据加密密钥               │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ⑤ 审计与监控 ────────────────────────────────────────────┐     │
│  │  nbaudit ── 审计守护 (OID:293)                                │     │
│  │    └── 记录所有安全操作（登录/认证/策略修改）                 │     │
│  │  nbauditreport ── 审计报告 CLI                                │     │
│  │  nbars ── 审计报告服务                                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ⑥ 合规与策略 ────────────────────────────────────────────┐     │
│  │  nbseccmd -setsecurityconfig     ── 安全策略                   │     │
│  │  bpinst -LEGACY_CRYPT            ── 旧版加密策略               │     │
│  │  bpnbaz                         ── 安全最佳实践分析器          │     │
│  │  nbcertconfig -setSecConfig      ── CA 使用策略               │     │
│  │  bpconfig                       ── 全局配置                   │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  安全配置存储路径:                                                   │
│  /usr/openv/var/vxss/         ── VxSS 证书/密钥存储                  │
│  /usr/openv/var/global/vxss/  ── 服务证书存储                        │
│  /usr/openv/var/global/       ── 全局安全配置                        │
│  /usr/openv/var/vxss/credentials/  ── 主机凭据                       │
│  /usr/openv/netbackup/bp.conf ── 旧版配置（CONNECT_OPTIONS）         │
│  /usr/openv/var/global/certmapinfo.json  ── 证书映射+TLS配置         │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. NBU 网络连接模型

### 5.1 CONNECT_OPTIONS

```
CONNECT_OPTIONS = localhost 1 0 2
格式: <local_host> <use_broker> <no_proxy> <use_tunnel>

参数说明:
  localhost   ── 本地连接优化地址
  use_broker=1 ── 启用 connection broker
  no_proxy=0   ── 允许 vnetd 代理
  use_tunnel=2 ── 隧道模式
```

bpbrm 可在运行时通过 `bpcr_adjust_connect_options` 调整连接选项，DTE 模式变化时可选择绕过代理直接连接。

### 5.2 TLS Session 复用

从 certmapinfo.json 中发现的配置：
```json
"tlsSessionResumption": {
    "enable": 1,
    "handshakeIntervalInMinutes": 30
}
```
NBU 支持 TLS 会话恢复（30 分钟间隔），减少频繁握手开销。

### 5.3 DTE 加密握手时序图

NBU DTE 加密握手在备份作业第 4 阶段（数据传输）建立，完整的时序如下：

```
 主/介质服务器(nbusvr103)         客户端/介质服务器(nbumed103)
 ┌──────────────────────┐          ┌──────────────────────┐
 │ nbjm (作业管理器)     │ CORBA   │ nbjm                  │
 │ 决定使用 DTE=On       │────────▶│ 查询策略 DTE 配置     │
 │                      │◀────────│ 返回 DTE_MODE=On      │
 ├──────────────────────┤          ├──────────────────────┤
 │ bprd (备份请求)       │ vnetd   │ bpcd (客户端守护)      │
 │ 通过 vnetd 认证连接   │────────▶│ 建立 TCP 连接          │
 ├──────────────────────┤          ├──────────────────────┤
 │ bpbrm (备份管理器)    │ vnetd   │ bpbrm (对端)          │
 │ 创建 BRMJobDteModeMsg │────────▶│ 检查对端 DTE 能力     │
 │ 查询 EMM DTE 配置     │         │ vnet_is_peer_dte_     │
 │ emmlib_QueryMedia     │         │ capable()              │
 │ DTESetting()          │         │                       │
 ├──────────────────────┤  TCP    ├──────────────────────┤
 │ bptm (数据读写)       │ TLS协商 │ bpdm (存储端)          │
 │ nbtls_config_init()   │════════▶│                       │
 │ nbtls_ctx_init()      │ 握手   │ nbtls_ctx_init()       │
 │ nbtls_handshake()     │ ╔════╗ │ nbtls_handshake()      │
 │ ← ClientHello         │ ║TLS ║ │ → ServerHello          │
 │ ← ServerHelloDone     │ ║1.2 ║ │ → Certificate           │
 │ → ClientKeyExchange   │ ║    ║ │ ← ChangeCipherSpec     │
 │ → ChangeCipherSpec    │ ╚════╝ │ ← Finished              │
 │ nbtls_io() 加密数据   │════════▶│ nbtls_io() 解密        │
 ├──────────────────────┤ 加密信 ├──────────────────────┤
 │ nbtls_io() 备份数据    │════════▶│ nbtls_io() 确认        │
 │ AES-CFB/BF/DES        │◀════════│ SACK/RETRY             │
 ├──────────────────────┤ Close  ├──────────────────────┤
 │ nbtls_cleanup()        │────────▶│ nbtls_cleanup()        │
 └──────────────────────┘          └──────────────────────┘
```

关键 API 调用链：

bpbrm 端（决策层）
```
emmlib_QueryMediaDTESetting()       ← EMM 查询介质服务器 DTE 配置
vnet_is_peer_dte_capable()          ← vnetd 查询对端 DTE 能力
vnet_set_dte_mode_in_tss()          ← 在 TSS 中设置 DTE 模式
bpcr_adjust_connect_options()       ← 调整连接选项（TLS/非TLS）
bpcr_get_dte_client_config_rqst()   ← CORBA 获取客户端 DTE 配置
refreshDteCache()                   ← 刷新 JM 端 DTE 缓存
BRMJobDteModeMsg                    ← BRM DTE 模式消息传递
```

bptm 端（数据层）
```
nbtls_config_init()                 ← TLS 配置初始化
nbtls_config_set_int/str()          ← 设置参数
nbtls_config_set_ssl_options()      ← SSL 选项
nbtls_ctx_init()                    ← TLS 上下文初始化
nbtls_handshake()                   ← TLS 握手
nbtls_io()                          ← 加密数据读写
nbtls_config_fin() / nbtls_cleanup() ← 清理
nbdte_psk_get() / nbdte_psk_put()   ← PSK 管理（可选）
```

### 5.4 网络通信矩阵

所有 NBU 进程间的网络通信关系：

```
源进程          目标进程          端口    协议    用途                加密方式
────────────     ────────────     ────   ────    ────────────────    ────────
nbjm            nbemm            CORBA  IIOP    作业/资源查询        vnetd-proxy
nbpem           nbemm            CORBA  IIOP    策略执行              vnetd-proxy
nbrb            nbemm            CORBA  IIOP    资源代理              vnetd-proxy
nbsl            nbemm            CORBA  IIOP    服务注册              vnetd-proxy
nbrmms          nbemm            CORBA  IIOP    存储管理              vnetd-proxy

bprd            bpdbm            13721  TCP     DB 操作              本地套接字
bprd            nbjm             CORBA  IIOP    作业提交              vnetd-proxy
bpdbm           bprd             13720  TCP     策略/调度查询         本地套接字
bpdbm           postgres         13785  TCP     NBDB 查询            localhost(无加密)

bpbrm           bpcd             13782  TCP     管控通道              IN-APP-TLS/vnetd
bpbrm           bptm             动态   TCP     数据通道控制           IN-APP-TLS
bptm            bpdm             动态   TCP     数据传输               IN-APP-TLS(nbtls)
bptm            ltid/vmd         13701  TCP     磁带/卷分配            vnetd-proxy

bpbackup        bprd             13720  TCP     备份请求              vnetd-proxy
bpbackup        bpbrm            动态   TCP     数据发送               IN-APP-TLS
bprestore       bprd             13720  TCP     恢复请求              vnetd-proxy
bprestore       bpbrm            动态   TCP     数据接收               IN-APP-TLS

客户端 → vnetd                  13724  TCP     认证入口               vnetd 内部
vnetd → bprd                    13720  TCP     转发请求               vnetd 内部
vnetd → bpcd                    13782  TCP     客户端接入              vnetd 内部
vnetd → nbproxy                 CORBA  IIOP    CORBA 代理             vnetd 内部

nbatd           vnetd            UDS    UNIX    令牌验证              UDS 安全
nbaudit         -                file   -       审计日志写入           -

nbkms           bptm             动态   TCP     密钥分发              IN-APP-TLS
nbkms           nbemm            CORBA  IIOP    KMS 注册              vnetd-proxy

nbwebsvc        nbemm/nbjm/...   CORBA  IIOP    Web UI 后端           vnetd(SSL:443)
nbwebsvc        postgres         13785  TCP     Web 查询              localhost(无加密)

nbsvcmon        所有服务         -      signal  健康/重启              -

动画说明（备份时 5 个阶段的网络流量变化）:
  阶段1(策略获取): nbjm←→nbemm(nbproxy)
  阶段2(作业调度): bprd→nbjm, nbjm→nbpem
  阶段3(连接建立): bpbrm↔bpcd(vnetd认证) + NF 流量
  阶段4(数据传输): bptm↔bpdm(TLS加密) + 大量数据流
  阶段5(重删/提交): bpdm→spws(MSDP内部) + 少量控制流
```

## 6. 与本文方案差距分析

### 6.1 加密算法

| 维度 | NBU | 本文方案 | 差距等级 |
|------|-----|---------|---------|
| 传输加密 | AES-128/256-CFB + TLS | SM4-GCM + TLCP | 国标合规 |
| 证书算法 | RSA 2048 | SM2 | 国标合规 |
| 密码套件 | OpenSSL 标准套件 | 国密套件 | 国标合规 |
| 哈希 | SHA-256 | SM3 | 国标合规 |
| FIPS | NB_FIPS_MODE=DISABLE | 不适用 | 无关 |
| 降级策略 | 允许降级明文(Preferred) | 永不降级 | 本文更严格 |

### 6.2 架构设计

| 维度 | NBU (4 层) | 本文方案 (2 层) | 分析 |
|------|-----------|---------------|------|
| 配置层级 | 全局→客户端→介质→映像 | 全局→计划 | NBU 粒度更细但复杂度高 |
| 决策矩阵 | 4 因素 → 数十种结果 | 3 种结果 | 本文可预测性更好 |
| 代理路径 | vnetd-proxy 兼容降级 | 无此设计 | NBU 版本兼容更友好 |
| 私钥保护 | 文件权限(未加密) | SM4 加密存储(计划) | 本文可做得更好 |
| 错误码 | DTE 8301~8314 | ENC-000~008 | 需完善 |
| TLS 会话复用 | 30 分钟间隔 | 未设计 | 可借鉴 |

### 6.3 可借鉴点

| 编号 | NBU 做法 | 本文可借鉴 | 优先级 |
|------|---------|-----------|--------|
| 1 | vnetd 代理路径兼容降级 | 混合版本过渡期设计类似兼容机制 | 中 |
| 2 | TLS Session 复用 (30min) | 减少频繁握手开销 | 低 |
| 3 | `bpcr_adjust_connect_options` 动态切换 | 连接参数动态调整机制 | 低 |
| 4 | BCFKS 凭据库 + credjkskey | 私钥/凭据加密存储参考 | 高 |
| 5 | `mangle_aes_256_gcm_encrypt` 模式 | 凭证加密实现参考 | 中 |
| 6 | certmapinfo.json 证书映射 | 主机-证书映射管理 | 中 |
| 7 | DTE 模式在 image 中持久化 | 加密状态持久化参考 | 中 |
| 8 | 作业日志记录 DTE 状态 | 对标 ENC-T-012 验收 | 高 |

## 7. 完整工具/服务字典

### 7.1 bp* 系列（C++ 传统服务）

| 命令 | 全称 | 角色 | 使用场景 | CORBA 接口 | 数据交互 |
|------|------|------|---------|-----------|---------|
| **bpbackup** | Backup Client | 备份客户端 CLI | 用户手动或脚本发起备份 | 无（直接 TCP） | 连接 bpcd(13782)→bprd(13720)；读本地文件系统 |
| **bprestore** | Restore Client | 恢复客户端 CLI | 用户发起恢复操作 | 同 bpbackup | 连接 bpcd→bprd；写本地文件系统 |
| **bplist** | List Files | 文件列表查询 | 查看备份集中可恢复的文件 | 无 | 连接 bpcd→bprd→读 NBDB |
| **bparchive** | Archive Client | 归档客户端 CLI | 用户发起归档操作 | 同 bpbackup | 连接 bpcd→bprd |
| **bpbkar** | Backup Archive Reader | 备份数据读取器 | 在客户端读取文件数据并发送到介质服务器 | 无 | 读取本地文件系统 → 发送给 bptm/bpdm |
| **bpcd** | Client Daemon | 客户端守护进程 (13782) | 接收客户端连接请求，代理转发到 master | 无 | bpbackup→bpcd→bprd；vnetd 认证 |
| **bprd** | Backup Request Daemon | 备份请求守护进程 (13720) | 接收 bpcd 转发请求，调度作业 | `Audit/*` | bpcd→bprd→nbpem→nbjm→bpdbm |
| **bpdbm** | Backup DB Manager | 数据库管理器 (PostgreSQL) | NBU 所有配置/作业/映像数据的数据库管理 | `Audit/*` | NBDB(13785) 读写；bprd/nbjm 等通过 bpdbm 访问 |
| **bpjobd** | Job Daemon | 作业守护进程 | 监控作业状态，写入作业日志 | `Audit/*` `Audit/AuditTrail` `Audit/Parameters` | bpbrm→bpjobd→NBDB；bprd/nbjm 查询 |
| **bpbrm** | Backup Restore Manager | 备份恢复管理器 | 按策略执行备份/恢复核心逻辑 | `PEM/*` `Audit/*` | bprd→bpbrm→bptm/bpdm→nbrb→nbemm；发送 DTE 模式决策 |
| **bptm** | Tape Manager | 磁带/存储管理器 | 读写备份数据到磁带或磁盘 | `DL/FATClient/*` `Audit/*` | bpbrm→bptm→存储设备；检查 DTE/加密 |
| **bpdm** | Disk Manager | 磁盘管理器 | 管理磁盘存储池的读写 | `Audit/*` | bpbrm→bpdm→磁盘；清理 EMM 数据 |
| **bpclntcmd** | Client Command | 客户端信息查询 | 查询主机名/FQDN/版本/证书状态 | 无（纯工具） | nbhostdb；vxss 证书状态检查 |
| **bpkeyfile** | Key File | 密钥文件管理 | 管理加密密钥文件（LEGACY_CRYPT） | 无 | 读写密钥文件 |
| **bpkeyutil** | Key Utility | 密钥工具 | 修改 NetBackup 密码短语 | 无 | 读写密钥库 |
| **bpinst** | Install | 安装/加密配置 | 配置旧版加密（LEGACY_CRYPT） | 无 | 修改 bp.conf |
| **bpcompatd** | Compat Daemon | 兼容性守护进程 | 处理旧版本客户端兼容性 | 无 | bpcd 兼容 |
| **bpfis** | File System Snapshot | 文件系统快照 | 管理 VSS/FSS 快照 | 无 | 调用系统快照接口 |
| **bpjava-msvc** | Java Master Service | Java 主服务 | Tomcat 与 NBU 后端桥接 | 无 | Web UI→bpjava-msvc→后端服务 |

### 7.2 nb* 系列（CORBA/C++ 服务）

| 命令 | 全称 | 角色 | CORBA 接口 | 数据交互 |
|------|------|------|-----------|---------|
| **nbemm** | Enterprise Media Manager | 企业介质管理 — 所有资源注册/发现中心 | `PEM/*` `DiskMediaServer/*` `Audit/*` | 所有进程与之注册；管理介质服务器/磁盘池/存储单元 |
| **nbrb** | Resource Broker | 资源代理 — 分配介质服务器和存储资源 | `DL/DiskService/*` `Audit/*` | nbjm→nbrb→nbemm；选择最优存储路径 |
| **nbjm** | Job Manager | 作业管理器 — 创建/调度/管理作业 | `Audit/*`（含 AuditTrail/Parameters） | nbpem→nbjm→bpdbm→nbrb→bpbrm |
| **nbpem** | Policy Execution Manager | 策略执行管理器 — 策略解析/调度匹配 | `PEM/*` `Audit/*` | bprd→nbpem→nbjm；查找策略和调度 |
| **nbrmms** | Remote Media & Storage Manager | 远程介质和存储管理 | `DL/DiskService/*` `DiskMediaServer/*` | 管理远程存储；nbjm/nbrb 调用 |
| **nbstserv** | Storage Service | 存储服务 | `Audit/*` | 管理 S3/云存储 |
| **nbsl** | Service Layer | 服务层 — 服务生命周期管理 | 无 | 父进程管理 nbjm/nbpem/nbrb 等 |
| **nbproxy** | Proxy | CORBA 代理 — 将 CORBA 请求转发到目标服务 | CORBA 代理 | nbpem/nbjm/nbrb → nbproxy → 后端 |
| **nbars** | Audit Reporting Service | 审计报告服务 | CORBA | 收集审计记录 |
| **nbatd** | Authentication Token Daemon | 认证令牌守护 — VxSS 身份认证 | VxSS | 管理主机身份证书/令牌 |
| **nbaudit** | Audit | 审计日志守护 | 无 | 收集所有服务的审计事件并写入文件 |
| **nbcertcmd** | Certificate Command | 证书管理 CLI | 无 | 管理 NBU CA 所有操作 |
| **nbcryptocmd** | Crypto Command | 加解密 CLI | 无 | 文件加密/解密/签名/哈希 |
| **nbdiscover** | Discover | 发现服务 | 无 | 自动发现客户端和资源 |
| **nbvault** | Vault | 保险库管理 | 无 | 离线介质管理 |
| **nbanomalymgmt** | Anomaly Management | 异常检测管理 | 无 | 备份异常检测 |
| **nbkms/nbkmscmd** | Key Management Service | 密钥管理服务 | CORBA | KMS 集成（外部密钥管理） |
| **nbhostdbcmd** | Host DB Command | 主机数据库管理 CLI | 无 | 管理主机注册信息 |

### 7.3 安全层详细

| 组件 | 角色 | 数据交互 |
|------|------|---------|
| **vnetd** | 网络认证网关 (13724) | 4 种代理模式：inbound/outbound/http_pbx_tunnel/http_api_tunnel；所有外部连接先经 vnetd 认证 |
| **vxss** | Veritas Security Service | 身份/凭据/证书管理框架；`/usr/openv/var/vxss/` 存储；VxSSIOP 为 CORBA 提供 TLS 通道 |
| **nbatd** | EAB 认证令牌守护 | 基于 EAB（External Authentication Broker）的令牌管理；`vxss/eab/data/` |
| **bpclntcmd -check_vxss** | VxSS 健康检查 | 验证本地 VxSS 设置和证书状态 |

### 7.4 配置文件和存储

| 文件 | 用途 |
|------|------|
| `/usr/openv/netbackup/bp.conf` | 主配置文件：SERVER/CLIENT/EMM/连接/超时/FIPS |
| `/usr/openv/var/global/nbcl.conf` | 服务层配置：MQ/通知服务开关 |
| `/usr/openv/var/global/nbservice.conf` | CORBA 服务配置：线程数/管理属性 |
| `/usr/openv/netbackup/nblog.conf` | 日志配置 |
| `/usr/openv/share/ciphers.txt` | 加密算法白名单 |
| `/usr/openv/var/vxss/certmapinfo.json` | 证书与主机映射 |
| `/usr/openv/var/vxss/credentials/keystore/` | 主机凭据密钥 |

### 7.5 数据流全景

#### 备份作业数据流

```
Phase 1: 请求阶段
  bpbackup CLI ──TCP──→ bpcd:13782 ──VxSS认证──→ bprd:13720
                                                      │
Phase 2: 调度阶段                                          ▼
  bprd ──CORBA──→ nbpem ──查找策略调度──→ nbjm ──创建作业ID──→ bpdbm ──NBDB
                                                      │
Phase 3: 执行阶段                                          ▼
  nbjm ──CORBA──→ nbrb ──资源分配──→ nbemm ──获取介质服务器列表
                  │
                  ▼
  nbrb ──CORBA──→ bpbrm ──启动备份恢复管理器
                  │
                  ▼
  bpbrm ──TCP──→ bptm/bpdm ──在介质服务器上启动数据读写
                  │
Phase 4: 数据传输     │
  bpbackup ──bpbkar──→ 读取文件系统
                   │
                   ▼ DTE 加密
              IN-APP-TLS / vnetd-proxy
                   │
                   ▼
             bptm/bpdm ──写入磁盘/磁带
                  │
Phase 5: 完成阶段     │
  bpbrm ──CORBA──→ bpjobd ──更新作业状态──→ NBDB
  bpbrm ──update_dte_mode_to_monitor──→ 作业记录 DTE 模式
```

#### 加密数据流

```
     ┌─── 客户端 ───┐          ┌─── 介质服务器 ───┐
     │ bpbackup     │          │ bptm/bpdm       │
     │ bpbkar       │  DTE     │                 │
     │     │        │◄════════►│     │           │
     │     │        │  加密     │     │           │
     │     ▼        │  通道     │     ▼           │
     │ libnbssl.so  │          │ libnbssl.so     │
     │ libnbtls.so  │          │ libnbtls.so     │
     └──────┬───────┘          └────────┬────────┘
            │                          │
            ▼                          ▼
     ┌──────────────┐          ┌──────────────┐
     │ vnetd-proxy  │          │ 存储设备     │
     │ inbound/     │          │ (磁带/磁盘)  │
     │ outbound     │          │              │
     └──────────────┘          └──────────────┘

控制通道: CORBA/IOP over VxSSIOP (TLS)
数据通道: TCP + DTE (IN-APP-TLS 或 vnetd-proxy)
认证通道: vnetd → nbatd → nbcertcmd
```

### 7.6 进程间 CORBA 服务依赖

```
nbsl (服务层父进程)
  ├── nbpem ── 策略执行 (nbproxy 代理 nbpem_cleanup/nbpem_email)
  ├── nbjm ─── 作业管理 (nbproxy 代理 nbjm)
  └── nbrb ─── 资源代理 (nbproxy 代理 PolicyManager/ServiceManager 等)

nbemm ── 企业介质管理（独立进程，所有服务查找）
  ├── bprd ── 备份请求（通过 EMM 查询介质服务器）
  ├── bpbrm ── 备份执行（emmlib_initialize 连接 EMM）
  ├── nbrmms ── 远程存储管理（DiskPollingService）
  └── nbstserv ── 存储服务

nbproxy (数据层 CORBA 代理)
  ├── PolicyManager-{id}
  ├── ServiceManagementEx-{id}
  ├── StorageService-{id}
  ├── CatalogManager-{id}
  ├── ClientManager-{id}
  └── HPManager-{id}
```

### 7.7 完整备份作业全景图 —— 时间×进程×数据流×加密决策

将进程架构、数据流、DTE 决策、加密握手、网络通信、日志审计整合为一张图：

```
时间 │ 用户层           控制层              数据层              存储层         日志
─────┼──────────────────────────────────────────────────────────────────────────
  t1 │ bpbackup ──TCP──▶ bpcd:13782
     │ [bplist/policy]  │ vnetd:13724 认证
     │                  │   nbatd 令牌验证
     │                  ▼
     │                  bprd:13720
     │                    │ CORBA
     │                    ▼
  t2 │                  nbpem ──查找策略──▶ nbemm
     │                    │ CORBA            │ 查询 NBDB via bpdbm
     │                    ▼                  ▼
     │                  nbjm ──创建作业──▶ bpdbm:13721
     │                    │ [DTE 决策点 1]   │ PostgreSQL:13785
     │                    ▼                  ▼ nbjobs.*.log
  t3 │                  nbrb ──分配资源──▶ nbemm
     │                    │ bpbrm 启动
     │                    ▼
     │                  bpbrm (备份管理器)
     │                    │ [DTE 决策点 2]
     │                    │ emmlib_QueryMediaDTESetting()
     │                    │ vnet_is_peer_dte_capable()
     │                    │ vnet_set_dte_mode_in_tss()
     │                    │ bpcr_adjust_connect_options()
     │                    ├──────────────────────┐
     │                    │ IN-APP-TLS 路径      │ vnetd-proxy 路径
     │                    │ [版本>=DTE_INAPP]    │ [低版本/NAT/跳过]
     │                    ▼                      ▼
     │     ┌────────────────────────┐  ┌──────────────────┐
     │     │ bpbrm──bpcd──bptm/bpdm │  │ bpbrm──vnetd─proxy──bptm/bpdm
     │     │ nbtls_config_init()    │  │ vnetd 转发 TLS    │
  t4 │     │ nbtls_handshake()  ←┐ │  │ 或无加密           │
     │     │ ╔══ TLS 1.2 ═══╗  │ │  │                    │
     │     │ ║握手+证书交换 ║  │ │  │                    │
     │     │ ╚═════════════╝  │ │  │                    │
     │     │ nbtls_io() 加密──┘ │  │ bptm/bpdm          │
     │     │ 备份数据(AES-CFB)  │  │ 写数据(可能未加密)   │
     │     └────────────────────────┘  └──────────────────┘
     │                    │              │
     │                    ▼              ▼
     │                 磁盘/磁带存储    [spws MSDP 重删]
     │                    │
     │                    │ CORBA
  t5 │                  bpbrm ──CORBA──▶ bpjobd
     │                    │ update_dte_mode_to_monitor()
     │                    ▼
     │                  NBDB (作业完成)
     │                    ▼
     │                  nbjm / bperror ← 可从 VxUL 日志回溯
     │                    │ nbjm.*.log     │ bperror
     │                    │ nbpem.*.log    │ nbaudit
     │                    │ bpbrm.*.log    │ 审计事件
     │                    ▼
     │                 结论: DTEMode=On 写入作业记录

 日志审计贯穿全程:
 ┌─────────────────────────────────────────────────────────────────────┐
 │ nbaudit           ← 安全事件: 登录/证书/加密协商                     │
 │ nbjm VxUL(OID117) ← 作业级日志: DTE 决策/分配/执行                  │
 │ bperror           ← 错误/警告: 加密失败/连接超时                     │
 │ bpdbjobs -L       ← 作业摘要: DTEMode 字段                          │
 │ nbseccmd          ← 配置命令本身无日志, 依赖 nbaudit 审计            │
 └─────────────────────────────────────────────────────────────────────┘
```

图中标记的 2 个 DTE 决策点对应的代码逻辑：

```
┌── DTE 决策点 1 (nbjm 端) ────────────────────────────────────────┐
│  nbjm::JobManager::refreshDteCache()                             │
│    ├── nbseccmd 查询全局 DTE 模式                                │
│    ├── 查询策略中的 DTE 设置                                     │
│    └── 缓存结果供后续作业使用                                    │
└──────────────────────────────────────────────────────────────────┘

┌── DTE 决策点 2 (bpbrm 端) ───────────────────────────────────────┐
│  bpbrm 对于每个作业:                                              │
│    ├── g_dte_mode = DTE_MODE_ON/OFF/ENFORCED                    │
│    ├── 跳过检查: Catalog/import/verify/skip_dte                │
│    ├── vnet_is_peer_dte_capable() → 对端能力                    │
│    ├── 客户端 DTE 模式: Off/On/Auto                             │
│    ├── 介质服务器 DTE: emmlib_QueryMediaDTESetting()            │
│    ├── 特殊处理: NAT/SAN/XBSA                                   │
│    ├── 最终模式 → BRMJobDteModeMsg → bpcr_adjust_connect_options│
│    └── update_dte_mode_to_monitor() → 写入作业记录              │
└──────────────────────────────────────────────────────────────────┘
```

## 8. 进程启动顺序

### 8.1 NBU 服务启动顺序（nbsvcmon.conf START_ORDER）

```
Phase 0: 基础设施层
  ┌─ 1. postgres   ── PostgreSQL 数据库（所有持久化数据的基础）
  │
Phase 1: 安全层
  ├─ 2. nbatd      ── EAB 认证令牌守护（身份认证基础设施）
  ├─ 3. nbazd      ── 访问控制
  ├─ 4. nbevtmgr   ── 事件管理器
  └─ 5. nbaudit    ── 审计日志

Phase 2: 核心服务层
  ├─ 6. nbemm      ── 企业介质管理（其他服务的注册中心）
  ├─ 7. nbrb       ── 资源代理
  ├─ 8. vmd        ── 卷管理器
  ├─ 9. ltid       ── 驱动器/磁带守护
  ├─10. bpdbm      ── 备份数据库管理
  ├─11. bprd       ── 备份请求守护
  └─12. bpcompatd  ── 兼容性守护

Phase 3: 作业与策略层
  ├─13. nbjm       ── 作业管理器
  ├─14. nbpem      ── 策略执行管理器
  └─15. nbsl       ── 服务层（管理所有 nbproxy 代理）

Phase 4: 网络与备份执行层
  ├─16. bmrd       ── 裸机恢复守护
  ├─17. vnetd      ── 网络认证网关（4 种代理进程）
  ├─18. bpcd       ── 客户端守护（需 vnetd 就绪）
  ├─19. nbvault    ── 保险库管理
  ├─20. nbstserv   ── 存储服务
  ├─21. nbim       ── 库存管理
  └─22. nbrmms     ── 远程介质和存储管理

Phase 5: 数据与扩展层
  ├─23. nbkms      ── 密钥管理服务
  ├─24. spoold     ── MSDP 重删存储（PDDE）
  ├─25. spad       ── MSDP 重删服务
  ├─26. nbars      ── 审计报告服务
  ├─27. nbdisco    ── 发现服务
  ├─28. nbwmc      ── Web 管理控制台（Tomcat）
  ├─29. nbmqbroker ── 消息队列（RabbitMQ）
  ├─30. nbcctd     ── CCT（证书透明）服务
  └─31. nbpas      ── 策略审计服务
```

### 8.2 进程父子关系

```
systemd (PID 1)
  ├── postgres (13785, scaleadmin)  ── NBDB
  ├── pgbouncer (scaleadmin)        ── 数据库连接池
  ├── vnetd -standalone (13724)     ── 认证网关
  │     ├── vnetd -proxy inbound_proxy
  │     ├── vnetd -proxy outbound_proxy
  │     ├── vnetd -proxy http_pbx_tunnel
  │     └── vnetd -proxy http_api_tunnel
  ├── nbatd                         ── 令牌守护
  ├── nbemm                         ── EMM 中心
  ├── nbrb                          ── 资源代理
  ├── bprd (13720)                  ── 请求守护
  ├── bpdbm                         ── 数据库管理器
  │     ├── bpdbm (child)
  │     ├── bpdbm (child)
  │     └── bpjobd                  ── 作业守护
  ├── bpcd (13782)                  ── 客户端守护
  ├── nbsl                          ── 服务层
  │     └── nbproxy dblib *         ── 7 个 CORBA 代理进程
  ├── nbpem                         ── 策略执行
  │     ├── nbproxy dblib nbpem
  │     ├── nbproxy dblib nbpem_cleanup
  │     └── nbproxy dblib nbpem_email
  ├── nbjm                          ── 作业管理器
  │     └── nbproxy dblib nbjm
  ├── nbrmms                        ── 远程存储
  │     └── bpstsinfo *             ── 存储轮询子进程
  ├── spws                          ── MSDP VPFS
  ├── ltid                          ── 卷管理
  ├── nbanomalymgmt                 ── 异常检测
  ├── nbdisco                       ── 发现
  ├── nbaudit                       ── 审计
  ├── bpcompatd                     ── 兼容
  ├── nbstserv                      ── 存储服务
  ├── nbvault                       ── 保险库
  ├── nbim                          ── 库存
  ├── bpclntcmd -cred_cache_mgr     ── 凭据缓存
  ├── bpjava-msvc                   ── Java 桥接
  │     └── bpjava-susvc *          ── Java 会话
  └── nbsvcmon                      ── 服务监控器
```

### 8.3 启动依赖链

```
postgres (数据库基础设施)
  └── nbemm (服务注册中心，所有其他服务依赖)
        ├── nbrb      ── 需要 EMM 查询资源
        ├── bpdbm     ── 需要 EMM 和数据库
        │     └── bpjobd ── bpdbm 子进程
        ├── bprd      └── 需要 bpdbm 和 EMM
        ├── nbjm/nbpem ── 需要 EMM 和 CORBA
        ├── nbsl        ── 服务层，管理 nbproxy
        └── vnetd/bpcd  ── 网络入口

nbatd (认证基础设施)
  └── vnetd (网络认证网关)
        └── bpcd (客户端接入)
              └── bpbackup/bprestore (客户端工具)

nbsvcmon (服务监控, PID 1)
  └── 监控所有 nbservice.conf 中 START_ORDER 的服务
        重启失败超过 RESTART_LIMIT(3) 次的服务
```

## 9. NBU 日志与审计分析

### 9.1 日志体系概览

NBU 有 4 层日志系统并行运行：

| 日志系统 | 存储路径 | 管理工具 | 用途 |
|---------|---------|---------|------|
| VxUL 统一日志 | `/usr/openv/logs/<OID>/` | vxlogcfg/vxlogview | 组件级详细日志（推荐） |
| bperror 问题 | `/usr/openv/netbackup/bperror/` | bperror | 作业状态/错误报告 |
| 旧版日志 | `/usr/openv/netbackup/logs/<component>/` | mklogdir | 临时调试日志 |
| 审计日志 | `/usr/openv/logs/nbaudit/` | nbauditreport | 安全操作审计 |

### 9.2 nblog.conf OID 配置体系

nblog.conf 通过 vxlogcfg 工具管理，每个组件由唯一的 OID（数字 ID）标识：

```
OID=组件名(LogDirectory/OIDNames)

18=nbatd,         111=nbemm,       116=nbpem,       117=nbjm
118=nbrb,         119=bmrd,        132=nbsl,        137=libraries
140=mmui,         143=mds,         144=da,          151=ndmp
156=ace,          158=ncfrai,      159=ncftfi,      163=nbsvcmon
166=nbvault,      178=dsm,         199=nbftsrvr,    200=nbftclnt
201=fsm,          202=stssvc,      210=ncfive,      219=rsrcevtmgr
220=dps,          221=mpms,        222=nbrmms,      226=nbstserv
230=rdsm,         231=nbevtmgr,    254=SPSV2RecoveryAsst
261=aggs,         263=wingui,      264=winbargui,   271=nbecmsg
272=expmgr,       286=nbkms,       293=nbaudit,     294=nbauditmsgs
309=ncf,          311=ncfnbservercom,               317=ncfbedspi
```

vxlogcfg 管理命令：
```
vxlogcfg -a -p ProductID -o OriginatorID -s KeyName=value    # 新增配置
vxlogcfg -l [-p ProductID [-o OriginatorID]]                  # 列出配置
vxlogcfg -r -p ProductID [-o OriginatorID] [-s KeyName]       # 删除配置
```

日志级别控制（vxlogcfg -s）:
- DiagLevel=0(禁用)~6(最详细)
- LogToConsole=0/1
- LogToFile=0/1
- MaxFileSize=bytes
- MaxFiles=count

### 9.3 bperror 问题报告系统

bperror 是 NBU 最常用的状态查看工具，存储格式为：
```
<unixtime> <type> <msgid> <severity> <host> <pid> <tid> <client> <text>
```

关键参数：
| 参数 | 说明 |
|------|------|
| -all | 所有事件（含状态） |
| -problems | 仅错误/警告 |
| -U | 原始格式 | 
| -backupid <id> | 按作业过滤 |
| -S <hh:mm> | 按起始时间过滤 |
| -e <hh:mm> | 按结束时间过滤 |

字段含义：
- type: 0=N/A, 1=status, 2=error, 3=warning, 4=info
- severity: 0=emergency~8=debug
- msgid: NBU 统一消息 ID

典型输出：
```
1785394747 1 1536 4 nbusvr103 0 0 0 *NULL* nbemm Volume nbusvr103:test:Internal_16 marked up
07/30/2026 04:06:57 nbusvr103 nbusvr103  SLP: 2 unexpected error conditions found by nbstserv
```

msdp 相关错误 ID 范围（部分）：
- 1536 = 卷状态变更
- 5930 = 认证失败（需 WEB 登录）
- 8301~8314 = DTE 加密相关（来自 libnbssl/libnbtls 模块）

### 9.4 nbaudit 审计日志

审计日志记录了所有安全敏感操作，存储在 `/usr/openv/logs/nbaudit/`，通过 `nbauditreport` 查看：
```
nbauditreport  # 显示所有审计记录
```

审计记录格式：
```
TIMESTAMP                USER                                DESCRIPTION
07/30/2026 14:16:17      nbwebsvc@NBU_HOSTS                  Automatic cleanup process deleted '2' system events.
07/27/2026 17:53:27      root@nbusvr103                      [bpdbm],[-],[Peer:nbumed103, uuid, IP:port],
                                                                [Destination: IP:port],
                                                                [Operation:Add Data to ErrorDB, Resp:0ms, Exit:0]
07/27/2026 17:32:51      root@nbusvr103                      [bprd],[-],[Peer:nbusvr103, uuid, IP:port],
                                                                [Destination: IP:13720],
                                                                [Operation:Login Attempted, UserName:root, Domain:...,
                                                                 Resp:72ms, Exit:0]
07/27/2026 13:45:34      45bc6618-...                        Host name '10.6.67.187' mapped to host ID '...@nbusvr103'
07/27/2026 13:39:25      root@nbusvr103                      [bprd],[job-uuid],[Peer:uuid, IP:port],
                                                                [Destination: 13720],[Operation:Backup initiation,
                                                                 Resp:1001ms, Exit:0]
```

审计记录包含的关键字段：
- Peer: 对端主机名/UUID/IP:Port（可追踪加密握手来源）
- Destination: 目标服务端口（13720=bprd, 13721=bpdbm, 13724=vnetd, 1556=nbdb）
- Operation: 操作类型（Login Attempted, Backup initiation, Policy Attributes）
- Exit code: 0=成功（加密相关错误会显示非零值）

### 9.5 加密相关日志/调试方法

启用 DTE 详细日志：
```bash
# 为 nbjm/nbpem/bpbrm 启用 VxUL 详细日志
vxlogcfg -a -p NB -o 117 -s DiagLevel=5    # nbjm
vxlogcfg -a -p NB -o 116 -s DiagLevel=5    # nbpem
vxlogcfg -a -p NB -o 18  -s DiagLevel=5    # nbatd

# 旧版日志（临时启用）
mkdir /usr/openv/netbackup/logs/bptm
mkdir /usr/openv/netbackup/logs/bpbrm
touch /usr/openv/netbackup/logs/bptm/bptm.log

# 查看实时 DTE 日志
tail -f /usr/openv/logs/nbjm/nbjm.*.log | grep -i -E 'dte|encrypt|tls|cert|830[0-9]|831[0-9]'

# 查看加密协商审计
nbauditreport | grep -i -E 'tls|ssl|cert|encrypt|auth'
```

### 9.6 管理命令链（加密配置路径）

```
┌─ nbseccmd ── DTE 全局/介质服务器加密配置 ──── 主入口
│   ├── -setsecurityconfig -dteglobalmode <0/1/2>   # 0=禁用, 1=首选, 2=强制
│   ├── -setsecurityconfig -dtemediamode <off/on>    # 介质服务器级别覆盖
│   ├── -setsecurityconfig -insecurecommunication     # 兼容 8.0 以下
│   ├── -setsecurityconfig -autoaddhostmapping        # 自动主机映射
│   ├── -setsecurityconfig -externalcertidentity      # 外部证书标识
│   ├── -getsecurityconfig -dteglobalmode             # 查询当前配置
│   └── -nbcaMigrate                                  # CA 迁移
│
├─ nbcertconfig ── 主机证书管理 ───────────────── 认证
│   ├── -configure                                    # 初始配置
│   ├── -authenticate                                 # 身份认证
│   ├── -u                                            # 更新用户证书
│   └── -s                                            # 服务器证书
│
├─ nbhostidentity ── 主机身份导入 ──────────────── 身份
│   ├── -import                                       # 导入主机身份
│   ├── -testpassphrase                               # 测试口令
│   └── -info                                         # 查看身份信息
│
├─ bpinst -LEGACY_CRYPT ── 旧版加密设置 ────────── 兼容
│   ├── -crypt_option denied|allowed|required
│   ├── -crypt_strength des_40|des_56
│   └── -policy_encrypt 0|1
│
├─ bpnbat ── 认证登录 ────────────────────────── 认证
│   └── -login -loginType WEB|WEBUI|APIKEY
│
├─ nbcredkeyutil ── 凭据密钥工具
│
└─ bpnbaz ── NBU 安全最佳实践分析器
```

注意：nbseccmd -getsecurityconfig 需要先执行 bpnbat -login（WEB 认证），否则返回 EXIT STATUS 5930（认证失败）。

### 9.7 各加密组件的日志位置总结

| 组件 | OID | VxUL 日志 | 旧版日志 | 关键事件 |
|------|-----|-----------|---------|---------|
| nbatd | 18 | /usr/openv/logs/nbatd/ | - | 令牌颁发/验证 |
| nbkms | 286 | /usr/openv/logs/nbkms/ | - | 密钥管理 |
| nbaudit | 293 | /usr/openv/logs/nbaudit/ | - | 安全操作审计 |
| nbjm | 117 | /usr/openv/logs/nbjm/ | - | 作业调度（含 DTE 决策） |
| nbpem | 116 | /usr/openv/logs/nbpem/ | - | 策略评估 |
| nbemm | 111 | /usr/openv/logs/nbemm/ | - | 服务注册/加密协商 |
| bpbrm | - | - | logs/bpbrm/ | 备份恢复管理（含连接加密） |
| bptm | - | - | logs/bptm/ | 数据传输（含数据流加密） |
| bpcd | - | - | logs/bpcd/ | 客户端通信 |
| vnetd | - | - | logs/vnetd/ | 网络代理 |
| nbcert | - | /usr/openv/netbackup/logs/nbcert/ | - | 证书管理 |
| nbseccmd | - | - | - | 安全配置（CLI 无日志） |

## 10. 实验验证结果

### 10.1 实验方法

通过远程 SSH 连接 10.6.67.187 (nbusvr103)，执行以下验证：
1. 配置检查：bp.conf / nbseccmd / nbdeployutil 配置导出
2. 作业调查：bpdbjobs 历史作业 DTE 状态
3. 日志分析：nbjm VxUL 日志中的 DTE 协商过程
4. 网络监听：ss 提取进程级端口绑定
5. 符号交叉验证：本地同步的 bpbrm/bptm 二进制 nm 导出

### 10.2 DTE 配置验证结果

| 配置项 | 值 | 含义 |
|--------|-----|------|
| CONNECT_OPTIONS (localhost) | `localhost 1 0 2` | localhost: 允许(1)/不验证证书(0)/TLSv1.2(2) |
| DEFAULT_CONNECT_OPTIONS | `0 1 0` (默认值, 未显式配置) | 非 localhost: 0=不指定/允许(1)/不要求TLS(0) |
| DTE_CLIENT_MODE | AUTOMATIC | 客户端 DTE 自动模式（首选但非强制） |
| NB_FIPS_MODE | DISABLE | FIPS 140-2 禁用 |
| ALLOW_ENCRYPTION | NO | 旧版加密未显式许可 |
| VMWARE_TLS_MINIMUM_V1_2 | YES | VMware 使用 TLS 1.2 |

### 10.3 已完成作业 DTE 状态

通过 `bpdbjobs -jobid <id> -L` 确认最近 MSDP 备份作业：

```
706 Backup Done 0 file-test-msdp full nbusvr103 nbumed103 21753 No On
704 Backup Done 0 file-test-msdp full nbusvr103 nbumed103 8896  No On
```

- **DTEMode = On**: DTE 数据传输加密已激活
- **FATPipe = No**: 未使用 FATPipe（快照加速管道）
- 目标介质服务器为 nbumed103 (10.6.67.251)，数据路径使用 IN-APP-TLS
- DTE `On` 表示 bpbrm↔bptm↔bpcd↔bpdm 之间的 TCP 数据流使用 TLS 加密

### 10.4 加密符号交叉验证（bpbrm）

bpbrm 二进制中提取的 DTE 相关符号：

```
类别          符号                              说明
─────        ────                              ────
配置获取       bpcr_get_dte_client_config_rqst   CORBA 请求 DTE 客户端配置
EMM 查询      emmlib_QueryMediaDTESetting       查询 EMM 中介质服务器 DTE 设置
模式控制      g_dte_mode / g_dte_mode_value      全局 DTE 模式状态
             dte_global_mode_str                 DTE 模式字符串（Off/On/Strict）
             disable_separate_comm_sock_for_dte  禁用独立 DTE 通信套接字
             enable_proxy_for_dte                为 DTE 启用代理
             is_media_server_dte_disabled        介质服务器 DTE 禁用标志
             is_data_channel_encrypted           数据通道加密状态
vnetd 集成   vnet_is_peer_dte_capable           查询对端 DTE 能力
             vnet_set_dte_mode_in_tss            在 TSS 中设置 DTE 模式
加密回调      set_connection_encryption_callback  设置连接加密回调
             connection_encryption_detected       检测连接是否已加密
             mangleGetLastSSLErrorCode           获取最后一个 SSL 错误码
IN-APP-TLS   inapp_tls_enabled_for_snap_backup   IN-APP-TLS 用于快照备份
消息传递      BRMJobDteModeMsg                    BRM DTE 模式消息
策略         OBV::PEM::PemPolicy::encryption()   PEM 策略加密方法
JM 集成      Veritas::NetBackup::JM::JobManager::refreshDteCache()
                                                 作业管理器 DTE 缓存刷新
证书路径     OBV::PEM::PemPolicy::*EcaCertPath*   ECA 证书路径
             OBV::PEM::PemPolicy::*deploymentCert* 部署证书源
SSL 套接字   Symantec::NetBackup::Ncf::NBCS::SSLSocket::*
                                                 NBCS SSL 套接字操作
```

### 10.5 加密符号交叉验证（bptm）

bptm 中直接使用 libnbtls 处理数据流加密：

```
类别          符号                              说明
─────        ────                              ────
TLS 配置      nbtls_config_init/fin               TLS 配置初始化/清理
             nbtls_config_set_int               设置整数配置项
             nbtls_config_set_str               设置字符串配置项
             nbtls_config_set_ssl_options       设置 SSL 选项
TLS 上下文    nbtls_ctx_init/fin                 TLS 上下文初始化/清理
TLS I/O       nbtls_handshake                     TLS 握手
             nbtls_io                            TLS 加密读写
PSK           nbdte_psk_get/put                   预共享密钥 Get/Put
DTE 模式      dteMode / DTE_MODE                  DTE 模式标志
             dte_context_initializer              DTE 上下文初始化
             determine_dte_mode_by_image          根据镜像确定 DTE 模式
              check_dte_support                   检查 DTE 支持
加密密钥      get_encryption_key                  获取加密密钥
             report_encryption_status            报告加密状态
             BH_MAY_BE_ENCRYPTED                 备份头可能已加密标记
磁带加密      scsi_establish_encryption            SCSI 建立加密
             scsi_report_encryption_capabilities  SCSI 报告加密能力
             manage_drive_encryption             管理磁带驱动器加密
             DRIVE_ENCRYPTION_ACTIVE             磁带驱动器加密激活标志
```

### 10.6 验证结论

| 验证项 | 结果 | 证据 |
|--------|------|------|
| DTE 是否启用 | ✅ 是 | bpdbjobs DTEMode=On |
| TLS 版本 | TLS 1.2 | CONNECT_OPTIONS "...2", VMWARE_TLS_MINIMUM_V1_2 |
| 加密库 | libnbtls + libnbssl | bptm 符号 nbtls_handshake/nbtls_io |
| PSK 支持 | ✅ 是 | nbdte_psk_get/put |
| IN-APP-TLS 路径 | ✅ 活跃 | bpbrm inapp_tls_enabled_*, vnet_set_dte_mode_in_tss |
| vnetd-proxy 路径 | ⚠️ 备用 | DEFAULT_CONNECT_OPTIONS 0=allow |
| 证书验证 | ⚠️ 不验证证书 | CONNECT_OPTIONS auth=0 |
| FIPS 模式 | ❌ 禁用 | NB_FIPS_MODE=DISABLE |
| 旧版加密 | ❌ 禁用 | ALLOW_ENCRYPTION=NO |
| 磁带加密 | ✅ 支持 | SCSI 加密命令 + manage_drive_encryption |

## 11. 安全风险分析

### 11.1 风险评级总览

| # | 风险项 | 严重度 | 影响面 | 利用难度 |
|---|--------|--------|--------|---------|
| R1 | 私钥未加密 PEM 文件 | **高** | 服务器提权后可窃取所有私钥 | 低（需本地 root） |
| R2 | 证书验证关闭 | **高** | MITM 攻击 | 中（需网络访问） |
| R3 | FIPS 模式禁用 | 中 | 不合规 | 低 |
| R4 | DTE 可降级明文 | 中 | 加密失效 | 低 |
| R5 | 审计覆盖不足 | 中 | 攻击溯源难 | 低 |
| R6 | vnetd 代理可观测 | 中 | 数据在代理节点暴露 | 高（需代理权限） |
| R7 | 旧版加密残留 | 低 | DES/40-bit 弱加密 | 高 |
| R8 | PRNG 依赖 OpenSSL | 低 | 熵源质量 | 极低 |
| R9 | nbseccmd 认证未持久化 | 低 | 配置查询需每隔登陆 | 无安全影响 |

### 11.2 R1: 私钥未加密 PEM 文件

```
风险描述:
  ┌─────────────────────────────────────────────────────────┐
  │ PrivKeyFile-2048.pem (RSA 2048 私钥, PEM 格式)          │
  │ 文件权限: 600 (rw-------)                                │
  │ 所有者: root                                             │
  │ 文件内容: -----BEGIN RSA PRIVATE KEY-----                │
  │           MIIEpQIBAAKCAQEA... (Base64 编码, 无加密)      │
  │           -----END RSA PRIVATE KEY-----                  │
  │                                                          │
  │ 同路径还有:                                              │
  │   - c44f05de-...-key.pem  (主机私钥, 未加密)             │
  │   - websvccreds/.../key.pem  (Web 服务私钥, 未加密)     │
  └──────────────────────────────────────────────────────────┘

攻击场景:
  1. 攻击者通过 Web 漏洞获取 nbwebsvc 权限
  2. 读取 /usr/openv/var/vxss/at/root/.VRTSat/profile/certstore/keystore/PrivKeyFile-2048.pem
  3. 使用该私钥冒充 NBU CA 签发伪造证书
  4. 实施中间人攻击，解密所有备份流量

缓解措施（按优先级）:
  [1] 启用文件系统加密（LUKS/eCryptfs）保护 /usr/openv/var/vxss/
  [2] 使用 HSM/KMS 存储私钥（nbkms 可集成外部 KMS）
  [3] 文件权限增强：限制 root 以外用户不可读（当前已 600）
  [4] 定期轮换私钥（nbcertcmd -renewKeyPair）
```

### 11.3 R2: 证书验证关闭

从 CONNECT_OPTIONS 和实验验证中确认：

```
DEFAULT_CONNECT_OPTIONS = 0 1 0
                        ↑
                  验证设置: 1 = verify server cert?
                          (实际行为: 握手时不验证证书链)

实际验证情况:
  CONNECT_OPTIONS localhost 1 0 2
                           ↑
                     auth = 0 = 不验证证书

  当 tlsSessionResumption.enable=1 时:
    - 初次连接: TLS 握手, 但有 cert_auth=0 不检查 CA 签名
    - 会话恢复(30min内): 使用 Session Ticket, 完全无证书
```

这意味着即使 DTE=On 的作业使用了 TLS 1.2，客户端也**不验证服务器证书**，存在 MITM 风险。攻击者可在网络路径上伪造证书劫持备份数据。

### 11.4 R3: FIPS 模式禁用

```
NB_FIPS_MODE = DISABLE

FIPS 禁用意味着:
  - 允许使用非 FIPS 认可的算法（如 DES、BF）
  - 允许使用 OpenSSL 默认的随机数生成器（非 FIPS 认证）
  - 允许使用 TLS 1.0（配置中虽指定 1.2，但无强制执行）
```

### 11.5 R4: DTE 可降级明文

```
DTE 降级条件:
  1. 全局 DTE = Preferred On（非 Enforced）
  2. 客户端不支持 DTE → 自动降级 vnetd-proxy
  3. vnetd-proxy 可选择不加密
  4. DEFAULT_CONNECT_OPTIONS = 0 1 0 → 不要求 TLS

降级链:
  客户端支持 DTE? → 否 → vnetd-proxy → 无加密
  客户端 DTE On?  → 否 → 使用 DEFAULT_CONNECT_OPTIONS(无TLS)
  介质服务器?      → 不支持 → 降级 vnetd-proxy
  NAT 客户端?      → 特殊处理 → 忽略 DTE 要求
  SAN 传输?        → DTE 不支持 → 明文传输
```

### 11.6 R5: 审计覆盖不足

| 安全事件 | nbaudit 记录 | 可回溯性 |
|---------|-------------|---------|
| 证书颁发/吊销 | ✅ 记录 | 完整 |
| 用户登录 | ✅ 记录 | 完整 |
| 备份作业(含 DTE) | ✅ 记录(exit code) | 可通过作业 ID 关联 |
| **DTE 配置变更** | ❌ 无记录 | **无法回溯** |
| **私钥访问** | ❌ 无记录 | **无法审计** |
| **TLS 握手失败** | ❌ 无独立记录 | 需在组件日志中查找 |
| **证书验证失败** | ❌ 无记录 | 证书验证已关闭(见 R2) |

`nbseccmd -setsecurityconfig` 本身不产生审计日志，只能通过 VxUL 日志间接查看调用时间。

### 11.7 R6: vnetd 代理可观测

vnetd-proxy 路径是 DTE 降级时的备用方案。代理进程可以看到：

```
vnetd inbound_proxy → 可以观测所有通过代理的数据
                    → 如果代理节点被攻破, 数据完整可见
                    → 与控制通道共享同一进程空间

对比 IN-APP-TLS:
  IN-APP-TLS → 端到端加密, 代理不可见数据内容
             → 但需要双方都支持
             → 本环境中 DTE=On 证明 IN-APP-TLS 已启用
```

### 11.8 风险缓解建议（对本文方案）

| 风险 | 本文方案应对 |
|------|------------|
| R1 私钥未加密 | 使用 SM4 加密存储私钥 + 密码派生保护 |
| R2 证书不验证 | 强制双向证书验证（mTLS）+ CRL/OCSP 检查 |
| R4 降级明文 | 永久禁用降级路径，加密失败即作业失败 |
| R5 审计不足 | 所有加密操作（配置变更/握手/密钥派生）强制审计 |
| R6 代理泄露 | 使用 IN-APP-TLS 直连，不设计代理降级路径 |
| 国密合规 | 替代 RSA/AES/SHA-256 为 SM2/SM4/SM3 |

## 12. 备份数据镜像格式与加密

### 12.1 镜像结构总览

NBU 备份镜像（Image）是一个多层嵌套的数据容器：

```
┌──────────────────────────────────────────────────────────────────┐
│  NBU 备份镜像（Image）                                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Media Header (介质头)                                       │  │
│  │   格式: tape_media_header                                   │  │
│  │   字段: media_id, block_size, volgrp, written_time, ...    │  │
│  │   位置: 磁带/文件开头的第一块                                  │  │
│  │   大小: 固定 (约 512 字节)                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Backup Header(s) (备份头)                                   │  │
│  │   格式: backup_hdr / bh_rec / bh_rec2                      │  │
│  │   字段: backup_id, filenum, block_size,                     │  │
│  │         image_attrib, dump_level, host_info,                │  │
│  │         BH_MAY_BE_ENCRYPTED  ← DTE 加密标记                │  │
│  │   每个备份片段 (fragment) 可有一个备份头                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ FRAG (片段)                                                │  │
│  │   fragment_num=0..n: 数据分片                               │  │
│  │   每个 fragment 包含:                                        │  │
│  │     ├── TIR Header (Table of Contents)                     │  │
│  │     ├── TIR Data (文件索引)                                 │  │
│  │     ├── AH Header(s) (加速头, MSDP 专用)                   │  │
│  │     ├── File Data Blocks (实际文件数据)                     │  │
│  │     │     格式: xfer_block (传输块)                         │  │
│  │     │     块大小: block_size (可配置, 默认 64KB)            │  │
│  │     │     数据: 原始文件数据或加密后的密文                     │  │
│  │     └── Tar Header/Trailer (tar 包裹，可选)                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ NBDB 索引记录 (数据库)                                      │  │
│  │   IMAGE 记录: backup_id, policy, schedule, TIR 位置        │  │
│  │   IMAGEDETAILS: 每个文件的路径/大小/属性                     │  │
│  │   FRAG 记录: fragment_list, media_id, offset, size         │  │
│  │   COPY 记录: 副本信息, DTEMode, 加密状态                    │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 12.2 关键数据结构

#### 介质头 (Media Header)

```
tape_media_header {
    char    media_id[11];        // 介质 ID (e.g., "Internal_16")
    int32_t block_size;          // 块大小 (字节)
    char    volgrp[32];          // 卷组
    int32_t written_time;        // 写入时间戳
    int32_t rec_offset;          // 记录偏移
    int32_t rec_length;          // 记录长度
    char    fms[32];             // 介质格式标识
    // ...更多字段
};
```

#### 备份头 (Backup Header)

```
backup_hdr {
    char    backup_id[128];      // 备份 ID (e.g., "nbusvr103_1234567890")
    int32_t filenum;             // 文件号
    int32_t block_size;          // 块大小
    int32_t dump_level;          // 备份级别 (0=全备, 1-9=增量)
    char    client_name[128];    // 客户端名
    char    policy_name[128];    // 策略名
    char    schedule_name[128];  // 调度名
    BH_image_attrib image_attrib; // 镜像属性 (含加密标记)
    int32_t bh_flags;            // BH_MAY_BE_ENCRYPTED  ← DTE
    // ...更多字段
};
```

#### 片段索引 (FRAG Record)

```
FRAG 记录 (由 db_initFRAG_REC 管理):
  backup_id, copy_num, fragment_num
  media_id, file_num, block_offset
  fragment_size (KB)
  fragment_type (DATA/TIR/AH)
  encryption_info:
    - DTE mode at write time
    - encryption algorithm used
    - key reference (if KMS)
```

### 12.3 加密数据布局

当 DTE=On 时，备份数据在 xfer_block 级别加密：

```
无加密 (DTE=Off):
┌──────────────────────────────────────────┐
│ Backup Header (明文)                      │
│ FRAG[0]: TIR (明文) → File Data (明文)   │
│ FRAG[1]: TIR (明文) → File Data (明文)   │
└──────────────────────────────────────────┘

IN-APP-TLS (DTE=On, nbtls):
┌──────────────────────────────────────────┐
│ Backup Header (明文, BH_MAY_ENCRYPTED=1) │
│ FRAG[0]: TIR (明文) → [nbtls_io]        │
│   ┌── TLS 记录 ──┐                       │
│   │ File Data    │ (AES-CFB 加密密文)    │
│   │ HMAC 校验    │                       │
│   └──────────────┘                       │
│ FRAG[1]: TIR (明文) → [nbtls_io]        │
│   ┌── TLS 记录 ──┐                       │
│   │ File Data    │ (加密密文)            │
│   └──────────────┘                       │
└──────────────────────────────────────────┘

SCSI 磁带加密 (T10/SSC):
┌──────────────────────────────────────────┐
│ Backup Header (明文)                      │
│ [SCSI 建立加密]                           │
│   scsi_establish_encryption_di()         │
│   scsi_modify_write_mode_di()            │
│ FRAG[0..n]: 磁带硬件自动加密             │
│   (t10 加密, 对 bptm 透明)                │
│ [SCSI 查询状态]                           │
│   scsi_report_encryption_status_di()     │
└──────────────────────────────────────────┘

LEGACY_CRYPT (旧版):
┌──────────────────────────────────────────┐
│ Backup Header (明文)                      │
│ 文件数据: DES-40/DES-56 加密             │
│ 密钥: bpkeyfile / passphrase             │
│ 强度: 弱 (40/56-bit)                     │
└──────────────────────────────────────────┘
```

### 12.4 数据加密层次

NBU 支持三层独立的加密机制，可以同时启用：

```
┌──── 层 1: 传输加密 (DTE IN-APP-TLS) ──────────────────────────┐
│  范围: TCP 数据流层面的 TLS 加密                               │
│  粒度: 整个 TCP 连接 (备份的所有 FRAG 数据)                    │
│  透明性: 对上层应用透明（bptm 通过 nbtls_io 读写）         │
│  密码套件: nbtls_config_set_ssl_options() 中配置              │
│  密钥: TLS 握手阶段协商 (临时会话密钥)                          │
│  生命周期: 备份作业期间                                       │
└──────────────────────────────────────────────────────────────┘

┌──── 层 2: SCSI 磁带加密 (T10/SSC) ────────────────────────────┐
│  范围: 磁带设备级别的硬件加密                                   │
│  粒度: 整盘磁带 (全局)                                         │
│  透明性: 对 bptm 完全透明（硬件处理）                            │
│  算法: 驱动器固件决定 (AES-256-GCM 等)                        │
│  密钥: scsi_establish_encryption() 通过 SCSI 命令设置          │
│  生命周期: 磁带使用周期                                         │
│  状态: DRIVE_ENCRYPTION_ACTIVE 跟踪                            │
└──────────────────────────────────────────────────────────────┘

┌──── 层 3: 旧版应用加密 (LEGACY_CRYPT) ────────────────────────┐
│  范围: 文件数据层面                                           │
│  粒度: 每个备份文件                                            │
│  算法: DES-40/DES-56                                           │
│  密钥: bpkeyfile 或 passphrase                                 │
│  状态: ALLOW_ENCRYPTION=NO (本环境已禁用)                      │
└──────────────────────────────────────────────────────────────┘
```

### 12.5 加密密钥体系

```
备份数据加密的密钥派生路径:

  [TLS 握手]                              [KMS 集成]
     │                                        │
     ▼                                        ▼
  临时会话密钥                             持久密钥
  (TLS_ECDHE_RSA_WITH_*)                    (由 nbkms 管理)
     │                                        │
     ▼                                        ▼
  nbtls_io() 加密数据                    get_encryption_key()
     │                                        │
     │                              ┌─────────┴──────────┐
     │                              ▼                    ▼
     │                          SCSI 加密密钥        LEGACY_CRYPT 密钥
     │                          (scsi_establish_)    (DES 密钥)
     │                                                     │
     │                                           ┌─────────┴──────────┐
     │                                           ▼                    ▼
     │                                       bpkeyfile            KMS KEK
     │                                       (passphrase)        (kbkms 封装)
     │
     ▼
  加密的数据写入 xfer_block

  注: IN-APP-TLS 和 SCSI 加密可同时启用:
      IN-APP-TLS 保护 TCP 传输
      SCSI 加密保护静态磁带数据
      两层独立, 互不干扰
```

### 12.6 bpdbjobs 命令中的 DTE 字段

从 `bpdbjobs -L` 确认 DTE 状态可以按以下级别查询:

```
bpdbjobs -jobid <id> -L
  └── DTEMode: On/Off ─── 作业级 DTE 状态

bpdbjobs -backupid <id> -L
  └── -image_dtemode <Off|On>     ← 映像级 DTE 设置
      -copy_dtemode <Off|On>      ← 副本级 DTE 设置
      -hierarchical_dtemode <Off|On> ← 层级 DTE 设置
```

bpdbjobs 的输出字段中:
```
706 Backup Done 0 file-test-msdp full nbusvr103 nbumed103 21753 No On
                                                                   ↑
                                                            DTEMode=On
```

### 12.7 验证本环境中的加密数据

```
本环境分析:
  ┌──────┬──────────────────────────────────────────────────────┐
  │ 层   │ DTE IN-APP-TLS (层1)                                  │
  │ 状态 │ ✅ 活跃                                                │
  │ 证据 │ bpdbjobs DTEMode=On                    (10.3)       │
  │     │ bptm nbtls_handshake/nbtls_io symbol   (10.5)       │
  │     │ bpbrm vnet_set_dte_mode_in_tss         (10.4)       │
  ├──────┼──────────────────────────────────────────────────────┤
  │ 层   │ SCSI 磁带加密 (层2)                                   │
  │ 状态 │ ⚠️ 支持但未验证激活                                     │
  │ 证据 │ bptm scsi_establish_encryption symbol  (10.5)       │
  │     │ DRIVE_ENCRYPTION_ACTIVE 全局变量                      │
  ├──────┼──────────────────────────────────────────────────────┤
  │ 层   │ LEGACY_CRYPT (层3)                                   │
  │ 状态 │ ❌ 禁用                                               │
  │ 证据 │ ALLOW_ENCRYPTION=NO                   (10.2)       │
  └──────┴──────────────────────────────────────────────────────┘

  备份镜像存储路径:
    MSDP (PureDisk): /usr/openv/storage/<pool>/           ←重删存储
    BasicDisk:       /usr/openv/netbackup/db/images/      ←普通磁盘
    磁带:            /dev/tape/by-path/... (SCSI VTL)     ←虚拟磁带

  镜像格式总结:
    MSDP → 内部 PDDE 格式 (重删 + 压缩 + 可选加密)
    磁盘 → 标准 NBU image 格式 (同上节数据结构)
    磁带 → 标准 NBU tape 格式 (media_header + backup_hdr + frag)
```

## 13. 验收标准完成情况

- [x] DTE 四层配置模型完整还原
- [x] 三个二进制加密符号导出并分类
- [x] 证书链完整追踪（CA→broker→主机）
- [x] 加密算法清单及国密支持说明
- [x] DTE 决策流程以文本流程图呈现
- [x] IN-APP-TLS vs vnetd-proxy 条件列表
- [x] 给本文方案 8 条具体改进建议
- [x] NBU 日志与审计分析（VxUL/bperror/nbaudit/加密调试）
- [x] 实验验证结果（DTE=On 确认/bpbrm+bptm 符号交叉验证）
- [x] 安全风险分析（R1~R9 评级及缓解建议）
- [x] 数据加密与镜像格式分析（镜像结构/加密布局/3层加密体系/密钥派生）

## 14. 调研方法记录

| 方法 | 执行情况 |
|------|---------|
| SSH 远程命令 | 执行 7 轮远程命令收集配置/运行时信息 |
| strings 分析 | bpbackup/bpbrm/bptm 三二进制 strings 提取 |
| nm 符号分析 | libnbssl/libnbtls/libcmncryptocore/libcredhelper 符号导出 |
| ldd 依赖分析 | bpbrm/bptm 动态链接依赖分析 |
| 文档对照 | 与 nbu-comparison.md/design.md/spec.md 交叉验证 |
