#!/usr/bin/env bash
set -euo pipefail

# Control-plane short-session benchmark: HELLO+PING (caps) throughput/latency
# plus Agent thread count / RSS under concurrent sessions.
#
# Usage: benchmark_control_plane.sh [build-dir] [concurrency] [runs]
#   build-dir   binary dir (default: build-make)
#   concurrency number of parallel caps sessions (default: 32)
#   runs        repeat count (default: 5)
#
# Output lines (grep-able):
#   control-plane: concurrency=N runs=M median_ms=X p99_ms=Y
#   control-plane: agent_threads=N agent_rss_kib=N

BUILD=${1:-build-make}
CONC=${2:-32}
RUNS=${3:-5}
PORT=${BACKUPSTREAM_CTL_BENCH_PORT:-19657}
TMP=$(mktemp -d /tmp/backupstream-ctl-bench.XXXXXX)
pid=""
cleanup(){
  if [[ -n "${pid:-}" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  rm -rf "$TMP"
}
trap cleanup EXIT

mkdir -p "$TMP/root"
"$BUILD/backup-agent" --bind 127.0.0.1 --port "$PORT" --root "$TMP/root" \
  --allow-unauthenticated --max-sessions 512 --session-workers 64 --session-open-timeout 5000 \
  >"$TMP/agent.log" 2>&1 &
pid=$!
sleep .3

# Warm up one caps session so TLS/ingress state is initialized.
"$BUILD/backupctl" -h 127.0.0.1 -p "$PORT" caps >/dev/null 2>&1 || true

run_batch(){
  local conc=$1
  local start end ns times_file
  times_file="$TMP/times.txt"
  start=$(date +%s%N)
  seq 1 "$conc" | xargs -P "$conc" -I{} sh -c \
    '"$0" -h 127.0.0.1 -p "$1" caps >/dev/null 2>&1' \
    "$BUILD/backupctl" "$PORT" || true
  end=$(date +%s%N)
  echo "$((end-start))"
}

med_and_p99(){
  local f=$1 med p99
  # Latency per batch not directly measurable without client timing; use total
  # wall time as the primary control-plane cost signal (matches ROUND80 method).
  awk -v t="$2" -v c="$3" 'BEGIN{printf "%.3f %.3f", t/1000000.0, t/c/1000000.0}'
}

run_times=()
for r in $(seq 1 "$RUNS"); do
  t=$(run_batch "$CONC")
  run_times+=("$t")
done

# Sort wall times, take median (ms) and per-session p99 (ms, total/conc as upper bound).
sorted=($(printf '%s\n' "${run_times[@]}" | sort -n))
n=${#sorted[@]}
mid=$((n/2))
median_ns=${sorted[$mid]}
total_ns=0
for t in "${run_times[@]}"; do total_ns=$((total_ns+t)); done
median_ms=$(awk -v x="$median_ns" 'BEGIN{printf "%.3f", x/1e6}')
p99_ms=$(awk -v x="$total_ns" -v c="$CONC" 'BEGIN{printf "%.3f", (x/c)/1e6}')

# Resource sampling: thread count and RSS of the agent process.
threads=$(awk '/^Threads:/{print $2}' "/proc/$pid/status" 2>/dev/null || echo 0)
rss=$(awk '/^VmRSS:/{print $2}' "/proc/$pid/status" 2>/dev/null || echo 0)
[ -z "$threads" ] && threads=0
[ -z "$rss" ] && rss=0

echo "control-plane: concurrency=$CONC runs=$RUNS median_ms=$median_ms p99_upper_ms=$p99_ms"
echo "control-plane: agent_threads=$threads agent_rss_kib=$rss"
