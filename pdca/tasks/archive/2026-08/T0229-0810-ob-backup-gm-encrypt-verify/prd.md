# PRD：OceanBase 备份加密与国密 SM4 支持验证并沉淀报告

## 问题

用户需确认 OceanBase 4.2.1.1 备份链路是否支持国密（SM4）加密。国密在备份链路分两维度：**备份存储加密**（落盘文件密文算法）与**备份传输加密**（OB→备份介质通道）。调研已在本会话完成（多轮源码证据 + 官方文档校验），本任务将成果正式沉淀为 PDCA 记录。

## 目标

- 固化"备份存储 SM4 结论"：备份加密逻辑存在（PASSWORD/PASSWORD_ENCRYPTION/TRANSPARENT_ENCRYPTION/DUAL_MODE），但无"备份独立选 SM4"开关；SM4 仅能经源 SM4 TDE 透明加密沿袭。
- 固化"备份传输国密结论"：OB 自身不发起国密握手（S3/OSS 介质走标准 HTTPS/TLS）；内部 TLS 国密套件仅限 BabaSSL 商业构建。
- 固化 TDE 开启 SM4 完整步骤与备份启用加密官方命令（SET ENCRYPTION ON IDENTIFIED BY ... ONLY / SET DECRYPTION IDENTIFIED BY ...）。

## 范围

- 交付物：`OceanBase_备份加密与国密SM4_验证报告.md`（已生成，登记为本任务 evidence）。
- 真集群只读探测（不触碰原数据），本机 podman 实验受限记录入报告。

## 验收标准

- [ ] AC-1: 报告登记为 evidence，含 SHA-256 摘要，可在 `records/T0229-0810-ob-backup-gm-encrypt-verify/evidence/` 访问。
- [ ] AC-2: 报告结论覆盖"存储加密 / 传输加密"两维度，SM4 不可选项结论带源码证据（ob_config.cpp 占位表 / EVP 实现 / 宏块沿袭）。
- [ ] AC-3: 报告含 TDE 开启 SM4 实操步骤（Oracle 模式表空间 + 合并重写 + V$OB_ENCRYPTED_TABLES 验证）。
- [ ] AC-4: 报告备份加密命令以官方知识库为准（SET ENCRYPTION ON IDENTIFIED BY / SET DECRYPTION IDENTIFIED BY / ALTER SYSTEM BACKUP ...），无手写"SET ENCRYPTION PASSWORD"类错误语法。

## 备注

- 本任务为 research 场景，无测试产物，跳过测试接缝确认。
- 报告作者：本会话调查（源码行号引用 OceanBase 工作树 commit 3abcb163）。