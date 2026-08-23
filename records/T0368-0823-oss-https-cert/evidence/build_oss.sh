#!/usr/bin/env bash
# 验收脚本：oss 接入 xmake 构建体系
# seam: oss/test/build_oss.sh -> oss/xmake.lua
# 用法: bash oss/test/build_oss.sh [mode] [期望版本]
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

MODE="${1:-release}"
EXPECT_VER="${2:-1.0.0.0}"
fail=0

say() { printf '\033[0;32m[PASS]\033[0m %s\n' "$1"; }
bad() { printf '\033[0;31m[FAIL]\033[0m %s\n' "$1"; fail=1; }

# 1. 构建 oss 目标
if ! xmake f -m "$MODE" >/dev/null 2>&1; then
    bad "xmake config -m $MODE 失败"
    exit 1
fi
if ! xmake build oss >/dev/null 2>&1; then
    bad "xmake build oss 失败"
    exit 1
fi
say "xmake build oss 成功"

# 2. 产物存在且可执行
BIN="$(find build -path "*$MODE/aio-oss" -type f 2>/dev/null | head -1)"
if [ -n "$BIN" ] && [ -x "$BIN" ]; then
    say "产物存在: $BIN"
else
    bad "未找到 aio-oss 产物 (mode=$MODE)"
    exit 1
fi

# 3. 版本注入生效（--version 含期望版本）
VER="$("$BIN" --version 2>/dev/null | tr -d '\r')"
if echo "$VER" | grep -q "$EXPECT_VER"; then
    say "--version 含 $EXPECT_VER (实际: $VER)"
else
    bad "--version 期望含 $EXPECT_VER, 实际: $VER"
fi

# 4. --help 正常展示 server 子命令
if "$BIN" --help 2>&1 | grep -q "server"; then
    say "--help 含 server 子命令"
else
    bad "--help 缺少 server 子命令"
fi

# 5. 版本文件内容正确
VFILE="$(find build -name "aio-oss.version" -type f 2>/dev/null | head -1)"
if [ -n "$VFILE" ] && [ "$(cat "$VFILE")" = "$EXPECT_VER" ]; then
    say "版本文件 aio-oss.version = $EXPECT_VER"
else
    bad "版本文件缺失或内容不符: $VFILE"
fi

# 6. 独立构建回归（cd oss && go build 仍可用）
if (cd oss && go build -mod=vendor -o /dev/null .) >/dev/null 2>&1; then
    say "cd oss && go build -mod=vendor 独立构建回归通过"
else
    bad "oss 独立 go build 回归失败"
fi

echo "----------------------------------------"
if [ "$fail" = "0" ]; then
    echo "RESULT: ALL PASS"
    exit 0
else
    echo "RESULT: FAIL"
    exit 1
fi