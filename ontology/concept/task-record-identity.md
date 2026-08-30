---
schema: pdca.asset/v1
id: ontology:concept/task-record-identity
type: concept
layer: Knowledge
status: active
summary: Task/Record 身份不变量与 ID 撞车重分配方法论（scan→create 临界区、统一入口、不可变 record identity）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/timeline-integrity-gate
---

# Task / Record Identity Invariants（task-record-identity）

来源：T0261 交叉验证 + T0262 落地（`scripts/task_identity.py`、`flow_audit.py` audit fail-closed、identity_diagnostics）。

## 已证实的不变量

1. `task.id` 分配的 scan→create 必须处于同一个仓库级临界区；仅"扫描后取最大值+1"不能防并发同 ID。
2. task 创建入口必须统一：triage、to-tickets、Act follow-up 统一 CLI `task_identity.py create`；仅保护 promotion 仍留竞态旁路。
3. record identity 必须在 task 创建时生成并保持不可变；audit 不应在 record 缺失时把 `task.id` 当临时 record identity。
4. occurrence 目录 identity 必须等于 payload `record_id`；严格 fail-closed 投影保留问题可见性。
5. 历史目录归并只能由 immutable relocation/alias receipt 表达（绑定源/目标 identity、原因、时间、操作者、digest）；无 receipt 时保持错误。

## T0262 落地形态

- 统一原子入口：仓库级 flock + `_next_task_id` reservation + `O_EXCL` create-only + 异常清理半成品；`create_task` 强制 `record="{task_id}-{slug}"`，不一致抛 `RECORD_MISMATCH`。
- 入口收敛：triage/to-tickets/Act follow-up 统一 `task_identity.py create`；promotion 复用 `_create_task_unlocked`。
- audit fail-closed：移除 `task.id` fallback，缺 record/非法路径写入 `records/__quarantine/flow-audit.json`。
- 只读诊断 `identity_diagnostics`：重复 task ID、重复 slug、event path mismatch、record 派生不匹配；接入 `validate-workflow.py --all` 与 `pdca-doctor.py`。

## ID 撞车重分配方法论（T0274）

- **主流方判定**：被其他任务作 parent 引用（主干）→ 保留；无引用时 `Txxxx-slug` 规范格式优先；其余按创建时间早者保留。
- **上下文感知引用判定**：撞车组内可能存在两棵任务树，按引用者 slug 特征词判定归属（如 CDM/报表 vs RPC），避免字符串级误伤。
- **执行顺序**：先引用扫描后重命名；records 旧格式统一为 `Txxxx-slug`；目录重命名仅替换 `Txxxx-` 前缀；flow-events 内 `record_id`/`task_id` 必须同步；验证 doctor duplicate/event_path_mismatches 无新增。
- 含活跃任务的撞车组整组跳过。

## 来源

- `（原知识层）task-record-identity-invariants.md`
- `（原知识层）id-collision-remediation.md`
