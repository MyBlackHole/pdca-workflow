/*
 * mysql_parse_pages.c — T0250 MySQL InnoDB 通用物理直读（页记录解码核心）。
 *
 * 记录 offsets 计算照 InnoDB 源码 rec_init_offsets_comp_ordinary 语义：
 *   nulls = rec-6；lens = nulls - ⌈n_null/8⌉；NULL 位图 LSB 起（byte 溢出向前）；
 *   变长 len 数组正序（先字段存高地址）；DATA_BIG_COL 用 2B 编码，
 *   0x4000 = external 位（off-page 数据经 20B REF 定位）。
 * 值解码照 row0mysql.cc / data0type：
 *   - 有符号整数/DATETIME/DECIMAL 首字节 ^0x80 符号位翻转
 *   - decimal2bin：负数逐字节按位取反
 *   - DATETIME2 5B 位域 ym<<22|day<<17|hour<<12|min<<6|sec
 *   - off-page LOB：8.0.13+ 新版 LOB_FIRST 页 data@696，DATA_LEN@54，
 *     读取实现拆分至 mysql_lob_read_8013.c（版本特性文件）；旧 BLOB 页（type 22）
 *     见 mysql_lob_legacy_pre8013.c（未实现）。
 *
 * 版本拆分索引（文件即版本特性）：
 *   mysql_versions.h        — 版本特性矩阵/页类型常量
 *   mysql_sdi_80.c             — 8.0+ SDI 布局（表定义内嵌页）
 *   mysql_layout_schema_56_57.c   — 5.6/5.7 schema 布局（--schema= 文件）
 *   mysql_lob_read_8013.c        — 8.0.13+ 新版 LOB 多段读取
 *   mysql_lob_legacy_pre8013.c      — 旧 BLOB 页（type 22）占位（未实现）
 * 四版本行格式 COMPACT/DYNAMIC 记录层一致，本文件统一解码（rec_offsets）。
 */
#include "mysql_sdi.h"
#include "mysql_lob_read_8013.h"

#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>
#include <zlib.h>

/* 解码后的统一单元格 */
typedef struct {
  uint8_t kind; /* 0 NULL, 1 整数/时间_us(存 i64), 2 浮点, 3 字符串(off/len→strbuf) */
  int64_t i64;
  double f64;
  uint32_t off, len;
} MysqlCell;

typedef struct {
  uint32_t page_idx; /* 下一物理页 */
  uint16_t consumed; /* 当前页已消费记录数（页内从头计数） */
  uint8_t *map;
  size_t map_len;
  int fd;
  int plain; /* 1 = map 为调用方明文缓冲(不 munmap), 0 = 本模块 mmap */
} MysqlCur;

/* 字段 offsets 说明 */
typedef struct {
  uint16_t off;
  uint16_t len;
  uint8_t kind; /* 0 FIX, 1 NULL, 2 VAR1, 3 VAR2, 4 EXT, 5 SYS */
} ColSpec;

static inline uint64_t be64(const uint8_t *p) {
  return ((uint64_t)be32(p) << 32) | be32(p + 4);
}

/* ── JSON binary（InnoDB json_binary 格式）解码为 JSON 文本 ──
 * 直接照搬 MySQL 8.0 sql-common/json_binary.cc 的解析架构与决策逻辑，
 * 仅把输出目标（MySQL 的 Json_dom 对象）换成文本缓冲：
 *   parse_binary → parse_value → parse_scalar / parse_array_or_object
 *   Value::element() / Value::key() 的 value-entry/key-entry 读取
 *   inlined_type / read_variable_length / offset_size / key_entry_size /
 *   value_entry_size 原样保留（offset 相对容器数据起点，整数字段小端）。
 * 文本化（转义/opaque base64）对应 sql/field.cc Field_json 的输出形式。 */
#define JBY_SMALL_OBJECT 0x0
#define JBY_LARGE_OBJECT 0x1
#define JBY_SMALL_ARRAY 0x2
#define JBY_LARGE_ARRAY 0x3
#define JBY_LITERAL 0x4
#define JBY_INT16 0x5
#define JBY_UINT16 0x6
#define JBY_INT32 0x7
#define JBY_UINT32 0x8
#define JBY_INT64 0x9
#define JBY_UINT64 0xA
#define JBY_DOUBLE 0xB
#define JBY_STRING 0xC
#define JBY_OPAQUE 0xF
#define JBY_NULL_LITERAL 0x0
#define JBY_TRUE_LITERAL 0x1
#define JBY_FALSE_LITERAL 0x2
#define JBY_SMALL_OFFSET_SIZE 2
#define JBY_LARGE_OFFSET_SIZE 4
#define JBY_KEY_ENTRY_SIZE_SMALL (2 + JBY_SMALL_OFFSET_SIZE)
#define JBY_KEY_ENTRY_SIZE_LARGE (2 + JBY_LARGE_OFFSET_SIZE)
#define JBY_VALUE_ENTRY_SIZE_SMALL (1 + JBY_SMALL_OFFSET_SIZE)
#define JBY_VALUE_ENTRY_SIZE_LARGE (1 + JBY_LARGE_OFFSET_SIZE)

