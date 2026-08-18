/*
 * mysql_layout_schema_56_57.c — MySQL 5.6/5.7 表定义布局解析（版本特性文件）。
 *
 * 版本背景：5.6/5.7 无 SDI 页（表定义在外部 .frm），本文件从 CLI
 * --schema= 文本文件构建 MysqlLayout。schema 文件每行一列：
 *   name:type[(prec[,scale]|fsp)][:pk][:unsigned][:null][:bool]
 * 类型 → dd::enum_column_types 编码（schema_dd_type），再经公共工具
 * （mysql_sdi.h: map_mtype/int_bytes/d2b/fsp_bytes）落为物理字段属性；
 * 物理列序 = PK 列 → DB_TRX_ID(6B) → DB_ROLL_PTR(7B) → 其余列，
 * 与 8.0+ SDI 布局（mysql_sdi_80.c）完全一致，故 rec_offsets 一套计算
 * 即可覆盖 5.6/5.7/8.0/8.4。
 */
#include "mysql_layout_schema_56_57.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* 文本类型 → dd::enum_column_types 编码（5.6/5.7 schema 专用） */
static int schema_dd_type(const char *type) {
  if (!strcmp(type, "tinyint")) return 2;
  if (!strcmp(type, "smallint")) return 3;
  if (!strcmp(type, "int")) return 4;
  if (!strcmp(type, "float")) return 5;
  if (!strcmp(type, "double")) return 6;
  if (!strcmp(type, "bigint")) return 9;
  if (!strcmp(type, "int24")) return 10;
  if (!strcmp(type, "year")) return 14;
  if (!strcmp(type, "varchar")) return 16;
  if (!strcmp(type, "text") || !strcmp(type, "blob")) return 24;
  if (!strcmp(type, "timestamp")) return 18;
  if (!strcmp(type, "datetime")) return 19;
  if (!strcmp(type, "time")) return 20;
  if (!strcmp(type, "decimal")) return 21;
  if (!strcmp(type, "char")) return 29;
  if (!strcmp(type, "bool")) return 4;   /* tinyint(1) → INT，is_bool 标记 */
  return -1;
}

