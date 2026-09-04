---
schema: pdca.asset/v1
id: ontology:domain/nbu-nbu-dte-architecture
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/nbu-nbu-dte-architecture/1.0.0
summary: NBU DTE 传输加密架构
domain:
- ontology:domain/nbu
relations:
  specializes:
  - ontology:domain/nbu
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'NBU DTE 传输加密架构' ontology/domain/zfs/nbu-nbu-dte-architecture.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# NBU DTE 传输加密架构

> 复用来源：records/T0148-0731-nbu-transfer-encrypt-research/ + records/T0162-0731-nbu-dte-packet-capture/ + records/T0163-0731-nbu-dte-enforced-mechanism/
> 实际验证环境：NBU 10.3.0.1, CentOS 7.9, nbusvr103(10.6.67.187) + nbumed103(10.6.67.251)
> 验证日期：2026-07-31

## 强制加密（Enforced）服务端机制（静态分析，T0163）

**核心结论：修改为 Enforced 无需重启服务端**，配置变更走"写配置 + 主动刷新通知"链路，进程内缓存热更新；缓存带 TTL 兜底。```
nbseccmd -setsecurityconfig -dteglobalmode 2     ← 配置入口（0/1/2）
   │ ① 写入安全配置（EMM）
   │ ② 发起 bpcr_refresh_dte_global_config_rqst   ← 关键：改配置即推送刷新，非重启触发
   ▼
bprd: "Refresh DTE Cache"（权限校验 + 集群广播 refresh_dte_for_cluster）
   │ ③ CORBA/bpcr 通道下发
   ├──▶ nbjm:  refreshDteCache (CORBA) → 更新进程内 m_globalDteInfo
   └──▶ nbemm: MdsServer::refreshGlobalDteCache → 更新 EMM 缓存
              (libVemmMT.so Get/PutQueryMediaDTESettingCache, CacheTemplate+DefaultTime TTL)
   ▼
执行点: nbjm 子作业调度期（***DTE*** 判定）→ 失败拒绝 或 dte_mode=6 下发 bpbrm/bptm
   → 连接建立期: VNET 协商（T0162 实证）
```

**关键组件**：
- nbseccmd: `-dteglobalmode 0|1|2`、`-dtemediamode off|on -mediaserver <ms>`、隐藏命令 `-cleardtecache`；引用 `bpcr_refresh_dte_global_config_rqst`（U）
- bprd: 实现 refresh 请求，操作名 "Refresh DTE Cache"，权限校验 "Not a valid server to request DTE cache refresh"，集群路径 `refresh_dte_for_cluster`
- nbjm: CORBA 方法 `JobManager_i::refreshDteCache`（完整 TAO skeleton），缓存变量 `NBJMSvc::m_globalDteInfo`
- nbemm: `MdsServer::refreshGlobalDteCache`，日志 "Successfully refreshed the MDS cache for Global DTE Mode to value [ %d ]"
- libVemmMT.so: `GetQueryMediaDTESettingCache`/`PutQueryMediaDTESettingCache`，`CacheTemplate<string,string,DefaultTime>`（TTL 兜底）

**强制守卫执行点 = nbjm 子作业调度期**（非连接建立期），错误串：
- "DTE mode is enforced, but media server is not DTE capable, media server version = "（< 9.1 → 作业失败，错误码 8301）
- "DTE global mode is enforced, but MEDIA_DTE_MODE is set OFF on media server"（错误码 8311）
- 日志前缀 `***DTE***`（Determining/Fetched/Re-fetching DTE mode）

**Enforced vs Preferred On**：
| 维度 | Enforced (2) | Preferred On (1) |
|---|---|---|
| 客户端 OFF / <9.1 | 作业失败（调度期拒绝） | 尽力加密，可排除个别客户端 |
| 生效方式 | 同链路，改配置即刷新 | 同链路 |
| 重启需求 | 无需重启（仅存量不安全连接需断开） | 无需重启 |

**Enforced vs insecurecommunication off**（两个独立维度）：
- insecurecommunication off：管控 legacy 明文端口/VNET 允许列表（官方文档建议重启）
- DTE Enforced：数据路径加密强度（应用层），热刷新生效
- NBU 10.3 实测全走 1556 (PBX)，legacy 端口已不参与（T0162）；Enforced 不隐含 insecurecommunication off，需分别配置

### 安全机制（T0163 补充）

**纵深防御四层 + 语义兜底 + 审计**：
1. 配置入口认证：nbseccmd 需 bpnbat WEB/WEBUI/APIKEY 登录（实测无登录→5930 拒绝）
2. 通道认证：bpcr_authenticate_connection / vnet_vxss_authenticate（每请求证书/主机身份）
3. 服务器身份白名单：bprd "Not a valid server to request DTE cache refresh"
4. 语义兜底：刷新≠降级——刷新只重载已落盘配置，恶意刷新最多缓存抖动（TTL 恢复），无法改配置值
5. 审计：bpcr_update_host_config_audit_rqst / Audit::tr_dte_global_mode（配置变更全程留痕）