/* MySQL 类型枚举（json_binary::Value::enum_type） */
enum { JSONT_ERROR = 0, JSONT_OBJECT, JSONT_ARRAY, JSONT_STRING,
       JSONT_LITERAL_NULL, JSONT_LITERAL_TRUE, JSONT_LITERAL_FALSE,
       JSONT_INT, JSONT_UINT, JSONT_DOUBLE, JSONT_OPAQUE };

/* 轻量 Value：关联到文档数据，m_data 指向容器/标量数据起点 */
/* 文本输出上下文 */
typedef struct {
  char *out;
  size_t cap;
  size_t used;
} JOut;

typedef struct {
  int type;               /* JSONT_* */
  const uint8_t *m_data;  /* 容器：count 起点；标量：数据起点 */
  size_t m_length;        /* 本值可读字节上限 */
  size_t m_element_count; /* 容器元素数；0 需另判 */
  bool m_large;           /* large 存储格式 */
} JValue;

/* base64（Opaque 值文本化，对应 MySQL base64_encode） */
static const char *jb64t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
static void jb_base64(const uint8_t *d, size_t n, JOut *o) {
  size_t i = 0;
  while (i + 2 < n && o->cap - o->used >= 4) {
    uint32_t v = (d[i] << 16) | (d[i + 1] << 8) | d[i + 2];
    o->out[o->used++] = jb64t[(v >> 18) & 63];
    o->out[o->used++] = jb64t[(v >> 12) & 63];
    o->out[o->used++] = jb64t[(v >> 6) & 63];
    o->out[o->used++] = jb64t[v & 63];
    i += 3;
  }
  if (i + 1 == n && o->cap - o->used >= 4) {
    uint32_t v = d[i] << 16;
    o->out[o->used++] = jb64t[(v >> 18) & 63];
    o->out[o->used++] = jb64t[(v >> 12) & 63];
    o->out[o->used++] = '='; o->out[o->used++] = '=';
  } else if (i < n && o->cap - o->used >= 4) {
    uint32_t v = (d[i] << 16) | (d[i + 1] << 8);
    o->out[o->used++] = jb64t[(v >> 18) & 63];
    o->out[o->used++] = jb64t[(v >> 12) & 63];
    o->out[o->used++] = jb64t[(v >> 6) & 63];
    o->out[o->used++] = '=';
  }
}

/* 双引号字符串转义输出（对应 json_dom.cc double_quote/escape_character） */
static void jb_quote(const uint8_t *s, size_t n, JOut *o) {
  const char *hex = "0123456789abcdef";
  if (o->cap - o->used < n + 2) return;
  o->out[o->used++] = '"';
  for (size_t i = 0; i < n; i++) {
    unsigned char c = s[i];
    if (c == '"' || c == '\\') {
      if (o->cap - o->used < 2) return;
      o->out[o->used++] = '\\'; o->out[o->used++] = (char)c;
    } else if (c == '\b') { o->out[o->used++] = '\\'; o->out[o->used++] = 'b'; }
    else if (c == '\t') { o->out[o->used++] = '\\'; o->out[o->used++] = 't'; }
    else if (c == '\n') { o->out[o->used++] = '\\'; o->out[o->used++] = 'n'; }
    else if (c == '\f') { o->out[o->used++] = '\\'; o->out[o->used++] = 'f'; }
    else if (c == '\r') { o->out[o->used++] = '\\'; o->out[o->used++] = 'r'; }
    else if (c <= 0x1f) {
      if (o->cap - o->used < 6) return;
      o->out[o->used++] = '\\'; o->out[o->used++] = 'u'; o->out[o->used++] = '0'; o->out[o->used++] = '0';
      o->out[o->used++] = hex[(c >> 4) & 0xf]; o->out[o->used++] = hex[c & 0xf];
    } else {
      if (o->cap - o->used < 1) return;
      o->out[o->used++] = (char)c;
    }
  }
  if (o->cap - o->used < 1) return;
  o->out[o->used++] = '"';
}

static inline int jb_is_error(const JValue *v) { return v->type == JSONT_ERROR; }
static uint8_t jb_offset_size(bool large) { return large ? JBY_LARGE_OFFSET_SIZE : JBY_SMALL_OFFSET_SIZE; }
static uint8_t jb_key_entry_size(bool large) { return large ? JBY_KEY_ENTRY_SIZE_LARGE : JBY_KEY_ENTRY_SIZE_SMALL; }
static uint8_t jb_value_entry_size(bool large) { return large ? JBY_VALUE_ENTRY_SIZE_LARGE : JBY_VALUE_ENTRY_SIZE_SMALL; }

static inline uint16_t jle16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static inline uint32_t jle32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static inline uint64_t jle64(const uint8_t *p) {
  return (uint64_t)jle32(p) | ((uint64_t)jle32(p + 4) << 32);
}
static int64_t jle_signed(const uint8_t *p, int n) {
  uint64_t v = jle64(p);
  switch (n) {
    case 2: v = (uint16_t)v; if (v & 0x8000) v |= ~0xFFFFULL; break;
    case 4: v = (uint32_t)v; if (v & 0x80000000U) v |= ~0xFFFFFFFFULL; break;
    default: break; /* 8 */
  }
  return (int64_t)v;
}
static double jle_double(const uint8_t *p) {
  uint64_t bits = jle64(p); double d; memcpy(&d, &bits, 8); return d;
}

