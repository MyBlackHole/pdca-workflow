---
name: to-tickets
description: Break a PRD into executable sub-tasks — generate task.json files for each sub-task, update parent children list. Use after PRD is finalized (flow-plan step 3) and before manual decomposition (step 4).
---
relations:
  specializes:
  - ontology:concept/task-decomposition
  - ontology:concept/vertical-slice
  - ontology:concept/tracer-bullet
  - ontology:concept/blocking-edges
  - ontology:concept/expand-contract
  relates_to:
  - ontology:concept/grilling-methodology
  - ontology:concept/domain-modeling
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
3. **本体一致性预检（拆分前）**：把候选子任务的 slug/标题交给本体冲突检查，若与既有 `ontology` 节点重名，提示「已有本体节点 X，建议复用而非新建任务」，或要求 slug 显式区分后再拆。

```bash
python3 "$PDCA_HOME/scripts/ontology-clash-check.py" "$PDCA_HOME" --candidates "<slug-or-title-1>,<slug-or-title-2>"
```

该检查**仅提示、不阻断**拆解产出；可在 PRD 内已声明「关联本体节点」时据此对齐边界。
3.5. **关系树驱动拆分（可选，顾问式）**：仅当 PRD 含 `## 拆分映射` 且父任务 `meta.ontology_fragment` 非空时启用。运行：

   ```bash
   python3 "$PDCA_HOME/scripts/ontology_tree_split.py" --ontology-dir "<meta.ontology_fragment>" --prd prd.md
   ```

   脚本解析 `## 拆分映射`（章节→节点），结合本体 `composed_of`/`specializes` 关系树输出候选子任务（含 `slug_base`、`ontology_node_type`、依赖边），**仅打印候选、不自动落盘**。确认后由调用方经 `task_identity.py` 逐个创建（node_type/依赖已自动推导，无需人工传参）。映射节点不存在、关系图成环时脚本报错退出，不生成错误骨架。未声明 `## 拆分映射` 时跳过本步，保持原有章节人工划分行为。

4. For each sub-task, create the sub-task skeleton through the atomic entrypoint (repository lock + ID reservation + immutable record):

```bash
python3 "$PDCA_HOME/scripts/task_identity.py" create \
  --slug <kebab-case-slug> \
  --title "<短标题>" \
  --parent <parent task ID> \
  --dependencies <direct-predecessor task IDs, comma-separated> \
  --scenario-type <inherit from parent> \
  --created-at <ISO now> \
  --ontology-fragment <继承父任务的 ontology_fragment，若父有> \
  --ontology-node-type <继承父任务的 ontology_node_type，若父有>
```

`task_identity.py` 已支持**自动继承**：若未显式传 `--ontology-fragment`/`--ontology-node-type` 而父任务 `meta` 中有值，则子任务自动继承，使拆分沿本体边界对齐。`--ontology-fragment` 指向存在的本体目录时会做轻量存在性校验。

The entrypoint assigns the global unique task ID, derives the immutable `meta.record`, creates `records/<record>/`, and writes `task.json` / `clarifications.jsonl` / `prd.md` atomically. **Never scan-and-write `task.json` directly.**

5. Update parent `task.json` → append sub-task IDs to `children` array.
6. Copy relevant sections of `prd.md` into each sub-task's `prd.md`.

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
- A sub-task inherits `meta.ontology_fragment` / `meta.ontology_node_type` from the parent unless overridden (`task_identity.py` 自动继承；拆分前应先经本体冲突预检).
- Always commit sub-task directories in the same commit as the parent update.
- `dependencies` 只存直接前置；禁止写入传递依赖全集。
- 拆解完成后必须通过 DAG 校验（`scripts/compute-frontier.py` 返回 `valid: true`）。

## Wide-refactor 分支（保绿序列化）

当重构的 **blast radius 横跨全库**（全局改名 / 改类型 / 改接口签名），
禁止单提交打穿全部调用点；按 expand → 分批迁移 → contract 序列化，逐批保持 CI 绿：

1. **expand**（1 个子任务）：新旧形式并存。新增新接口/新名，保留旧形式；旧形式仍被契约测试覆盖（断言旧接口未被删除）。
2. **分批迁移**（按 blast radius 分批，每批 1 个子任务，`blocked by expand`）：每批迁移一批调用点后跑完整测试，提交时 CI 必须保持绿（逐批绿）。
3. **contract**（1 个子任务，`blocked by` 全部迁移批）：无调用者后删除旧形式，做收尾清理。
4. **批次内无法保绿时**：合并到共享集成分支，末尾加 `integrate-and-verify` 子任务统一验证。

`dependencies` 声明这批 blocking edges：`expand → 迁移批 → contract`，只存直接前置。

**硬指标**：
- 逐批 CI 绿比例 = 100%（每批提交必须跑完整测试，可用脚本断言每批都绿）。
- expand 阶段旧形式仍在 → 契约测试可断言旧接口存在（未过早删除）。
- 单批迁移调用点数可审计（批定义含调用点清单）。

## Dispatch（仅在 P6 终审后）

Read the doctor result for the abstract `agent.spawn` capability. When available, pass each confirmed child PRD through the current environment Adapter. When unavailable, execute child tasks sequentially in the main session.

- Pass the child task's `prd.md` content as the prompt
- The subagent runs a full PDCA cycle (plan→do→check→act→archive) independently
- The subagent does NOT do user alignment — all user-facing decisions stay in the parent session
- Collect return values: conclusion summary + evidence manifest path
- After all subagents complete, merge evidence back to parent task's evidence/
- Never dispatch before the parent P6 final confirmation
- Never guess or call a platform-specific tool when `agent.spawn` is unavailable

## 已知坑

- 子任务在父 P6 final_confirmation 前**禁止调度**（T0265）。
- `agent.spawn` 不可用时不猜平台工具，由主 session 顺序执行。
