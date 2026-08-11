---
schema: pdca.asset/v1
id: T0247-0811-backup-doc-optimize
phase: check
source_ids: [doc-v24, convergence-map-v2]
---

## 上下文
T0246 归档的《数据库备份传输加密_国密实现.md》（679 行、13 块 Mermaid）经用户复核发现存在多余/重复文字：独立场景引导反复出现、与 s3file 无关语义多处重述、高频短语过度展开、头部信息块相互重叠。用户确认精简目标是**文字层**，非组件（s3file/s3mount/filemount/mc 均为 6200 release 真实组件，保留）。

Do 阶段追加用户指令，一并纳入本任务收敛链：
1. **删除"源 TDE SM4 透明沿袭"相关内容**（OB/gaussDB 对比表、现状段、架构图、术语表 TDE 条目）——该语义为数据库引擎自带 TDE 密文被备份拷贝，属自有内容，予以移除；
2. **新增 10.4 国密硬件加速支持**——经用户再确认，仅保留 **CPU 指令集加速**（信创 CPU SM4/SM3 指令），删除密码卡/PKCS#11/软件引擎等展开，并入十章；后按用户质疑补充 **SM2 无原生指令**（鲲鹏 920 无 SM2 指令/引擎、兆芯 GMI 待下一代，经 websearch 核实）；
3. **补充自身国密支持调研**（来源 `database_国密/备份链路国密支持_PDCA总结与NFS传输调研.md`）：
   - OB 现状：补"备份加密算法取值表空占位、SM4 仅白名单"源码依据（`ob_config.cpp`）；
   - gaussDB：补工具层 `nm -D` 无 `EVP_sm*` 符号、cipher 编译期宏、AK/SK AES-128-CBC 证据，及客户端层国密明确"不作用于备份链路"；
   - 10.2 NFS：补 Linux 定制版内核证据（`crypto/sm4.c` 已注册、`gss_krb5` enctype 白名单仅国际算法从不请求 SM）、华为 OceanStor 国密边界（管理面/块复制/静态加密，NFS 数据面无国密开关）、NFS 国密落地三路径。

## 假设与结果
| AC | 验收标准 | 结果 |
|----|---------|------|
| AC-1 | 总览独立场景引导去重（一句话提点 + 指向五/六章） | ✅ L20 改"独立场景见第五/六章"，L30 改"见第五/六章" |
| AC-2 | 与 s3file 无关语义去重 | ✅ 删总览主线2末句与 9.3 重复句，保留 OB 现状段与对比表 OB 行 |
| AC-3 | 高频短语短引用，术语表承担定义 | ✅ 图节点/对比表已是短词，术语表未动无漂移 |
| AC-4 | 头部信息块合并精简 | ✅ L16 角色约定精简，备份方向解释移至一章 |
| AC-5 | 结构不变 | ✅ 文字层精简 + 删除 TDE 内容 + 新增 10.4 小节（均为用户指令范围内变更） |
| AC-6 | 13 块 Mermaid 语法自检 PASS | ✅ 括号/引号配平全部通过（含删 TDE 节点后） |
| AC-7 | 事实与拓扑结论一致 | ✅ 精简不引入新事实；TDE 沿袭结论按指令移除，10.4 仅 CPU 指令加速途径 |

## 分析
- 收敛链：convergence.json 2 条声明全覆盖 7 项 AC；evidence doc-v24（supersede v23，digest sha256:a1ccd5fb…）+ convergence-map-v2（supersede v1）均登记且 digest 匹配；validate-convergence `valid: true`。
- 文字精简 6 处：主线2 末句、角色约定括号、独立场景（L20）、存储数据面（L30）、9.3 介质总结重复句；皆为删除/合并重复表述。
- TDE 沿袭删除：OB 对比表 3 行存储列、L494 现状段（去"SM4 只能经源表 TDE 透明沿袭"）、国密现状第 1 条、8.1 图 S3 桶节点；gaussDB 对比表、现状引擎层（三层改两层）、国密现状第 1 条、架构图 TDE 节点与连线；术语表 TDE 条目。受影响结论改为"无独立 SM4 备份开关 / 存储靠 ZFS 自身加密"。
- 10.4 国密硬件加速支持：仅 CPU 指令集（信创 CPU SM4/SM3 指令 → GMSSL 系自动启用；x86 无 SM4 指令回退软件实现，损耗 ~90% 见 10.3）。

## 失败原因（仅 rejected/partial）
无。

## 适用边界
本结论仅针对《数据库备份传输加密_国密实现.md》文字精简 + TDE 沿袭移除 + 10.4 硬件加速小节。不涉及：
- 组件、协议、端口、配置开关等事实变更；
- 章节结构增删（10.4 为并入十章的小节）；
- 其他文档（调研报告、knowledge）的同步（OB/gaussDB 知识资产中含 TDE 沿袭结论，需在 Act 阶段核对）。

## 下一轮建议
- Act 阶段核对 `knowledge/backup/ob-backup-gm-encrypt-support.md`、`gs-roach-gm-encrypt-support.md` 是否含"源 TDE 沿袭"旧结论，若有需同步修正，避免知识库与文档结论冲突。
- 本轮补充调研（OB 无 SM4 开关源码、gaussDB `nm -D` 无 SM、Linux 内核 crypto 国密注册但 NFS gss_krb5 不调用、华为 OceanStor 国密边界）可在 Act 阶段沉淀为 knowledge 资产。