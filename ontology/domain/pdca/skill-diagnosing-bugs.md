---
schema: pdca.asset/v1
id: ontology:domain/skill-diagnosing-bugs
name: diagnosing-bugs
summary: Systematically diagnose bugs using structured approaches.
description: Structured diagnosis loop for hard bugs and performance regressions — build a tight feedback loop, reproduce, hypothesise, instrument, fix, regression-test. Use when the user reports something broken, throwing, failing, or slow.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-diagnosing-bugs/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/failure-mode
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


---
name: diagnosing-bugs
description: Structured diagnosis loop for hard bugs and performance regressions — build a tight feedback loop, reproduce, hypothesise, instrument, fix, regression-test. Use when the user reports something broken, throwing, failing, or slow.
---

A discipline for hard bugs. Skip phases only when explicitly justified.

## Phase 0 — Read context + Redact

Before touching the system, load shared context and protect secrets:

- If the repo has `CONTEXT.md` / ADR docs, read them first — use their shared vocabulary in later phases.
- Redact before running anything: replace secrets (tokens, keys, internal hosts, headers) in commands, captured output, and pasted artefacts with `<REDACTED>`.
- Keep credentials in environment variables — never in commands, files, or logs.
- When pasting an artefact, quote only the load-bearing lines, not the whole blob.

A bug that leaks credentials during diagnosis is worse than the bug itself.

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
10. HITL bash script as last resort — use `hitl-loop.template.sh` in this skill's directory: it drives each manual step, records the result, and keeps the loop structured while a human clicks.

Tighten 三维（更快/更锐/更确定）：更快（缩短循环至秒级）、更锐（断言用户精确症状而非“未崩溃”）、更确定（固定时间/seed/隔离文件系统，100×并行提升非确定性复现率至>50%）。

**Completion**: one command you've already run, that is red-capable (asserts the user's exact symptom), deterministic, fast, and agent-runnable. 10回路已完整枚举（10 loops: failing test/curl/CLI/browser trace/harness/property/bisection/differential/HITL）按序尝试，HITL为last resort。

## Phase 2 — Reproduce + minimise

Run the loop, confirm it reproduces the user's bug (not a different one). Minimise: cut inputs, callers, config one at a time until every remaining element is load-bearing.

**Explicit stop if you cannot build a feedback loop.** List what you tried and why each failed. Ask the user for the environment, artefacts, or permission to add temporary instrumentation. Do NOT enter Phase 3 without a pass/fail loop — hypothesising without a loop is guessing.

**Non-deterministic bugs**: the goal is no longer a clean reproduction but a higher reproduction rate. Run the trigger 100×, run loops in parallel, narrow the timing window. A 1% flake is not debuggable; a 50% flake is. Target a rate you can iterate against.

## Phase 3 — Hypothesise

Generate 3–5 ranked, falsifiable hypotheses before testing any. Show to user if present.

Format — two-sided prediction: "If X is the cause, then changing Y will make the bug disappear; changing Z will make it worse."

## Phase 4 — Instrument

Each probe maps to one prediction. Change one variable at a time. Prefer debugger/REPL over logging. Tag every debug log with a unique prefix (`[DEBUG-xxxx]`). For perf: baseline measurement first, bisect second.

## Phase 4.5 — Fix Approval（修复前用户确认门禁）

**硬门禁：未获用户书面确认，不得进入 Phase 5 改代码。**

- 向用户展示：已验证假设/根因（区分假设/设计错误、实现/环境错误、流程/证据遗漏三类，根因≠现象）、修复方案、回归测试计划、影响范围、回滚策略
- 获用户明确确认后，用 CLI 落盘（`captured:true`，时间戳由 CLI 生成）：
  ```bash
  python3 "$PDCA_HOME/scripts/append-confirmation.py" --task-dir <task-dir> --source fix_confirmation --response confirmed --summary "<根因+方案+影响范围>"
  ```
- `fix_confirmation:confirmed` 未落盘前，禁止任何代码修改；`rejected` 则返回 Phase 3 重做假设

科学依据：HITL Approval-Gate 模式（Agent 做事、Human 做决策）与 Zeller 科学调试法（假设→预测→实验→结论）的 Fix 前确认点；2-3 个战略门禁优于全量门禁，避免审批疲劳。

## Phase 5 — Fix + regression test

**前置**：`clarifications.jsonl` 中 `fix_confirmation:confirmed` 已存在（`captured:true`）。

Write regression test at the correct seam (one that exercises the real bug pattern). Watch it fail → apply fix → watch it pass → re-run original Phase 1 loop.

## Phase 6 — Cleanup + post-mortem

- Original no longer reproduces
- Regression test passes (or absence of seam documented)
- All `[DEBUG-*]` instrumentation removed
- Correct hypothesis stated in commit message
- Ask: what would have prevented this bug?
- If the answer points at architecture (no good seam, tight coupling), hand off to `improve-codebase-architecture` — do not let the architectural fix die inside this loop.

## Exit

Bug fixed, regression test added, hypothesis recorded.

## 已知坑

- 先复现再修复；无复现条件下乱改代码会引入回归且无法验证。
- 未获 `fix_confirmation:confirmed` 就改代码属绕过门禁；存量任务缺确认由 `flow_audit` 记 `fix-confirmation` WARN 留痕，不阻断但须补录。
