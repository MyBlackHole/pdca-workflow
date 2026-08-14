#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define PS 16384U
#define FIL_PAGE_TYPE 24U
#define PAGE_HEADER 38U
#define PAGE_DATA (38 + 36 + 20) /* 94 */
#define PAGE_NEW_INFIMUM (PAGE_DATA + 5)
#define REC_N_NEW_EXTRA_BYTES 5

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((p[0] << 8) | p[1]); }
static uint32_t rd32r(const uint8_t *p) { return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3]; }

/* 表 schema（poc_orders 7 列）:
   0 id BIGINT NOT NULL PK      fixed 8
   1 customer_id INT NOT NULL   fixed 4
   2 amount DECIMAL(12,2) NOT NULL  fixed 6? (dec62)  -- 实际上 DECIMAL(12,2)=5B 保存，但 fixed=6?
   3 created_at DATETIME(6) NN  fixed 5
   4 status VARCHAR(16) NN      varlen
   5 payload VARCHAR(96) NN     varlen
   6 active TINYINT(1) NN       fixed 1
*/
static const int nfields = 7;
static const uint8_t fixed[7] = {8, 4, 0, 5, 0, 0, 1}; /* 0=varlen, 5=dec/datetime 实测 */
/* 实际 DECIMAL(12,2) 用 dec_get_binary_size: intPart 10 位? 我们需要字典确认, 先用0探测 */
#define IS_VAR(i) (fixed[i] == 0)

/* 解析一条记录 -- 返回 0 成功, 打印字段 */
static int parse_rec(const uint8_t *page, uint32_t org) {
  uint8_t e0 = page[org - 5], e1 = page[org - 4], e2 = page[org - 3], e3 = page[org - 2], e4 = page[org - 1];
  uint16_t sh = (uint16_t)((e1 << 8) | e2);
  uint8_t status = sh & 7;
  if (status != 0) return -1; /* 只解析 ORDINARY */

  /* null bitmap 起始 = origin-6 */
  const uint8_t *nulls = page + org - (REC_N_NEW_EXTRA_BYTES + 1);
  uint32_t n_nullable = 0; /* 全部 NOT NULL */
  const uint8_t *lens = nulls; /* -= bytes(n_null) = -0 */

  /* 进行: 读取长, 累加 offs */
  ulong offs = 0;
  ulong ends[8]; /* 每个字段结束偏移 */
  uint32_t i = 0;
  uint32_t lbase = 0;
  const uint8_t *L = lens;
  for (i = 0; i < nfields; i++) {
    if (!IS_VAR(i)) { offs += fixed[i]; ends[i] = offs; }
    else {
      /* varlen: 1-2 字节 */
      uint32_t len = *L; L--;
      ends[i] = offs += len;
    }
  }
  /* 打印字段(0..n-1): 字段 i 数据 = [ends[i-1]..ends[i]) */
  printf("  org=0x%03x ends0..6 =", org);
  for (i = 0; i < nfields; i++) printf(" %lu", ends[i]);
  printf("\n");
  /* 显示关键: org..org+20 原始 */
  printf("  raw:");
  for (i = 0; i < 40; i++) printf(" %02x", page[org + i]);
  printf("\n");
  return 0;
}

int main(int argc, char **argv) {
  if (argc < 2) return 1;
  FILE *f = fopen(argv[1], "rb");
  if (!f) return 1;
  uint8_t *b = malloc(PS);
  for (int pi = 4; pi < 8; pi++) {
    fseek(f, (long)pi * PS, SEEK_SET);
    if (fread(b, 1, PS, f) != PS) break;
    uint16_t typ = rd16(b + FIL_PAGE_TYPE);
    if (typ != 17855) { printf("page %d: type %u skip\n", pi, typ); continue; }
    printf("== page %d ==\n", pi);
    uint32_t inf = PAGE_NEW_INFIMUM;
    uint16_t nxt = rd16(b + inf - 2);
    uint32_t cur = inf + nxt;
    int k = 0;
    while (cur < PS && k < 5) {
      if (parse_rec(b, cur) != 0) break;
      uint16_t n2 = rd16(b + cur - 2);
      if (n2 == 0) break;
      cur += n2;
      if (cur >= PS) break;
      k++;
    }
  }
  free(b);
  fclose(f);
  return 0;
}