---
schema: pdca.asset/v1
id: T0333-0820-backup-log-recovery
phase: check
source_ids:
  - backup-recovery-research-report
  - backup-recovery-pg-basebackup
  - backup-recovery-mysql-clean
  - backup-recovery-mysql-runtime-copy
  - backup-recovery-unrecovered-crash
---

## 上下文

任务目标：备份出来的 PostgreSQL / MySQL 数据文件，在**非正常关闭**（在线备份 / 运行中复制 / 异常退出）
场景下数据不一致。核心待答问题：**有齐全的日志文件（MySQL redo / PG WAL）时，如何把不一致的备份
数据恢复到一致状态**，从而复用既有 mysqlbin / pgbin 物理直读转 Parquet。

用户决策链（Q9/Q10/Q11）：核心价值 = 路径 B（自研离线重放）技术方案设计（research，不写实现代码）；
A（借力 xtrabackup --prepare / pg_ctl 恢复）作对照基线与衔接备选；双平台覆盖、PG 优先；
恢复目标态 = 等价正常关闭快照。

## 假设与结果

| AC | 假设 | 结果 | 证据 |
|---|---|---|---|
| AC-1 | 恢复方法论（起点定位 / redo·WAL 前滚 / undo 回滚·clog aborted / 一致性校验 + 适用版本）可写出 | **PASS**：方法论四环节 + 双库版本差异（redo 512B 块、pg_control/backup_label）完整 | research-report §2 |
| AC-2 | 路径 B 技术方案（架构 / 前滚·回滚算法 / pg_control 与 undo·trx_sys 依赖 / 风险 / 工程量 S/M/L）可设计 | **PASS**：架构图 + 模块算法 + 依赖表 + 5 项风险 + 工程量（PG S–M ~1 周 / MySQL L ~1 月） | research-report §3 |
| AC-3 | PG 容器验证：非正常关闭样本 + 齐全 WAL → 恢复 → pgbin → SQL 对照一致 | **PASS**：pg_basebackup 在线备份 → WAL 恢复（redo LSN C/7F000028→C/7F79F380）→ pgbin 55000 行 diff=0；未恢复直接转换 SIGSEGV 崩溃为对照 | pg-basebackup-recovery.md、unrecovered-crash.md |
| AC-4 | MySQL 容器验证：在线备份产物 → 恢复 → mysqlbin → SQL 对照一致；undo/trx_sys 缺口记录边界 | **PASS**：运行中复制混入未提交行实证（+500）；干净关闭恢复后 10500 行 diff=0；purge 缺口（30 行回滚残留）记录为边界 | mysql-runtime-copy.md、mysql-recovery.md |
| AC-5 | 衔接说明：恢复产物输入 mysqlbin/pgbin 的调用方式、可见性契约、已知限制 | **PASS**：调用命令 + 可见性契约 + 已知限制（clog 同快照、purge 校验、未覆盖 TDE/压缩页/minimal） | research-report §5 |
| AC-6 | research-report + evidence 登记 + 结论（B 是否值得立项） | **PASS**：报告 + manifest/record 登记 + 结论（PG 立项 / MySQL 借力 A 过渡） | research-report §6、manifest.jsonl |

## 分析

1. **PG 恢复可行性高且验证闭环**：无独立 undo，WAL 重放后 clog 天然标记 aborted，恢复 = 仅前滚。
   容器实证完整走通"在线备份 → WAL 恢复 → pgbin → SQL 全量逐字段对照"，55000 行 diff=0，
   吞吐 62.8 万 rows/s。未恢复直接转换 SIGSEGV 崩溃（UBSAN numeric 溢出）反向证明"备份产物必须
   经日志恢复"——这是任务核心价值的最直接实证。
2. **MySQL 恢复复杂度高一个量级**：需 redo 前滚 + undo 回滚 + trx_sys 活跃事务判定三件套，
   undo/trx_sys 页本身需先被 redo 前滚到一致版本才能回滚（两阶段次序），工程量为 L。
   purge 缺口（干净关闭态仍有 30 行回滚残留）进一步说明自研回滚还需覆盖物理清理，边界已记录。
3. **路径 A 作为衔接备选成立**：xtrabackup --prepare / pg_ctl 启动恢复均已实证可用，可作为
   MySQL 侧过渡方案与 PG 侧对照基线。
4. **无失败 AC**，全部 6 条 PASS。Ch2 Grill 四项可靠性追问（源码依据 / 替代解释排除 / 关键信息
   覆盖 / 工程量依据）均通过。

## 适用边界

- 验证样本为容器构造（PG18 / MySQL8.0），真实生产备份产物未覆盖；PG9.6/11 与 MySQL5.6/5.7 的
  恢复机制基于源码推断，未逐一容器验证（redo/WAL 格式版本差异已在方法论标注）。
- 未覆盖：TDE 加密备份、压缩页恢复、wal_level=minimal（无 FPI）、PITR 时间点恢复、增量/CDC。
- MySQL purge 缺口（回滚残留 30 行）为自研实现前必须解决的前置问题。
- 工程量评估基于参考实现源码规模与既有 T0300/T0301 实现经验，非实测工时。

## 下一轮建议（用户修正：双平台均自研）

**用户明确：MySQL/PG 恢复均定位为自研**（AC-6 原"MySQL 借力 xtrabackup 过渡"建议不采纳）。

- **跟进任务（双平台自研恢复引擎）**：PG 优先实现（S–M，~1 周原型），MySQL 随后实现（L，
  需先解决 undo/trx_sys 两阶段前滚-回滚次序与 purge 缺口）。
  - PG 原型范围 = pg_control/backup_label 解析 + WAL XLogRecord 读取器 + heap/btree
    FPI/增量重放 + 输出一致 heap+clog → 接 pgbin；验收沿用本任务 AC-3 的 SQL 全量逐字段对照口径。
  - MySQL 原型范围 = checkpoint/redo 读取器 + MLOG 前滚 + undo 回滚 + trx_sys 判定 → 输出一致
    ibd → 接 mysqlbin；验收沿用 AC-4 对照口径，并新增 purge 残留校验。
- 建议将"在线备份恢复点语义"与"MySQL purge 缺口"沉淀为知识条目（Act 阶段执行）。
