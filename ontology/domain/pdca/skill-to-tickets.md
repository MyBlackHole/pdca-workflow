---
schema: pdca.asset/v1
id: ontology:domain/skill-to-tickets
name: to-tickets
summary: Break down tasks into actionable tickets for tracking.
description: Break a PRD into executable sub-tasks — generate task.json files for each sub-task, update parent children list. Use after PRD is finalized (flow-plan step 3) and before manual decomposition (step 4).
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/skill-to-tickets/1.0.2
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/triage
    - ontology:concept/domain-modeling
  testable_signal: "运行 grep -q 'ontology:domain/skill-to-tickets' ontology/domain/pdca/skill-to-tickets.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


--
name: to-tickets
description: Break a PRD into executable sub-tasks — generate task.json files for each sub-task, update parent children list. Use after PRD is finalized (flow-plan step 3) and before manual decomposition (step 4).
---

Parse `prd.md` and produce sub-task skeletons.

## Input

- `prd.md` in the current task directory
- Parent `task.json` with `id`, `meta.ontology_role` and `meta.execution_contract`

## Process

1. Read `prd.md` and identify work units along the ontology tree（见 `ontology:concept/pdca` 设计核心：每本体一子任务；`## 拆分映射` 章节→节点为输入，本体关系树为拆分主轴）。
2. Scan `pdca/tasks/` and `pdca/tasks/archive/` for all `task.json` files to find duplicates and to pass `check-design-vocab` sanity; the **next task ID must not be computed manually** — use the uniform identity entrypoint.
3. **本体一致性预检（拆分前，阻断门禁）**：把候选子任务的 slug/标题交给本体冲突检查，若与既有 `ontology` 节点重名，提示「已有本体节点 X，建议复用而非新建任务」，exit code=1 阻断拆解产出；无冲突 exit code=0 通过。已在 PRD `## 关联本体节点` 声明复用时，视为预期复用，提示后可继续（不阻断）。

```bash
python3 "$PDCA_HOME/scripts/ontology-clash-check.py" "$PDCA_HOME" --candidates "<slug-or-title-1>,<slug-or-title-2>"
```

该检查为**阻断式门禁**：未声明复用时冲突即阻断；已声明复用时仅提示对齐边界后放行。
3.5. **关系树驱动拆分（默认，叶→根）**：当父任务 `meta.ontology_fragment` 非空时**默认启用**。运行：

   ```bash
   python3 "$PDCA_HOME/scripts/ontology_tree_split.py" --ontology-dir "<meta.ontology_fragment>" --prd prd.md
   ```

   脚本解析 `## 拆分映射`（章节→节点），结合本体 `composed_of`/`specializes` 关系树输出候选子任务（含 `slug_base`、`ontology_node_type`、依赖边），**仅打印候选、不自动落盘**。确认后由调用方经 `task_identity.py` 逐个创建（node_type/依赖已自动推导，无需人工传参）。映射节点不存在、关系图成环时脚本报错退出，不生成错误骨架。**有 `meta.ontology_fragment` 且无 `## 拆分映射` 时报错退出**（`[ontology-tree-split] ERROR: PRD 未含 '## 拆分映射' 小节或解析为空`，exit 1），不回退；无 fragment 或 `ontology_exempt=true` 时跳过。

4. For each sub-task, create the sub-task skeleton through the atomic entrypoint (repository lock + ID reservation + immutable record):

```bash
python3 "$PDCA_HOME/scripts/task_identity.py" create \
  --slug <kebab-case-slug> \
  --title "<短标题>" \
  --parent <parent task ID> \
  --dependencies <direct-predecessor task IDs, comma-separated> \
  --ontology-role <inherit from parent> \
  --created-at <ISO now> \
  --ontology-fragment <继承父任务的 ontology_fragment，若父有> \
  --ontology-node-type <继承父任务的 ontology_node_type，若父有>
```

`task_identity.py` 已支持**自动继承**：若未显式传 `--ontology-fragment`/`--ontology-node-type` 而父任务 `meta` 中有值，则子任务自动继承，使拆分沿本体边界对齐。`--ontology-fragment` 指向存在的本体目录时会做轻量存在性校验。

