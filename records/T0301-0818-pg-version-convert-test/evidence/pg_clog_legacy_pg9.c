/*
 * pg_clog_legacy_pg9.c — PostgreSQL 9.x 及更早 CLOG 读取（pg_clog 目录，版本特性文件）。
 *
 * 版本背景：PG10+ 将提交日志目录由 pg_clog/ 更名为 pg_xact/（pg_clog_reader_pg10.c
 * 按 PG10+ 布局实现，实测 PG18.4）。PG9.x 及更早目录为 pg_clog/。
 * 格式事实（T0301 实测 PG9.6）：SLRU 段 32 页/段、2-bit xid 状态编码与 pg_xact
 * 完全一致，仅目录名不同——故直接复用 pg_clog_xid_status（目录已参数化）。
 */
#include "pg_clog_legacy_pg9.h"
#include "pg_clog_reader_pg10.h"

int pg_clog_legacy_xid_status(const char *pgclog_dir, TransactionId xid)
{
  return pg_clog_xid_status(pgclog_dir, xid);
}