---
schema: pdca.asset/v1
id: T0246-0810-backup-gm-transport-encryption
phase: check
source_ids: [doc-v22, convergence-map-v19]
---

## 上下文

任务目标：在 /home/black/Documents/备份传输存储加密/ 产出单份总文档，讲清 aio-tools 6200 release 各类数据库备份传输加密支持国密的现状、实现路径与架构图。依据：6200 release 源码组件梳理 + database_国密 8 份调研。

## 假设与结果

| # | 假设/要求 | 结果 |
|---|----------|------|
| H1 | 单份总文档含六类对象 + 独立场景（备份卷复制 ZFS→S3 / ZFS→ZFS 快照发送、S3 系列资源备份 mc→ZFS）分节 | 达成：文档 679 行，6 类对象节（PG/MySQL/文件系统/SBT/OB/gaussDB）+ 独立场景章（五：备份卷复制 ZFS→S3、ZFS→ZFS 快照发送；六：S3 系列资源备份 mc→ZFS）+ 介质总结章（十） |
| H2 | 每节三段式 + Mermaid 架构图 | 达成：13 张 flowchart，语法自检 PASS（引号/括号配平） |
| H3 | 拓扑符合用户逐轮修正 | 达成：fsdeamon 仅 PG；文件系统=aio-speed(Worker)⇄aio-speedd(数据源)、不用 fsbackup/fs-backup；PG=fs-cli(Worker)⇄aio-speedd(数据源)、不用 aio-speed；MySQL=xtrabackup+aio-speed(数据源)→aio-speedd+xbstream(Worker)；ZFS→S3 为独立场景（s3file，s3mount 在挂载资源端）；OB 与 s3file 无关；ZFS 与 S3/OBS 分开表达 |
| H4 | 已按用户要求裁减 | 达成：无 tls_cert 细节、无 afsd、无 zfsdeamon、无数据流图（全为架构图）；移除全部国密网关/IPSec/安全网关实现表述，网关字样清零 |

## 分析

- 验收标准 11 项（AC-1..AC-11）逐条对照通过：路径/文件名 ✓、总览图+对比表 ✓（表头已中性化为"备份发起组件/备份接收组件"）、六节三段式 ✓、每节≥1 架构图 ✓、文件系统 ZFS 路径与独立章节 S3 路径 ✓、PG/MySQL/文件系统组件与方向 ✓、统一国密手段 ✓、介质总结 ✓、架构级无 file:line ✓、与调研结论一致 ✓、Mermaid 闭合 ✓。
- 证据链：doc-v22（当前有效）取代 v1..v21；convergence-map-v19；validate-convergence 返回 valid:true。全部 AC 由 doc-v22 覆盖。
- 多轮需求变更（7 次用户拓扑修正 + ZFS→ZFS 场景新增 + 国密网关移除 + ZFS 明文写入修正 + 文件系统→NFS 直接备份场景（传输国密 + 先国密加密再写 NFS）+ 各架构图增加挂载资源端使用（iSCSI 挂载 ZFS 透明解密获取明文 / s3mount / NFS 解密 / OB 直连 S3/OSS IP:端口恢复，不经挂载）；删除统一国密落地手段章节；OB/gaussDB 架构图标题改为“当前架构图”、小节改为“国密支持现状”（传输不可国密）；OB 拆分 S3 与 OSS 两个实现（OSS 后端由 ZFS 承载，复用 ZFS 自身存储加密，新增 7.2 子节与架构图；OB→OSS 链路为 HTTP 明文，区别于 S3 的 HTTPS；OB 增加 NFS 备份支持（NFS 后端由 ZFS 承载，复用 ZFS 自身存储加密，新增 7.3 子节与架构图）；OB 架构图删除 TDE 内容（数据本身属性，与备份链路无关）；OB→NFS 改为 OB 服务器本机挂载 NFS 目录后直接写读（本机文件操作，非远端拉取）；7.3 恢复侧改为从 NFS 介质读取（ZFS 透明解密）；4.2 文件系统→NFS 挂载资源端改用 filemount 挂载解密（对齐 s3mount 模式），术语表新增 filemount；新增独立场景“S3 系列资源备份（mc→ZFS）”（mc = MinIO Client，S3 下拉至 ZFS），独立为第六章并与数据库章节同级，后续章节编号顺延（OB→八、gaussDB→九、介质总结→十，内部 7.x→8.x、9.x→10.x），术语表新增 mc）已全程同步到文档/PRD/收敛链；残留旧表述扫描全零。

## 失败原因（仅 rejected/partial）

无。

## 适用边界

- 文档为架构+链路级（组件/协议/端口/配置开关），不含单函数实现细节，不构成实施代码。
- 存储侧数据基于调研结论（gs_roach 不支持国密、OB 无独立 SM4 开关、NFS 原生不支持国密、ZFS SM4 需 ICP 扩展）。
- 密钥管理为建议性（现状内置常量密钥，建议进化为 KMS）。

## 下一轮建议

- 若需实施：结合 GMSSL 双后端、SBT/RPC 协商头落地为代码改造，可复用本文档的链路图作为改造点索引。
- 密钥管理（DEK/KEK 分层、KMS 托管）可作为独立跟进任务。
