# MySQL 备份恢复一致性 — 机制与边界

> 来源：T0333-0820-backup-log-recovery（容器实证 MySQL 8.0）
> 关系：T0325 `mysql/normal-shutdown-visibility-scope.md` 的上游——该篇解决"正常关闭快照
> 可见性只需 delete-mark 过滤"，本篇解决"在线备份产物如何恢复到一致态 + 自研边界"。

## 核心结论

**MySQL 恢复一致性 = redo 前滚 + undo 回滚 + trx_sys 判定 + purge，四要素缺一不可**。
复杂度比 PG（仅 WAL 重放）高一个量级。

## 恢复流程（在线备份场景）

1. **起点定位**：checkpoint LSN（≤8.0.29 在 `ib_logfile0` checkpoint 头 / 8.0.30+ 在
   `#innodb_redo` 的 `#ib_redo*`）。在线备份（xtrabackup）依赖 `xtrabackup_checkpoints` 的
   `to_lsn` 作为重放终点。8.0.30+ redo 为 512B 块环形文件。
2. **前滚**：redo 记录物理字节级（`MLOG_1/2/4/8BYTE`、`MLOG_WRITE_STRING`、`MLOG_REC_INSERT/
   DELETE` 等），应用前按页 LSN（`FIL_PAGE_LSN`）与记录 LSN 对比幂等跳过。
   参考源码：`log0recv.cc`（log_recv_parse / recv_apply_log_rec）、`srv0start.cc`。
3. **回滚**：从 trx_sys（8.0 前 `ibdata1` / 8.0 后 `mysql.ibd`）取活跃事务，沿 undo log
   （`TRX_UNDO_INSERT` / `TRX_UNDO_UPDATE` 链）回滚：INSERT 回滚=移除/delete-mark；UPDATE/DELETE
   回滚=恢复旧版本。参考：`trx0roll.cc`、`trx0undo.cc`。
4. **trx_sys/undo 页需先被前滚**：trx_sys 与 undo 页本身可能未刷盘 → 必须先经 redo 前滚出
   一致版本才能回滚。**两阶段次序（全部前滚 → 再回滚）是自研实现最大工程点。**

## 在线备份不一致实证

- 运行中复制 .ibd（含活跃事务 500 行未提交）→ mysqlbin 直接转换：**rows=10500**（混入未提交
  500 行，活跃事务行无 delete-mark 被读出）；基线 10000。
- 干净关闭（shutdown）后复制 → mysqlbin 转换：10500 行（500 行已提交），与 SQL 全量逐字段
  diff=0 PASS。
- 补充：poc_orders 表运行中复制读出 1000530 vs 基线 1000000（+530 未提交）。

## purge 缺口（关键边界）

- 干净关闭态（shutdown）仍可能残留**已回滚事务的行**：实证 30 行（id 1000617–1000920）在
  SQL 中不存在但 mysqlbin 读出。原因：shutdown 不保证 purge（物理清理已回滚行）完成。
- 结论：**自研恢复引擎必须把 purge 纳入一致性校验**（恢复完成标志 / 与 SQL 对照）；
  仅 redo+undo+trx_sys 不够。

## 边界与风险

- MLOG 类型数十种（含压缩页 `MLOG_ZIP_*`、加密页）；首版自研建议仅覆盖未压缩/未加密常规表。
- 8.0 元数据在 SDI 页（ibd 内嵌），5.6/5.7 在 .frm 需 `--schema=` 参数化（T0325 已知）。
- TDE 加密备份产物恢复、`wal_level` 等价场景、PITR 时间点恢复均未覆盖。