/*
 * mysql_sdi.c — MySQL 8.0+ 表定义布局解析（SDI 驱动，版本特性文件）。
 *
 * 版本背景：8.0+ 表定义内嵌于 .ibd 的 FIL_PAGE_SDI 页（zlib 压缩 JSON），
 * 本文件负责从 SDI 页自动构建 MysqlLayout。5.6/5.7 无 SDI（表定义在 .frm），
 * 请用 mysql_layout_schema.c（--schema= 文件，版本特性文件）。
 * 类型 → InnoDB 物理语义的工具函数（map_mtype/d2b/int_bytes/fsp_bytes）
 * 为四版本公共（声明于 mysql_sdi.h，供本文件与 schema 布局共用）。
 *
 * SDI 记录解析照 ibd2sdi：FIL_PAGE_SDI 页内 record 首 4B 为 (type,type2,id)，
 * partial-length 编码与普通 record 一致，压缩 payload 在 rec+33 起。
 * 布局构建照 dict0dd.cc / data0type / rem0rec（详见 mysql_sdi.h）。
 */
#include "mysql_sdi.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>

/* ---------------- 最小 JSON 树 ---------------- */
enum { J_NULL, J_BOOL, J_NUM, J_STR, J_OBJ, J_ARR };
typedef struct JVal JVal;
typedef struct { char *k; JVal *v; } JPair;
typedef struct JVal {
  int type;
  long long num;
  char *str;
  JPair *obj;
  size_t nobj, cap;
  JVal **arr;
  size_t narr, capa;
} JVal;

static JVal *j_new(int type) {
  JVal *v = calloc(1, sizeof(JVal));
  v->type = type;
  return v;
}
static void j_free(JVal *v) {
  if (!v) return;
  if (v->type == J_STR) free(v->str);
  if (v->type == J_OBJ) {
    for (size_t i = 0; i < v->nobj; i++) { free(v->obj[i].k); j_free(v->obj[i].v); }
    free(v->obj);
  }
  if (v->type == J_ARR) {
    for (size_t i = 0; i < v->narr; i++) j_free(v->arr[i]);
    free(v->arr);
  }
  free(v);
}
static JVal *j_obj_add(JVal *o, char *k, JVal *v) {
  if (o->nobj == o->cap) {
    o->cap = o->cap ? o->cap * 2 : 8;
    o->obj = realloc(o->obj, o->cap * sizeof(JPair));
  }
  o->obj[o->nobj].k = k;
  o->obj[o->nobj].v = v;
  o->nobj++;
  return v;
}
static void j_arr_add(JVal *a, JVal *v) {
  if (a->narr == a->capa) {
    a->capa = a->capa ? a->capa * 2 : 8;
    a->arr = realloc(a->arr, a->capa * sizeof(JVal *));
  }
  a->arr[a->narr++] = v;
}

