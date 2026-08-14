/*
 * mysql_parse_pages.h — T0250 MySQL InnoDB 物理直读公共接口。
 *
 * 该接口由 mysqlbin.cpp（动态 schema，SDI 驱动）调用。
 * 每行每列解码为一个 MysqlCell（kind 标志区分数值/浮点/字符串）。
 */
#ifndef MYSQL_PARSE_PAGES_H
#define MYSQL_PARSE_PAGES_H

#include "mysql_sdi.h"

#include <stddef.h>
#include <stdint.h>

/* 解码后的统一单元格：kind 0 NULL, 1 整数/时间_us, 2 浮点, 3 字符串 */
typedef struct {
  uint8_t kind;
  int64_t i64;
  double f64;
  uint32_t off, len; /* kind==3 时指向调用方 strbuf */
} MysqlCell;

/* 页游标：跨 batch 保持当前物理页位置 */
typedef struct {
  uint32_t page_idx;
  uint16_t consumed;
  uint8_t *map;
  size_t map_len;
  int fd;
  int plain; /* 1 = map 指向外部明文缓冲(不 munmap), 0 = range 内部 mmap */
} MysqlCur;

/* 从 .ibd 解析最多 max_rows 条记录，cells 需 n_fields*max_rows 容量。
 * 返回实际行数；0 表示文件结束。 */
size_t mysql_parse_pages_range(const char *path, const MysqlLayout *L,
                               MysqlCell *cells, size_t n_fields, size_t max_rows,
                               MysqlCur *cur, char *strbuf, size_t strbuf_cap,
                               size_t *strbuf_used, uint64_t *leaf_pages,
                               uint64_t *nonleaf_pages, uint64_t *other_pages);

void mysql_parse_pages_close(MysqlCur *cur);

#endif /* MYSQL_PARSE_PAGES_H */