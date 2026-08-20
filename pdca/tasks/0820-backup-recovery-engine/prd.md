# 跟进：双平台自研恢复引擎（PG优先）— 规格文档（PRD）

## 问题陈述

- **现状**: T0333 已实证——备份（非正常关闭）的 PG 数据文件不满足既有 pgbin 正常关闭快照前提，
  直接物理直读会得到错误/崩溃结果（SIGSEGV + UBSAN numeric 溢出）。恢复一致性目前依赖
  `pg_ctl` 启动重放（路径 A，借力工具）。
- **目标**: 自研离线 WAL 恢复引擎（路径 B），不启动数据库，纯离线把备份产物（heap + WAL +
  pg_control/backup_label）恢复到等价正常关闭快照，接既有 pgbin 转 Parquet。
- **差距**: 现有工具链无任何 WAL 解析/重放能力；PG 恢复机制已在 T0333 调研完整（起点定位 /
  XLogRecord 格式 / FPI 幂等 / clog 天然正确），缺的是实现。

## 解决方案

独立工具 `pgwrecover`（C，与 pgbin 同构建体系）：解析 pg_control/backup_label 定位恢复起点 →
遍历 WAL XLogRecord（CRC 校验 + FPI 识别）→ 对 heap/btree 页按页 LSN 幂等重放 → 输出一致
heap + clog 目录 → 调既有 pgbin 转换 Parquet。用户决策（T0333 修正）：MySQL 恢复亦为自研，
本任务 PG 优先实现（development），MySQL 引擎作为后续迭代。

## Seam 分析

### 声明的测试接缝
- seam: tests/pgwrecover/test_pgwrecover.py -> src/pg/pgwrecover.cpp
- seam: tests/pgwrecover/test_pg_control.py -> src/pg/pg_control_reader.c
- seam: tests/pgwrecover/test_wal_reader.py -> src/pg/wal_reader.c

### 验收可测性
- AC-3/4/5 为端到端容器验证（PG18 容器构造在线备份样本），全量逐字段对照 PASS/FAIL 明确。
- AC-1/2 为单元级解析验证（pg_control 字段、XLogRecord 头/CRC/FPI 识别），独立可构造。
- 异常路径：缺 WAL / CRC 损坏 / 无 backup_label 场景可独立构造。

## 用户故事

1. 作为数据迁移工程师，我想要对备份产物执行离线 WAL 恢复，以便不启动数据库就获得一致数据文件。
2. 作为工具链用户，我想要恢复引擎输出与 pgbin 兼容的一致 heap+clog，以便复用既有转换路径。
3. 作为运维，我想要明确的恢复失败诊断（CRC 校验、起点定位），以便定位备份数据问题。

## 实现决策

**不包含具体文件路径或代码片段**。新增模块：

- 入口 CLI：`pgwrecover <backup_dir> <out_heap> <out_clog> [--pg-version=N]`
- pg_control/backup_label 解析器：读 `ControlFileData`（checkPoint/checkPointCopy）、backup_label
  （START WAL LOCATION / CHECKPOINT LOCATION / BACKUP METHOD），输出恢复起点 LSN。
- WAL XLogRecord 读取器：XLogPageHeader + XLogRecordHeader 解析（xl_rmid/xl_info/xl_prev/
  xl_tot_len）、CRC32C 校验、FPI 判定（xl_info 的 XLR_BLOCK_ID_DATA_SHORT/LONG + block data 头）。
- heap/btree 重放器：按 rmgr id 分派（RM_HEAP_ID/RM_HEAP2_ID/RM_BTREE_ID），FPI 落页
  （RestoreBlockImage 语义），增量记录按页 LSN 幂等跳过。
- 输出：一致 heap 文件 + pg_xact 目录（clog 原样透传，重放后天然正确）。

架构决策：独立工具（不解耦进 pgbin）；首版 PG18，`--pg-version` 预留适配（参照 T0301 模式）；
仅覆盖 heap+btree 的 FPI/增量，其余 rmgr 记录跳过（不影响目标表数据页）。

**源码复用策略（用户指令）**：直接拷贝 PG 官方源码中可前端复用的文件，采用 pg_waldump 同款
"frontend 链接 xlogreader" 模式，而非自研解析器。已从容器 PG18.4 提取到
`third_party/pg184/src/`：
- `xlogreader.c`（WAL 读取器，官方 pg_waldump 即前端链接此文件）、`xlogstats.c`
- `src/common/fe_memutils.c`、`stringinfo.c`（前端内存/字符串设施）
- `heapam_xlog.c`、`nbtxlog.c`（重放算法参考，因强依赖后端设施不直接链接，仅对照实现）

前端化裁剪方式与 T0301 已有先例一致（heaptuple.c/mcxt.c/aset.c 等已前端化编译入 pgbin）。
缺失的 PG 头文件从容器源码补全到 `third_party/pg184/include/`；`postgres.h` 依赖的
pg_config 等以 port/ 适配层补全。

## 测试决策

- 单元测试：解析器（pg_control 字段值 / XLogRecord 头 / CRC / FPI 识别）——对容器样本可预期值断言。
- 集成测试：构造样本 → pgwrecover → pgbin → parquet vs SQL 全量逐字段对照（复用 T0333/T0301
  verify 脚本思路）。
- 端到端容器验证：PG18 容器构造在线备份样本（活跃事务 + pg_basebackup -X stream），
  验证恢复后一致性，对齐 T0333 实证基线（未恢复崩溃对照）。

## 验收标准

- [ ] AC-1: pg_control + backup_label 解析器：正确读出恢复起点 LSN（checkPoint.redo /
  START WAL LOCATION），字段级单元测试 PASS
- [ ] AC-2: WAL XLogRecord 读取器：正确解析记录头/CRC/FPI 标志，CRC 损坏记录可检测拒绝，单元测试 PASS
- [ ] AC-3: heap/btree 重放：FPI 落页 + 页 LSN 幂等跳过，单元测试构造 FPI 与增量记录验证 PASS
- [ ] AC-4: 端到端容器验证：PG18 在线备份样本 → pgwrecover → pgbin → parquet vs SQL 全量逐字段
  diff=0 PASS（对齐 T0333 实证基线）
- [ ] AC-5: 未恢复直接转换崩溃对照：同一备份样本不恢复直接 pgbin SIGSEGV，恢复后转换正常，
  差异实证记录（对齐 T0333 基线）
- [ ] AC-6: 知识沉淀（引擎实现要点）+ evidence 登记 + 结论（含 MySQL 引擎推进路径）

## 范围外

- MySQL 恢复引擎实现（后续迭代，本任务仅 PG；MySQL 机制知识已沉淀 T0333）
- 其余 rmgr（gin/gist/spgist/seq/logical）重放
- TDE 加密备份、压缩页、wal_level=minimal（无 FPI）、PITR 时间点恢复
- 真实生产备份产物（环境无样本，用容器构造）

## 备注

- 复用资产：T0333 知识沉淀 `knowledge/pg/backup-recovery-wal-replay.md`（机制）、
  `third_party/pg184`（WAL/clog 头文件）、容器 t0216-pg（PG18）、T0301 `--pg-version` 适配模式、
  T0333 实证基线（未恢复崩溃 / 恢复后 55000 行 diff=0）。
- 验证对比基线：T0333 pg_basebackup 实验（redo LSN C/7F000028 → end C/7F79F380，55000 行）。
- 依赖：T0333（父任务，已归档）。