/* 递归下降 JSON 解析；*pp 指向开始处，解析后移动到结束。 */
static JVal *j_parse(const char **pp);
static void skip_ws(const char **pp) {
  while (**pp == ' ' || **pp == '\t' || **pp == '\n' || **pp == '\r') (*pp)++;
}
static char *j_str_parse(const char **pp) {
  const char *p = *pp;
  if (*p != '"') return NULL;
  p++;
  size_t cap = 16, n = 0;
  char *out = malloc(cap);
  while (*p && *p != '"') {
    char c = *p++;
    if (c == '\\') {
      if (!*p) break;
      c = *p++;
      if (c == 'n') c = '\n';
      else if (c == 't') c = '\t';
      else if (c == 'r') c = '\r';
      else if (c == 'b') c = '\b';
      else if (c == 'f') c = '\f';
      else if (c == 'u') {
        unsigned v = 0;
        for (int i = 0; i < 4 && *p; i++, p++) {
          v <<= 4;
          char h = *p;
          if (h >= '0' && h <= '9') v |= h - '0';
          else if (h >= 'a' && h <= 'f') v |= h - 'a' + 10;
          else if (h >= 'A' && h <= 'F') v |= h - 'A' + 10;
        }
        if (n + 4 > cap) { cap = n + 4 + 16; out = realloc(out, cap); }
        if (v < 0x80) out[n++] = (char)v;
        else if (v < 0x800) {
          out[n++] = (char)(0xC0 | (v >> 6));
          out[n++] = (char)(0x80 | (v & 0x3F));
        } else {
          out[n++] = (char)(0xE0 | (v >> 12));
          out[n++] = (char)(0x80 | ((v >> 6) & 0x3F));
          out[n++] = (char)(0x80 | (v & 0x3F));
        }
        continue;
      }
    }
    if (n + 1 > cap) { cap *= 2; out = realloc(out, cap); }
    out[n++] = c;
  }
  out[n] = 0;
  *pp = (*p == '"') ? p + 1 : p;
  return out;
}
static JVal *j_parse(const char **pp) {
  skip_ws(pp);
  char c = **pp;
  if (c == '{') {
    JVal *o = j_new(J_OBJ);
    (*pp)++;
    skip_ws(pp);
    if (**pp == '}') { (*pp)++; return o; }
    for (;;) {
      skip_ws(pp);
      char *k = j_str_parse(pp);
      if (!k) break;
      skip_ws(pp);
      if (**pp != ':') break;
      (*pp)++;
      JVal *v = j_parse(pp);
      j_obj_add(o, k, v ? v : j_new(J_NULL));
      skip_ws(pp);
      if (**pp == ',') { (*pp)++; continue; }
      break;
    }
    if (**pp == '}') (*pp)++;
    return o;
  }
  if (c == '[') {
    JVal *a = j_new(J_ARR);
    (*pp)++;
    skip_ws(pp);
    if (**pp == ']') { (*pp)++; return a; }
    for (;;) {
      JVal *v = j_parse(pp);
      j_arr_add(a, v ? v : j_new(J_NULL));
      skip_ws(pp);
      if (**pp == ',') { (*pp)++; continue; }
      break;
    }
    if (**pp == ']') (*pp)++;
    return a;
  }
  if (c == '"') {
    JVal *s = j_new(J_STR);
    s->str = j_str_parse(pp);
    return s;
  }
  if (c == 't' && strncmp(*pp, "true", 4) == 0) { JVal *b = j_new(J_BOOL); b->num = 1; *pp += 4; return b; }
  if (c == 'f' && strncmp(*pp, "false", 5) == 0) { JVal *b = j_new(J_BOOL); b->num = 0; *pp += 5; return b; }
  if (c == 'n' && strncmp(*pp, "null", 4) == 0) { JVal *z = j_new(J_NULL); *pp += 4; return z; }
  {
    char *end;
    JVal *n = j_new(J_NUM);
    n->num = strtoll(*pp, &end, 10);
    *pp = end;
    return n;
  }
}

static const JVal *j_get(const JVal *o, const char *key) {
  if (!o || o->type != J_OBJ) return NULL;
  for (size_t i = 0; i < o->nobj; i++)
    if (strcmp(o->obj[i].k, key) == 0) return o->obj[i].v;
  return NULL;
}

/* ---------------- 类型映射 ---------------- */
int map_mtype(int dd) {
  switch (dd) {
    case 2: case 3: case 4: case 9: case 10: case 11: case 12: case 13:
    case 14: case 22: case 23: case 8:
      return MF_INT;
    case 15: return MF_DATE;
    case 5: return MF_FLOAT;
    case 6: return MF_DOUBLE;
    case 21: return MF_DECIMAL;
    case 19: return MF_DATETIME2;
    case 18: return MF_TIMESTAMP2;
    case 20: return MF_TIME2;
    case 16: case 28: return MF_VARCHAR; /* 16 VARCHAR, 28 VARSTRING */
    case 31: return MF_JSON; /* JSON（InnoDB json_binary 格式） */
    case 29: return MF_STRING;
    case 24: case 25: case 26: case 27: case 30: case 32: return MF_BLOB;
    case 17: return MF_POINT;
    default: return MF_UNKNOWN;
  }
}

int d2b(int d) {
  if (d <= 1) return d;
  if (d <= 2) return 1;
  if (d <= 4) return 2;
  if (d <= 6) return 3;
  return 4;
}
int int_bytes(int dd) {
  switch (dd) {
    case 2: return 1;  /* TINYINT */
    case 3: return 2;  /* SMALLINT */
    case 10: return 3; /* INT24/MEDIUMINT */
    case 4: return 4;  /* INT */
    case 9: return 8;  /* BIGINT */
    case 22: return 1; /* ENUM（≤255 成员 1B，>255 2B 需查 charlen） */
    case 23: return 1; /* SET */
    case 14: return 1; /* YEAR（year-1900） */
    default: return 8;
  }
}
int fsp_bytes(int fsp) {
  if (fsp >= 5) return 3;
  if (fsp >= 3) return 2;
  if (fsp >= 1) return 1;
  return 0;
}

