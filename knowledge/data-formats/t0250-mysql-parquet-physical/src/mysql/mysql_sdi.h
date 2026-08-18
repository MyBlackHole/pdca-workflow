/*
 * mysql_sdi.h — T0250 MySQL InnoDB 通用物理直读（SDI 驱动）公共类型。
 *
 * 从 .ibd 的 FIL_PAGE_SDI 页（zlib 压缩 JSON）提取权威表布局，
 * 替代硬编码 schema；字段语义照 InnoDB 源码（rem0rec.ic / data0type /
 * dict0dd.cc / row0mysql.cc），由 mysql_parse_pages.c 计算记录 offsets。
 */
#ifndef MYSQL_SDI_H
#define MYSQL_SDI_H

#include "mysql_versions.h"

#include <stddef.h>
#include <stdint.h>

#define MYSQL_PS 16384
#define PAGE_NEW_INFIMUM 99
#define PAGE_HEADER 38
#define PAGE_N_RECS_OFF (PAGE_HEADER + 16)
#define PAGE_LEVEL_OFF (PAGE_HEADER + 26)

/* 大端读取工具（解析公共依赖，多文件共用） */
static inline uint32_t be16(const uint8_t *p) { return ((uint32_t)p[0] << 8) | p[1]; }
static inline uint32_t be32(const uint8_t *p) {
  return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
         ((uint32_t)p[2] << 8) | p[3];
}

/* 布局构建公共工具（由 mysql_layout_schema.c 与 mysql_sdi.c 共用；
 * 依赖 SDI/表定义的类型元数据 → InnoDB data0type 语义映射） */
int map_mtype(int dd);
int d2b(int d);
int int_bytes(int dd);
int fsp_bytes(int fsp);

/* dd enum_column_types 的物理分类（与 data0type 对应） */
enum { MF_INT = 0, MF_FLOAT, MF_DOUBLE, MF_DECIMAL, MF_DATETIME2, MF_TIMESTAMP2,
       MF_TIME2, MF_STRING, MF_VARCHAR, MF_BLOB, MF_POINT, MF_DATE, MF_JSON, MF_UNKNOWN };

typedef struct {
  char *name;
  uint8_t dd_type; /* dd::enum_column_types 值 */
  uint8_t mtype;   /* 上表分类 */
  uint16_t fixed;  /* 定长字节数（0 = 变长） */
  uint8_t nullable;
  uint8_t is_big;      /* BLOB 或 fixed>255 → DATA_BIG_COL */
  uint8_t sys;         /* 0 普通列；1 DB_TRX_ID；2 DB_ROLL_PTR */
  uint16_t precision;  /* DECIMAL 总精度 */
  uint8_t scale;       /* DECIMAL 小数位 */
  uint8_t fsp;         /* DATETIME/TIMESTAMP/TIME 小数秒精度 */
  uint8_t is_bool;     /* tinyint(1) → BOOLEAN */
  uint8_t is_unsigned; /* BIGINT/INT UNSIGNED（无符号位翻转） */
  uint32_t charlen;    /* VARCHAR/CHAR 长度（字节） */
  uint16_t n_enum;     /* ENUM/SET 成员个数 */
  char **enum_vals;    /* ENUM/SET 成员值数组（index 1 起） */
} MysqlField;

typedef struct {
  uint16_t n_fields; /* 物理字段数（含系统列） */
  uint16_t n_nullable;
  uint16_t n_pk;       /* 主键列数（物理序前缀） */
  MysqlField *fields;  /* 物理字段序（主键 → 系统列 → 其余） */
} MysqlLayout;

/* 读取 .ibd 的 SDI 表定义，构建物理布局。返回 0 成功。 */
int mysql_layout_from_ibd(const uint8_t *map, size_t map_len, MysqlLayout *out);
/* 从 CLI schema 文件构建物理布局（5.6/5.7 无 SDI 时用）。返回 0 成功。 */
int mysql_layout_from_schema_file(const char *path, MysqlLayout *out);
void mysql_layout_free(MysqlLayout *l);

#endif /* MYSQL_SDI_H */
