/*
 * mysql_versions.h — T0250 MySQL InnoDB 版本特性矩阵（文件即版本差异清单）。
 *
 * 拆分原则：凡随 MySQL 版本变化的解析事实集中在此，并在文件名/文件头
 * 标注对应版本；解析实现按版本特性拆分为独立文件，便于一眼看出
 * “哪段逻辑属于哪个版本”：
 *   5.6/5.7   表定义在 .frm（无 SDI）→ 布局走 mysql_layout_schema_56_57.c
 *   8.0+      表定义在 .ibd SDI 页     → 布局走 mysql_sdi_80.c
 *   8.0.13+   off-page 大值走新版 LOB  → 读取走 mysql_lob_read_8013.c
 *   8.0.13 前 旧 BLOB 页（type 22）    → mysql_lob_legacy_pre8013.c（未实现）
 *
 * 行格式：5.6 默认 COMPACT、5.7/8.0/8.4 默认 DYNAMIC，但两者记录头与
 * 变长长度数组布局一致，解析统一（mysql_parse_pages.c:rec_offsets）；
 * 差异由变长列 external 位（0x4000）表达行外存储，四版本同一套计算。
 */
#ifndef MYSQL_VERSIONS_H
#define MYSQL_VERSIONS_H

/* 页类型常量（各版本通用，含新旧 LOB 差异值） */
#define FIL_PAGE_TYPE_BLOB 22    /* 旧 BLOB 页：8.0.13 之前及 5.6/5.7 */
#define FIL_PAGE_TYPE_LOB_FIRST 24 /* 新版 LOB 首段：8.0.13+ */
#define FIL_PAGE_TYPE_LOB_DATA 23   /* 新版 LOB 数据页：8.0.13+ */
#define FIL_PAGE_TYPE_INDEX 17855
#define FIL_PAGE_TYPE_SDI 17853    /* 8.0+ 表定义页 */

/* 表定义来源（布局构建分派依据） */
enum {
  MYSQL_LAYOUT_SCHEMA = 0, /* 5.6/5.7：--schema= 文件（.frm 外部定义） */
  MYSQL_LAYOUT_SDI = 1     /* 8.0+   ：.ibd 内嵌 SDI 页自动解析 */
};

/* off-page 大值版本边界：
 *   >= 8.0.13 → 新版 LOB（LOB_FIRST=24 / LOB_DATA=23），mysql_lob_read_8013.c
 *   <  8.0.13 → 旧 BLOB 页（FIL_PAGE_TYPE_BLOB=22），mysql_lob_legacy_pre8013.c
 *  5.6/5.7/8.0/8.4 的 COMPACT/DYNAMIC 大值均经“变长 external 位 → REF(20B)
 *  → 版本对应 LOB 页”路径，本工程仅验证/实现 8.0.13+ 新版（AC-8）。 */
#define MYSQL_LOB_NEW_VERSION 80130

#endif /* MYSQL_VERSIONS_H */