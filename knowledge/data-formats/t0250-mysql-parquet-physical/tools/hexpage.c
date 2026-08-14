#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define PS 16384U
#define FT 24U
static uint16_t rd16(const uint8_t*p){return (p[0]<<8)|p[1];}
static uint32_t rd32r(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
int main(int c,char**v){
  if(c<3)return 1;
  FILE*f=fopen(v[1],"rb");if(!f)return 1;
  uint8_t*b=malloc(PS);long pg=strtol(v[2],0,10);
  fseek(f,pg*PS,SEEK_SET);
  if(fread(b,1,PS,f)!=PS){perror("read");return 1;}
  fclose(f);
  long start=strtol(v[3],0,0);
  long n = c>4 ? strtol(v[4],0,0) : 128;
  printf("page=%ld type=%u at 0x%lx:\n", pg, rd16(b+FT), start);
  for(long i=0;i<n;i++){
    if(i%16==0)printf("  0x%03lx: ", start+i);
    printf("%02x ", b[(size_t)start+i]);
    if(i%16==15)printf("\n");
  }
  printf("\n");
  return 0;
}