/* 变长长度：MySQL read_variable_length 语义（7bit 小端，最高位续续） */
static bool jb_read_variable_length(const uint8_t *data, size_t data_length,
                                    size_t off, uint32_t *length, uint8_t *num) {
  size_t i;
  size_t max_bytes = data_length < 5 ? data_length : 5;
  uint32_t len = 0;
  for (i = 0; i < max_bytes; i++) {
    len |= (uint32_t)(data[off + i] & 0x7f) << (7 * i);
    if ((data[off + i] & 0x80) == 0) { *num = (uint8_t)(i + 1); *length = len; return false; }
  }
  return true;
}

/* 一个值是否会被内联进 value entry（MySQL inlined_type 逐字镜像） */
static bool jb_inlined_type(uint8_t type, bool large) {
  switch (type) {
    case JBY_LITERAL: case JBY_INT16: case JBY_UINT16: return true;
    case JBY_INT32: case JBY_UINT32: return large;
    default: return false;
  }
}

/* 标量解析（MySQL parse_scalar 逐字镜像，输出到文本） */
static JValue jb_parse_scalar(uint8_t type, const uint8_t *data, size_t len,
                              JOut *o) {
  JValue v; v.type = JSONT_ERROR;
  char *p = o->out + o->used;
  size_t avail = o->cap - o->used;
  switch (type) {
    case JBY_LITERAL:
      if (len < 1) { v.type = JSONT_ERROR; return v; }
      switch (data[0]) {
        case JBY_NULL_LITERAL: v.type = JSONT_LITERAL_NULL;
          if (avail >= 4) { memcpy(p, "null", 4); o->used += 4; } break;
        case JBY_TRUE_LITERAL: v.type = JSONT_LITERAL_TRUE;
          if (avail >= 4) { memcpy(p, "true", 4); o->used += 4; } break;
        case JBY_FALSE_LITERAL: v.type = JSONT_LITERAL_FALSE;
          if (avail >= 5) { memcpy(p, "false", 5); o->used += 5; } break;
        default: v.type = JSONT_ERROR; break;
      }
      break;
    case JBY_INT16:
      if (len < 2) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_INT; o->used += (size_t)sprintf(p, "%lld", (long long)jle_signed(data, 2)); break;
    case JBY_INT32:
      if (len < 4) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_INT; o->used += (size_t)sprintf(p, "%lld", (long long)jle_signed(data, 4)); break;
    case JBY_INT64:
      if (len < 8) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_INT; o->used += (size_t)sprintf(p, "%lld", (long long)(long long)jle_signed(data, 8)); break;
    case JBY_UINT16:
      if (len < 2) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_UINT; o->used += (size_t)sprintf(p, "%llu", (unsigned long long)jle16(data)); break;
    case JBY_UINT32:
      if (len < 4) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_UINT; o->used += (size_t)sprintf(p, "%llu", (unsigned long long)jle32(data)); break;
    case JBY_UINT64:
      if (len < 8) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_UINT; o->used += (size_t)sprintf(p, "%llu", (unsigned long long)jle64(data)); break;
    case JBY_DOUBLE: {
      if (len < 8) { v.type = JSONT_ERROR; break; }
      v.type = JSONT_DOUBLE;
      double d = jle_double(data);
      /* my_gcvt 输出：整数型 double 不带小数点（近似 .0） */
      if (d == (double)(long long)d && d == d && d != (double)0x7ff8000000000000ULL)
        o->used += (size_t)sprintf(p, "%.0f", d);
      else
        o->used += (size_t)sprintf(p, "%.15g", d);
      break;
    }
    case JBY_STRING: {
      uint32_t str_len; uint8_t n;
      if (jb_read_variable_length(data, len, 0, &str_len, &n)) { v.type = JSONT_ERROR; break; }
      if (len < (size_t)n + str_len) { v.type = JSONT_ERROR; break; }
      jb_quote(data + n, str_len, o); v.type = JSONT_STRING;
      break;
    }
    case JBY_OPAQUE: {
      if (len < 1) { v.type = JSONT_ERROR; break; }
      uint8_t type_byte = data[0];
      uint32_t val_len; uint8_t nn;
      if (jb_read_variable_length(data + 1, len - 1, 0, &val_len, &nn)) { v.type = JSONT_ERROR; break; }
      if (len < 1 + (size_t)nn + val_len) { v.type = JSONT_ERROR; break; }
      const char *pre = "base64:type";
      size_t pl = strlen(pre);
      if (o->cap - o->used >= pl + 1) {
        memcpy(o->out + o->used, pre, pl); o->used += pl;
        int w = sprintf(o->out + o->used, "%u:", type_byte);
        o->used += (size_t)(w < 0 ? 0 : w);
        jb_base64(data + 1 + nn, val_len, o);
      }
      v.type = JSONT_OPAQUE;
      break;
    }
    default: v.type = JSONT_ERROR; break;
  }
  return v;
}

/* 数组/对象解析（MySQL parse_array_or_object → Value 构造，逐字镜像） */
static JValue jb_parse_array_or_object(int arrtype, const uint8_t *data,
                                       size_t len, bool large, JOut *o);
static JValue jb_parse_value(uint8_t type, const uint8_t *data, size_t len, JOut *o);

