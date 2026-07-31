#!/bin/bash
# init-external.sh — 在外部项目中初始化 PDCA 工作流引用
# 用法: ./init-external.sh /path/to/external-project
# 在外部项目根目录创建 AGENTS.md，通过 PDCA_HOME 环境变量连接到管理中心

set -euo pipefail

PDCA_SRC="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"
[ -z "$TARGET" ] && echo "用法: $0 /path/to/external-project" && exit 1
[ ! -d "$TARGET" ] && echo "错误: $TARGET 不存在" && exit 1

AGENTS_FILE="$TARGET/AGENTS.md"

if [ -f "$AGENTS_FILE" ]; then
  if grep -q "PDCA_HOME" "$AGENTS_FILE"; then
    echo "AGENTS.md 已有 PDCA_HOME 配置，跳过"
    exit 0
  fi
  echo "追加 PDCA 工作流引用到 $AGENTS_FILE"
  echo "" >> "$AGENTS_FILE"
else
  echo "创建 $AGENTS_FILE"
fi

cat "$PDCA_SRC/templates/PDCA_HOME.md" >> "$AGENTS_FILE"
echo "✅ 完成。确保 shell 配置中包含: export PDCA_HOME=$PDCA_SRC"