# aio-tools 各类数据库备份传输加密支持国密的实现梳理 — 规格文档

## 问题陈述

- **现状**: aio-tools 6200 release 中，各数据库/数据源备份的传输链路加密能力不同——RPC 层（aio-speed ⇄ aio-speedd）已有 TLS（OpenSSL 国际算法），SBT 层（Oracle libobk / DM dmsbtex）裸 TCP 明文，S3 落盘侧（s3file / my-fuse）已用 GMSSL SM4-CBC，国密支持分散、缺失系统性实现梳理。
- **目标**: 在 `/home/black/Documents/备份传输存储加密/` 产出单份总文档，分节讲清 **PG系列、MySQL系列、文件系统、Oracle、DM、OB、gaussDB** 七类对象"如何实现备份传输加密支持国密"，每类对象配实现国密加密的**架构图**与**数据流图**（Mermaid）。
- **差距**: 现状无覆盖全链路的结构性实现文档；实现细节散落于 6200 release 源码与 `/home/black/Documents/database_国密/` 的 8 份调研文档。

## 解决方案

单份总览文档，每类对象按"现状 → 国密落地方案 → 目标态"三段式组织，统一以 Mermaid 表达架构图与数据流图，并将介质/存储侧（S3 落盘、NFS、存储网关）与统一国密落地手段（GMSSL 双后端、SBT 协商头、IPSec/网关叠加）并入总结章节。

## Seam 分析

documentation 场景，无测试产物，跳过测试接缝确认（对齐 flow-plan P3.5 条款）。

### 验收可测性

- 每类对象小节 PASS 判定：存在"现状/落地方案/目标态"三段 + 至少 1 张 Mermaid 架构图
- Mermaid 语法可渲染（可用 mmdc/git 渲染或人工校验语法闭合）
- 内容一致性：与 database_国密 调研结论无矛盾表述

## 用户故事

1. 作为备份产品架构师，我想要一份覆盖 PG/MySQL/文件系统/Oracle/DM/OB/gaussDB 的备份传输加密国密实现总览，以便向客户与密评解释各数据源"传输层国密如何落地、现状缺口在哪"。
2. 作为研发工程师，我想要每类对象的现状链路与目标态图，以便定位改造点（协商头/双后端/网关叠加）。
3. 作为方案售前，我想要统一落地手段与介质侧安全说明，以便给出跨数据源一致的国密合规方案。

## 实现决策

**文档结构**（单份总文档，路径 `/home/black/Documents/备份传输存储加密/`，文件名待用户确认）：

1. 开篇：总体备份架构总览图（Worker→数据源 双平面：RPC 数据面 + SBT/XBSA 面 + 存储/卷复制面）+ 对象链路对比表（客户端组件/服务端组件/协议/端口/现状加密/国密缺口）
2. 分节（现状 → 国密落地方案 → 目标态架构图）。关键：**存储资源分两类——ZFS（Worker 本地备份存储，ZFS 自身存储加密）与 S3/OBS（远端对象存储，独立表达）**；**备份由 Worker 侧客户端主动连接数据源侧服务端发起**：
   - **PG 系列**：Worker 侧 fsdeamon（仅 PG 备份服务）+ fs-cli（aio-speedd 的客户端，PG 不用 aio-speed）⇄ 数据源侧 aio-speedd（:6611）+ fsbackup.ko → 落 Worker 侧 ZFS；现状传输 TLS(OpenSSL)/`--encrypt` XOR、ZFS 加密可选题；国密方案=传输层国密 TLS（SM2 证书链 + RFC 8998）
   - **MySQL 系列**：xtrabackup→xbstream 流，Worker 侧 aio-speed `--nc` 主动 tcp 连接数据源侧 aio-speedd 实现「远程流→本地流」（传输）→ 落 ZFS（ZFS 自身加密）；国产化 MySQL 系（goldendb 等）同路径
   - **文件系统**：Worker 侧 aio-speed 主动 tcp 连接数据源侧 aio-speedd，目录文件/文件块级拉取（不使用 fsbackup / fs-backup）→ 落 Worker 侧 ZFS
   - **独立场景：备份卷 ZFS→S3 复制**（与数据库备份无关）：备份完成后 s3file 读 ZFS 卷快照（zfs send）→ S3（`--gmssl` SM4-CBC 密文）；挂载资源端 s3mount 挂载还原
   - **Oracle（SBT）**：RMAN SBT（libobk.so ⇄ FileTransferAgent）；裸 TCP 明文；国密方案=SBT 层新增协商头 + 同连接升级国密 TLS + SM2 证书
   - **DM（SBT）**：DM SBT/DMS API（dmsbtex ⇄ dm-ftp）；裸 TCP 明文；国密方案=同上 SBT 协商头路径
   - **OB OceanBase**：OB 原生备份到 S3/OSS（标准 HTTPS/TLS，不发起国密，与 s3file 无关）；源 TDE SM4 透明沿袭；介质侧前置国密网关
   - **gaussDB**：gs_roach 物理备份，源端 roach agent ⇄ Worker 上 backUpAgent（加载 xbsa 库 API）直写 ZFS；gs_roach 工具不支持国密；引擎 TDE SM4；gsql/JDBC TLCP；备份链路靠网关/沿袭
