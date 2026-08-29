#!/usr/bin/env bash
# 安装 pre-commit 钩子，使本体门禁成为提交级硬门禁。
# 仅在本体（ontology/）或任务（pdca/tasks/）相关文件变更时运行 ci-ontology-gate。
# 用法：bash scripts/install-git-hook.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOK="$ROOT/.git/hooks/pre-commit"

if [ -f "$HOOK" ] && ! grep -q "ci-ontology-gate.py" "$HOOK"; then
  BACKUP="$HOOK.pre-ontology-gate.bak"
  cp "$HOOK" "$BACKUP"
  echo "已备份既有 pre-commit 到 $BACKUP"
fi

cat > "$HOOK" <<'HOOK_EOF'
#!/bin/sh
# 本体硬门禁（由 install-git-hook.sh 安装）
ROOT=$(git rev-parse --show-toplevel)
CHANGED=$(git diff --cached --name-only)
echo "$CHANGED" | grep -qE '^(ontology/|pdca/tasks/)' || exit 0
python3 "$ROOT/scripts/ci-ontology-gate.py" $CHANGED
HOOK_EOF

chmod +x "$HOOK"
echo "已安装 pre-commit 硬门禁：$HOOK"
echo "卸载：删除该文件或恢复 .bak 备份"
