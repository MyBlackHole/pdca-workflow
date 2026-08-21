#!/usr/bin/env bash
set -euo pipefail

# Zero-warning + -Werror build gate.
# Usage: gate_warnings.sh [build-dir] [root]
#   build-dir  where make output artifacts live (default: build-make)
#   root       project root (default: repo root, two levels up from tests/)
#
# Fails when:
#   - a clean build emits any "warning:" line, or
#   - the build does not run under -Werror (verified with a deliberate probe).
# Exits 0 on a clean zero-warning build with -Werror in effect.

ROOT=${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
BUILD=${2:-build-make}

cd "$ROOT"

echo "== gate_warnings: clean build with TLS default =="
make clean >/dev/null
build_log="$(mktemp)"
make 2>&1 | tee "$build_log"
warnings="$(grep -c 'warning:' "$build_log" || true)"
rm -f "$build_log"
if [ "$warnings" -ne 0 ]; then
  echo "gate_warnings: FAIL - build emitted $warnings warning(s)" >&2
  exit 1
fi
echo "gate_warnings: build produced 0 warnings"

echo "== gate_warnings: -Werror probe =="
probe_dir="$(mktemp -d)"
probe="$probe_dir/probe.cpp"
cat > "$probe" <<'EOF'
int main(){int unused_var=42;(void)0;return 0;}
EOF
# Compile without -Werror to confirm the probe actually triggers a warning.
probe_err="$(mktemp)"
if ! g++ -std=c++11 -Wall -Wextra -Wpedantic -fsyntax-only "$probe" 2>"$probe_err"; then
  echo "gate_warnings: FAIL - probe failed to compile" >&2
  cat "$probe_err" >&2
  rm -rf "$probe_dir" "$probe_err"
  exit 1
fi
if ! grep -q 'warning:' "$probe_err"; then
  echo "gate_warnings: FAIL - probe does not trigger a warning under -Wall" >&2
  rm -rf "$probe_dir" "$probe_err"
  exit 1
fi
rm -f "$probe_err"
# Compile with -Werror to confirm it is rejected.
if g++ -std=c++11 -Wall -Wextra -Wpedantic -Werror -fsyntax-only "$probe" 2>/dev/null; then
  echo "gate_warnings: FAIL - -Werror did not reject the warning probe" >&2
  rm -rf "$probe_dir"
  exit 1
fi
rm -rf "$probe_dir"
echo "gate_warnings: -Werror rejects warning-producing code as expected"

echo "== gate_warnings: project build compiles under -Werror =="
make clean >/dev/null
# Rebuild with -Werror injected into CXXFLAGS through make's variable.
# CXXFLAGS from the Makefile uses '+=' so we append via the command line.
werr_log="$(mktemp)"
make CXXFLAGS+="-Werror" 2>&1 | tee "$werr_log"
werr_warnings="$(grep -c 'warning:' "$werr_log" || true)"
make_failed=0
if grep -E 'error:' "$werr_log" >/dev/null; then
  make_failed=1
fi
rm -f "$werr_log"
if [ "$werr_warnings" -ne 0 ] || [ "$make_failed" -ne 0 ]; then
  echo "gate_warnings: FAIL - -Werror build produced warnings/errors" >&2
  exit 1
fi
echo "gate_warnings: PASS"
