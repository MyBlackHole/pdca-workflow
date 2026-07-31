---
name: to-tickets
description: Break a PRD into executable sub-tasks — generate task.json files for each sub-task, update parent children list. Use after PRD is finalized (flow-plan step 3) and before manual decomposition (step 4).
---

Parse `prd.md` and produce sub-task skeletons.

## Input

- `prd.md` in the current task directory
- Parent `task.json` with `id` and `meta.scenario_type`

## Process

1. Read `prd.md` and identify independent work units (sections, features, or phases).
2. Scan `pdca/tasks/` and `pdca/tasks/archive/` for all `task.json` files to find the highest numeric ID (e.g., `T0100`).
3. For each sub-task, create a directory `pdca/tasks/<slug>/` with:

```json
{
  "id": "T<NEXT>",
  "parent": "<parent task ID>",
  "slug": "<kebab-case-slug>",
  "title": "<短标题>",
  "meta": {
    "phase": "plan",
    "active": true,
    "scenario_type": "<inherit from parent>"
  },
  "states": {
    "created": "<ISO now>",
    "plan": null,
    "do": null,
    "check": null,
    "act": null
  }
}
```

4. Update parent `task.json` → append sub-task IDs to `children` array.
5. Copy relevant sections of `prd.md` into each sub-task's `prd.md`.

## Rules

- ID allocation is monotonic: scan both active and archived tasks.
- Do not create sub-tasks for units smaller than one PDCA cycle.
- A sub-task inherits `scenario_type` from the parent unless overridden.
- Always commit sub-task directories in the same commit as the parent update.

## Dispatch（仅在 P6 终审后）

Read the doctor result for the abstract `agent.spawn` capability. When available, pass each confirmed child PRD through the current environment Adapter. When unavailable, execute child tasks sequentially in the main session.

- Pass the child task's `prd.md` content as the prompt
- The subagent runs a full PDCA cycle (plan→do→check→act→archive) independently
- The subagent does NOT do user alignment — all user-facing decisions stay in the parent session
- Collect return values: conclusion summary + evidence manifest path
- After all subagents complete, merge evidence back to parent task's evidence/
- Never dispatch before the parent P6 final confirmation
- Never guess or call a platform-specific tool when `agent.spawn` is unavailable