**"直接改配置文件"结构性不可行**：NBU 无 DTE 文本配置文件（bp.conf/var/global/mds.db 实测均不含）；DTE 存于 nbdb (PostgreSQL)，密码 AES-256-CTR 加密存于 vxdbms.conf（密钥在内部密钥库），psql 直连需认证（实测 fe_sendauth 拒绝），改库后缓存隔离（TTL 内不生效）+ 审计留痕。合法唯一入口 = nbseccmd -setsecurityconfig。

**服务程序读取路径（双层架构，非全部直连）**：只有 **nbemm 直连 nbdb**（ldd: libnbdbMT.so + libVdbMT.so，符号 VxDBMS_Conf::GetEMMConnectString）；应用进程（nbjm）经 emmlib API → libVemmMT.so（ldd 无 nbdb，CORBA/TAO IPC）→ 双层缓存（nbemm EMM 缓存 → nbjm GetQueryMediaDTESettingCache）→ 才见新值。改库需穿透 5 层：密码加密 → psql 认证 → nbemm 缓存 → nbjm 缓存 → 审计。

## 单端口协商机制（抓包实证，T0162）

**核心结论**：加密与否是**连接内协商结果，非端口属性**（STARTTLS 式）。

```
同一端口 1556 (PBX) ← 注意：实际通信端口为 1556，非 13782/13724！
  │
  ├── TCP 连接建立
  │       ▼
  ├── 明文 VNET 头: "ack=<n>\nextension=<service>\n\n"   (ASCII 明文)
  │       ▼
  ├── 响应: "\x1c" (1 字节)
  │       ▼
  ├── 响应: "badfeed" + 4字节长度 + JSON 协商载荷
  │         {ca_roots, connection_id, proxy_version:6, peer_host, dte_mode, ...}
  │       ▼
  ├── dte_mode=6 (bpbrm/bptm 数据路径) ──▶ TLS 1.2 升级 (0x16 0x03 0x01)
  │       │                                │
  │       │                                ▼
  │       │                        加密数据 (0x17 0x03 0x03)
  │       │
  └── 控制面 (GIOP/CORBA 明文流, 如 nbemm/bpjobd/bpdbm) ──▶ 保持明文
```

**实证数据**（30 流分类）：
- 25 流以 `ack=` 明文头开头 → 全部升级 TLS
- 1 流纯 GIOP 明文（`47494f50`），无 TLS
- 4 流抓包中途已建立的 TLS 会话

**dte_mode 字段**（JSON 协商载荷）：

| 服务 | dte_mode | 含义 |
|------|---------|------|
| bpbrm / bptm | 6 | DTE 启用（数据路径） |
| nbemm / bpjobd | -1 | 不参与 DTE（控制面） |
| bpdbm / bpcompatd | 0 | 不参与 DTE（控制面） |

**动态生效佐证**：nbusvr103 uptime 84 天（2026-05-08 启动），每次作业新建连接重新协商，无需重启服务。改配置后仅影响新连接；重启的目的仅为强制断开存量不安全连接。

## 决策矩阵（四层）

```
全局 DTE 模式（域级别）
  ├── Preferred Off  （首选关闭）
  ├── Preferred On   （首选开启，10.0+ 全新安装默认）
  └── Enforced       （强制加密，不支持则作业失败）

客户端 DTE 模式（主机级别）
  ├── Off
  ├── On
  └── Auto（10.0+ 默认）

介质服务器 DTE 模式（主机级别）
  ├── Off
  └── On（默认）

映像 DTE 模式（作业/备份集级别）
  ├── Off
  └── On
```

## 实际配置验证（nbusvr103）

```
# bp.conf
DEFAULT_CONNECT_OPTIONS = 0 1 0       # 默认: 允许加密/验证证书/不要求TLS
CONNECT_OPTIONS = localhost 1 0 2     # 本地: 允许/不验证/TLSv1.2
NB_FIPS_MODE = DISABLE                # FIPS 140-2 禁用
DTE_CLIENT_MODE = AUTOMATIC           # 客户端 DTE 自动模式
ALLOW_ENCRYPTION = NO                 # 旧版加密禁用

# 已验证的作业 DTE 状态
bpdbjobs -L: DTEMode = On            # file-test-msdp 备份作业
```

## 关键符号（bpbrm 二进制提取）

