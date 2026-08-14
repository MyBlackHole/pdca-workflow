#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define PS 16384U
#define FT 24U
#define FIL_PAGE_DATA 38U
#define FSEG_HEADER_SIZE 10U
#define PAGE_HEADER (FIL_PAGE_DATA + 26) /* PAGE_HEADER 偏移 = 38 */
#define PAGE_DATA (PAGE_HEADER + 36 + 2 * FSEG_HEADER_SIZE)
#define PAGE_NEW_INFIMUM (PAGE_DATA + 5)

static uint16_t rd16(const uint8_t*p){return (uint16_t)((p[0]<<8)|p[1]);}
static uint32_t rd32r(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}

int main(int c,char**v){
  if(c<2)return 1;
  FILE*f=fopen(v[1],"rb");if(!f)return 1;
  uint8_t*b=malloc(PS);
  for(int pi=0; pi<5; pi++){
    if(fread(b,1,PS,f)!=PS)break;
    uint16_t type=rd16(b+FT);
    if(type!=17855)continue;
    uint16_t level=rd16(b+PAGE_HEADER+PAGE_NEW_INFIMUM-PAGE_DATA-5+? );
    (void)level;
  }
  return 0;
}