/* 容器值元素定位：value entry offset（MySQL Value::value_entry_offset） */
static size_t jb_value_entry_offset(const JValue *c, size_t pos) {
  size_t off = 2 * jb_offset_size(c->m_large);
  if (c->type == JSONT_OBJECT)
    off += c->m_element_count * jb_key_entry_size(c->m_large);
  return off + jb_value_entry_size(c->m_large) * pos;
}
static size_t jb_key_entry_offset(const JValue *c, size_t pos) {
  return 2 * jb_offset_size(c->m_large) + jb_key_entry_size(c->m_large) * pos;
}

/* MySQL Value::element() 逐字镜像：读 value entry，内联或按 offset 递归 */
static JValue jb_element(const JValue *c, size_t pos, JOut *o) {
  JValue err; err.type = JSONT_ERROR;
  if (pos >= c->m_element_count) return err;
  bool large = c->m_large;
  uint8_t es = jb_value_entry_size(large);
  size_t eo = jb_value_entry_offset(c, pos);
  uint8_t type = c->m_data[eo];
  if (jb_inlined_type(type, large))
    return jb_parse_scalar(type, c->m_data + eo + 1, es - 1, o);
  uint32_t vo = large ? jle32(c->m_data + eo + 1) : jle16(c->m_data + eo + 1);
  if (c->m_length < vo || vo < eo + es) return err;
  return jb_parse_value(type, c->m_data + vo, c->m_length - vo, o);
}

/* MySQL Value::key() 逐字镜像：读 key entry 取键 */
static JValue jb_key(const JValue *c, size_t pos, JOut *o) {
  JValue err; err.type = JSONT_ERROR;
  if (pos >= c->m_element_count) return err;
  bool large = c->m_large;
  size_t oss = jb_offset_size(large);
  size_t kes = jb_key_entry_size(large);
  size_t ves = jb_value_entry_size(large);
  size_t eo = jb_key_entry_offset(c, pos);
  size_t ko = large ? (size_t)jle32(c->m_data + eo) : (size_t)jle16(c->m_data + eo);
  uint16_t kl = jle16(c->m_data + eo + oss);
  jb_quote(c->m_data + ko, kl, o);
  JValue v; v.type = JSONT_STRING; return v;
}

/* 对象/数组正文：逐元素渲染（对应 MySQL 的遍历 element()/key()） */
static int jb_render_container(const JValue *c, JOut *o) {
  bool large = c->m_large;
  if (c->type == JSONT_OBJECT) {
    if (o->cap - o->used < 1) return -1;
    o->out[o->used++] = '{';
    for (size_t i = 0; i < c->m_element_count; i++) {
      if (i) o->out[o->used++] = ',';
      jb_key(c, i, o);
      if (o->cap - o->used < 1) return -1;
      o->out[o->used++] = ':';
      JValue ev = jb_element(c, i, o);
      if (jb_is_error(&ev)) return -1;
    }
    o->out[o->used++] = '}';
  } else {
    if (o->cap - o->used < 1) return -1;
    o->out[o->used++] = '[';
    for (size_t i = 0; i < c->m_element_count; i++) {
      if (i) o->out[o->used++] = ',';
      JValue ev = jb_element(c, i, o);
      if (jb_is_error(&ev)) return -1;
    }
    o->out[o->used++] = ']';
  }
  return 0;
}

static JValue jb_parse_array_or_object(int arrtype, const uint8_t *data,
                                       size_t len, bool large, JOut *o) {
  JValue err; err.type = JSONT_ERROR;
  size_t oss = jb_offset_size(large);
  if (len < 2 * oss) return err;
  uint32_t ec = large ? jle32(data) : jle16(data);
  uint32_t bytes = large ? jle32(data + oss) : jle16(data + oss);
  if (bytes > len) return err;
  size_t hs = 2 * oss;
  if (arrtype == JSONT_OBJECT) hs += (size_t)ec * jb_key_entry_size(large);
  hs += (size_t)ec * jb_value_entry_size(large);
  if (hs > bytes) return err;
  JValue c;
  c.type = arrtype; c.m_data = data; c.m_length = bytes;
  c.m_element_count = ec; c.m_large = large;
  (void)oss;
  if (jb_render_container(&c, o)) { err.type = JSONT_ERROR; return err; }
  (void)ec; (void)bytes; (void)hs;
  return c;
}

static JValue jb_parse_value(uint8_t type, const uint8_t *data, size_t len, JOut *o) {
  switch (type) {
    case JBY_SMALL_OBJECT: return jb_parse_array_or_object(JSONT_OBJECT, data, len, false, o);
    case JBY_LARGE_OBJECT: return jb_parse_array_or_object(JSONT_OBJECT, data, len, true, o);
    case JBY_SMALL_ARRAY: return jb_parse_array_or_object(JSONT_ARRAY, data, len, false, o);
    case JBY_LARGE_ARRAY: return jb_parse_array_or_object(JSONT_ARRAY, data, len, true, o);
    default: return jb_parse_scalar(type, data, len, o);
  }
}

/* 将 JSON binary 文档渲染为文本。返回 0 成功；文本写入 out（需足够空间）。 */
static int json_to_text(const uint8_t *doc, size_t len, char *out, size_t cap) {
  JOut o = { out, cap, 0 };
  if (len == 0) { memcpy(out, "null", 4); return 0; }
  /* MySQL parse_binary：parse_value(doc[0], doc+1, len-1) */
  JValue v = jb_parse_value(doc[0], doc + 1, len - 1, &o);
  if (jb_is_error(&v)) return -1;
  out[o.used] = 0;
  return 0;
}

