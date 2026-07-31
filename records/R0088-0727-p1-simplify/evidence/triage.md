---
name: triage
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.
disable-model-invocation: true
---

# Triage

Move a fuzzy request through: `needs-triage` → `needs-info` → `ready-to-plan` or `wontfix`.

Two categories: `bug` (existing behaviour broken) or `enhancement` (new/improvement).

## Process

### 1. Classify

| Input shape | category | scenario_type |
|-------------|----------|---------------|
| Bug report / defect | `bug` | `bugfix` |
| New feature / module | `enhancement` | `development` |
| "Research / analyse X" | `enhancement` | `research` |
| "Write docs for X" | `enhancement` | `documentation` |
| "Design architecture for X" | `enhancement` | `design` |
| "Review code in X" | `enhancement` | `review` |
| Refactor / optimisation | `enhancement` | `development` |
| Uncertain | keep `needs-triage` | leave blank |

### 2. Deduplicate

Search: `pdca/tasks/**/task.json` (incl. archive), `knowledge/out-of-scope/`, `knowledge/**/*.md`.

### 3. Verify the claim

- **Bug**: reproduce from steps; check git log / code logic
- **Enhancement**: search for existing implementation; check if existing modules can extend

### 4. Grill (if info is insufficient)

Load `skills/grilling/SKILL.md` to fill gaps. Log Q&A to `clarifications.jsonl` (`source: "triage"`).

### 5. Output

**ready-to-plan**: create `pdca/tasks/<MMDD-slug>/` with:
- `task.json` — `meta.phase: "plan"`, `status: "Pending"`, category + scenario_type
- `prd.md` — skeleton (problem + known info + gaps)
- `triager-brief.md` — classification, verification result, information gaps, dedup results, recommended next steps

**wontfix**: write to `knowledge/out-of-scope/<slug>.md` with the request description, rejection reasons, and date. Close the issue.

## Exit
- `ready-to-plan` → Plan phase
- `wontfix` → archive, no further action