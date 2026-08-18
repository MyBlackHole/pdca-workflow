/*
 * pg_versions.h — PostgreSQL 版本特性矩阵（文件即版本差异清单）。
 *
 * 拆分原则：凡随 PG 版本变化的物理解析事实集中在此，并在文件名/文件头
 * 标注对应版本；解析实现按版本特性拆分为独立文件：
 *   heap 头/可见性（t_infomask 偏移）   → pg_heap_reader.c（PG12+ 实测）
 *   CLOG 提交日志：PG10+ pg_xact        → pg_clog_reader.c（已实现）
 *   CLOG 提交日志：PG9.x 及更早 pg_clog  → pg_clog_legacy.c（未实现）
 *
 * 版本事实（T0250 实测/逆向）：
 *   - t_infomask 偏移随 PG 版本变化：PG12+ 为 20，PG11 及更早为 24。
 *     本工程通过编译期 PG 官方头（HeapTupleHeaderData）访问，偏移由目标
 *     版本头决定；以下宏仅作阅读索引，禁止硬编码旧偏移（AC-10 根因之一）。
 *   - CLOG 目录名：PG10+ 为 pg_xact/，PG9.x 及更早为 pg_clog/。
 *     SLRU 段文件（32 页/段）与 2-bit xid 状态编码各版本一致。
 */
#ifndef PG_VERSIONS_H
#define PG_VERSIONS_H

/* heap 元组头 t_infomask 偏移（阅读索引；实际访问走编译期 PG 头） */
#define PG12_INFOMASK_OFFSET 20
#define PG11_AND_EARLIER_INFOMASK_OFFSET 24

/* CLOG 目录名（PG 版本迁移事实） */
#define PG10_PLUS_CLOG_DIR "pg_xact"
#define PG9_AND_EARLIER_CLOG_DIR "pg_clog"

/* 本工程编译依据（third_party/pg184 = PG18.4） */
#define PG_BASE_VER 180400

#endif /* PG_VERSIONS_H */