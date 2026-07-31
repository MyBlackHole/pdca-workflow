---
name: improve-codebase-architecture
description: Analyze the PDCA project structure for architecture issues — detect bad smells in flows/skills/pdca structure, generate a typed Markdown report with file:line references. Use during review or at the end of development to catch structural drift.
---

Analyze the project structure and produce an architecture improvement report.

## Analysis dimensions

1. **Flow coverage** — Which `scenario_type` values lack a corresponding flow path? Check `flows/` against the types in `flows/flow-do/SKILL.md`.
2. **Skill consistency** — Every skill reference in `flows/flow-*/SKILL.md` should point to an existing `skills/<name>/SKILL.md`. Report orphans (referenced but missing) and orphans (exist but unreferenced).
3. **Knowledge–process mapping** — Principles in `knowledge/` should have corresponding implementation in `flows/` or `skills/`. Report gaps.
4. **File smells** — Files over 200 lines, duplicated step patterns, mixed responsibilities.

## Output format

Write `architecture-report.md` in the task directory:

```markdown
# Architecture Report

## missing (must fix)
- <type>: <file>:<line> — <description>

## warning (should fix)
- <type>: <file>:<line> — <description>

## info (consider)
- <type>: <file>:<line> — <description>
```

## Rules

1. Every issue must have a file:line reference or be explicitly marked as "project-wide".
2. Sort issues by impact (missing > warning > info), then by file path.
3. Do not report issues outside the PDCA project structure (flows/, skills/, knowledge/, pdca/).
4. Suggest a concrete fix for each "missing" item.