/* rec_init_offsets_comp_ordinary：计算各字段物理偏移
 * 备注：版本差异——本函数为 COMPACT/DYNAMIC 统一实现（5.6 COMPACT 与
 *  5.7/8.0/8.4 DYNAMIC 记录头与长度数组布局一致，AC-1 四版本实测通过）；
 *  版本差异不在记录层，而在：① 表定义来源（5.6/5.7 schema vs 8.0+ SDI，
 *  见 mysql_layout_from_schema_file / mysql_layout_from_ibd）；② off-page
 *  LOB 页格式（本实现仅 8.0.13+ 新版，见 read_lob）。DYNAMIC 与 COMPACT 的
 *  行外存储差别由变长字段 external 位（DATA_BIG_COL 2B 高位置 0x4000）表达，
 *  故同一套 offsets 计算即可覆盖四版本。 */
static int rec_offsets(const uint8_t *page, uint16_t org, const MysqlLayout *L,
                       ColSpec *out) {
  uint16_t nulls = org - 6;
  uint16_t lens = (uint16_t)(nulls - ((L->n_nullable + 7) / 8));
  uint16_t offs = 0;
  uint32_t null_mask = 1;
  for (uint16_t i = 0; i < L->n_fields; i++) {
    const MysqlField *f = &L->fields[i];
    if (f->nullable) {
      if (!(null_mask & 0xff)) { nulls--; null_mask = 1; }
      if (page[nulls] & null_mask) {
        null_mask <<= 1;
        out[i].kind = 1; out[i].off = 0; out[i].len = 0;
        continue;
      }
      null_mask <<= 1;
    }
    if (f->fixed && !f->is_big) {
      out[i].kind = 0; out[i].off = offs; out[i].len = f->fixed;
      offs += f->fixed;
    } else {
      uint16_t l = page[lens];
      lens--;
      if (f->is_big && (l & 0x80)) {
        l = (uint16_t)((l << 8) | page[lens]);
        lens--;
        uint8_t ext = (l & 0x4000) ? 1 : 0;
        out[i].kind = ext ? 4 : 3;
        out[i].off = offs; out[i].len = l & 0x3fff;
        offs += out[i].len;
      } else {
        out[i].kind = 2; out[i].off = offs; out[i].len = l;
        offs += l;
      }
    }
    if (f->sys) out[i].kind = 5;
  }
  return 0;
}

static inline int64_t dec_signed(const uint8_t *b, uint16_t off, uint16_t ln) {
  uint64_t v = 0;
  for (int i = 0; i < ln; i++) v = (v << 8) | b[off + i];
  v ^= (1ULL << (8 * ln - 1));
  /* 翻转后按 ln 位宽符号扩展（0x8000 在 16 位 = -32768 而非 32768） */
  int64_t sv = (int64_t)v;
  if (sv & (1LL << (8 * ln - 1))) sv -= (1LL << (8 * ln));
  return sv;
}

/* decimal2bin → unscaled 值（注意：scale 位为“分”仅当 scale=2） */
static int64_t dec_decimal(const uint8_t *b, uint16_t off, uint16_t size,
                           uint16_t precision, uint8_t scale) {
  int intg = (int)precision - scale;
  int i0 = intg / 9, ix = intg - i0 * 9;
  int f0 = scale / 9, fx = scale - f0 * 9;
  int ihi = d2b(ix), isize = i0 * 4 + ihi;
  uint8_t raw[64];
  if (size > 64) size = 64;
  memcpy(raw, b + off, size);
  int neg = !(raw[0] & 0x80);
  if (neg) for (int i = 0; i < size; i++) raw[i] = (uint8_t)~raw[i];
  raw[0] &= 0x7f;
  /* 整数段：先 ihi 字节放 ix 位数，再 i0 个 4B 9位组 */
  uint64_t vint = 0;
  int pos = 0;
  for (int j = 0; j < ihi; j++) vint = (vint << 8) | raw[pos++];
  if (i0) {
    for (int j = 0; j < i0; j++) {
      vint = vint * 1000000000ULL + be32(raw + pos);
      pos += 4;
    }
  }
  /* i0==0 时 vint 已是完整的 ix 位整数（存于 ihi 字节），无需补零 */
  uint64_t frac = 0;
  for (int j = 0; j < f0; j++) {
    frac = frac * 1000000000ULL + be32(raw + pos);
    pos += 4;
  }
  if (fx) {
    uint32_t fb = 0;
    for (int j = 0; j < d2b(fx); j++) fb = (fb << 8) | raw[pos++];
    frac = frac * 1ULL + fb;
  }
  uint64_t unscaled = vint * 1ULL;
  for (int j = 0; j < scale; j++) unscaled *= 10;
  unscaled += frac;
  return neg ? -(int64_t)unscaled : (int64_t)unscaled;
}

