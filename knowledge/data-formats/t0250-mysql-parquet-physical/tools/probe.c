#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define PS 16384U
#define FIL_PAGE_TYPE 24U
#define PAGE_DATA 94U
#define PAGE_NEW_INFIMUM (PAGE_DATA + 5)

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((p[0] << 8) | p[1]); }

/* 尝试多种布局, 打印 customer/amount/status 位置, 人工校验 */
int main(int argc, char **argv) {
  if (argc < 2) return 1;
  FILE *f = fopen(argv[1], "rb");
  if (!f) return 1;
  uint8_t *b = malloc(PS);
  for (int pi = 5; pi < 6; pi++) {
    fseek(f, (long)pi * PS, SEEK_SET);
    if (fread(b, 1, PS, f) != PS) break;
    uint32_t inf = PAGE_NEW_INFIMUM;
    uint32_t cur = inf + rd16(b + inf - 2);
    int k = 0;
    while (cur < PS && k < 3) {
      uint8_t e1 = b[cur - 4], e2 = b[cur - 3];
      uint8_t status = ((e1 << 8) | e2) & 7;
      if (status == 0) {
        /* 打印 data 区 40B, 标注候选位置 */
        printf("rec#%d org=0x%03x\n", k, cur);
        printf("  [0]=%02x [1]=%02x  id@[1..8)=%02x%02x..\n", b[cur], b[cur+1], b[cur+1], b[cur+2]);
        printf("  seg:");
        for (int i = 0; i < 48; i++) printf("%02x ", b[cur+i]);
        printf("\n");
      }
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