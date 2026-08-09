#!/usr/bin/env bash
# hitl-loop.template.sh — structured HITL driver for diagnosing-bugs Phase 1 step 10.
# Use only as a last resort when no agent-runnable feedback loop can be built and
# a human must interact with the system. Each step records the observed result so
# the loop stays structured while a human clicks.
#
# Copy this file next to the skill and edit the STEP array for the current bug.
set -euo pipefail

REDACTED='<REDACTED>'

# Edit these for the current diagnosis. One entry per manual step.
STEPS=(
  "reproduce the symptom and paste the exact output"
  "run the narrowed input once more and record pass/fail"
  "apply the temporary instrumentation and record the result"
)

RESULT_FILE="hitl-results.log"

run_step() {
  local i="$1"
  local step="$2"
  echo "=== Step $i: $step ===" | tee -a "$RESULT_FILE"
  read -r -p "[hitl] execute the step, then paste the observed result (use ${REDACTED} for anything sensitive): " observed
  echo "$i: $observed" >> "$RESULT_FILE"
}

echo "Hitl loop starting. Results recorded in $RESULT_FILE. Redact anything sensitive with ${REDACTED}."
for i in "${!STEPS[@]}"; do
  run_step "$((i + 1))" "${STEPS[$i]}"
done

echo "Loop finished. Feed $RESULT_FILE back into diagnosing-bugs Phase 2."
