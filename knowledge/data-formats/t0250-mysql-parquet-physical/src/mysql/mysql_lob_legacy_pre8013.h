/*
 * mysql_lob_legacy.h — MySQL 旧 BLOB 页读取（8.0.13 之前及 5.6/5.7，版本特性）。
 *
 * 版本背景：8.0.13 之前及 5.6/5.7 的 off-page 大值使用旧 BLOB 页
 * （FIL_PAGE_TYPE_BLOB=22），物理格式与 8.0.13+ 新版 LOB 不同
 * （见 mysql_lob_read.c）。本文件为旧格式占位：未实现（AC-8 验证范围
 * 仅 8.0.13+ 新版 LOB），调用恒返回 -1。文件即“旧 BLOB 版本特性”的
 * 承载点，后续逆向旧布局只需填充本实现。
 */
#ifndef MYSQL_LOB_LEGACY_H
#define MYSQL_LOB_LEGACY_H

#include <stddef.h>
#include <stdint.h>

/* 旧 BLOB 页（type 22）多段读取占位：未实现，恒返回 -1。
 * 签名与 mysql_lob_read 一致，便于版本分派处无缝切换。 */
int mysql_lob_legacy_read(const uint8_t *map, size_t map_len, uint16_t pageno,
                          uint8_t *dst, size_t dst_cap, uint32_t *out_len);

#endif /* MYSQL_LOB_LEGACY_H */