/* DATETIME2/TIMESTAMP2 → epoch 微秒（本地时区按 UTC 处理，timegm） */
static int64_t dec_datetime(const uint8_t *b, uint16_t off, uint8_t base,
                            uint8_t fsp) {
  uint64_t v = 0;
  for (int i = 0; i < base; i++) v = (v << 8) | b[off + i];
  v ^= (1ULL << (8 * base - 1));
  uint64_t ym = v >> 22;
  struct tm t0;
  memset(&t0, 0, sizeof(t0));
  t0.tm_year = (int)(ym / 13) - 1900;
  t0.tm_mon = (int)(ym % 13) - 1;
  t0.tm_mday = (int)((v >> 17) & 31);
  t0.tm_hour = (int)((v >> 12) & 31);
  t0.tm_min = (int)((v >> 6) & 63);
  t0.tm_sec = (int)(v & 63);
  t0.tm_isdst = 0;
  time_t epoch = timegm(&t0);
  uint32_t us = 0;
  int fl = fsp_bytes(fsp);
  if (fl) {
    for (int i = 0; i < fl; i++) us = (us << 8) | b[off + base + i];
  }
  /* MySQL my_datetime_packed_to_binary 的 frac 缩放：
     dec1/2(1B)=微秒/10000, dec3/4(2B)=微秒/100, dec5/6(3B)=微秒原值 */
  if (fl == 1) us *= 10000;
  else if (fl == 2) us *= 100;
  return (int64_t)epoch * 1000000LL + us;
}

/* 页压缩(FIL_PAGE_COMPRESSED=14)解压为普通页。
 * 控制信息 V1(fil0types.h): version@26 u8, alg@27 u8(1=zlib),
 *   orig_type@28 u16, orig_size@30 u16, comp_size@32 u16;
 * zlib 流起始于 FIL_PAGE_DATA(38) 起 comp_size 字节, 目标 orig_size 字节,
 * 解压后与 38B 头拼接恢复整页。返回 0 成功, -1 失败。 */
static int page_zip_decompress(const uint8_t *pg, uint8_t *out) {
  const uint8_t version = pg[26];
  const uint16_t comp_size = be16(pg + 32);
  const uint16_t orig_size = be16(pg + 30);
  const uint16_t orig_type = be16(pg + 28);
  if (version != 1 || pg[27] != 1) return -1; /* 仅 zlib / V1 控制信息 */
  if (comp_size > MYSQL_PS || orig_size > MYSQL_PS - 38) return -1;
  memcpy(out, pg, 38); /* 保留页头(含压缩控制字段, 下面修正) */
  uLongf dlen = orig_size;
  if (uncompress(out + 38, &dlen, pg + 38, comp_size) != Z_OK) return -1;
  /* 恢复原始页类型, 清零压缩控制字段(FIL_PAGE_FILE_FLUSH_LSN 区) */
  out[24] = (uint8_t)(orig_type >> 8);
  out[25] = (uint8_t)(orig_type & 0xFF);
  memset(out + 26, 0, 8);
  return 0;
}

