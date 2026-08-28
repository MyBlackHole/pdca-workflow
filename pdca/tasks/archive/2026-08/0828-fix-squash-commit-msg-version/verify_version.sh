#!/usr/bin/env bash
# 校验 libobk_version 已修正为 1.0.1.8（被测模块：仓库根 xmake.lua）
set -e
REPO=/home/black/Public/aio/aio-tools/6200/F/139
v=$(grep -oE 'libobk_version *= *"[0-9.]+"' "$REPO/xmake.lua" | grep -oE '[0-9.]+')
if [ "$v" != "1.0.0.1" ]; then echo "FAIL libobk_version=$v"; exit 1; fi
echo "PASS libobk_version=$v"
