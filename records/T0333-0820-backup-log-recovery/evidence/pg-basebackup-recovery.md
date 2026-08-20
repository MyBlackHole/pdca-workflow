# PG 在线备份 → WAL 恢复一致性 → 物理直读转换 — 验证记录

- 场景: pg_basebackup 在线备份(活跃事务窗口内) + -X stream 齐全 WAL
- 表: poc_backup_orders (7 列, 与 poc_orders 同构), 50000 已提交 + 5000 活跃事务行
- 备份: START WAL LOCATION C/7F000028, CHECKPOINT C/7F79F280
- 恢复(借力 pg recovery): `starting backup recovery with redo LSN C/7F000028 → completed ... end LSN C/7F79F380 → consistent recovery state reached`
- 恢复后实例: 55000 行 (min=1 max=55000) 与主库一致
- pgbin 转换恢复后 heap: rows=55000 skipped_invisible=0 skipped_dead=0, 62.8 万 rows/s
- 全量逐字段对照 (parquet vs SQL TSV): rows=55000 diff=0 **PASS**

## 对照实验: 未恢复直接转换
- 同一备份产物**不应用 WAL 直接 pgbin**: SIGSEGV 段错误
- UBSAN: numeric 解码溢出 (pg_heap_reader.c:151), heap 页含未刷盘/不一致数据
- 结论: **备份产物必须经日志恢复到一致态才能物理直读转换**
