#!/usr/bin/env bash
# build_pgwrecover.sh — 离线 WAL 恢复引擎（多版本支持 T3971 / Slice2）
#
# 三层架构（最终版）：
#   L1 引擎核心  src/pg/pgwrecover.cpp + src/pg/l3/  — 版本无关 CLI/分发/中性 ABI
#   L3 抽象层    src/pg/l3/l3.h                       — 稳定 redo 中性 ABI（PgwRecoverVtbl）
#   L2 redo 实现 src/pg/versions/<ver>/ + src/pg/pg18 — 从 PG 源码拷贝、改写调 L3 的 redo 栈
#                                                 （一个 L2 可覆盖多版本；git 跟踪，diff 即版本差异）
#
# 单二进制 + 每版本 .so：
#   - 每版本 L2 编译进独立 libpgwrecover_<ver>.so（各自符号空间，隔离 PG 同名符号）。
#   - 主二进制 pgwrecover 仅持 L3 中性 ABI，运行时按 --version  dlopen 对应 .so。
#   - --version 缺省时由 pg_control 版本推导（16/17/18）；未知版本报错。
#
# 用法:
#   bash scripts/build_pgwrecover.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/src/pg"
L3="$ROOT/src/pg/l3"
OUT="$ROOT/build"
mkdir -p "$OUT"

# 版本清单（dir:libname:PG_BASE_VER:minimal）；minimal=1 时仅编 heap/btree/gin
# （Slice3 最小 L2，暴露可变面）。可扩展：新增版本只需加一行。
VERSIONS=(
  "src/pg/versions/pg16:16:1300:1"
  "src/pg/versions/pg18:18:1800:0"
)

# ---- 构建某版本的 .so（隔离符号空间） ----
build_so() {
  local VERSRC="$1" NAME="$2" BASEVER="$3" MINIMAL="$4"
  if [ ! -d "$VERSRC" ]; then echo "错误: 未找到 $VERSRC" >&2; exit 1; fi
  echo "== 构建 libpgwrecover_$NAME.so (VERSRC=$VERSRC, PG_BASE_VER=$BASEVER, minimal=$MINIMAL) =="

  local MINFLAGS=""
  [ "$MINIMAL" = "1" ] && MINFLAGS="-DPGW_MINIMAL"
  local CFLAGS="-O2 -std=gnu11 -DFRONTEND -DPG_BASE_VER=$BASEVER $MINFLAGS -fPIC \
    -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter -Wno-unused-variable \
    -ffunction-sections -fdata-sections \
    -I$VERSRC -I$L3 -I$VERSRC/port/linux -I$VERSRC/port -I$APP"

  local OBJS=""
  # 公共模块（编译两次，每次用版本特定 -I 路径）
  local COMMON="$APP/common"
  local COMMON_LIST="fe_buffer fe_nbt_aux fe_gin_aux pg_redo_btree \
           pg_lzcompress xlogreader snprintf"
  for c in $COMMON_LIST; do
    gcc $CFLAGS -c "$COMMON/$c.c" -o "$OUT/$c.o.$NAME"
    OBJS+=" $OUT/$c.o.$NAME"
  done

  # 版本特定 redo（仅架构性差异文件）
  local REDO_LIST=""
  if [ "$MINIMAL" = "1" ]; then
    REDO_LIST="fe_bufpage fe_heap_aux fe_memutils pg_redo_heap_official"
  else
    REDO_LIST="fe_bufpage fe_heap_aux fe_memutils pg_redo_heap_official \
           pg_redo_seq_official fe_hash_aux fe_spgist_aux fe_brin_aux fe_gist_aux"
  fi
  for c in $REDO_LIST; do
    if [ -f "$VERSRC/$c.c" ]; then
      gcc $CFLAGS -c "$VERSRC/$c.c" -o "$OUT/$c.o.$NAME"
      OBJS+=" $OUT/$c.o.$NAME"
    fi
  done

  # 应用层（按该版本头编译，符号封闭在 .so 内）
  for f in pg_wal_stub pg_control_reader wal_reader pg_replay pg_redo_dispatch; do
    gcc $CFLAGS -c "$APP/$f.c" -o "$OUT/$f.o.$NAME"
    OBJS+=" $OUT/$f.o.$NAME"
  done

  # .so 导出桩（引用本版本 pg_replay_run）
  gcc $CFLAGS -c "$L3/pg_redo_plugin.c" -o "$OUT/pg_redo_plugin.o.$NAME"
  OBJS+=" $OUT/pg_redo_plugin.o.$NAME"

  # 缺漏的后端公共符号桩（按版本头编译，封闭在 .so 内）
  gcc $CFLAGS -c "$APP/fe_mcxt_stub.c" -o "$OUT/fe_mcxt_stub.o.$NAME"
  OBJS+=" $OUT/fe_mcxt_stub.o.$NAME"

  gcc -shared -o "$OUT/libpgwrecover_$NAME.so" $OBJS \
    -Wl,--gc-sections -lpthread -llz4 -lzstd
  echo "== 完成: $OUT/libpgwrecover_$NAME.so =="
}

# ---- 构建版本无关引擎主二进制 ----
build_engine() {
  echo "== 构建 pgwrecover (版本无关引擎) =="
  local CXXFLAGS="-O2 -std=c++20 -Wall -Wextra -Wno-sign-compare \
    -Wno-unused-parameter -Wno-format-truncation \
    -ffunction-sections -fdata-sections -I$L3"
  local CFLAGS_ENG="-O2 -std=gnu11 -Wall -Wextra -Wno-sign-compare \
    -Wno-unused-parameter -Wno-format-truncation \
    -ffunction-sections -fdata-sections -I$L3"

  gcc $CFLAGS_ENG -fPIC -c "$L3/l3_replay.c" -o "$OUT/l3_replay.o"
  g++ $CXXFLAGS -fPIC -c "$APP/pgwrecover.cpp" -o "$OUT/pgwrecover.o"

  g++ $CXXFLAGS -o "$OUT/pgwrecover" "$OUT/l3_replay.o" "$OUT/pgwrecover.o" \
    -Wl,--gc-sections -Wl,-rpath="$OUT" -ldl
  echo "== 完成: $OUT/pgwrecover =="
}

for v in "${VERSIONS[@]}"; do
  IFS=':' read -r dir name basever minimal <<< "$v"
  build_so "$ROOT/$dir" "$name" "$basever" "$minimal"
done
build_engine
echo "== 已构建版本模块:"
ls -1 "$OUT"/libpgwrecover_*.so