bpbrm 中 DTE 决策的核心符号：
```
g_dte_mode / g_dte_mode_value        # 全局 DTE 模式状态
dte_global_mode_str                  # DTE 模式字符串
emmlib_QueryMediaDTESetting          # EMM 查询介质服务器 DTE 设置
vnet_is_peer_dte_capable             # vnetd 查询对端 DTE 能力
vnet_set_dte_mode_in_tss            # 在 TSS 中设置 DTE 模式
bpcr_adjust_connect_options          # 调整连接选项
bpcr_get_dte_client_config_rqst     # CORBA 获取客户端 DTE 配置
BRMJobDteModeMsg                     # BRM DTE 模式消息
update_dte_mode_to_monitor          # 更新 DTE 模式到监控
```

## 关键符号（bptm 二进制提取）

bptm 中数据加密的核心符号：
```
nbtls_config_init / fin              # TLS 配置
nbtls_ctx_init / fin                 # TLS 上下文
nbtls_handshake                      # TLS 握手
nbtls_io                             # 加密读写
nbdte_psk_get / put                  # PSK 管理
dte_context_initializer              # DTE 上下文
get_encryption_key                   # 获取加密密钥
scsi_establish_encryption            # SCSI 磁带加密
scsi_report_encryption_capabilities  # SCSI 查询加密能力
DRIVE_ENCRYPTION_ACTIVE              # 驱动器加密状态
BH_MAY_BE_ENCRYPTED                 # 备份头加密标记
```

## 加密库栈

```
libnbssl.so (libopenssl 封装) → 实际 OpenSSL 调用
libnbtls.so (32 KB)          → TLS 轻量封装
libnbcertmgmt.so (1.6 MB)    → 证书管理
libcmncryptocore.so (534 KB) → 核心加解密 (mangle)
libcredhelperMT.so           → 凭据管理
libvxVxSSIOPST.so            → VxSS 安全身份 (CORBA TLS)
```

## 证书体系

```
NBU CA (RSA 2048, 自签名)
  ├── 主机证书 (RSA 2048, 为每个主机颁发)
  ├── 密钥对 (RSA 2048, nbcertcmd -authenticate)
  └── 配置: NBCA:ON ECA:OFF

私钥存储:
  /usr/openv/var/vxss/at/root/.VRTSat/profile/certstore/keystore/
  └── PrivKeyFile-2048.pem (未加密 PEM, 600 root)
```

## 备份镜像格式

```
Media Header → Backup Header(s) → FRAG[0..n]
  └── 每个 FRAG: TIR Header + TIR Data + AH Header + File Data Blocks
  └── 加密级别: DTE IN-APP-TLS (nbtls_io) / SCSI T10 / LEGACY_CRYPT
```

## 安全风险（已验证）

| ID | 风险 | 严重度 |
|----|------|--------|
| R1 | 私钥未加密 PEM 文件 | 高 |
| R2 | 证书验证关闭 | 高 |
| R3 | FIPS 禁用 | 中 |
| R4 | DTE 可降级明文 | 中 |
| R5 | 审计覆盖不足 | 中 |
| R6 | vnetd 代理可观测 | 中 |
| R7 | 旧版加密残留 | 低 |
| R8 | nbseccmd 认证未持久化 | 低 |

## 关键规则（已验证）

- Enforced 模式下，客户端 Off 或版本 < 9.1 → 作业失败（不降级）
- Preferred On → 低版本主机自动跳过加密（降级到 vnetd-proxy）
- DTE 决策流程: 全局配置 → 跳过条件 → 对端版本 → 客户端模式 → 介质服务器 → NAT/SAN特殊处理
- 备份数据 xfer_block 级别通过 nbtls_io 加密，AES-CFB/BF/DES
- 介质服务器 DTE On 参与资源调度，优先分配

## 错误码（8301~8314）

| 码 | 含义 |
|----|-------|
| 8301 | 全局 Enforced 但介质服务器 < 9.1 |
| 8308 | 映像 DTE=On 但客户端 < 9.1 |
| 8310 | 客户端 DTE=On 但介质服务器 Off |
| 8311 | 全局 Enforced 但介质服务器 DTE Off |
| 8314 | DTE_CLIENT_MODE=On 但介质服务器 Off |

## 证书体系

- 内置 NetBackup CA，安装时自动签发基于主机 ID 的证书
- 私钥 AES-256-CBC 加密存储
- 支持外部 CA 导入（10.0+）
- 证书部署安全级别：高/中/低
- tls-keygen 中的 Ed25519 类似 NBU 的主机 ID 证书

## TLCP 与 DTE 对比

| 维度 | NBU DTE | TLCP |
|---|---|---|
| 协议 | TLS 1.3 | GB/T 38636-2020 |
| 证书算法 | Ed25519/RSA | SM2 |
| 对称加密 | AES-256-GCM | SM4-GCM/SM4-CBC |
| 密钥 | 单密钥对 | 双密钥对（签名+加密） |
