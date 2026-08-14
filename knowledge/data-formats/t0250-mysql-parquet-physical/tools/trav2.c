#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define PS 16384U
#define FT 24U
#define FIL_PAGE_DATA 38U
#define FSEG_HEADER_SIZE 10U
#define PAGE_HEADER 38U
#define PAGE_DATA (PAGE_HEADER + 36 + 2 * FSEG_HEADER_SIZE) /* 94 */
#define PAGE_NEW_INFIMUM (PAGE_DATA + 5)                     /* 99 = 0x63 */

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((p[0] << 8) | p[1]); }

int main(int argc, char **argv) {
  if (argc < 2) return 1;
  FILE *f = fopen(argv[1], "rb");
  if (!f) return 1;
  uint8_t *b = malloc(PS);
  for (int pi = 0; pi < 3; pi++) {
    if (fread(b, 1, PS, f) != PS) break;
    uint16_t typ = rd16(b + FT);
    if (typ != 17855) { pi--; continue; }
    uint32_t inf = PAGE_NEW_INFIMUM;
    uint16_t nxt = rd16(b + inf - 2);
    uint32_t cur = inf + nxt;
    printf("== page (inf next=%u cur=0x%x) ==\n", nxt, cur);
    int i = 0;
    while (cur < PS && i < 8) {
      /* extra: origin 起往前 5B */
      uint8_t e0 = b[cur - 5], e1 = b[cur - 4], e2 = b[cur - 3], e3 = b[cur - 2], e4 = b[cur - 1];
      uint8_t info = e0 >> 4, n_owned = e0 & 0xF;
      uint16_t sh = (uint16_t)((e1 << 8) | e2);
      uint8_t status = sh & 0x7;
      uint16_t heap = sh >> 3;
      uint16_t n2 = (uint16_t)((e3 << 8) | e4);
      printf("  rec#%d origin=0x%03x info=%u owned=%u status=%u heap=%u next=0x%04x id_bytes=[%02x %02x %02x %02x %02x %02x %02x %02x]\n",
             i, cur, info, n_owned, status, heap, n2,
             b[cur], b[cur+1], b[cur+2], b[cur+3], b[cur+4], b[cur+5], b[cur+6], b[cur+7]);
      if (n2 == 0 || status == 3) break;
      cur += n2;
      if (cur >= PS) break;
      i++;
    }
  }
  free(b);
  fclose(f);
  return 0;
}