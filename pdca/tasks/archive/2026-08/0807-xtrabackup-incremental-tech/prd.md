# GoldendB-XtraBackup 8.0 增量实现方案调研 — 规格文档 (PRD)

## 问题陈述

需要明确本项目（percona-xtrabackup-8.0.25-17）**支持哪些 MySQL 增量备份实现方案**，产出清晰的支持矩阵与各方案技术要点，以供基于本工具做增量备份能力评估与后续调用决策。除项目自身实现外，还需通过联网调查业界**第三方/其它增量技术**以及本项目**缺失（未实现）**的方案，形成对照。

## 调研对象

`/home/black/Downloads/goldendb-xtrabackup/percona-xtrabackup-percona-xtrabackup-8.0.25-17`
（已核实为标准 Percona XtraBackup 8.0.25-17 源码快照，非定制版本、非 git 仓库）

## 背景顺序

1. 已静态核实项目内含多条增量实现路径（LSN 页级对比、changed-page bitmap、redo archiving），claim 成立。
2. P1/P2 澄清确认：产出物为任务目录 `research-report.md` + 沉淀 `knowledge/`；范围=全链路（捕获+准备+恢复）。
3. 研究方向确认：确立「支持哪些增量方案」清单，并延展调查第三方/缺失方案。

## 调研内容（Do 阶段执行）

### A. 本项目已实现的增量方案（支持矩阵，结论前置）
对每条方案给出：名称 / 实现技术原理 / 触发参数与调用 / delta 落盘格式 / 版本与 Server 依赖 / 适用场景 / 局限。

- A1 **LSN 页级对比增量**（主路径）
  - 触发：`--incremental`/`--incremental-basedir`/`--incremental-lsn`
  - 原理：`wf_incremental_process` 逐页读 `FIL_PAGE_LSN`，仅拷贝 `incremental_lsn` 之后改动的页
  - delta 格式：`.delta` 文件，`XTRA` 魔数 + 页号表 + delta 页（write_filt.cc:104-174）
  - 相关开关：`--incremental-force-scan`（force 全扫描）
- A2. **Changed Page Bitmap / page tracking 加速**（Percona Server 专属）
  - 触发：`FLUSH CHANGED_PAGE_BITMAPS`；Server 侧 `ib_modified_log_*.xbm` 位图文件（4096B/块 + 校验和 + RB-tree 合并）
  - 作用：用位图直接定位修改页，避免整表 LSN 全扫描
  - 版本/Server 依赖：需 Percona Server 8.0 / XtraDB 在线位图
- A3. **Redo Log Archiving（redo 归档支撑）**
  - 触发：`innodb_redo_log_archive_dirs`；`Archived_Redo_Log_Monitor`
  - 作用：备份期间归档 redo，避免长时备份 redo 被覆盖，保证一致点
- **A4. 增量 prepare 还原技术**
  - `--apply-log-only`（仅合并 redo，不恢复数据页，供后续叠加增量）
  - delta 应用（delta 页写回基线）
  - `--redo-lag`、`--rollback-only`
  - prepare 时 LSN 重定向（`incremental_to_lsn`/`incremental_last_lsn`）
- **A5. 基于历史备份元数据的增量**：`--incremental-history-name` / `--incremental-history-uuid`

### B. 第三方 / 业界其它增量方案（联网调查）
- B1. MySQL Enterprise Backup (MEB) 的增量支持方式与差异
- B2. MySQL 8.0.17+ 原生 page tracking（`INFORMATION_SCHEMA.INNODB_PAGE_TRACKING` / `ALTER INSTANCE ... SET INNODB_PAGE_TRACKING`），MEB 用，Percona 为对应实现
- B3. 逻辑级增量方案对比：binlog 增量回溯（mysqldump/`mysqlbinlog` + Flashback）、Canal/Debezium/Binlog real-time、第三方 `pt` 、`gh-ost` 等
- B4. 物理增量其它技术：binlog-based replica、块级别（dm/块复制）、ZFS/Ceph snapshot 增量等（概述）

### C. 本项目缺失（未实现）的增量方案（差距分析）
- C1. 原生应用 MySQL 8.0 官方 page tracking 到全 MySQL 版本（当前需 Percona Server）
- C2. binlog 级增量导出（PXB 不提供 binlog 应用/订阅）
- C3. 加密表空间 / 个别页压缩场景的增量限制
- 输出为「支持矩阵：方案 × 是否支持 × 依赖 × 说明」

### D. 交付
- 任务目录 `research-report.md`
- 通用结论沉淀 `$PDCA_HOME/knowledge/`

## 用户故事

- 作为备份工具选型者，我想知道本 XBack 支持哪些增量方案，以便选择合适的增量备份策略。
- 作为开发者，我想知道每条增量方案的技术原理与关联代码/参数，以便调用或扩展。
- 作为决策者，我想对照第三方/缺失方案，判断本工具的增量能力边界。

## 实现/测试决策

- 证据来源：项目源码静态分析（在证据目录登记 code anchors）+ man/文档 + 联网官方资料（websearch/webfetch）。
- 关键代码锚点列入 `evidence/ac-source-anchors.md`，供 Check 阶段核验。
- 不实际编译/运行（无构建；源码为只读快照）。

## 范围外

- 不涉及 PXB 全量/压缩/加密备份原理（仅其与增量相交部分）。
- 不做增量备份的试用运行与性能基准。
- 不作为项目代码改进入手。

## 验收标准

- [ ] AC-1: 给出「本项目支持增量方案」清单一览表（方案/原理/触发参数/依赖/适用场景）
- [ ] AC-2: A1 的 LSN 增量对比原理用代码锚点佐证（write_filt.cc 及调用链）
- [ ] AC-3: A2 changed page bitmap 技术与 Server 版本依赖给出代码与官方佐证
- [ ] AC-4: A3 redo log archiving 机制给出代码与官方佐证
- [ ] AC-5: A4 增量 prepare 技术（apply-log-only/delta 应用/redo-lag/rollback-only）说明完整
- [ ] AC-6: 附「方案 × 是否支持 × 依赖 × 说明」支持矩阵表
- [ ] AC-7: 联网调查列出≥3 种第三方/业界增量方案并标注本项目缺失项
- [ ] AC-8: research-report.md 完成，并沉淀 knowledge/
- [ ] AC-9: 每章至少一处源码/官方引用；报告含至少一个 ASCII/图表结构示意

## 备注

- 本任务为 research 类型，产出物为文档；PDCP 门禁在 P6 终审后进入 Do。