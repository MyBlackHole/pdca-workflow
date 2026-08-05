# cdm-data-cli 受控采集 CLI — 规格文档

## 问题陈述

`collection-service` 经既有 rpc 工具通道在 CDM 主机执行固定 `cdm-data-cli` 命令，输出 JSONL 供入库。当前无该 CLI：需实现受控 Topic 子命令、参数白名单、Keyset 扫描与字段归一化，复用 `aio-cdm` 既有 ORM（只读）。

## 解决方案

实现 `cdm-data-cli`：固定三个 Topic 子命令（`resource`/`task`/`capacity`）、`verify-credentials` 连通性校验、`--username/--password/--backup-domain-id/--cursor` 等白名单参数、稳定 Keyset 扫描、JSONL 逐行输出、结构化 stderr 错误行、字段归一化与 entity_key 组装。

## Seam 分析

- 测试接缝：CLI 子进程级测试（构造参数 → 断言 JSONL 行/退出码/stderr）；参数白名单拒绝用例；Keyset 排序稳定性。
- Mock/Stub：CDM 业务库数据以测试 fixture 构造；既有 ORM 模型复用读取。

## 用户故事

1. 作为采集链路上游，我想要固定 Topic 子命令输出稳定 JSONL，以便 collection-service 校验入库。
2. 作为安全边界，我想要参数白名单与固定命令，以便不被当作任意 shell/CLI 执行（§1、§3.4.1）。

## 实现决策

- 落地仓库：**aio-cdm 本仓**（新增 CLI 入口，复用既有 ORM 只读，不修改既有模型；§3.4.1）。
- 依赖契约：T0215（CLI 子方案）、主方案 §6.2（JSONL 契约）、§3.5.2（entity_key 组装）、§3.5.3（维度字段）。
- 关键规则：不用 offset（Keyset 稳定排序）；`task` Topic 仅接受 Worker 传入的 `source_update_time` 增量起点（§6.2）；关系两端 key 由 CLI 按 `backup_domain_id` 组装输出（§3.5.4）；容量只输出成功样本不输出失败 Worker（§3.5.5/§17.4）。

## 测试决策

- CLI 契约测试（三 Topic JSONL 快照）、参数白名单拒绝、Keyset 分页稳定、`verify-credentials`、CLI 版本与 ORM 模型版本匹配校验（§3.4.1）。

## 验收标准

- [ ] AC-1: `resource`/`task`/`capacity` 三个固定子命令可用，参数仅白名单（`--username`、`--password`、`--backup-domain-id`、`--cursor` 等），任意未知参数拒绝（CLI 子方案 §4、§6.2）。
- [ ] AC-2: 输出为逐行合法 JSON（JSONL），每行恰好一个业务记录，日志/诊断只进 stderr，失败前 stderr 输出结构化错误行 `{"error_code":..., "message":...}`（§6.2、§6.4）。
- [ ] AC-3: 全量扫描使用稳定 Keyset 排序，不使用 offset（§6.2）。
- [ ] AC-4: `task` Topic 接受 `source_update_time` 增量起点并按 `>=` 过滤；`task_run_key` 仅作并列排序不参与游标（§3.5.5、§6.2）。
- [ ] AC-5: entity_key 按 `{backup_domain_id}:{source_table}:{source_id}` 组装输出；关系 key 由 CLI 在同一一致性快照内解析（§3.5.2、§3.5.4）。
- [ ] AC-6: 复用既有 ORM 只读模型，不改既有字段/关系/语义；字段缺失或版本不匹配即失败不静默降级（§3.4.1）。
- [ ] AC-7: 容量 Topic 只输出成功 Worker 样本；`verify-credentials` 固定命令可用于连通性测试（§3.1.7、§3.5.5）。

## 范围外

- 不实现任意 shell/SQL/路径参数。
- 不修改 `aio-cdm` 既有 ORM 定义。

## 备注

- 依赖：T0215；下游：T0218（channel 调用）、T0222（CLI/JSONL 侧压测）。
- CLI 发布版本须与目标 CDM ORM/Schema 版本匹配（§3.4.1）。
