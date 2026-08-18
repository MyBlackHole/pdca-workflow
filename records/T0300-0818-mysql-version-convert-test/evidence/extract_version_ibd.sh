#!/usr/bin/env bash
# T0300 版本转换测试 — 从 MySQL 四版本容器 volume 提取干净关闭的 .ibd
#
# 用法: bash bench/extract_version_ibd.sh [输出目录]
# 默认输出: evidence/mysql/versions/
#
# 流程: 每个容器 SET innodb_fast_shutdown=0 → mysqladmin shutdown(全量刷盘)
#       → podman unshare 拷贝 volume 内 poct25/poc_orders.ibd 并 chown 回当前用户
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/evidence/mysql/versions}"
VOL_ROOT=/home/black/.local/share/containers/storage/volumes

declare -A VOLS=(
  [t0250-mysql56]=3aa4d77b71862db5ddeedc29acf60e73a57218f7120ff0a8917e1c548b840587
  [t0250-mysql57]=f0f9373565169f5e0c775c8c8cbf17ccb7ac64fb162b79543e65e008e256daae
  [t0250-mysql8]=03418972f8f8d3c8d751924a72420642628e80abeaa7b96eabe336ee43c30e76
  [t0250-mysql84]=91270505628c7779b1895f9b01b339c3c69f743c5e7f3794cc86d988d4ffc7a4
)
declare -A VERS=( [t0250-mysql56]=56 [t0250-mysql57]=57 [t0250-mysql8]=80 [t0250-mysql84]=84 )

# 1. 干净关闭（innodb_fast_shutdown=0 全量刷盘）
for c in "${!VOLS[@]}"; do
  echo "== shutdown $c =="
  podman exec "$c" mysql -uroot -ptest -e "SET GLOBAL innodb_fast_shutdown=0;" 2>/dev/null
  podman exec "$c" mysqladmin -uroot -ptest shutdown 2>/dev/null || true
done
sleep 3

# 2. 提取 .ibd（podman unshare 以 root 访问 volume；chown 0:0 = 命名空间根
#    = 宿主调用者 uid，保证宿主侧 black 可读）
for c in "${!VOLS[@]}"; do
  v="${VOLS[$c]}"; ver="${VERS[$c]}"
  dst="$OUT/$ver"
  mkdir -p "$dst"
  echo "== extract $c -> $dst/poc_orders.ibd =="
  podman unshare sh -c "cp '$VOL_ROOT/$v/_data/poct25/poc_orders.ibd' '$dst/poc_orders.ibd' && chown 0:0 '$dst/poc_orders.ibd'"
  ls -la "$dst/poc_orders.ibd"
done
echo "== done =="