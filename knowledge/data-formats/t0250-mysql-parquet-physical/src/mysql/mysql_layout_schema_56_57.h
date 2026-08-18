/*
 * mysql_layout_schema.h — MySQL 5.6/5.7 表定义布局（版本特性文件）。
 *
 * 版本背景：5.6/5.7 无 SDI 页（表定义存于外部 .frm），本文件从 CLI
 * --schema= 文本文件构建 MysqlLayout。8.0+ 请用 mysql_sdi_80.c（SDI 驱动）。
 * 文件即“5.6/5.7 版本特性”的唯一承载：新增旧版本支持只需改这里。
 */
#ifndef MYSQL_LAYOUT_SCHEMA_H
#define MYSQL_LAYOUT_SCHEMA_H

#include "mysql_sdi.h"

/* 从 schema 文件构建物理布局（5.6/5.7 无 SDI 时用）。返回 0 成功。 */
int mysql_layout_from_schema_file(const char *path, MysqlLayout *out);

#endif /* MYSQL_LAYOUT_SCHEMA_H */