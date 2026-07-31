# 备份复制传输加密 — 技术设计文档

## 问题陈述

- **现状**: 备份/复制数据传输链路中，RPC 层（Agent↔Worker）已有 OpenSSL mTLS 加密；dmsbtex（达梦 SBT）和 libobk（Oracle SBT）使用裸 TCP 明文传输，无任何加密保护，无法满足等保三级 L3-CES7-25 要求。
- **目标**: 为所有备份数据网络传输链路支持国密 TLS（SM2/SM3/SM4 + TLCP 协议），用户可在计划/保护层面控制开关。
- **差距**: 当前 tls_cert 库硬编码 OpenSSL `TLS_method()`，缺乏 GMSSL 后端；tls_keygen 仅支持 Ed25519 密钥；dmsbtex/libobk 无任何加密基础设施。

## PoC 结论（基于 xmake-repo GMSSL v3.1.1）

### 已验证功能

| 测试项 | 结果 |
|--------|------|
| SM2 密钥生成 + PEM | ✅ |
| X.509 CA 证书签名 + 自验 | ✅ |
| CA → 服务端证书链 + 验签 + 提取 Subject | ✅ |
| SM4-GCM 加解密 + 篡改检测 | ✅ |
| TLCP/TLS13 上下文创建 | ✅ |
| GMSSL SM2 证书 → OpenSSL 验签 | ✅（双向兼容） |

### 已知限制

| 限制 | 影响 |
|------|------|
| GMSSL 不支持 Ed25519 | 现有 tls-keygen 签发的证书链无法由 GMSSL 解析/验签 |
| OpenSSL SM2 证书 → GMSSL 验签失败 | 公钥解析正常，但 `sm2_do_verify` 签名验证失败（SM2 实现间互操作差异） |
| `x509_cert_sign_to_der` 不自动分配内存 | 需两段式调用（先算长度，再分配写入） |

**结论**：不能直接替换 OpenSSL。存量 Ed25519 证书和 OpenSSL 签发的 SM2 证书均存在兼容问题。需采用双后端设计。

## 核心架构设计

### 1. tls_cert：双后端 TLS 抽象层

**当前问题**：`tls_cert.c` 硬编码 OpenSSL API（`TLS_method()`、`SSL_CTX_new()`、`EVP_PKEY_ED25519`），不支持国密。

**改造方案**：增加 GMSSL 后端，通过编译时/运行时选择切换。

```
tls_cert_init_client_ex(TLS_BACKEND_OPENSSL)  → OpenSSL TLS 1.3 + mTLS（现有路径，不变）
tls_cert_init_client_ex(TLS_BACKEND_GMSSL)    → GMSSL TLCP + SM2/SM4（新增）
tls_cert_init_client_ex(TLS_BACKEND_AUTO)     → 根据目标组件能力协商
```

运行时自动选择逻辑：
- 目标组件声明支持国密 TLCP → 选 GMSSL 后端
- 目标组件仅支持 OpenSSL → 选 OpenSSL 后端（兼容存量 Ed25519 证书）
- 两者都不支持 → 按策略报错或降级

### 2. tls-keygen：新增 SM2 子命令，保留 Ed25519

**当前**：`tls-keygen` 仅支持 Ed25519。

**改造**：新增 `--alg sm2` 选项。Ed25519 路径保持不动，用于存量兼容。

### 3. 证书目录规划

```
/opt/aio/cfg/certs/
├── ca.crt              # OpenSSL CA 证书（Ed25519，存量，保持不动）
├── ca.key              # OpenSSL CA 私钥（存量）
├── host.crt            # 主机证书（Ed25519，存量）
├── host.key            # 主机私钥（存量）
├── sm2_ca.crt          # SM2 CA 证书（新增，GMSSL 签发）
├── sm2_ca.key          # SM2 CA 私钥（新增）
├── sm2_host_sign.crt   # 主机签名证书（新增，TLCP 双证书之一）
├── sm2_host_sign.key   # 主机签名私钥（新增）
├── sm2_host_kenc.crt   # 主机加密证书（新增，TLCP 双证书之二）
└── sm2_host_kenc.key   # 主机加密私钥（新增）
```

### 4. 配置设计

**`/opt/aio/cfg/rdb.conf`** `[security]` 节新增：

```ini
[security]
; 传输加密开关：0=关闭（默认），1=开启
transfer_encrypt_enable = 0

; 加密策略：enforced（强制，不支持则失败），preferred（首选，不支持则降级警告）
transfer_encrypt_policy = enforced

; 加密算法：auto（自动选择），sm2（强制国密），rsa（强制 OpenSSL）
transfer_encrypt_alg = auto

; 组件级独立覆盖开关，格式：<组件名>=<0|1>
; component_transfer_encrypt_override = 
```

**粒度控制**：
- **全局策略**：rdb.conf 作为域级别默认值
- **计划级开关**：上层按备份计划/保护/复制计划独立设置
- **组件级覆盖**：通过 `component_transfer_encrypt_override` 或环境变量单独控制

### 4a. 决策矩阵

```
全局策略  组件能力              计划开关          作业结果
─────────────────────────────────────────────────────────────
enforced  支持国密 TLS          on/未设置 → 加密传输（TLCP）
enforced  支持国密 TLS          off      → 明文传输（计划级显式关闭）
enforced  仅支持 OpenSSL        on/未设置 → 加密传输（TLS 1.3）
enforced  仅支持 OpenSSL        off      → 明文传输
enforced  不支持 TLS            任意     → 作业失败 ENC-004
preferred 支持国密 TLS          on/未设置 → 加密传输（TLCP）
preferred 仅支持 OpenSSL        on/未设置 → 加密传输（TLS 1.3）
preferred 不支持               任意     → 明文传输（写入告警日志）
off       任意                 任意     → 明文传输
```

