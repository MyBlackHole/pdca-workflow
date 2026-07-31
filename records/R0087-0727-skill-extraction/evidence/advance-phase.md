---
name: advance-phase
description: Update task.json meta.phase to the next phase and set relevant timestamps. Use when transitioning between PDCA phases.
---

Update `task.json` with the target phase:

- Set `meta.phase` to `<next-phase>`
- If advancing to `do`, set `status` → `InProgress`
- If advancing to `check`, set `status` → `Completed` and `completed_at` → current time
- If advancing to `act`, set `meta.record` to the current record ID

Completion criterion: `task.json` is updated and committed.