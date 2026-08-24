#!/usr/bin/env bash
# T0392 工具级多场景 e2e 测试
# 覆盖: aio-speed/rdbcomm 双算法、mTLS 开关、fail-closed、keygen 工具链
# 用法: test/e2e_tool_scenarios.sh [build_dir]
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
BIN=${1:-$ROOT/build/linux/x86_64/debug}
SPEED=$BIN/aio-speed
SPEEDD=$BIN/aio-speedd
RDBC=$BIN/rdbcomm
RDBCD=$BIN/rdbcommd
KEYGEN=$BIN/tls-keygen
CERT_DIR=/opt/aio/cfg/certs
WORK=/tmp/e2e_t0392.$$
LOG=$WORK/report.log
PASS=0; FAIL=0

cleanup() {
	for f in "$WORK"/srv_*.pid; do
		[ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null
	done
	rm -rf "$WORK"
}
trap cleanup EXIT
mkdir -p "$WORK"
echo "=== T0392 e2e 场景矩阵 $(date '+%F %T') ==="

check() { # check <场景号> <描述> <实际关键字断言结果 0/1> <证据>
	local id=$1 desc=$2 ok=$3 ev=$4
	if [ "$ok" = "0" ]; then
		echo "[PASS] $id $desc"; PASS=$((PASS+1))
	else
		echo "[FAIL] $id $desc | $ev"; FAIL=$((FAIL+1))
	fi
}

wait_port() { # wait_port <port> <timeout_s>
	local port=$1 t=${2:-10}
	for _ in $(seq "$t"); do
		ss -tln 2>/dev/null | grep -q ":$port " && return 0
		sleep 1
	done
	return 1
}

start_server() { # start_server <bin> <port> <extra args...>
	local bin=$1 port=$2; shift 2
	local wd="$WORK/wd_$port"; mkdir -p "$wd"
	( cd "$wd" && setsid nohup "$bin" -p "$port" "$@" \
		>"$WORK/srv_$port.log" 2>&1 </dev/null & echo $! >"$WORK/srv_$port.pid" )
	wait_port "$port" || return 1
}

# ---------- 服务端实例 ----------
start_server "$SPEEDD" 16611 --mtls-enable=1 \
	|| { echo "FATAL: aio-speedd 16611 启动失败"; exit 1; }
start_server "$SPEEDD" 16613 || { echo "FATAL: 明文 speedd 启动失败"; exit 1; }
RPC_TLS_CERT_DIR=/nonexistent start_server "$RDBCD" 16614 \
	|| { echo "FATAL: plain rdbcommd 启动失败"; exit 1; }
start_server "$RDBCD" 16610 --mtls-enable=1 \
	|| { echo "FATAL: mTLS rdbcommd 启动失败"; exit 1; }

run_cli() { # run_cli <timeout> <cmd...>
	local t=$1; shift
	timeout "$t" env RPC_TLS_CERT_DIR=$CERT_DIR "$@" 2>&1
	local rc=$?
	return $rc
}

# ---------- S1/S2: aio-speed 双算法 ----------
out=$(timeout 10 "$SPEED" -h 127.0.0.1 -p 16611 -c "echo sm4-e2e" --mtls-enable 1 2>&1); rc=$?
grep -q "sm4-e2e" <<<"$out"; r=$?
check S1 "aio-speed mTLS SM4(默认) 执行命令" $r "rc=$rc out=$out"

out=$(timeout 10 "$SPEED" -h 127.0.0.1 -p 16611 -c "echo aes-e2e" --mtls-enable 1 --tls-algorithm=TLS_AES_256_GCM_SHA384 2>&1); rc=$?
grep -q "aes-e2e" <<<"$out"; r=$?
check S2 "aio-speed mTLS AES 显式算法" $r "rc=$rc out=$out"

# ---------- S3: 明文对明文 ----------
out=$(timeout 10 "$SPEED" -h 127.0.0.1 -p 16613 -c "echo plain-e2e" 2>&1); rc=$?
grep -q "plain-e2e" <<<"$out"; r=$?
check S3 "aio-speed 明文客户端↔明文服务端" $r "rc=$rc out=$out"

# ---------- S4: fail-closed 明文连 mTLS ----------
out=$(timeout 10 "$SPEED" -h 127.0.0.1 -p 16611 -c "echo should-not-pass" 2>&1); rc=$?
{ [ $rc -ne 0 ] && ! grep -q "should-not-pass" <<<"$out"; }; r=$?
check S4 "明文客户端连 mTLS 服务端被拒(fail-closed)" $r "rc=$rc out=$out"

# ---------- S5: 无效算法名 ----------
out=$(timeout 10 "$SPEED" -h 127.0.0.1 -p 16611 -c "x" --mtls-enable 1 --tls-algorithm=TLS_BOGUS 2>&1); rc=$?
{ [ $rc -ne 0 ] && grep -qiE 'invalid|unknown|algorithm' <<<"$out"; }; r=$?
check S5 "无效算法名被拒" $r "rc=$rc out=$out"

# ---------- S6: 错误端口快速失败 ----------
t0=$(date +%s)
out=$(timeout 15 "$SPEED" -h 127.0.0.1 -p 16699 -c "x" 2>&1); rc=$?
t1=$(date +%s)
{ [ $rc -ne 0 ] && [ $((t1-t0)) -lt 12 ]; }; r=$?
check S6 "错误端口连接快速失败(<12s)" $r "rc=$rc dur=$((t1-t0))s"

# ---------- S7: rdbcomm mTLS（T0394 回归锚）----------
out=$(timeout 10 "$RDBC" -h 127.0.0.1 -p 16610 -c "echo rdb-mtls-e2e" --mtls-enable 1 2>&1); rc=$?
grep -q "rdb-mtls-e2e" <<<"$out"; r=$?
check S7 "rdbcomm mTLS SM4 升级并执行(T0394 回归)" $r "rc=$rc out=$out"

# ---------- S8: rdbcomm 明文 ----------
out=$(timeout 10 env RPC_TLS_CERT_DIR=/nonexistent "$RDBC" -h 127.0.0.1 -p 16614 -c "echo rdb-plain-e2e" 2>&1); rc=$?
grep -q "rdb-plain-e2e" <<<"$out"; r=$?
check S8 "rdbcomm 明文模式执行" $r "rc=$rc out=$out"

# ---------- S9: keygen 非法 CN ----------
out=$(timeout 10 "$KEYGEN" ca -n "Bad Space CN" -a sm2 -o "$WORK/kg" 2>&1); rc=$?
{ [ $rc -ne 0 ] && grep -q "invalid CN" <<<"$out"; }; r=$?
check S9 "keygen 拒绝含空格 CN 并提示(T0387)" $r "rc=$rc out=$out"

# ---------- S10: keygen 自包含目录 ----------
kgd="$WORK/kgdir"; rm -rf "$kgd"
timeout 10 "$KEYGEN" ca -n E2E_Test_CA -a sm2 -o "$kgd/ca" >/dev/null 2>&1 && \
timeout 10 "$KEYGEN" create -n E2E_Test_CA -a sm2 >/dev/null 2>&1 && \
timeout 10 "$KEYGEN" sign -n E2E_Test_CA -a sm2 \
	--ca-cert "$kgd/ca/sm2_ca.crt" --ca-key "$kgd/ca/sm2_ca.key" >/dev/null 2>&1; rc=$?
{ [ $rc -eq 0 ] && [ -f "$CERT_DIR/E2E_Test_CA/sm2_host.crt" ] && \
  [ -f "$CERT_DIR/E2E_Test_CA/sm2_ca.crt" ]; }; r=$?
check S10 "keygen sign -n 自包含目录(含 CA 拷贝,T0388)" $r "rc=$rc dir=$(ls "$CERT_DIR/E2E_Test_CA" 2>/dev/null | tr '\n' ',')"
rm -rf "$CERT_DIR/E2E_Test_CA"   # 清理验收产物，还原现网

# ---------- 汇总 ----------
echo "=== 汇总: PASS=$PASS FAIL=$FAIL ===" | tee -a "$LOG"
[ $FAIL -eq 0 ]