/* 解压 SDI 记录 payload（rec+33 起 length 字节，zlib） */
static unsigned char *inflate_rec(const unsigned char *pg, uint16_t rec,
                                  uint16_t length, unsigned long *out_len) {
  const unsigned char *src = pg + rec + 33;
  size_t avail = MYSQL_PS - (rec + 33);
  if (avail < length) length = (uint16_t)avail;
  unsigned long cap = 65536;
  unsigned char *out = malloc(cap);
  for (;;) {
    int rc = uncompress(out, &cap, src, length);
    if (rc == Z_OK) { *out_len = cap; return out; }
    if (rc == Z_BUF_ERROR) { cap *= 2; out = realloc(out, cap); continue; }
    free(out);
    return NULL;
  }
}

/* 解析 column_type_utf8 的 enum('a','b','c') / set('x','y') 成员，存 f->enum_vals（index 1 起） */
static void parse_enum_members(MysqlField *f, const char *ctyp) {
  if (!ctyp) return;
  const char *p = strchr(ctyp, '(');
  if (!p) return;
  p++;
  f->enum_vals = NULL;
  f->n_enum = 0;
  int cap = 0;
  while (*p && *p != ')') {
    if (*p == '\'' || *p == '"') {
      char quote = *p++;
      char tmp[512];
      int tlen = 0;
      while (*p && *p != quote) {
        if (tlen < (int)sizeof(tmp) - 1) tmp[tlen++] = *p;
        p++;
      }
      if (*p == quote) p++;
      tmp[tlen] = 0;
      if (f->n_enum + 2 > cap) { /* index 0 保留为空 */
        cap = cap ? cap * 2 : 16;
        char **nv = realloc(f->enum_vals, (size_t)cap * sizeof(char *));
        if (!nv) { free(f->enum_vals); f->enum_vals = NULL; f->n_enum = 0; return; }
        f->enum_vals = nv;
      }
      f->enum_vals[f->n_enum + 1] = strdup(tmp);
      f->n_enum++;
    } else if (*p == ',') {
      p++;
    } else {
      p++;
    }
  }
}

/* 释放 ENUM 成员 */
static void free_enum_members(MysqlField *f) {
  if (f->enum_vals) {
    for (uint16_t i = 1; i <= f->n_enum; i++) free(f->enum_vals[i]);
    free(f->enum_vals);
    f->enum_vals = NULL;
    f->n_enum = 0;
  }
}

/* 根据列对象填充字段（普通用户列） */
static void fill_field(MysqlField *f, const JVal *c) {
  const JVal *nm = j_get(c, "name");
  const JVal *ty = j_get(c, "type");
  const JVal *nl = j_get(c, "is_nullable");
  const JVal *pr = j_get(c, "numeric_precision");
  const JVal *sc = j_get(c, "numeric_scale");
  const JVal *fsp = j_get(c, "datetime_precision");
  const JVal *llen = j_get(c, "char_length");
  const JVal *ctyp = j_get(c, "column_type_utf8");
  memset(f, 0, sizeof(*f));
  f->name = nm && nm->str ? strdup(nm->str) : strdup("?");
  f->dd_type = (uint8_t)(ty ? ty->num : 0);
  f->mtype = (uint8_t)map_mtype(f->dd_type);
  f->nullable = nl && nl->num;
  f->precision = pr ? (uint16_t)pr->num : 0;
  f->scale = sc ? (uint8_t)sc->num : 0;
  f->fsp = fsp ? (uint8_t)fsp->num : 0;
  f->charlen = llen ? (uint32_t)llen->num : 0;
  /* tinyint(1) → BOOLEAN（MySQL 兼容映射） */
  if (f->dd_type == 2 && ctyp && ctyp->str && strcmp(ctyp->str, "tinyint(1)") == 0)
    f->is_bool = 1;
  /* UNSIGNED：column_type_utf8 含 "unsigned"（如 bigint unsigned） */
  if (ctyp && ctyp->str && strstr(ctyp->str, "unsigned")) f->is_unsigned = 1;
  /* ENUM/SET：解析成员列表用于字符串化 */
  if ((f->dd_type == 22 || f->dd_type == 23) && ctyp && ctyp->str)
    parse_enum_members(f, ctyp->str);
  switch (f->mtype) {
    case MF_INT:
      if (f->dd_type == 22) /* ENUM：成员数<256 用 1B，否则 2B（get_enum_pack_length） */
        f->fixed = (uint16_t)(f->n_enum < 256 ? 1 : 2);
      else if (f->dd_type == 23) /* SET：位图 (n+7)/8，>4 用 8B（get_set_pack_length） */
        f->fixed = (uint16_t)(((int)f->n_enum + 7) / 8 > 4 ? 8 : ((int)f->n_enum + 7) / 8);
      else
        f->fixed = (uint16_t)int_bytes(f->dd_type);
      break;
    case MF_FLOAT: f->fixed = 4; break;
    case MF_DOUBLE: f->fixed = 8; break;
    case MF_POINT: f->fixed = 25; break;
    case MF_DECIMAL: {
      int intg = (int)f->precision - f->scale;
      int i0 = intg / 9, ix = intg - i0 * 9;
      int f0 = f->scale / 9, fx = f->scale - f0 * 9;
      f->fixed = (uint16_t)(i0 * 4 + d2b(ix) + f0 * 4 + d2b(fx));
      break;
    }
    case MF_DATETIME2: f->fixed = (uint16_t)(5 + fsp_bytes(f->fsp)); break;
    case MF_TIMESTAMP2: f->fixed = (uint16_t)(4 + fsp_bytes(f->fsp)); break;
    case MF_TIME2: f->fixed = (uint16_t)(3 + fsp_bytes(f->fsp)); break;
    case MF_DATE: f->fixed = 3; break; /* day + month*32 + year*512（my_date_to_binary） */
    default: f->fixed = 0; break; /* VARCHAR/CHAR/TEXT/BLOB */
  }
  f->is_big = (f->mtype == MF_BLOB) || (f->fixed > 255) || (f->charlen > 255);
}

