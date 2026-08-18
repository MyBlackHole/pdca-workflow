/*
 * pg_clog_legacy_pg9.c — PostgreSQL 9.x 及更早 CLOG 读取（pg_clog 目录，版本特性文件）。
 *
 * 版本背景：PG10+ 将提交日志目录由 pg_clog/ 更名为 pg_xact/（pg_clog_reader_pg10.c
 * 按 PG10+ 布局实现，实测 PG18.4）。PG9.x 及更早目录为 pg_clog/，格式
 * 推测与 PG10+ 一致（SLRU 32 页/段、2-bit xid 状态），仅目录名不同；
 * 本文件为占位：未实现，恒返回 -1。版本分派处当前仅调用 pg_clog_xid_status，
 * 若目标数据目录为 pg_clog 会显式返回失败，而非静默错读。
 */
#include "pg_clog_legacy_pg9.h"

int pg_clog_legacy_xid_status(const char *pgclog_dir, TransactionId xid) {
  (void)pgclog_dir; (void)xid;
  return -1; /* 旧 CLOG 目录格式未实现（见头文件说明） */
}