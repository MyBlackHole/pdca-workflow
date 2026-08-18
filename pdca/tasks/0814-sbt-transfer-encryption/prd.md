# PRD — 备份复制传输加密（SBT 链路国密 TLS）

## 问题陈述

- **现状**: 备份/复制数据传输链路中，RPC 层（Agent↔Worker，aio-speed↔aio-speedd）已有常规 TLS 加密；dmsbtex（达梦 SBT → dm-ftp）和 libobk（Oracle SBT → FileTransferAgent）使用裸 TCP 明文传输，无法满足等保三级 L3-CES7-25 要求。
- **目标**: aio-tools 数据链路支持国密 TLS（SM2/SM3/SM4，TLS1.3 RFC 8998 单证书国密套件），用户可在配置层控制开关（security 节 + 计划级开关），单端口加密/非加密并存，开启即强制（失败不降级明文）。
- **差距**: tls_cert 仅 OpenSSL 常规套件（Ed25519 证书）；tls_keygen 仅 Ed25519；dmsbtex/libobk/oss 无加密基础设施。

## 解决方案

同端口以"明文协商头 + 同连接升级 TLS"模型提供国密加密：
- **协商头**: 客户端发起连接先发明文协议头（能力宣告：加密开关 + 国密套件就绪），服务端返回能力响应，客户端按配置与双方能力决定升级 TLS
- **开启即强制**: 配置开启则必须加密，目标不支持国密 → 作业失败（ENC-004），不静默降级明文
- **配置变更不重启**: 连接建立时读取配置，新连接按新配置协商，存量连接不受影响

## Seam 分析

### 测试接缝

- **tls_cert 双后端 vtable**: 后端抽象层（`tls_backend_vtable_t`）是核心接缝——本仓已有 `libs/tests/tls_cert_test.c` 覆盖 OpenSSL 路径；新增 GMSSL 后端测试
- **tls_keygen SM2 子命令**: CLI 层接缝，验证生成 SM2 密钥+证书链可被 GMSSL 加载
- **SBT 协商层**: dmsbtex/libobk 的 network/protocol 层的"协商头→升级"接缝，端到端需要 dm-ftp/FileTransferAgent 服务端配合
- **oss https**: Go http.Server 的 ListenAndServeTLS 接缝

### 声明的测试接缝

- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c
- seam: libs/tls_cert.c -> third_party/gmssl/include/gmssl/tls.h
- seam: dmsbtex/network.c -> dmsbtex/protocol.h
- seam: libobk/lib/logic/oracleCmdTbl.c -> libobk/include/protocol.h
- seam: oss/test/build_oss.sh -> oss/cmd/server.go

### 验收可测性

- 每个 AC 有明确 pass/fail：符号隐藏（nm）、抓包密文（tcpdump）、抓包明文（对照）、失败语义（日志含"传输加密失败"）
- 边界/异常路径可独立构造：证书过期/缺失、目标不支持、配置关闭

## 用户故事

1. 作为 DBA，我希望开启传输加密后备份数据在链路上为国密 TLS 密文，以便满足等保 L3-CES7-25。
2. 作为 DBA，我希望加密建立失败时作业明确失败并提示原因，以便不会在"以为加密实则未加密"的状态下运行。
3. 作为管理员，我希望同一端口同时服务加密/非加密连接且配置变更不重启，以便平滑升级存量环境。

## 实现决策

**不包含具体文件路径或代码片段**。记录：

- **tls_cert 双后端 vtable**（ADR-0001 采纳）：`tls_backend_openssl.c`（封装现有 OpenSSL mTLS）+ `tls_backend_gmssl.c`（封装 GMSSL TLS1.3 RFC 8998），统一到连接生命周期 vtable
- **协议选型修正**: ADR-0001 原选 TLCP（GB/T 38636 双证书），本任务改为 **TLS1.3 RFC 8998 单证书**（`TLS_cipher_sm4_gcm_sm3`=0x00c6，GMSSL `tls13_do_connect/accept`），对齐设计文档
- **tls_keygen 新增 SM2 子命令**: 生成 SM2 密钥与证书链（GMSSL 工具链，因 GMSSL 不兼容 OpenSSL 签发 SM2 证书）
- **单端口协商**: RPC 层复用现有协议头扩展能力宣告；SBT 层（dmsbtex protocol.h network_header_t、libobk protocol.h activeioHeader）新增协商头，服务端默认兼容无协商头存量客户端
- **配置**: [security] 节新增传输加密开关（0/1），复用 rdb-config 现有机制，连接建立时读取
- **oss https**: Go `http.Server` + `ListenAndServeTLS`，加载 SM2 证书链（GMSSL 后端的证书体系）
- **证书目录**: 沿用 /opt/aio/cfg/certs/，新增 sm2_ca/sm2_host 前缀文件

## 测试决策

- 仅测外部行为：加密链路可用性、协商结果、失败语义、密文/明文对照
- 被测模块：tls_cert 后端、tls_keygen、SBT 网络层、oss server
- 现有测试先例：`libs/tests/tls_cert_test.c`、`dmsbtex/test/`、`libobk/test/`、`oss/test/build_oss.sh`（T0251 建立）

## 验收标准

- [ ] AC-1: tls_cert 双后端 vtable 重构完成，OpenSSL 存量路径行为不变（既有 mTLS 测试通过），GMSSL 后端可完成 TLS1.3 RFC 8998 握手
- [ ] AC-2: tls_keygen 新增 SM2 子命令，生成 SM2 证书链可被 GMSSL 后端加载并完成握手
- [ ] AC-3: [security] 节新增传输加密开关（0/1），连接建立时读取，配置变更不重启生效
- [ ] AC-4: dmsbtex↔dm-ftp SBT 链路新增协商头，配置开启时同连接升级国密 TLS，抓包为密文
- [ ] AC-5: libobk↔FileTransferAgent SBT 链路新增协商头，配置开启时升级国密 TLS，抓包为密文
- [ ] AC-6: 配置关闭时明文路径行为完全不变（存量兼容）；服务端默认兼容无协商头的存量客户端
- [ ] AC-7: 加密建立失败（证书过期/缺失/目标不支持）→ 作业失败，日志含"传输加密失败"原因，不降级明文
- [ ] AC-8: oss (aio-oss) 支持 https（SM2 证书链），https 请求可正常服务
- [ ] AC-9: 国密 TLS 加密链路性能重测，产出本仓独立的性能报告（对照明文/OpenSSL TLS/GMSSL TLS1.3）

## 范围外

- UI 页面开关、作业详情页展示（ENC-T-001~006、012）：属上层仓库
- 存储加密（落盘 SM4）：另一需求（存储加密 PRD）
- aarch64 交叉编译产物：本任务在 x86_64 验证，aarch64 库已预编译可用
- OpenSSL 常规套件路线扩展（如 AES）：不属国密需求

## 备注

- 设计文档来源：`/home/black/Public/aio/F/139/备份传输存储加密/备份复制传输加密.md`
- 需求来源：`/home/black/Public/aio/F/139/【安全】支持备份复制传输加密以保障备份数据安全传输.md`（SUB-1 G-01）
- GMSSL 3.1 预编译库已就位：`third_party/gmssl/lib_{x86_64,aarch64}/libgmssl.so.3.1`，三个工程已有手动链接先例
- ADR-0001（双后端 TLS 架构）为本任务架构来源，协议选型按本 PRD 修正为 RFC 8998
- 动态库部署需 LD_LIBRARY_PATH 含 gmssl 路径（生产部署注意）