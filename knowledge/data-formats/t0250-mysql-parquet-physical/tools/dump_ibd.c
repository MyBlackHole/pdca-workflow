/* InnoDB .ibd 页结构预研 dump 工具（T0250）
 * 功能：
 *   1. 遍历 .ibd，统计各 FIL_PAGE_TYPE 页数
 *   2. 对每个 INDEX 叶页（PAGE_LEVEL==0 且 FIL_PAGE_TYPE==17855），打印
 *      页头关键字段：n_recs / heap_top / n_heap / free / garbage / level / index_id
 *   3. 打印失控的首条 user record 的原始字节（前 64 字节），供字段布局推断
 *
 * 使用：./dump_ibd <file.ibd>
 * 页大小硬编码 16384（MySQL 默认），如需一般化可从 FIL 页读取。
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define UNIV_PAGE_SIZE 16384U
#define FIL_PAGE_OFFSET 4U
#define FIL_PAGE_PREV 8U
#define FIL_PAGE_NEXT 12U
#define FIL_PAGE_TYPE 24U
#define FIL_PAGE_INDEX 17855U
#define FIL_PAGE_SDI 17853U
#define FIL_PAGE_TYPE_ALLOCATED 0U
#define FIL_PAGE_INODE 17855U

#define PAGE_HEADER 38U           /* FSEG_PAGE_DATA, 紧接 FIL 头 */
#define PAGE_N_DIR_SLOTS 0U
#define PAGE_HEAP_TOP 2U
#define PAGE_N_HEAP 4U
#define PAGE_FREE 6U
#define PAGE_GARBAGE 8U
#define PAGE_LAST_INSERT 10U
#define PAGE_N_RECS 16U
#define PAGE_MAX_TRX_ID 18U
#define PAGE_LEVEL 26U
#define PAGE_INDEX_ID 28U
#define PAGE_DATA (PAGE_HEADER + 36 + 2 * 10) /* +36 页头私有 +2*10 FSEG */
#define PAGE_NEW_INFIMUM (PAGE_DATA + 5)      /* + REC_N_NEW_EXTRA_BYTES */

/* COMPACT/DYNAMIC 记录 extra 布局（相对记录 origin 的偏移） */
#define REC_NEXT 2U          /* 2B 下一条记录相对偏移（有符号） */
#define REC_NEW_STATUS 3U    /* 低 3 bit */
#define REC_NEW_HEAP_NO 4U   /* heap_no=byte4|byte5 高13bit */
#define REC_NEW_N_OWNED 5U   /* 低 4 bit */
#define REC_NEW_INFO_BITS 5U /* 高 4 bit */

static uint16_t rd16(const uint8_t *p) {
  return (uint16_t)((p[0] << 8) | p[1]);
}
static uint32_t rd32(const uint8_t *p) {
  return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
         ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}

static const char *page_type_name(uint16_t t) {
  switch (t) {
    case FIL_PAGE_INDEX: return "INDEX";
    case FIL_PAGE_SDI: return "SDI";
    case FIL_PAGE_TYPE_ALLOCATED: return "ALLOCATED";
    case 17852: return "UNDO_LOG";
    case 17854: return "IBUF_BITMAP";
    case 17856: return "XDES";
    case 17857: return "BLOB";
    case 17858: return "ZLOB?";
    case 17859: return "ZLOB_FIRST";
    case 17860: return "ZLOB_DATA";
    case 17861: return "ZLOB_TAIL";
    default: return "OTHER";
  }
}

int main(int argc, char **argv) {
  if (argc < 2) {
    fprintf(stderr, "usage: dump_ibd <file.ibd>\n");
    return 1;
  }
  FILE *f = fopen(argv[1], "rb");
  if (!f) { perror("open"); return 1; }
  fseek(f, 0, SEEK_END);
  long sz = ftell(f);
  fseek(f, 0, SEEK_SET);

  uint8_t *buf = malloc(UNIV_PAGE_SIZE);
  if (!buf) { perror("malloc"); return 1; }

  long npages = sz / UNIV_PAGE_SIZE;
  printf("=== %s : %ld bytes = %ld pages (16KB) ===\n", argv[1], sz, npages);

  /* 页类型统计 */
  uint32_t typecount[65536] = {0};
  int shown = 0; /* 已展示的叶页数 */
  int shown_nonleaf = 0, shown_bad = 0;
  for (long p = 0; p < npages; p++) {
    if (fread(buf, 1, UNIV_PAGE_SIZE, f) != UNIV_PAGE_SIZE) break;
    uint16_t type = rd16(buf + FIL_PAGE_TYPE);
    typecount[type]++;
  }
  printf("\n-- 页类型统计 --\n");
  for (uint32_t t = 0; t < 65536; t++) {
    if (typecount[t]) printf("  type %5u (%-11s): %u 页\n", t, page_type_name(t), typecount[t]);
  }

  /* 遍历叶页显示头部 + 首记录 raw */
  printf("\n-- 各叶页（PAGE_LEVEL=0）头部 --\n");
  rewind(f);
  for (long p = 0; p < npages; p++) {
    if (fread(buf, 1, UNIV_PAGE_SIZE, f) != UNIV_PAGE_SIZE) break;
    uint16_t type = rd16(buf + FIL_PAGE_TYPE);
    if (type != FIL_PAGE_INDEX) continue;
    uint16_t level = rd16(buf + PAGE_HEADER + PAGE_LEVEL);
    if (level != 0) continue;
    uint32_t page_no = rd32(buf + FIL_PAGE_OFFSET);
    uint32_t n_recs = rd16(buf + PAGE_HEADER + PAGE_N_RECS);
    uint16_t n_heap = rd16(buf + PAGE_HEADER + PAGE_N_HEAP);
    uint32_t heap_top = rd16(buf + PAGE_HEADER + PAGE_HEAP_TOP);
    uint16_t n_dir = rd16(buf + PAGE_HEADER + PAGE_N_DIR_SLOTS);
    uint32_t index_id = rd32(buf + PAGE_HEADER + PAGE_INDEX_ID);
    printf("page=%u n_recs=%u n_heap=%u heap_top=%u n_dir=%u index_id=%u",
           page_no, n_recs, n_heap, heap_top, n_dir, index_id);
    if (shown < 3 || p == npages - 1) {
      /* 首 user record: infimum 的 next 指针 */
      uint32_t inf = PAGE_NEW_INFIMUM;
      int16_t nxt = (int16_t)rd16(buf + inf - REC_NEXT);
      uint32_t first = (uint32_t)(inf + nxt);
      printf("  first_rec_off=%u", first);
      if (shown < 3) {
        printf("\n    [first user record raw 0x%02x..0x%02x]\n", first, first + 63);
        for (int i = 0; i < 64; i++) {
          if (i % 16 == 0) printf("      %04x: ", first + i);
          printf("%02x ", buf[first + i]);
          if (i % 16 == 15) printf("\n");
        }
      }
      shown++;
    }
    printf("\n");
  }
  free(buf);
  fclose(f);
  return 0;
}