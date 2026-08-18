/*
 * mysql_lob_read.h — MySQL off-page 大值读取（8.0.13+ 新版 LOB，版本特性）。
 *
 * 版本背景：8.0.13 起 off-page 大值（TEXT/MEDIUMTEXT/BLOB/JSON 等 ≥8192B
 * 行外存储）使用新版 LOB 页（LOB_FIRST=24 / LOB_DATA=23）。8.0.13 之前
 * 及 5.6/5.7 使用旧 BLOB 页（FIL_PAGE_TYPE_BLOB=22），见 mysql_lob_legacy.c
 * （未实现）。行外触发条件：变长列 external 位（rec_offsets 的 0x4000），
 * 记录内仅存 20B REF，REF+4 为 LOB_FIRST 页号。
 */
#ifndef MYSQL_LOB_READ_H
#define MYSQL_LOB_READ_H

#include <stddef.h>
#include <stdint.h>

/* 新版 LOB（8.0.13+）多段拼接读取。pageno 为 LOB_FIRST 页号，结果写入 dst。
 * 返回 0 成功（out_len 为实际字节数），-1 失败（页不存在/非 LOB/超容量）。 */
int mysql_lob_read(const uint8_t *map, size_t map_len, uint16_t pageno,
                   uint8_t *dst, size_t dst_cap, uint32_t *out_len);

#endif /* MYSQL_LOB_READ_H */