/* 解码单个字段到 cell */
static int decode_field(const uint8_t *page, uint16_t org, const ColSpec *cs,
                        const MysqlField *f, const uint8_t *map, size_t map_len,
                        MysqlCell *cell, char *strbuf, size_t strbuf_cap,
                        size_t *strbuf_used) {
  cell->kind = 0;
  cell->i64 = 0;
  cell->off = 0;
  cell->len = 0;
  if (cs->kind == 1) { cell->kind = 0; return 0; } /* NULL */
  const uint8_t *src = page + org + cs->off;
  uint16_t ln = cs->len;

  if (f->sys) {
    cell->kind = 1;
    cell->i64 = 0;
    for (int i = 0; i < ln; i++) cell->i64 = (cell->i64 << 8) | src[i];
    return 0;
  }
  if (cs->kind == 4) {
    /* 外部 LOB：20B REF */
    const uint8_t *ref = src;
    uint16_t pageno = (uint16_t)be32(ref + 4);
    uint32_t llen = 0;
    if (mysql_lob_read(map, map_len, pageno, (uint8_t *)strbuf + *strbuf_used,
                 strbuf_cap - *strbuf_used, &llen) != 0) return -1;
    cell->kind = 3;
    cell->off = (uint32_t)*strbuf_used;
    cell->len = llen;
    *strbuf_used += llen;
    return 0;
  }

  switch (f->mtype) {
    case MF_INT:
      cell->kind = 1;
      if (f->is_unsigned) {
        /* UNSIGNED 整型：大端直读无符号位翻转 */
        uint64_t uv = 0;
        for (int i = 0; i < ln; i++) uv = (uv << 8) | src[i];
        cell->i64 = (int64_t)uv;
      } else if (f->dd_type == 22) {
        /* ENUM：无符号 index，映射为成员字符串（Field_enum::val_str） */
        uint64_t ev = 0;
        for (int i = 0; i < ln; i++) ev = (ev << 8) | src[i];
        if (ev > 0 && ev <= f->n_enum && f->enum_vals && f->enum_vals[ev]) {
          const char *vs = f->enum_vals[ev];
          int vlen = (int)strlen(vs);
          if (*strbuf_used + vlen > strbuf_cap) return -1;
          memcpy(strbuf + *strbuf_used, vs, (size_t)vlen);
          cell->kind = 3;
          cell->off = (uint32_t)*strbuf_used;
          cell->len = vlen;
          *strbuf_used += vlen;
        } else {
          /* index 0 或超界 → 空字符串（MySQL 语义） */
          cell->kind = 3;
          cell->off = (uint32_t)*strbuf_used;
          cell->len = 0;
        }
      } else if (f->dd_type == 23) {
        /* SET：位图，bit i → enum_vals[i]（Field_set::val_str，index 从 0 起） */
        uint64_t sv = 0;
        for (int i = 0; i < ln; i++) sv = (sv << 8) | src[i];
        cell->kind = 3;
        cell->off = (uint32_t)*strbuf_used;
        cell->len = 0;
        uint64_t bit = sv;
        for (uint16_t i = 0; bit && i < f->n_enum; i++, bit >>= 1) {
          if (bit & 1) {
            const char *vs = f->enum_vals[i + 1];
            int vlen = (int)strlen(vs);
            if (cell->len > 0) {
              if (*strbuf_used + cell->len + 1 > strbuf_cap) return -1;
              strbuf[*strbuf_used + cell->len++] = ',';
            }
            if (*strbuf_used + cell->len + vlen > strbuf_cap) return -1;
            memcpy(strbuf + *strbuf_used + cell->len, vs, (size_t)vlen);
            cell->len += vlen;
          }
        }
        *strbuf_used += cell->len;
      } else if (f->dd_type == 14) {
        /* YEAR：1B year-1900，无翻转 */
        cell->i64 = src[0] == 0 ? 0 : (int64_t)src[0] + 1900;
      } else {
        cell->i64 = dec_signed(page, org + cs->off, ln);
      }
      break;
    case MF_FLOAT: {
      float fv;
      memcpy(&fv, src, 4); /* InnoDB 按主机字节序存 FLOAT */
      cell->kind = 2;
      cell->f64 = (double)fv;
      break;
    }
    case MF_DOUBLE:
      cell->kind = 2;
      memcpy(&cell->f64, src, 8); /* 小端主机序，x86 直接拷贝 */
      break;
    case MF_DATE: {
      /* DATE 3B：InnoDB 按 DATA_INT 存储（符号位翻转）。
         tmp = (be24 ^ 0x800000) = day + month*32 + year*512 → epoch 微秒 */
      uint32_t tmp = (((uint32_t)src[0] << 16) | ((uint32_t)src[1] << 8) | src[2]) & 0x7fffff;
      struct tm t0;
      memset(&t0, 0, sizeof(t0));
      t0.tm_year = (int)(tmp / 512) - 1900;
      t0.tm_mon = (int)((tmp / 32) % 16) - 1;
      t0.tm_mday = (int)(tmp % 32);
      t0.tm_isdst = 0;
      cell->kind = 1;
      cell->i64 = (int64_t)timegm(&t0) * 1000000LL;
      break;
    }
    case MF_DECIMAL:
      cell->kind = 1;
      cell->i64 = dec_decimal(page, org + cs->off, ln, f->precision, f->scale);
      break;
    case MF_DATETIME2:
      cell->kind = 1;
      cell->i64 = dec_datetime(page, org + cs->off, 5, f->fsp);
      break;
    case MF_TIMESTAMP2: {
      /* TIMESTAMP：4B 大端秒（无符号，不翻转符号位）+ frac */
      uint32_t sec = be32(src);
      uint32_t us = 0;
      int fl = fsp_bytes(f->fsp);
      for (int i = 0; i < fl; i++) us = (us << 8) | src[4 + i];
      if (fl == 1) us *= 10000;
      else if (fl == 2) us *= 100;
      cell->kind = 1;
      cell->i64 = (int64_t)sec * 1000000LL + us;
      break;
    }
    case MF_TIME2: {
      /* TIME2 解码（MySQL my_time_packed_from_binary 语义）：
         int3 = TIMEF_INT_OFS(0x800000) + hms(hour<<12|min<<6|sec)，
         frac 按 fsp 字节数缩放（dec3/4 存微秒/100 → 解码×100），
         负值整体<0x800000，frac 反向补码（0x10000-frac） */
      int64_t bin = 0;
      int fl2 = fsp_bytes(f->fsp);
      int nbytes = 3 + fl2;
      for (int i = 0; i < nbytes; i++) bin = (bin << 8) | src[i];
      int64_t intv = bin >> (8 * fl2);           /* 高 3 字节 = int3 */
      int64_t intpart = intv - 0x800000;          /* 有符号 hms */
      int64_t fraw = bin & ((1LL << (8 * fl2)) - 1); /* 尾 frac 字节 */
      int64_t hms;
      int64_t frac;
      if (intpart >= 0) {
        hms = intpart;
        frac = fraw;
        if (fl2 == 1) frac *= 10000;
        else if (fl2 == 2) frac *= 100;
        /* fl2==3 为微秒原值 */
      } else {
        /* 负值（源码 my_time_packed_from_binary case3/4 语义，
           InnoDB TIME2 对 3B+frac 布局统一适用）：
           intpart++（借位到整秒）；frac 从 0x100^len 反向补码取绝对值 */
        int64_t neg_int = intpart + 1;
        hms = -neg_int;
        if (fl2 == 1) frac = (0x100 - fraw) * 10000;
        else if (fl2 == 2) frac = (0x10000 - fraw) * 100;
        else if (fl2 == 3) frac = 0x1000000 - fraw;
      }
      int64_t sec = (hms >> 12) * 3600 + ((hms >> 6) & 63) * 60 + (hms & 63);
      int64_t micros = sec * 1000000LL + frac;
      if (intpart < 0) micros = -micros;
      cell->kind = 1;
      cell->i64 = micros;
      break;
    }
    case MF_JSON: {
      /* InnoDB json_binary → JSON 文本 */
      if (*strbuf_used + (size_t)ln * 8 + 64 > strbuf_cap) return -1;
      char tmp[65536];
      if (ln > 65000) return -1;
      memcpy(tmp, src, ln);
      char *out = strbuf + *strbuf_used;
      size_t cap = strbuf_cap - *strbuf_used;
      if (json_to_text((const uint8_t *)tmp, ln, out, cap) != 0) {
        /* 解析失败：原样输出（防丢失） */
        if (*strbuf_used + (size_t)ln > strbuf_cap) return -1;
        memcpy(strbuf + *strbuf_used, src, ln);
        cell->kind = 3;
        cell->off = (uint32_t)*strbuf_used;
        cell->len = ln;
        *strbuf_used += ln;
        break;
      }
      cell->kind = 3;
      cell->off = (uint32_t)*strbuf_used;
      cell->len = (uint32_t)strlen(strbuf + *strbuf_used);
      *strbuf_used += cell->len;
      break;
    }
    case MF_STRING:
    {
      /* CHAR 定长 PAD SPACE：trim 尾部空格（MySQL CHAR 语义） */
      while (ln > 0 && src[ln - 1] == 0x20) ln--;
      if (*strbuf_used + ln > strbuf_cap) return -1;
      memcpy(strbuf + *strbuf_used, src, ln);
      cell->kind = 3;
      cell->off = (uint32_t)*strbuf_used;
      cell->len = ln;
      *strbuf_used += ln;
      break;
    }
    case MF_VARCHAR:
    case MF_BLOB:
    default:
      if (*strbuf_used + ln > strbuf_cap) return -1;
      memcpy(strbuf + *strbuf_used, src, ln);
      cell->kind = 3;
      cell->off = (uint32_t)*strbuf_used;
      cell->len = ln;
      *strbuf_used += ln;
      break;
  }
  return 0;
}

