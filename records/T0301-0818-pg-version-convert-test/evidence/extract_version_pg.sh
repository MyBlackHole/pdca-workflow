#!/usr/bin/env bash
# T0301 — PG 三版本 heap+CLOG 固化提取
#
# 用法: bash bench/extract_version_pg.sh [输出目录]
# 默认输出: evidence/pg/versions/
#
# 流程(每容器): CHECKPOINT 刷脏页 → pg_relation_filepath 定位 poc_orders heap
#   → podman unshare 拷贝 heap + CLOG 目录(9.6=pg_clog/, 11/18=pg_xact/)
#   → chown 0:0(命名空间根=宿主调用者)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/evidence/pg/versions}"
VOL_ROOT=/home/black/.local/share/containers/storage/volumes

declare -A VERS=( [t0301-pg96]=96 [t0301-pg11]=11 [t0216-pg]=18 )
declare -A CLDIR=( [t0301-pg96]=pg_clog [t0301-pg11]=pg_xact [t0216-pg]=pg_xact )

for c in "${!VERS[@]}"; do
  ver="${VERS[$c]}"; cl="${CLDIR[$c]}"
  echo "== $c (ver=$ver clog=$cl) =="
  podman exec "$c" psql -U test -d poct25 -c "CHECKPOINT;" >/dev/null 2>&1
  rel="$(podman exec "$c" psql -U test -d poct25 -tAc "SELECT pg_relation_filepath('poc_orders');")"
  rel="${rel//[$'\t\r\n']/}"
  src="$(podman inspect "$c" --format '{{range .Mounts}}{{.Source}}{{end}}')"
  pgdata="$(podman exec "$c" sh -c 'echo "$PGDATA"')"
  mntdest="$(podman inspect "$c" --format '{{range .Mounts}}{{.Destination}}{{end}}')"
  reltopgdata="${pgdata#$mntdest}"   # 容器 PGDATA 相对挂载点(空 或 /18/docker)
  base="$src$reltopgdata"
  echo "  heap: $rel  base: $base"
  mkdir -p "$OUT/$ver"
  podman unshare sh -c \
    "cp '$base/$rel' '$OUT/$ver/poc_orders_heap' && cp -r '$base/$cl' '$OUT/$ver/$cl' && chown -R 0:0 '$OUT/$ver'"
  ls -la "$OUT/$ver"
done
echo "== done =="