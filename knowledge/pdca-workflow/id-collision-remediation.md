# ID 撞车重分配方法论（T0274）

## 场景

历史任务重复分配 task_id（`identity.duplicate_task_ids` 撞车组）。每组同一 task_id 被 2-3 个真实独立任务占用，各自有独立 task.json/record/归档状态。需全链路重分配：为"非主流"方分配新 ID，同步 task.json、records 目录、parent/children 引用链、归档目录名。

## 主流方判定规则

1. 被其他任务作为 parent 引用（任务树主干）→ 保留原 ID。
2. 无引用时，record 格式规范（`Txxxx-slug`）优先；旧格式（`Rxxxx` 或裸 `Txxxx`）重分配。
3. 其余按创建时间早者保留。

## 上下文感知引用判定（关键）

**问题**：撞车组内可能存在两棵任务树（如 T0214 的 CDM/报表树 与 RPC 树），两树子任务 parent 均指向同一旧 ID。字符串级替换无法区分归属，会误伤另一棵树。

**解法**：按引用者 slug 特征词判定归属——

- CDM/报表链特征词：`report`、`cdm`、`collection`、`deployment`、`acceptance`
- RPC 链特征词：`rpc`、`worker`、`epoll`

命中 CDM 特征且非 RPC → 引用指向重分配方，parent 改向新 ID；命中 RPC 特征 → 引用指向保留方，保持旧 ID。

**限制**：
- 特征词需人工核定，确保与真实任务树命名一致。
- 无法区分时须回退到显式枚举引用者目录。
- 含活跃任务的撞车组（DEFERRED_IDS）整组跳过，任何任务（含归档侧）都不改写。

## 脚本模板（scripts/remediate-id-collisions.py）

- `REASSIGNMENTS` 常量裁决表：旧 ID → (纯 slug 目录片段, 新 ID)。
- **纯 slug + 后缀匹配定位**目录：支持 `<slug>` 与 `<Txxxx>-<slug>` 两种命名，重命名后重跑仍可定位（幂等）。
- 三校验模式：
  - `--check-cover`：裁决表覆盖 doctor 全量（apply 前）。
  - `--check-disposable`：可处置组必须全部 archive。
  - `--check-deferred`：待办组必须含活跃任务。
- 幂等性：重复 apply 无二次改写（digest 一致）。

## 执行顺序（安全要点）

1. **先引用扫描，后重命名**：引用归属判定须在 records/目录重命名前完成。
2. records 旧格式（R0142/R0244/裸 T0225）统一为 `Txxxx-slug` 规范格式，验证无外部引用后执行。
3. 目录重命名仅替换 `Txxxx-` 前缀为 `Tyyyy-`，不改变 slug 主体。
4. **flow-events 同步**：records 目录重命名后，`records/<record>/flow-events/*.json` 内的 `record_id`/`task_id` 字段必须同步为新值，否则 doctor `event_path_mismatches` 新增（T0274 教训：初始遗漏 22 项，补同步后恢复基线）。
5. 验证指标：doctor duplicate_task_ids 降至仅剩活跃待办组；event_path_mismatches 无新增；无新增悬空引用。

## 复用指引

后续 11 组含活跃任务的撞车（T0216/T0218/T0219/T0220/T0221/T0222/T0228/T0229/T0248/T0250/T0252）归档后，追加 REASSIGNMENTS 裁决表项即可复用本方法论。
