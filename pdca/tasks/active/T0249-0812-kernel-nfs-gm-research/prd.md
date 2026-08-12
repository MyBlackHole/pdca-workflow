# 研究 kernel-OLK-6.6 的 NFS 国密支持 — PRD

## 问题陈述

- **现状**: `/home/black/Downloads/kernel-OLK-6.6.zip`（openEuler OLK 6.6 内核源码，92265 条目，292MB）已下载未解压；既有知识 `backup-crypto/gm-support-surfaces.md` 断言"NFS 协议层不能原生国密（RPCSEC_GSS/krb5 白名单仅含国际算法）"，但该结论缺少 OLK-6.6 源码级实证
- **目标**: 解压内核源码，基于源码实证 NFS 是否支持国密（SM2/SM3/SM4），更新既有知识资产
- **差距**: 既有结论无源码证据支撑；NFS 数据面国密路径未在 OLK-6.6 上核验

## 解决方案

1. 解压 `kernel-OLK-6.6.zip` 到 `/home/black/Downloads/kernel-OLK-6.6-src/`
2. 聚焦 NFS 数据面国密路径核查：
   - `net/sunrpc/auth_gss/`：RPCSEC_GSS/krb5 enctype 白名单算法集（gss_krb5 _mech/_crypto）
   - `fs/nfs/`、`fs/nfsd/`：是否引用 sm4/sm3/sm2
   - NFS 挂载安全选项（sec=krb5/krb5i/krb5p）支持的算法族
3. 全内核关键路径佐证：`crypto/sm3.c`/`sm4.c` 注册存在性、arch 加速（arm64 CE）
4. 产出结论，更新 `knowledge/backup-crypto/gm-support-surfaces.md`（一致则补充源码证据，不一致则修正）

## Seam 分析

### 测试接缝

- 研究型任务，无代码测试；验证手段为源码静态证据 + 文件存在性检查 + 关键算法名 grep。

### 声明的测试接缝

research 场景无测试产物，跳过 seam 声明。

### 验收可测性

- 每项 AC 可基于源码文件、注册表（alg_name/crypto_register）或 grep 结果独立判定。

## 用户故事

1. 作为备份/存储工程师，我想要确认 NFS 介质是否可能原生走国密传输，以便选择备份链路的国密实现路径（协议原生 vs 网关/IPsec 叠加）。

## 实现决策

- 解压目标：`/home/black/Downloads/kernel-OLK-6.6-src/`
- 核查范围：NFS 数据面（gss 协商白名单、NFS 客户端/服务端引用）、crypto 层佐证
- 产出：`records/T0249…/conclusion.md` + 更新 `knowledge/backup-crypto/gm-support-surfaces.md`

## 测试决策

- 无测试代码；验收依赖源码静态证据链（grep 算法名 + 读取白名单定义）。

## 验收标准

- [ ] AC-1: `kernel-OLK-6.6.zip` 解压成功，源码根目录存在（kernel-OLK-6.6/）
- [ ] AC-2: RPCSEC_GSS/krb5 enctype 白名单已定位并列出算法集（gss_krb5_mech/gss_krb5_crypto 相关文件）
- [ ] AC-3: NFS 客户端（fs/nfs/）与服务端（fs/nfsd/）对 sm4/sm3/sm2 的引用情况已核查（grep 结论）
- [ ] AC-4: crypto 层 sm4/sm3 注册存在性佐证已记录
- [ ] AC-5: 研究结论已产出（是否支持国密，支持/不支持的路径与依据），并更新既有 gm-support-surfaces.md 知识资产（补充源码证据或修正结论）

## 范围外

- 不构建内核、不做运行态挂载验证
- 不枚举全内核（IPsec/TLS 等其他子系统）国密支持面
- 不对 NFS 协议无关子模块做全面审计

## 备注

- 既有知识资产：`knowledge/backup-crypto/gm-support-surfaces.md` 第 3 节（Linux 定制版 NFS 内核国密边界），本任务为其源码级实证