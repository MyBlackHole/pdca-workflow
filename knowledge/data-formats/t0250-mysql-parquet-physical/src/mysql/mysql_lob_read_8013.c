/*
 * mysql_lob_read_8013.c — MySQL off-page 大值多段读取（8.0.13+ 新版 LOB，版本特性文件）。
 *
 * 版本背景：8.0.13+ 大值行外存储用新版 LOB（LOB_FIRST=24 / LOB_DATA=23）。
 * 8.0.13 之前及 5.6/5.7 为旧 BLOB 页（type 22，见 mysql_lob_legacy_pre8013.c）。
 * 本实现仅覆盖 8.0.13+ 新版（AC-8 验证范围），旧格式未适配。
 *
 * 物理布局：由 index list 驱动 —— LOB_FIRST 页内 flst base@64（len 4B +
 * first fil_addr 6B = page 4B + off 2B），每 entry 60B（index_entry_t：
 * PAGE_NO@48 4B, DATA_LEN@52 2B, NEXT@6 6B fil_addr）；entry 依 next 指针
 * 串成段链，首段（PAGE_NO==LOB_FIRST 自身）数据位于页内 @696，其余段命中
 * LOB_DATA 页时 payload 位于页内 @49（本版本实测，与 MySQL 8.0 LOB 物理
 * 格式对齐）。各段依链表顺序拼接写入 dst。
 */
#include "mysql_lob_read_8013.h"

#include "mysql_sdi.h"
#include "mysql_versions.h"

#include <string.h>

int mysql_lob_read(const uint8_t *map, size_t map_len, uint16_t pageno,
                   uint8_t *dst, size_t dst_cap, uint32_t *out_len) {
  size_t pg_off = (size_t)pageno * MYSQL_PS;
  if (pg_off + MYSQL_PS > map_len) return -1;
  const uint8_t *pg = map + pg_off;
  uint32_t ftype = be16(pg + 24);
  if (ftype != FIL_PAGE_TYPE_LOB_FIRST) return -1;

  size_t used = 0;

  uint32_t nseg = be32(pg + 64); /* index list 段数 */
  if (nseg > 10) nseg = 10;      /* index array 固定 600B/60B = 10 entry */
  uint32_t npage = be32(pg + 68);
  uint16_t noff = be16(pg + 72);
  for (uint32_t i = 0; i < nseg; i++) {
    if (npage == 0xFFFFFFFFu && noff == 0xFFFF) break;
    size_t e_off = (size_t)npage * MYSQL_PS + noff;
    if (e_off + 60 > map_len) return -1;
    const uint8_t *e = map + e_off;
    uint32_t seg_page = be32(e + 48);
    uint32_t seg_len = be16(e + 52);
    size_t spg_off = (size_t)seg_page * MYSQL_PS;
    if (spg_off + MYSQL_PS > map_len) return -1;
    const uint8_t *spg = map + spg_off;
    if (seg_page == pageno) {
      if (used + seg_len > dst_cap) return -1;
      memcpy(dst + used, spg + 696, seg_len);
    } else {
      if (be16(spg + 24) != FIL_PAGE_TYPE_LOB_DATA) return -1;
      if (used + seg_len > dst_cap) return -1;
      memcpy(dst + used, spg + 49, seg_len);
    }
    used += seg_len;
    npage = be32(e + 6);
    noff = be16(e + 10);
  }
  *out_len = (uint32_t)used;
  return 0;
}