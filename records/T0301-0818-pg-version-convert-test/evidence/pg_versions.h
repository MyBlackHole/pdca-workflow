/*
 * pg_versions.h — PostgreSQL 版本特性矩阵（文件即版本差异清单）。
 *
 * 拆分原则：凡随 PG 版本变化的物理解析事实集中在此，并在文件名/文件头
 * 标注对应版本；解析实现按版本特性拆分为独立文件：
 *   heap 头/可见性（t_infomask 偏移）   → pg_heap_reader.c（PG12+ 实测）
 *   CLOG 提交日志：PG10+ pg_xact        → pg_clog_reader_pg10.c（已实现）
 *   CLOG 提交日志：PG9.x 及更早 pg_clog  → pg_clog_legacy_pg9.c（未实现）
 *
 * 版本事实（T0301 实测 pg9.6/pg11/pg18.4 三容器 pageinspect + 原始字节对拍）：
 *   - heap 元组头字节偏移与 varlena 编码各版本一致（无版本差异）：
 *     xmin/xmax/cid@0/4/8，ctid@12，infomask2@18，infomask@20，t_hoff@22，
 *     头 24B；varlena 为 packed 格式（1B 头最低位=1 长度=头>>1；4B 头
 *     低 2 位=00/10 长度=(va_header>>2)&0x3FFFFFFF）。
 *     早前"PG12 移除 t_xvac 使头 28B→24B"及"PG13- 老格式 varlena"推论
 *     均无实例支撑（t_xvac 与 t_cid 同处 t_field3 union 4B），已废弃。
 *   - CLOG 目录名随 PG 版本迁移：PG10+ 为 pg_xact/，PG9.x 及更早为 pg_clog/。
 *     SLRU 段文件（32 页/段）与 2-bit xid 状态编码各版本一致。
 */
#ifndef PG_VERSIONS_H
#define PG_VERSIONS_H

/* heap 元组头布局偏移（T0301 实测各版本一致，仅作阅读索引；实际访问
 * 用 pg_heap_reader.c 同名宏，禁止硬编码旧偏移） */
#define PG_HEAP_INFOMASK_OFF 20
#define PG_HEAP_INFOMASK2_OFF 18
#define PG_HEAP_T_HOFF_OFF 22
#define PG_HEAP_HEADER_SIZE 24 /* 头部大小（含 padding），即 t_bits 起点 */

/* CLOG 目录名（PG 版本迁移事实） */
#define PG10_PLUS_CLOG_DIR "pg_xact"
#define PG9_AND_EARLIER_CLOG_DIR "pg_clog"

/* 本工程编译依据（third_party/pg184 = PG18.4） */
#define PG_BASE_VER 180400

#endif /* PG_VERSIONS_H */