/* 从 .ibd 物理页解析记录，填充 cells（每行 n_fields 个连续 cell）。
 * 返回本批行数。 */
size_t mysql_parse_pages_range(const char *path, const MysqlLayout *L,
                               MysqlCell *cells, size_t n_fields, size_t max_rows,
                               MysqlCur *cur, char *strbuf, size_t strbuf_cap,
                               size_t *strbuf_used, uint64_t *leaf_pages,
                               uint64_t *nonleaf_pages, uint64_t *other_pages) {
  if (!cur->map) {
    cur->fd = open(path, O_RDONLY);
    if (cur->fd < 0) return 0;
    struct stat st;
    if (fstat(cur->fd, &st) != 0) return 0;
    cur->map_len = (size_t)st.st_size;
    cur->map = (uint8_t *)mmap(NULL, cur->map_len, PROT_READ, MAP_PRIVATE, cur->fd, 0);
    if (cur->map == MAP_FAILED) {
      cur->map = NULL;
      return 0;
    }
  }
  size_t n_pages = cur->map_len / MYSQL_PS;
  size_t total = 0;

  while (total < max_rows && cur->page_idx < n_pages) {
    const uint8_t *page = cur->map + (size_t)cur->page_idx * MYSQL_PS;
    uint32_t ftype = be16(page + 24);
    uint8_t dec[16384];
    if (ftype == 14) { /* FIL_PAGE_COMPRESSED: 先解压再按普通页处理 */
      if (page_zip_decompress(page, dec) != 0) { cur->page_idx++; continue; }
      page = dec;
      ftype = be16(page + 24);
    }
    uint32_t level = be16(page + PAGE_LEVEL_OFF);
    uint32_t nrecs = be16(page + PAGE_N_RECS_OFF);

    if (ftype == FIL_PAGE_TYPE_INDEX && level == 0) {
      (*leaf_pages)++;
      uint16_t org = PAGE_NEW_INFIMUM + (int16_t)be16(page + PAGE_NEW_INFIMUM - 2);
      uint32_t idx = 0;
      ColSpec specs[128];
      while (idx < nrecs && total < max_rows) {
        if (org >= MYSQL_PS) break;
        if (idx >= cur->consumed) {
          /* 过滤 delete-mark（REC_INFO_DELETED_FLAG 0x20，byte0 bit5） */
          if (!((page[org - 5] >> 5) & 1)) {
            rec_offsets(page, org, L, specs);
            MysqlCell *row_cells = cells + total * n_fields;
            int ok = 1;
            for (uint16_t f = 0; f < L->n_fields; f++) {
              if (decode_field(page, org, &specs[f], &L->fields[f], cur->map,
                               cur->map_len, &row_cells[f], strbuf, strbuf_cap,
                               strbuf_used) != 0) {
                ok = 0;
                break;
              }
            }
            if (!ok) break;
            total++;
          }
        }
        org += (int16_t)be16(page + org - 2);
        idx++;
      }
      if (idx >= nrecs) cur->consumed = 0;
    } else if (ftype == FIL_PAGE_TYPE_INDEX) {
      (*nonleaf_pages)++;
    } else {
      (*other_pages)++;
    }
    cur->page_idx++;
  }
  return total;
}

void mysql_parse_pages_close(MysqlCur *cur) {
  if (cur->map && !cur->plain) munmap(cur->map, cur->map_len);
  if (cur->fd >= 0) close(cur->fd);
  cur->map = NULL;
  cur->fd = -1;
}
