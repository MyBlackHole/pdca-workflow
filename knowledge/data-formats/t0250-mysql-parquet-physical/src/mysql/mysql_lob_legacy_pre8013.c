/*
 * mysql_lob_legacy_pre8013.c — MySQL 旧 BLOB 页读取（8.0.13 之前及 5.6/5.7，版本特性文件）。
 *
 * 版本背景：8.0.13 之前及 5.6/5.7 的 off-page 大值使用旧 BLOB 页
 * （FIL_PAGE_TYPE_BLOB=22）。已知事实（本工程逆向期间观察，供后续实现）：
 *   - 旧 BLOB 页由若干 8KB 分片组成，首片记录 BLOB 元信息；
 *   - 行内 20B REF 中记录了首分片页号与总长度；
 *   - 分片链经页内 BTR_CUR 预留字段（FIL_PAGE_NEXT/FIL_PAGE_PREV，偏移 8/4）
 *     串联，非 8.0.13+ 的 index list 段链。
 * 本文件为占位：未实现（AC-8 验证范围仅 8.0.13+ 新版 LOB），恒返回 -1。
 * 版本分派处（decode_field 的 external 列）当前仅调用 mysql_lob_read，
 * 若目标 .ibd 含旧 BLOB 页会解码失败并显式报错，而非静默错读。
 */
#include "mysql_lob_legacy_pre8013.h"

int mysql_lob_legacy_read(const uint8_t *map, size_t map_len, uint16_t pageno,
                          uint8_t *dst, size_t dst_cap, uint32_t *out_len) {
  (void)map; (void)map_len; (void)pageno; (void)dst; (void)dst_cap; (void)out_len;
  return -1; /* 旧 BLOB 格式未实现（见头文件说明） */
}