3. 统一国密落地手段章（借鉴国密网关调研）：① RPC/SBT 协商头 + 同连接升级国密 TLS（SM2 证书链 + RFC 8998 TLS_SM4_GCM_SM3）② 链路叠加国密网关（国密 TLS 隧道 / IPSec-SM / 安全网关）③ 存储加密双路径：ZFS 自身加密 / s3file SM4 密文（独立场景）
4. 介质/存储侧安全总结附节：备份卷 ZFS→S3（SM4 s3file、s3mount 挂载资源端）、NFS 介质（标准机制不支持国密，需网关）、存储静态加密（ZFS 加密数据集、华为 SM4、S3 介质静态加密可配等）

**内容边界**：架构+链路级，覆盖组件/协议/端口/配置开关，不引用源码 file:line、不贴大段代码（用户已确认，覆盖 triager-brief 中"附源码引用"的推荐项）。

**图规范**：仅 Mermaid。每类对象至少 1 张架构图（flowchart）；链路对比用表格；总体架构一张全景 flowchart。

## 测试决策

无测试产物（documentation 场景）。校验手段：Mermaid 语法闭合检查；与 database_国密 调研结论一致性比对。

## 验收标准

- [ ] AC-1: 文档建成于 `/home/black/Documents/备份传输存储加密/`，为单份总文档，文件名反映其内容主旨
- [ ] AC-2: 开篇包含整体备份架构总览图（Mermaid flowchart）与对象链路对比表（覆盖六类对象 + 独立场景备份卷 ZFS→S3）
- [ ] AC-3: 六类对象（PG系列/MySQL系列/文件系统/SBT系列(Oracle+DM)/OB/gaussDB）每节均按"现状 → 国密落地方案 → 目标态"三段编写；独立场景（备份卷 ZFS→S3 复制）单独叙述并与数据库备份区分
- [ ] AC-4: 每类对象与独立场景每节至少含 1 张 Mermaid 架构图（flowchart）
- [ ] AC-5: 文件系统类别覆盖 ZFS 资源路径（ZFS 自身存储加密）；独立章节"备份卷 ZFS→S3"覆盖 S3 资源路径（s3file `--gmssl` 上传 SM4 密文，s3mount 在挂载资源端还原）
- [ ] AC-6: PG 备份由 fs-cli（aio-speedd 的客户端）主动连接数据源侧 aio-speedd，不使用 aio-speed，调度归属 fsdeamon（仅 PG）；MySQL 备份为 xtrabackup → aio-speed（tcp）⇄ aio-speedd（`--nc` 远程流→本地流）；文件系统备份不使用 fsbackup，由 aio-speed（tcp）⇄ aio-speedd 文件级拉取；存储加密归属 ZFS 自身加密，分别在对应小节体现
- [ ] AC-7: 含统一国密落地手段章节（GMSSL 双后端 / RPC/SBT 协商头同连接升级 / 国密网关与 IPSec 叠加）
- [ ] AC-8: 含介质/存储侧安全总结附节（独立场景 ZFS→S3 落盘 SM4、NFS 需网关、存储静态加密）
- [ ] AC-9: 内容为架构+链路级（组件/协议/端口/配置开关），不出现源码 file:line 引用
- [ ] AC-10: 与 database_国密 调研结论一致（gs_roach 工具不支持国密、OB 无独立 SM4 备份开关、NFS 原生不支持国密等），无矛盾表述
- [ ] AC-11: 全部 Mermaid 代码块语法正确（flowchart 结构闭合）

## 范围外

- 不深入单函数级实现细节
- 不贴大段源码
- 不做代码改造（纯文档任务）
- 不覆盖 SQLServer 等其他未列数据源

## 备注

- 输入：6200 release 源码组件梳理 + database_国密 8 份调研（备份复制传输加密.md、国密SM4全流程.md、gs_roach报告.md、OB验证报告.md、备份链路PDCA总结.md、国密网关调研.md、NFS国密源码分析.md、openEuler_NFS报告.md）
- 已确认决策记录于 `clarifications.jsonl`（round 1, 8 题）