The entrypoint assigns the global unique task ID, derives the immutable `meta.record`, creates `records/<record>/`, and writes `task.json` / `clarifications.jsonl` / `prd.md` atomically. **Never scan-and-write `task.json` directly.**

5. Update parent `task.json` → append sub-task IDs to `children` array.
6. Copy relevant sections of `prd.md` into each sub-task's `prd.md`, rewritten per 子票 PRD 实质化规范第 1 条（回链父 AC 编号，非原文照搬）。

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

## 子票 PRD 实质化规范（final_confirmation 前必备）

骨架创建后、父票 final_confirmation 前，每个子票 `prd.md` 必须满足：

1. **验收继承**：每条子 AC 注明回链父 PRD 编号，格式 `AC-x（回链父 AC-y）`；无父 AC 可链时注明来源（triage brief 期望行为第 N 条）。
2. **拆分映射对齐**：`## 拆分映射` 每行 `章节 -> 节点` 的节点须与本子票 `task.json` 的 `ontology_anchor` 一致；单子票单节点，一对多即拆分过粗，打回重拆。
3. **测试接缝声明**：`ontology_projection` 子票的 `execution_contract` 若要求修改可执行代码，PRD 必须含 `### 声明的测试接缝`（格式 `- seam: <测试文件> -> <被测模块>`）；其他职责或不修改可执行代码的契约可免声明，但须在 PRD 写明免责依据。skill 名称不得作为该门禁的任务路由字段。
4. **反例拒收**：`- [ ] AC-1 示例验收` 原样未改即视为未实质化，`plan→do` 拒收。

## Rules

- ID allocation is monotonic and repository-global: the `task_identity.py` entrypoint scans both active and archived tasks inside its lock; never hand-derive the next ID.
- Do not create sub-tasks for units smaller than one PDCA cycle.
- A sub-task inherits `ontology_role` and the execution contract from the parent unless an explicit ontology batch changes them.
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

`parent` 与 `dependencies` 只用于表达拆分关系、直接前置边与 ready-set 调度，不使任何任务成为另一任务的生命周期控制者或验收代理。每个拆出的任务都须作为独立 PDCA 循环，完成自己的 P6 终审后再调度。

读取 doctor 对抽象能力 `agent.spawn` 的探测结果。该能力是调度必需项：当前任务的协调 Agent 必须通过 Adapter，一次性启动与当前 PDCA 任务一对一绑定的全新子 Agent/子智能体上下文。若能力不可用，必须 fail-closed 并保持当前任务未执行；不得回退协调 Agent，也不得复用既有子 Agent 上下文。

- 将当前任务的 `prd.md`、task metadata 与明确的 context pointer 作为持久化输入
- 每个独立 PDCA 任务都获得一个全新子 Agent 上下文，不共享其他任务或协调 Agent 的活动上下文
- 子 Agent 在当前任务上下文内自主执行
- 拆分主轴为本体树（见 `ontology:concept/pdca` 设计核心）：每本体一子任务；`ontology_modeling`、`ontology_projection`、`ontology_conformance_verification` 三个专业职责下的子任务都跑完整循环，不保留其他职责别名
- 派发后协调 Agent 立即进入 `suspended_waiting_agent` 并停止运行
- 恢复后只读当前任务持久化产物并执行 `ontology_conformance_verification`，禁止检查其他任务
- 需要用户确认时，当前任务只持久化 `awaiting_confirmation`，由主会话转交真实确认；子 Agent 不得代签
- Never dispatch before the current task P6 final confirmation
- Never guess or call a platform-specific tool when `agent.spawn` is unavailable

## 已知坑

- 当前任务在自身 P6 final_confirmation 前**禁止调度**（T0265）。
- `agent.spawn` 不可用时 fail-closed，当前任务保持未执行；不得猜平台工具、不得由协调 Agent 执行、不得复用任何既有子 Agent 上下文。