### 5. 各工具改造详情

#### 5.1 RPC 层（aio-speed / aio-speedd）

RPC 层的 `rpc_server_connect()` 中根据配置选择 GMSSL/OpenSSL 握手。新增 `sec_transfer_encrypt_enabled()` + `sec_transfer_encrypt_alg()` 配置接口。

数据流：
```
Agent CLI (aio-speed)
  → rpc_server_connect(ip, port)
    → sec_transfer_encrypt_enabled()?
        → 根据 alg 选择后端：
            sm2  → tls_cert_init_client_ex(GMSSL) → TLCP 握手
            rsa  → 已有 OpenSSL mTLS 路径
            auto → 探测目标能力后选择
```

#### 5.2 dmsbtex（达梦 SBT）

裸 TCP 链路新增 TLS 握手层。保持 `send_data()` / `recv_data()` 接口不变，握手后在 SSL 结构体上读写。

#### 5.3 libobk（Oracle SBT）

改造模式与 dmsbtex 一致：连接建立后插入 TLS 握手，SSL 读写替换 `send()`/`recv()`。

### 6. 编译集成

GMSSL 库已在 `third_party/gmssl/`，为预编译二进制（`lib_x86_64/` + `lib_aarch64/`）。各目标在 xmake.lua 中新增 `gmssl` 链接依赖。

## 双后端运行时选择策略

```
                        ┌─ alg=sm2 → GMSSL 后端
  sec_transfer_encrypt ──┼─ alg=rsa → OpenSSL 后端（存量 Ed25519）
                        └─ alg=auto → 握手阶段探测
                              ├─ 目标 TLCP 就绪 → GMSSL
                              └─ 目标仅 OpenSSL → OpenSSL
```

`auto` 模式的探测机制：
1. 客户端发起标准 TCP 连接
2. 服务端返回能力宣告（TLCP 就绪 / 仅 OpenSSL）
3. 客户端根据结果选择后端握手
4. 协商结果缓存在连接上下文，后续复用

## 错误处理与降级

按需求要求：**加密传输失败时作业明确失败，不会静默降级为明文**。

### 细分错误码

| 错误码 | 失败场景 | 检测时机 |
|--------|---------|---------|
| ENC-001 | 证书已过期 | 握手时返回 |
| ENC-002 | 证书 CN 不匹配 | verify callback |
| ENC-003 | 算法套件协商失败 | 握手时协商失败 |
| ENC-004 | 组件不支持加密 | init 时检测 |
| ENC-005 | 证书未部署 | 服务端未找到客户端 CA |
| ENC-006 | 跨站点证书不可信 | verify callback |
| ENC-007 | TLS 协议版本不匹配 | 握手时协商失败 |
| ENC-008 | 全局强制但组件不支持 | 连接前策略检查 |

## 验收映射

| 需求编号 | 对应设计 | 验证方法 |
|---------|---------|---------|
| ENC-T-001~002 | 上层 UI + RPC 配置传递，底层传输层提供能力 | 页面截图 + 作业前后对比 |
| ENC-T-003~004 | 保护粒度配置 | 页面截图 |
| ENC-T-005~006 | 复制计划独立开关，不继承 | 页面截图 + 作业对比 |
| ENC-T-007 | tls_cert GMSSL 后端 + 日志记录加密套件 | 作业日志含国密套件说明 |
| ENC-T-008 | GMSSL TLCP 协议加密 | 抓包验证密文 |
| ENC-T-009 | 错误处理规则，不降级明文 | 失败作业截图 x3+ |
| ENC-T-010 | 组件兼容性运行时检测 | 失败作业截图 |
| ENC-T-011 | 复用存储加密硬件加速能力，软件回退 | 性能测试报告 |
| ENC-T-012 | 上层详情页 + 作业详情展示 | 页面截图 |

## 性能预期

### SM4-GCM 对称加密吞吐

- **硬件加速可用**（SM4-NI / ARMv8 CE）：加密吞吐可达 1600+ MB/s，备份链路瓶颈一般在磁盘 I/O
- **纯软件回退**（国产 CPU 无 SM4 指令集）：加密吞吐约 85-100 MB/s，对千兆网络备份充分，万兆链路可能有瓶颈

### SM2 非对称操作性能

SM2 仅在 TLCP 握手阶段使用（每次连接建立时一次）：
- 单次握手 SM2 操作总量：~500-2000 us，对单次备份无感
- 大量并发连接（100+）时握手延迟叠加可达百毫秒级，可通过 TLS session 复用缓解

## 范围外

- S3 工具（s3-tool / s3tools）HTTPS 传输层——不在本次需求范围
- rdbcomm 传输加密——已排除
- xbsa 本地存储接口——不涉及网络传输
- 硬件指令集加速（SM4-NI/ARMv8 Crypto Extensions）——复用存储加密的同一能力，不单独建设
- 外部 CA 导入——本次仅实现内置 CA 自签发，后续迭代

## 备注

- GMSSL 库预编译路径：`third_party/gmssl/lib_{x86_64,aarch64}/libgmssl.a`
- OpenSSL 版本保持 3.6.1 不变，与 GMSSL 完全独立
- 证书路径沿用现有 `/opt/aio/cfg/certs/` 目录，新增 `sm2_` 前缀文件
- tls_cert 重构保持向后兼容，现有 OpenSSL mTLS 行为不变
- 存量 Ed25519 证书由 OpenSSL 后端维护，存量节点不降级；新增 SM2 证书由 GMSSL 后端管理
