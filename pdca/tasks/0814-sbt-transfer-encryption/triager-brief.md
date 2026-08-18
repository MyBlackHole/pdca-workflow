# Triage Brief — 备份复制传输加密（SBT 链路国密 TLS）

## 分类

- category: `enhancement`（新功能，等保 L3-CES7-25 合规整改）
- scenario_type: `development`
- 需求编号: SUB-1（G-01），功能编号 ENC-T-001~012

## 需求描述

aio-tools 数据链路支持国密 TLS（SM2/SM3/SM4）。现状：RPC 层（Agent↔Worker）已有
常规 TLS；dmsbtex（达梦 SBT）/ libobk（Oracle SBT）使用裸 TCP 明文传输，不满足等保
三级 L3-CES7-25「传输过程采用密码技术保护」。

设计文档：《备份复制传输加密.md》给定：

1. **tls_cert 双后端**：OpenSSL 存量路径不变，新增 GMSSL 后端承载国密套件
   （TLS1.3 国密套件 TLS_SM4_GCM_SM3，RFC 8998）

2. **单端口协商模型**：同一端口明文/加密并存，连接建立时能力宣告 →
   配置开启则同连接内升级 TLS；目标不支持则作业失败（不降级明文）

3. **tls_keygen 新增 SM2 子命令**（保留 Ed25519 存量）

4. **SBT 层**（dmsbtex/libobk ↔ dm-ftp/FileTransferAgent）：裸 TCP 新增协商头 +
   TLS 握手层，服务端默认兼容无协商头的存量客户端

5. **配置**：security 节新增传输加密开关（0=关/1=开），作业发起时读取，无需重启

6. **错误处理**：ENC-001~007 全失败语义，不降级明文

## 关键验证结果

- **已确认现场**：`dmsbtex/network.c` 无 TLS 代码（裸 TCP）；`libs/tls_cert.c`
  仅 OpenSSL（SSL_CTX_new(TLS_method())），无 GMSSL 引用
- **GMSSL 依赖已就位**：`third_party/gmssl/` 含 include + lib_x86_64 + lib_aarch64
  （libgmssl.so.3.1），双架构预编译库已具备
- **tls_keygen** 现仅支持 Ed25519（EVP_PKEY_ED25519），无 SM2
- **dm-ftp / FileTransferAgent** 均为独立服务端程序（install/ 有产物）；FileTransferAgent
  源码在 `libobk/main.c`；dm-ftp 源码位置待确认
- **oss** 已有 xmake.lua（go 项目），需加 https 支持

## 信息缺口

1. dm-ftp 的服务端源码在哪个目录（非 install 产物）？→ 需全局检索 dm-ftp 工程
2. `数据库备份传输加密_国密实现.md`（30187 字节）是否为同一需求的前置版本/可行性验证，改造面与其重复度？
3. 上层 UI（页面开关）不在本仓范围——本任务只负责底层传输层能力 + 配置传递协议
4. 协商头协议格式需与 RPC 层现有协议头对齐，还是 SBT 独立定义
5. 单证书国密套件模式：GMSSL 下 SM2 证书链签发需 GMSSL 工具链，tls_keygen 是否
   直接调用 GMSSL API 而非 OpenSSL（GMSSL 不兼容 OpenSSL 签发的 SM2 证书）

## 查重

- 前作 **T0148**（0731-nbu-transfer-encrypt-research）：NBU DTE 逻辑调研，已完成，
  知识沉淀于 knowledge/nbu/，为本文档 NBU 参考模型来源，不重复
- 未发现同主题开发任务（grep 国密/SM2/传输加密，仅 panic 上述调研任务）

## 建议下一步

- P2 grill 确认信息缺口（尤其 dm-ftp 源码位置、协商头对齐、GMSSL API 使用）
- P3 PRD：按设计文档确立 AC（对齐 ENC-T 编号中本仓可验证部分）
- P6 终审 → Do：分解为 tls_cert 双后端 / tls_keygen SM2 / SBT 协商与升级 三个子模块