int mysql_layout_from_ibd(const uint8_t *map, size_t map_len, MysqlLayout *out) {
  memset(out, 0, sizeof(*out));
  /* 1) 找 SDI 页并取首条记录（照 ibd2sdi: id==1 的 record） */
  JVal *json = NULL;
  for (size_t pi = 0; pi < map_len / MYSQL_PS; pi++) {
    const uint8_t *pg = map + pi * MYSQL_PS;
    uint32_t ftype = ((uint32_t)pg[24] << 8) | pg[25];
    if (ftype != FIL_PAGE_TYPE_SDI) continue;
    uint16_t rec = PAGE_NEW_INFIMUM + (int16_t)(((uint16_t)pg[PAGE_NEW_INFIMUM - 2] << 8) | pg[PAGE_NEW_INFIMUM - 1]);
    while (rec > 0 && rec < MYSQL_PS) {
      uint8_t partial = pg[rec - 6];
      uint16_t length = (partial & 0x80) ? (uint16_t)(((partial & 0x3f) << 8) | pg[rec - 7]) : partial;
      uint32_t id = ((uint32_t)pg[rec] << 24) | ((uint32_t)pg[rec + 1] << 16) |
                    ((uint32_t)pg[rec + 2] << 8) | pg[rec + 3];
      if (id == 1) {
        unsigned long out_len = 0;
        unsigned char *raw = inflate_rec(pg, rec, length, &out_len);
        if (raw) {
          const char *p = (const char *)raw;
          json = j_parse(&p);
          free(raw);
        }
        if (!json) return -1;
        break;
      }
      int16_t nxt = (int16_t)(((uint16_t)pg[rec - 2] << 8) | pg[rec - 1]);
      rec = nxt > 0 ? (uint16_t)(rec + nxt) : 0;
    }
    if (json) break;
  }
  if (!json) {
    fprintf(stderr, "[sdi] 未找到表 SDI 定义\n");
    return -1;
  }

  const JVal *dd = j_get(json, "dd_object");
  if (!dd) { j_free(json); return -1; }
  const JVal *cols = j_get(dd, "columns");
  const JVal *idxs = j_get(dd, "indexes");
  if (!cols) { j_free(json); return -1; }

  /* 2) 物理字段序 = PRIMARY（聚集索引）elements 顺序。
   *    elements 顺序即 InnoDB 物理列序：主键列 + 系统列 + 其余列。
   *    element.hidden==false 才是真正主键列；true 为系统列/附加列。 */
  const int MAXC = 128;
  MysqlField tmp[MAXC];
  int n = 0;
  int n_pk = 0;
  const JVal *pk_idx = NULL;
  if (idxs) {
    for (size_t i = 0; i < idxs->narr; i++) {
      const JVal *nm = j_get(idxs->arr[i], "name");
      if (nm && nm->str && strcmp(nm->str, "PRIMARY") == 0) { pk_idx = idxs->arr[i]; break; }
    }
  }
  if (pk_idx) {
    const JVal *el = j_get(pk_idx, "elements");
    if (el) {
      for (size_t j = 0; j < el->narr && n < MAXC; j++) {
        const JVal *opx = j_get(el->arr[j], "column_opx");
        if (!opx || opx->num < 0 || opx->num >= (long long)cols->narr) continue;
        const JVal *c = cols->arr[opx->num];
        const JVal *h = j_get(c, "hidden");
        if (h && h->num == 2) {
          /* 系统列（hidden=2）：DB_ROW_ID 6B / DB_TRX_ID 6B / DB_ROLL_PTR 7B，
           * 物理记录占位保持 offsets 对齐 */
          const JVal *cnm = j_get(c, "name");
          memset(&tmp[n], 0, sizeof(MysqlField));
          tmp[n].name = cnm && cnm->str ? strdup(cnm->str) : strdup("?");
          if (cnm && cnm->str && strcmp(cnm->str, "DB_ROLL_PTR") == 0) {
            tmp[n].sys = 2; tmp[n].fixed = 7;
          } else if (cnm && cnm->str && strcmp(cnm->str, "DB_TRX_ID") == 0) {
            tmp[n].sys = 1; tmp[n].fixed = 6;
          } else { /* DB_ROW_ID */
            tmp[n].sys = 3; tmp[n].fixed = 6;
          }
          tmp[n].mtype = MF_INT;
          n++;
          continue;
        }
        const JVal *eh = j_get(el->arr[j], "hidden");
        if (!(eh && eh->num)) n_pk++;
        fill_field(&tmp[n++], c);
      }
    }
  }
  if (n == 0) {
    /* 3b 兜底：无 PRIMARY（GEN_CLUST_INDEX 隐式聚集索引）→
     * DB_ROW_ID(6B) + 系统列 + 其余列(ordinal 升序) */
    memset(&tmp[n], 0, sizeof(MysqlField));
    tmp[n].name = strdup("DB_ROW_ID");
    tmp[n].sys = 3; /* 隐式 row id，占位不输出 */
    tmp[n].fixed = 6;
    tmp[n].mtype = MF_INT;
    n++;
    for (size_t j = 0; j < cols->narr && n < MAXC; j++) {
      const JVal *h = j_get(cols->arr[j], "hidden");
      if (!h || h->num != 2) continue;
      const JVal *nm = j_get(cols->arr[j], "name");
      memset(&tmp[n], 0, sizeof(MysqlField));
      tmp[n].name = nm && nm->str ? strdup(nm->str) : strdup("?");
      tmp[n].sys = (nm && nm->str && strcmp(nm->str, "DB_TRX_ID") == 0) ? 1 : 2;
      tmp[n].fixed = tmp[n].sys == 1 ? 6 : 7;
      tmp[n].mtype = MF_INT;
      n++;
    }
    for (int ord = 1; ord <= 10000 && n < MAXC; ord++) {
      for (size_t j = 0; j < cols->narr; j++) {
        const JVal *c = cols->arr[j];
        const JVal *h = j_get(c, "hidden");
        if (h && h->num == 2) continue;
        const JVal *op = j_get(c, "ordinal_position");
        if (!op || op->num != ord) continue;
        if (n >= MAXC) break;
        fill_field(&tmp[n++], c);
      }
    }
  }
  if (n == 0) { j_free(json); return -1; }

  /* 4) 输出 */
  out->n_fields = (uint16_t)n;
  out->n_pk = (uint16_t)n_pk;
  out->n_nullable = 0;
  out->fields = calloc(n, sizeof(MysqlField));
  memcpy(out->fields, tmp, n * sizeof(MysqlField));
  for (int i = 0; i < n; i++)
    if (out->fields[i].nullable) out->n_nullable++;

  j_free(json);
  return 0;
}

void mysql_layout_free(MysqlLayout *l) {
  if (!l || !l->fields) return;
  for (int i = 0; i < l->n_fields; i++) {
    free(l->fields[i].name);
    free_enum_members(&l->fields[i]);
  }
  free(l->fields);
  l->fields = NULL;
  l->n_fields = 0;
}
