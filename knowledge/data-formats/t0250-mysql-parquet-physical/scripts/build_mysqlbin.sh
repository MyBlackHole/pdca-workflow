#!/usr/bin/env bash
# build_mysqlbin.sh — 编译 MySQL InnoDB 物理直读 → Parquet 工具（T0250）
# 依赖: Arrow C++（pyarrow 2500）
# 用法: bash scripts/build_mysqlbin.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build"
P=/home/black/Public/aio/Idea/Parquet/.venv/lib/python3.14/site-packages/pyarrow
ARROW_INC="$P/include"

mkdir -p "$OUT"

CFLAGS="-O2 -g -std=gnu11 -ffunction-sections -fdata-sections"
CXXFLAGS="-O2 -g -std=c++20 -ffunction-sections -fdata-sections -I$ARROW_INC"

echo "== 编译 tde_decrypt =="
g++ $CXXFLAGS -c "$ROOT/src/mysql/tde_decrypt.cpp" -o "$OUT/tde_decrypt.o"
echo "== 编译 mysql_sdi（8.0+ SDI 布局）=="
gcc $CFLAGS -c "$ROOT/src/mysql/mysql_sdi_80.c" -o "$OUT/mysql_sdi.o"
echo "== 编译 mysql_layout_schema_56_57（5.6/5.7 schema 布局）=="
gcc $CFLAGS -c "$ROOT/src/mysql/mysql_layout_schema_56_57.c" -o "$OUT/mysql_layout_schema.o"
echo "== 编译 mysql_lob_read_8013（8.0.13+ 新版 LOB）=="
gcc $CFLAGS -c "$ROOT/src/mysql/mysql_lob_read_8013.c" -o "$OUT/mysql_lob_read.o"
echo "== 编译 mysql_lob_legacy_pre8013（旧 BLOB 占位）=="
gcc $CFLAGS -c "$ROOT/src/mysql/mysql_lob_legacy_pre8013.c" -o "$OUT/mysql_lob_legacy.o"
echo "== 编译 mysql_parse_pages =="
gcc $CFLAGS -c "$ROOT/src/mysql/mysql_parse_pages.c" -o "$OUT/mysql_parse_pages.o"
g++ $CXXFLAGS -c "$ROOT/src/mysql/mysqlbin.cpp" -o "$OUT/mysqlbin.o"

echo "== 链接 mysqlbin =="
g++ $CXXFLAGS -o "$OUT/mysqlbin" \
  "$OUT/tde_decrypt.o" "$OUT/mysql_parse_pages.o" "$OUT/mysql_sdi.o" \
  "$OUT/mysql_layout_schema.o" "$OUT/mysql_lob_read.o" "$OUT/mysql_lob_legacy.o" \
  "$OUT/mysqlbin.o" \
  -L"$P" -Wl,-rpath,"$P" -Wl,--gc-sections \
  -l:libarrow.so.2500 -l:libparquet.so.2500 -lpthread -lz -lcrypto

echo "== 完成: $OUT/mysqlbin =="