int mysql_layout_from_schema_file(const char *path, MysqlLayout *out) {
  memset(out, 0, sizeof(*out));
  FILE *fp = fopen(path, "r");
  if (!fp) return -1;
  const int MAXC = 128;
  MysqlField tmp[MAXC];
  int pkmark[MAXC];
  int n = 0, n_pk = 0;
  char line[512];
  while (fgets(line, sizeof(line), fp) && n < MAXC) {
    char *p = line;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '#' || *p == '\n' || *p == '\r' || *p == 0) continue;
    char *eol = strpbrk(p, "\r\n");
    if (eol) *eol = 0;
    /* 去掉尾部注释 */
    char *hash = strchr(p, '#');
    if (hash) *hash = 0;
    char name[128], type[32];
    int is_pk = 0, is_null = 0, is_unsigned = 0;
    long prec = 0, scale = 0, fsp = 0, clen = 0;
    char *colon = strchr(p, ':');
    if (!colon) continue;
    size_t nl = (size_t)(colon - p);
    if (nl >= sizeof(name)) nl = sizeof(name) - 1;
    memcpy(name, p, nl); name[nl] = 0;
    /* 解析类型 + 属性 */
    char *tp = colon + 1;
    char tbase[32] = {0};
    int tlen = 0;
    char *lp = tp;
    while (*lp && *lp != ':' && *lp != '(') tbase[tlen++] = *lp++;
    tbase[tlen] = 0;
    if (*lp == '(') {
      lp++;
      long a = strtol(lp, &lp, 10);
      if (*lp == ',') { scale = strtol(lp + 1, &lp, 10); prec = a; }
      else { fsp = a; prec = a; }
      if (*lp == ')') lp++;
    }
    /* 剩余属性 */
    while (*lp) {
      if (*lp != ':') { lp++; continue; }
      lp++;
      if (!strncmp(lp, "pk", 2) && (lp[2] == 0 || lp[2] == ':')) { is_pk = 1; lp += 2; continue; }
      if (!strncmp(lp, "unsigned", 8)) { is_unsigned = 1; lp += 8; continue; }
      if (!strncmp(lp, "null", 4)) { is_null = 1; lp += 4; continue; }
      if (!strncmp(lp, "bool", 4)) { is_unsigned = 1; lp += 4; continue; }
      lp++;
    }
    (void)clen;
    int dd = schema_dd_type(tbase);
    if (dd < 0) continue;
    memset(&tmp[n], 0, sizeof(MysqlField));
    tmp[n].name = strdup(name);
    tmp[n].dd_type = (uint8_t)dd;
    tmp[n].mtype = (uint8_t)map_mtype(dd);
    tmp[n].nullable = (uint8_t)is_null;
    tmp[n].is_unsigned = (uint8_t)is_unsigned;
    if (!strcmp(tbase, "bool")) tmp[n].is_bool = 1;
    if (!strcmp(tbase, "decimal")) { tmp[n].precision = (uint16_t)prec; tmp[n].scale = (uint8_t)scale; }
    if (!strcmp(tbase, "datetime") || !strcmp(tbase, "timestamp") || !strcmp(tbase, "time"))
      tmp[n].fsp = (uint8_t)fsp;
    if (!strcmp(tbase, "varchar") || !strcmp(tbase, "char"))
      tmp[n].charlen = (uint32_t)prec;
    if (is_pk) n_pk++;
    pkmark[n] = is_pk;
    switch (tmp[n].mtype) {
      case MF_INT:
        if (tmp[n].is_bool) tmp[n].fixed = 1;
        else tmp[n].fixed = (uint16_t)int_bytes(dd);
        break;
      case MF_FLOAT: tmp[n].fixed = 4; break;
      case MF_DOUBLE: tmp[n].fixed = 8; break;
      case MF_DECIMAL:
        tmp[n].fixed = (uint16_t)(1 + d2b(tmp[n].precision - tmp[n].scale) + d2b(tmp[n].scale));
        break;
      case MF_DATETIME2: case MF_TIMESTAMP2:
        tmp[n].fixed = (uint16_t)(5 + fsp_bytes(tmp[n].fsp)); break;
      case MF_TIME2:
        tmp[n].fixed = (uint16_t)(3 + fsp_bytes(tmp[n].fsp)); break;
      case MF_STRING:
        tmp[n].fixed = (uint16_t)prec; tmp[n].charlen = (uint32_t)prec; break;
      case MF_VARCHAR:
        tmp[n].fixed = 0; break;
      case MF_BLOB: tmp[n].fixed = 0; break;
      default: break;
    }
    tmp[n].is_big = (tmp[n].mtype == MF_BLOB) || (tmp[n].fixed > 255) || (tmp[n].charlen > 255);
    n++;
  }
  fclose(fp);
  if (n == 0) return -1;

  /* 物理列序：PK 列（保持 schema 序）+ 系统列 + 非 PK 列（保持 schema 序） */
  MysqlField tmp2[MAXC];
  int m = 0;
  for (int i = 0; i < n; i++) if (pkmark[i]) tmp2[m++] = tmp[i];
  /* DB_TRX_ID 6B + DB_ROLL_PTR 7B 占位 */
  memset(&tmp2[m], 0, sizeof(MysqlField)); tmp2[m].name = strdup("DB_TRX_ID");
  tmp2[m].sys = 1; tmp2[m].fixed = 6; tmp2[m].mtype = MF_INT; m++;
  memset(&tmp2[m], 0, sizeof(MysqlField)); tmp2[m].name = strdup("DB_ROLL_PTR");
  tmp2[m].sys = 2; tmp2[m].fixed = 7; tmp2[m].mtype = MF_INT; m++;
  for (int i = 0; i < n; i++) if (!pkmark[i]) tmp2[m++] = tmp[i];

  out->n_fields = (uint16_t)m;
  out->n_pk = (uint16_t)n_pk;
  out->n_nullable = 0;
  out->fields = calloc(m, sizeof(MysqlField));
  memcpy(out->fields, tmp2, m * sizeof(MysqlField));
  for (int i = 0; i < m; i++)
    if (out->fields[i].nullable) out->n_nullable++;
  return 0;
}