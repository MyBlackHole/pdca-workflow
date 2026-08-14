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
2. Scan `pdca/tasks/` and `pdca/tasks/archive/` for all `task.json` files to find duplicates and to pass `check-design-vocab` sanity; the **next task ID must not be computed manually** — use the uniform identity entrypoint.
3. For each sub-task, create the sub-task skeleton through the atomic entrypoint (repository lock + ID reservation + immutable record):

```bash
python3 "$PDCA_HOME/scripts/task_identity.py" create \
  --slug <kebab-case-slug> \
  --title "<短标题>" \
  --parent <parent task ID> \
  --dependencies <direct-predecessor task IDs, comma-separated> \
  --scenario-type <inherit from parent> \
  --created-at <ISO now>
```

The entrypoint assigns the global unique task ID, derives the immutable `meta.record`, creates `records/<record>/`, and writes `task.json` / `clarifications.jsonl` / `prd.md` atomically. **Never scan-and-write `task.json` directly.**

4. Update parent `task.json` → append sub-task IDs to `children` array.
5. Copy relevant sections of `prd.md` into each sub-task's `prd.md`.

## Blocking edges（依赖边）

- **`dependencies`** 数组声明该子任务的**直接前置**（直接依赖的任务 ID），
  仅存直接边；传递依赖由校验器推导，不冗余存储。
- 无前置则省略 `dependencies`（缺省 `[]`）。
- 引用必须指向真实存在的任务 ID；自环/循环引用非法。

## Ready-set 计算

拆解完成后**立即**校验依赖图并计算 ready-set：

```bash
python3 scripts/compute-frontier.py < dag.json
```

- **ready-set** = 所有"未完成且所有直接前置已完成"的任务集合（可并行任务集）。
- 依赖图非法（有环 / 缺失引用 / 自环）→ 拒绝拆解产出，修复依赖后再校验。
- 顺序执行时按 `batches` 分批：每批是当前全部可并行任务，批间串行。

## Rules

- ID allocation is monotonic and repository-global: the `task_identity.py` entrypoint scans both active and archived tasks inside its lock; never hand-derive the next ID.
- Do not create sub-tasks for units smaller than one PDCA cycle.
- A sub-task inherits `scenario_type` from the parent unless overridden.
- Always commit sub-task directories in the same commit as the parent update.
- `dependencies` 只存直接前置；禁止写入传递依赖全集。
- 拆解完成后必须通过 DAG 校验（`scripts/compute-frontier.py` 返回 `valid: true`）。

## Dispatch（仅在 P6 终审后）

Read the doctor result for the abstract `agent.spawn` capability. When available, pass each confirmed child PRD through the current environment Adapter. When unavailable, execute child tasks sequentially in the main session.

- Pass the child task's `prd.md` content as the prompt
- The subagent runs a full PDCA cycle (plan→do→check→act→archive) independently
- The subagent does NOT do user alignment — all user-facing decisions stay in the parent session
- Collect return values: conclusion summary + evidence manifest path
- After all subagents complete, merge evidence back to parent task's evidence/
- Never dispatch before the parent P6 final confirmation
- Never guess or call a platform-specific tool when `agent.spawn` is unavailable
