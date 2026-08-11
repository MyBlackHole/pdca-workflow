---
schema: pdca.asset/v1
id: T0229-0810-ob-backup-gm-encrypt-verify
phase: check
source_ids: [verify-report]
---

## 上下文

用户需确认 OceanBase 4.2.1.1 备份链路是否支持国密（SM4）。国密在备份链路分两维度：备份存储加密（落盘文件密文算法）与备份传输加密（OB→备份介质通道）。验证经多轮源码取证（OceanBase 工作树 commit `3abcb163`）+ 真集群只读探测 + 官方知识库校验完成，成果已沉淀为报告并登记 evidence。

## 假设与结果

| 假设 | 验证结果 | 证据 |
|------|---------|------|
| 备份数据加密逻辑存在 | ✅ PASSWORD/PASSWORD_ENCRYPTION/TRANSPARENT_ENCRYPTION/DUAL_MODE 四模式枚举 | `ob_encryption_util.h:224-234` |
| 备份可独立配置国密 SM4 | ❌ 无 SM4 可选值（算法取值表空占位 `{"None",""}`） | `ob_config.cpp:40-41` |
| SM4 备份密文来源 | ✅ 仅源 SM4 TDE 透明沿袭（宏块 encrypt_id 原样拷贝） | `ob_macro_block.cpp` |
| 底层引擎支持 SM4 | ✅ EVP_sm4_* 全模式实现；`is_sm_algorithm` 声明无实现 → 启用路径留给安全/企业版 | `ob_encryption_util_os.cpp:85-92`、`ob_encryption_util.h:249-250` |
| 备份传输链路启用国密 | ❌ S3/OSS 介质走标准 HTTP(S)/TLS 无 SM2/SM3/SM4；内部 TLS 国密套件仅 BabaSSL 构建 | `ob_storage_s3_base.cpp:195`、`easy_ssl.c:83-87,1014` |
| 备份加密命令语法 | ✅ 以官方知识库为准（SET ENCRYPTION ON IDENTIFIED BY ... ONLY / SET DECRYPTION IDENTIFIED BY ...） | 官方知识库链接（报告中 §八） |

## 关键发现

1. **存储维度**：口令加密（PASSWORD_ENCRYPTION）实际落地为 AES 族；SM4 只能在源表 SM4 TDE 时随透明加密进备份文件。真集群 `tde_method=none`，本地 podman 社区镜像不支持 Oracle 租户模式，无法原样线上复现 SM4 备份密文。
2. **传输维度**：OB 自身不发起国密握手；国密 TLS（ECC-SM2-WITH-SM4-SM3）属 BabaSSL 商业构建的内部通信能力，不覆盖备份介质。要传输国密需介质侧国密网关做 SM2/SM3/SM4 TLS 终止。
3. 报告含 TDE 开启 SM4 完整实操步骤（Oracle 模式表空间 + progressive_merge + MAJOR FREEZE + V$OB_ENCRYPTED_TABLES 验证）与备份启用加密官方命令全链路（配置路径/归档/全量/增量/恢复/视图校验）。

## 验收标准达成

- AC-1 ✅：报告已登记 evidence（verify-report，SHA-256 `b7496b...`，`records/T0229-*/evidence/`）。
- AC-2 ✅：报告 §二/§三 证据一~三覆盖存储/传输两维度 + 源码行号证据。
- AC-3 ✅：报告 §七 TDE 开启 SM4 步骤完整（Oracle 表空间 SM4-CBC/GCM）。
- AC-4 ✅：报告 §八 命令全部以官方知识库语法为准，无 "SET ENCRYPTION PASSWORD" 类错误语法。

## 适用边界

- 结论基于开源 4.2.x 代码库（commit `3abcb163`）与真集群 4.2.1.1 只读探测；**企业版**备份口令加密能否直选 SM4 无法从开源证明，需企业版文档或实测终判。
- 未在真集群执行任何写操作（TDE 未开、未建表、未触发冻结、无备份产物），符合"绝不影响原数据"约束。

## Conclusion

verdict=confirmed，disposition=projected。用户实际需求（备份链路国密）结论已闭环：备份加密逻辑存在，但 4.2.1.1 无"备份独立选 SM4"开关；SM4 仅经源 SM4 TDE 透明沿袭（存储维度），传输维度需介质侧国密网关。