/*
 * pg_clog_legacy.h — PostgreSQL 9.x 及更早 CLOG 读取（pg_clog 目录，版本特性）。
 *
 * 版本背景：PG10+ 将提交日志目录由 pg_clog/ 更名为 pg_xact/（见
 * pg_clog_reader.c，已实现）。PG9.x 及更早的 pg_clog/ 目录格式与 pg_xact
 * 一致（T0301 实测 PG9.6），实现见 pg_clog_legacy_pg9.c，复用目录参数化的
 * pg_clog_xid_status。文件即“旧 CLOG 目录版本特性”的承载点。
 */
#ifndef PG_CLOG_LEGACY_H
#define PG_CLOG_LEGACY_H

#include "pg_clog_reader_pg10.h"

/* 旧 CLOG（PG9.x 及更早，pg_clog 目录）读取：复用 pg_clog_xid_status（同格式）。
 * 签名与 pg_clog_xid_status 一致，便于版本分派处无缝切换。 */
int pg_clog_legacy_xid_status(const char *pgclog_dir, TransactionId xid);

#endif /* PG_CLOG_LEGACY_H */