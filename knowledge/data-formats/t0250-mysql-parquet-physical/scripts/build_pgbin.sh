#!/usr/bin/env bash
# build_pgbin.sh — 编译 PG 物理直读 → Parquet 工具（T0250）
# 依赖: PG18.4 backend 源码文件（third_party/pg184/src/） + Arrow C++（pyarrow 2500）
# 用法: bash scripts/build_pgbin.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PGINC="$ROOT/third_party/pg184/include"
PGSRC="$ROOT/third_party/pg184/src"
OUT="$ROOT/build"
P=/home/black/Public/aio/Idea/Parquet/.venv/lib/python3.14/site-packages/pyarrow
ARROW_INC="$P/include"

mkdir -p "$OUT"

CFLAGS="-O2 -std=gnu11 -ffunction-sections -fdata-sections -I$PGINC -I$PGINC/port/linux -I$PGINC/port"
CXXFLAGS="-O2 -std=c++20 -ffunction-sections -fdata-sections -I$ARROW_INC"

echo "== 编译 PG backend 依赖对象 =="
# 本项目复制的 PG18.4 源码文件布局：
#   src/access/common/heaptuple.c, src/utils/mmgr/<mmgr>.c, src/snprintf.c
for f in "heaptuple:access/common" "mcxt:utils/mmgr" "aset:utils/mmgr" \
         "generation:utils/mmgr" "slab:utils/mmgr" "bump:utils/mmgr" \
         "alignedalloc:utils/mmgr"; do
  src=${f%%:*}; dir=${f##*:}
  gcc $CFLAGS -c "$PGSRC/$dir/$src.c" -o "$OUT/$src.o"
done
gcc $CFLAGS -c "$PGSRC/snprintf.c" -o "$OUT/pg_snprintf.o"

echo "== 编译本项目源码 =="
gcc $CFLAGS -c "$ROOT/src/pg/pg_heap_reader.c" -o "$OUT/pg_heap_reader.o"
gcc $CFLAGS -c "$ROOT/src/pg/pg_clog_reader.c" -o "$OUT/pg_clog_reader.o"
gcc $CFLAGS -c "$ROOT/src/pg/pg_clog_legacy.c" -o "$OUT/pg_clog_legacy.o"
gcc $CFLAGS -c "$ROOT/src/pg/stub_pg.c" -o "$OUT/stub_pg.o"
g++ $CXXFLAGS -c "$ROOT/src/pg/pgbin.cpp" -o "$OUT/pgbin.o"

echo "== 链接 pgbin =="
g++ $CXXFLAGS -o "$OUT/pgbin" \
  "$OUT/pg_heap_reader.o" "$OUT/pg_clog_reader.o" "$OUT/pg_clog_legacy.o" \
  "$OUT/heaptuple.o" "$OUT/mcxt.o" "$OUT/aset.o" "$OUT/generation.o" \
  "$OUT/slab.o" "$OUT/bump.o" "$OUT/alignedalloc.o" "$OUT/stub_pg.o" \
  "$OUT/pgbin.o" "$OUT/pg_snprintf.o" \
  -L"$P" -Wl,-rpath,"$P" -Wl,--gc-sections \
  -l:libarrow.so.2500 -l:libparquet.so.2500 -lpthread

echo "== 完成: $OUT/pgbin =="