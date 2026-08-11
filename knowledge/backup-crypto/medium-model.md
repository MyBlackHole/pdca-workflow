---
title: 备份国密介质承接模型（ZFS / S3 / OSS / NFS）
topic: backup-crypto
created_at: 2026-08-11
source_record: records/T0246-0810-backup-gm-transport-encryption/conclusion.md
base:
  - aio-tools 6200 release 源码组件梳理
  - database_国密 8 份调研结论
  - OceanBase 4.2.1.1 验证基线
---

# 备份国密介质承接模型

## 结论

针对**数据库备份数据在"传输"与"存储"两个维度的国密支持**，介质维度存在一套可复用的承接模型，按备份目标介质分四类：

| 介质 | 存储国密承接方式 | 挂载/还原手段 | 传输国密 |
|------|-----------------|---------------|----------|
| ZFS（本地 / 远端 / 后端承载） | **ZFS 自身存储加密**（信创平台选 SM4；ZFS 透明加密，写入即密文） | iSCSI 挂载，ZFS 透明解密直接获取明文 | 由备份链路升级国密 TLS |
| S3（对象存储） | **s3file 以 SM4 密文上传**（`--gmssl` SM4-CBC）；或介质侧静态加密可配 | 挂载资源端 **s3mount** 挂载密文块解密还原 | 现状标准 HTTPS（国际套件） |
| OSS（后端 ZFS 承载） | 复用 **ZFS 自身存储加密**（OSS 后端由 ZFS 实现） | OB 备份工具直连 OSS IP:端口 恢复（不经挂载） | OB→OSS 为 **HTTP 明文**（未启用 TLS） |
| NFS（后端 ZFS 承载 / 通用 NFS） | **后端 ZFS 自身存储加密**（NFS 由 ZFS 提供）；或 Worker 侧先 SM4 加密再写 NFS（NFS 协议层无原生国密） | **filemount 挂载 NFS 密文块解密**（文件系统→NFS）；OB 场景 NFS 介质读取（ZFS 透明解密） | 由 Worker 应用层升级国密；NFS 协议层不能原生国密 |

## 关键模式

1. **ZFS 是国密兜底介质**：ZFS 自身存储加密（透明加密）为通用承载能力，凡是后端落 ZFS 的介质（OSS / NFS）均可直接复用，无需备份工具改造。
2. **S3 走应用层密文**：S3 无透明加密对接，需 s3file 在 Worker 侧以 SM4 密文写入，挂载资源端以 s3mount/filemount 解密还原——密文能力落在应用层工具而非介质本身。
3. **传输国密与存储国密解耦**：传输靠备份链路（aio-speed/aio-speedd RPC、SBT 协商头）升级国密 TLS；存储靠介质模型。两轴独立评估、独立落地。
4. **工具层不支持 ≠ 全部不可国密**：部分数据库（如 gaussDB gs_roach 硬编码 AES、OB 无独立 SM4 备份开关）传输不可国密，但存储侧仍可经 ZFS/S3 密文承接——评估时应两轴分离。

## 边界 / 失效条件

- 依赖 aio-tools **6200 release** 组件形态（fsdeamon / s3file / aio-speed / backUpAgent 等），未来 release 组件可能演进。
- "OB/gaussDB 传输不可国密"为 **现状事实**（OB 4.2.1.1 验证基线；gs_roach 套件硬编码 AES-*），**不构成永久限制**，未来版本可能支持。
- NFS 协议层无原生国密（RPCSEC_GSS/Kerberos enctype 无 SM 条目），国密必须落应用层；ZFS SM4 需在 ICP 加密框架注册 `sm4-gcm`（纯软件损耗 ~90%，需硬件加速/信创 CPU SM4 指令）。
- 文档为架构+链路级，不含单函数实现细节。

## 复用场景

- 新数据库接入备份国密评估时，先按"传输链路 X 存储介质"两轴套用本模型定位缺口。
- 新介质对接（如 MinIO/腾讯 COS）时，判断介质侧是否具备透明加密（类 ZFS）或需应用层密文（类 S3）。
- 密评/等保 L3-CES7-25 数据链路要求核查的介质侧能力速查。