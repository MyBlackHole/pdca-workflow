#!/usr/bin/env bash
# tls-keygen 黑盒测试：覆盖错误码可读化（T0402 / T3989）。
# 不测实现细节，只验证 stderr 含路径+系统原因+错误码含义，而非裸数字。
set -u

BIN="${TLS_KEYGEN_BIN:-./build/linux/x86_64/release/tls-keygen}"
CERT_DIR="${TLS_KEYGEN_CERT_DIR:-/opt/aio/cfg/certs}"
KEY_PATH="$CERT_DIR/sm2_ca.key"
CERT_PATH="$CERT_DIR/sm2_ca.crt"

fail() { echo "FAIL: $1"; exit 1; }

# 准备：清掉默认目录，确保后续写失败场景干净可复现
rm -rf "$CERT_DIR"

echo "=== T1: 写失败应给出可读原因(路径+Permission denied+错误码含义) ==="
# 非 root 向 /root 下写密钥，触发 EACCES
OUT=$("$BIN" ca -n "MySM2RootCA" -a sm2 --key /root/tls_keygen_deny.key 2>&1)
RC=$?
echo "$OUT"
echo "exit=$RC"
echo "$OUT" | grep -q '/root/tls_keygen_deny.key' || fail "缺少目标路径"
echo "$OUT" | grep -qi 'Permission denied'        || fail "缺少系统原因(strerror)"
echo "$OUT" | grep -q 'failed to write output file' || fail "缺少错误码 -3 的含义短语"
echo "$OUT" | grep -qE '\(code: -3\)'            || fail "应保留 code: -3 便于脚本判定"
echo "T1 passed"

echo "=== T2: 成功路径 stdout 无回归 ==="
mkdir -p "$CERT_DIR"
OUT=$("$BIN" ca -n "MySM2RootCA" -a sm2 2>&1)
RC=$?
echo "$OUT"
[ "$RC" -eq 0 ] || fail "成功路径应退出 0"
echo "$OUT" | grep -q 'Creating CA (sm2)... done' || fail "成功文案应保留"
[ -f "$KEY_PATH" ] && [ -f "$CERT_PATH" ] || fail "应生成密钥与证书"
echo "T2 passed"

# === aio-oss server 启动失败显式化（T3990）===
OSS_BIN="${TLS_KEYGEN_BIN:+${TLS_KEYGEN_BIN%/tls-keygen}/aio-oss}"
OSS_BIN="${OSS_BIN:-./build/linux/x86_64/release/aio-oss}"
if [ -x "$OSS_BIN" ]; then
  echo "=== T3: oss --tls 无证书应给出可读错误并退出(非静默) ==="
  EMPTY_DIR=$(mktemp -d)
  OOUT=$("$OSS_BIN" server --store /tmp/oss-emulator-store --tls --cert-dir "$EMPTY_DIR" 2>&1)
  ORC=$?
  echo "$OOUT"
  echo "exit=$ORC"
  echo "$OOUT" | grep -q 'tls-keygen' || fail "缺少 tls-keygen 生成提示"
  echo "$OOUT" | grep -q 'ed25519_host.crt' || fail "缺少期望证书路径"
  [ "$ORC" -ne 0 ] || fail "应非零退出"
  echo "T3 passed"

  echo "=== T4: oss 绑定特权端口失败应显式化并退出(不挂起) ==="
  TOUT=$("$OSS_BIN" server --store /tmp/oss-emulator-store 2>&1)
  TRC=$?
  echo "$TOUT"
  echo "exit=$TRC"
  echo "$TOUT" | grep -qi 'failed to listen' || fail "缺少监听失败提示"
  [ "$TRC" -ne 0 ] || fail "应非零退出(否则可能挂起)"
  echo "T4 passed"
  rm -rf "$EMPTY_DIR" /tmp/oss-emulator-store
else
  echo "SKIP: aio-oss binary not found at $OSS_BIN"
fi

echo "ALL tls-keygen black-box tests passed"
