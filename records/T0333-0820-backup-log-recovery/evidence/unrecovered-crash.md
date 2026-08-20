# 未恢复备份产物直接转换 — 崩溃证据

- 场景: pg_basebackup 在线备份(含活跃事务)产物, **不应用 WAL 直接 pgbin 转换**
- 输入: poc_backup_test heap (368640B, 90页) + pg_xact
- 结果: **SIGSEGV 段错误** (pg_parse_heap_range)
- UBSAN (pgbin_dbg): `signed integer overflow: 0x166bf6cc1f8a166fa3aecd4968000000 * 10 cannot be represented in type '__int128'` at src/pg/pg_heap_reader.c:151
- 解读: 未恢复 heap 页含未刷盘/未初始化/不一致数据, 被当作 numeric 解码出天文数字 → 溢出崩溃
- 结论: **备份产物不恢复一致性无法直接转换** (AC 前提实证)
