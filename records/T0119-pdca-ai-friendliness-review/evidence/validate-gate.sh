#!/usr/bin/env bash
# validate-gate.sh — 校验 PDCA 阶段转换门禁条件
#
# 用法:
#   ./scripts/validate-gate.sh <task-dir>
#
# 示例:
#   ./scripts/validate-gate.sh pdca/tasks/0727-pdca-ai-friendliness-review
#
# 返回值:
#   0 — 门禁通过，可推进到下一阶段
#   1 — 门禁未通过（原因输出到 stderr）
#   2 — 参数错误或 task.json 无法读取

set -euo pipefail

TASK_DIR="${1:-}"
if [ -z "$TASK_DIR" ]; then
  echo "用法: $0 <task-dir>" >&2
  echo "示例: $0 pdca/tasks/0727-pdca-ai-friendliness-review" >&2
  exit 2
fi

TASK_JSON="$TASK_DIR/task.json"
if [ ! -f "$TASK_JSON" ]; then
  echo "错误: 未找到 $TASK_JSON" >&2
  exit 2
fi

# 读取当前 phase
PHASE=$(python3 -c "
import json
with open('$TASK_JSON') as f:
    t = json.load(f)
print(t.get('meta', {}).get('phase', 'unknown'))
")

case "$PHASE" in
  plan)
    echo "校验 plan → do 门禁..."
    CLARIFICATIONS="$TASK_DIR/clarifications.jsonl"
    if [ ! -f "$CLARIFICATIONS" ]; then
      echo "FAIL: 未找到 clarifications.jsonl" >&2
      echo "提示: Plan 阶段尚未完成方案终审（步骤 6），请先完成用户确认" >&2
      exit 1
    fi
    if python3 -c "
import json
with open('$CLARIFICATIONS') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            if rec.get('source') == 'final_confirmation':
                print('found')
                break
        except json.JSONDecodeError:
            pass
" | grep -q found; then
      echo "PASS: clarifications.jsonl 包含 final_confirmation 记录"
    else
      echo "FAIL: clarifications.jsonl 中未找到 final_confirmation 记录" >&2
      echo "提示: Plan 阶段尚未完成方案终审（步骤 6），请先完成用户确认" >&2
      exit 1
    fi
    ;;

  do)
    echo "校验 do → check 门禁..."
    PRD="$TASK_DIR/prd.md"
    if [ ! -f "$PRD" ]; then
      echo "FAIL: 未找到 prd.md" >&2
      echo "提示: 缺少需求文档，请先在 Plan 阶段产出 prd.md" >&2
      exit 1
    fi
    echo "OK: prd.md 存在"

    # 查找对应的 record-id（从 task.json 的 meta.record 或通过 slug 推断）
    RECORD_ID=$(python3 -c "
import json
with open('$TASK_JSON') as f:
    t = json.load(f)
print(t.get('meta', {}).get('record', ''))
")
    if [ -z "$RECORD_ID" ]; then
      SLUG=$(python3 -c "
import json, os
with open('$TASK_JSON') as f:
    t = json.load(f)
print(t.get('slug', os.path.basename(os.path.dirname('$TASK_JSON'))))
")
      RECORD_ID="T$(python3 -c "
import json
with open('$TASK_JSON') as f:
    t = json.load(f)
print(t.get('id', '').lstrip('T'))
")-$SLUG"
    fi

    MANIFEST="records/$RECORD_ID/evidence/manifest.jsonl"
    if [ -f "$MANIFEST" ] && [ -s "$MANIFEST" ]; then
      COUNT=$(wc -l < "$MANIFEST")
      echo "PASS: $MANIFEST 存在且有 $COUNT 条证据记录"
    else
      echo "FAIL: $MANIFEST 不存在或为空" >&2
      echo "提示: 请先登记证据（register-evidence）再推进到 Check 阶段" >&2
      exit 1
    fi
    ;;

  check)
    echo "校验 check → act 门禁..."
    RECORD_ID=$(python3 -c "
import json
with open('$TASK_JSON') as f:
    t = json.load(f)
print(t.get('meta', {}).get('record', ''))
")
    if [ -z "$RECORD_ID" ]; then
      echo "FAIL: task.json 中 meta.record 未设置" >&2
      echo "提示: 请先记录当前 record ID 到 meta.record" >&2
      exit 1
    fi
    CONCLUSION="records/$RECORD_ID/conclusion.md"
    if [ -f "$CONCLUSION" ]; then
      echo "PASS: $CONCLUSION 存在"
    else
      echo "FAIL: $CONCLUSION 不存在" >&2
      echo "提示: 请先写结论文档（write-conclusion）再推进到 Act 阶段" >&2
      exit 1
    fi
    ;;

  act)
    echo "校验 act → archive 门禁..."
    if python3 -c "
import json
with open('$TASK_JSON') as f:
    t = json.load(f)
disp = t.get('meta', {}).get('disposition', {})
if isinstance(disp, dict) and 'outcome' in disp and 'reason' in disp and 'at' in disp:
    print('found')
" | grep -q found; then
      echo "PASS: meta.disposition 已配置"
    else
      echo "FAIL: meta.disposition 未配置或缺少 outcome/reason/at 字段" >&2
      echo "提示: Act 阶段尚未完成记录处置（步骤 3），请先设置 disposition 后再归档" >&2
      exit 1
    fi
    ;;

  archive)
    echo "任务已归档，无需推进"
    ;;

  *)
    echo "错误: 未知阶段 '$PHASE'" >&2
    exit 2
    ;;
esac

echo "门禁校验通过，可以安全推进到下一阶段。"
exit 0
