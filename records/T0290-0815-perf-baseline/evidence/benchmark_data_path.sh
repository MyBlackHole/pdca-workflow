#!/usr/bin/env bash
set -euo pipefail

# Data-path benchmark: large regular-file PUT/GET throughput (MiB/s) plus
# Agent resource (threads / RSS) under a sustained single-file transfer.
#
# Usage: benchmark_data_path.sh [build-dir] [size-mib] [runs]
#   build-dir   binary dir (default: build-make)
#   size-mib    file size in MiB (default: 256)
#   runs        repeat count (default: 3)
#
# Output lines (grep-able):
#   data-path: size_mib=N runs=M put_median_mibps=X get_median_mibps=Y
#   data-path: agent_threads=N agent_rss_kib=N

BUILD=${1:-build-make}
SIZE_MB=${2:-256}
RUNS=${3:-3}
PORT=${BACKUPSTREAM_DATA_BENCH_PORT:-19663}
TMP=$(mktemp -d /tmp/backupstream-data-bench.XXXXXX)
pid=""
cleanup(){
  if [[ -n "${pid:-}" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  rm -rf "$TMP"
}
trap cleanup EXIT

mkdir -p "$TMP/root" "$TMP/work"
truncate -s "$((SIZE_MB*1024*1024))" "$TMP/work/source.bin"
printf 'backupstream-data-bench-begin\n' | dd of="$TMP/work/source.bin" bs=1 conv=notrunc status=none
printf 'backupstream-data-bench-end\n' | dd of="$TMP/work/source.bin" bs=1 seek="$((SIZE_MB*1024*1024-64))" conv=notrunc status=none

"$BUILD/backup-agent" --bind 127.0.0.1 --port "$PORT" --root "$TMP/root" \
  --allow-unauthenticated --max-sessions 128 --session-workers 64 \
  >"$TMP/agent.log" 2>&1 &
pid=$!
sleep .3

CTL=("$BUILD/backupctl" -h 127.0.0.1 -p "$PORT")

time_transfer(){
  local dir=$1
  local start end ns bytes
  bytes=$((SIZE_MB*1024*1024))
  start=$(date +%s%N)
  if [[ $dir == put ]]; then
    "${CTL[@]}" put --no-resume --no-sparse --no-checksum --durability none \
      "$TMP/work/source.bin" "/data-path.bin" >/dev/null
  else
    rm -f "$TMP/work/get.bin"
    "${CTL[@]}" get --no-resume --no-sparse --no-checksum --durability none \
      "/data-path.bin" "$TMP/work/get.bin" >/dev/null
  fi
  end=$(date +%s%N); ns=$((end-start))
  awk -v bytes="$bytes" -v ns="$ns" 'BEGIN{printf "%.2f", (bytes/1048576.0)/(ns/1e9)}'
}

put_times=()
get_times=()
for r in $(seq 1 "$RUNS"); do
  put_times+=("$(time_transfer put)")
  cmp -s "$TMP/work/source.bin" "$TMP/root/data-path.bin" || { echo "data-path: PUT mismatch" >&2; exit 1; }
  get_times+=("$(time_transfer get)")
  cmp -s "$TMP/work/source.bin" "$TMP/work/get.bin" || { echo "data-path: GET mismatch" >&2; exit 1; }
done

median_of(){
  local arr=("$@")
  local sorted n mid
  sorted=($(printf '%s\n' "${arr[@]}" | sort -n))
  n=${#sorted[@]}; mid=$((n/2))
  printf '%s' "${sorted[$mid]}"
}

put_med=$(median_of "${put_times[@]}")
get_med=$(median_of "${get_times[@]}")

threads=$(awk '/^Threads:/{print $2}' "/proc/$pid/status" 2>/dev/null || echo 0)
rss=$(awk '/^VmRSS:/{print $2}' "/proc/$pid/status" 2>/dev/null || echo 0)
[ -z "$threads" ] && threads=0
[ -z "$rss" ] && rss=0

echo "data-path: size_mib=$SIZE_MB runs=$RUNS put_median_mibps=$put_med get_median_mibps=$get_med"
echo "data-path: agent_threads=$threads agent_rss_kib=$rss"
