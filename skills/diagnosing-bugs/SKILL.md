---
name: diagnosing-bugs
description: Structured diagnosis loop for hard bugs and performance regressions — build a tight feedback loop, reproduce, hypothesise, instrument, fix, regression-test. Use when the user reports something broken, throwing, failing, or slow.
---

A discipline for hard bugs. Skip phases only when explicitly justified.

## Phase 1 — Build a feedback loop

A tight pass/fail signal for the bug is everything. Spend disproportionate effort here.

Ways to construct one (try in order):
1. Failing test at the seam that reaches the bug
2. Curl / HTTP script against a dev server
3. CLI invocation with fixture input, diff against known-good
4. Headless browser script (Playwright/Puppeteer)
5. Replay a captured trace
6. Throwaway harness — minimal subset exercising the bug path
7. Property / fuzz loop — 1000 random inputs
8. Bisection harness — `git bisect run`
9. Differential loop — same input, old vs new
10. HITL bash script as last resort

Tighten: faster, sharper signal, more deterministic.

**Completion**: one command you've already run, that is red-capable (asserts the user's exact symptom), deterministic, fast, and agent-runnable.

## Phase 2 — Reproduce + minimise

Run the loop, confirm it reproduces the user's bug (not a different one). Minimise: cut inputs, callers, config one at a time until every remaining element is load-bearing.

## Phase 3 — Hypothesise

Generate 3–5 ranked, falsifiable hypotheses before testing any. Show to user if present.

Format: "If X is the cause, then changing Y will make the bug disappear."

## Phase 4 — Instrument

Each probe maps to one prediction. Change one variable at a time. Prefer debugger/REPL over logging. Tag every debug log with a unique prefix (`[DEBUG-xxxx]`). For perf: baseline measurement first, bisect second.

## Phase 5 — Fix + regression test

Write regression test at the correct seam (one that exercises the real bug pattern). Watch it fail → apply fix → watch it pass → re-run original Phase 1 loop.

## Phase 6 — Cleanup

- Original no longer reproduces
- Regression test passes (or absence of seam documented)
- All `[DEBUG-*]` instrumentation removed
- Correct hypothesis stated in commit message
- Ask: what would have prevented this bug?

## Exit

Bug fixed, regression test added, hypothesis recorded.