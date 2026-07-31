#!/usr/bin/env bash
# Strict wrapper retained as the stable shell entry point.

set -euo pipefail

TASK_DIR="${1:-}"
if [ -z "$TASK_DIR" ]; then
  echo "用法: $0 <task-dir>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/validate-workflow.py" --task-dir "$TASK_DIR" --gate
