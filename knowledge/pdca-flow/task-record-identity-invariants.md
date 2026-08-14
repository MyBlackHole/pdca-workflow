# Task / Record Identity Invariants

来源：T0261 对真实任务历史、真实 transition 路径和并发创建行为的交叉验证；T0262 实施方案落地（统一入口 `scripts/task_identity.py`、audit fail-closed、身份诊断）。

## 已证实的不变量

1. `task.id` 分配的 scan→create 必须处于同一个仓库级临界区。仅“扫描 active/archive 后取最大值加一”不能防止并发会话选择相同 ID。
2. task 创建入口必须统一。只保护 Improvement Candidate promotion，而让 triage、to-tickets 或 Act follow-up 继续直接写文件，仍会留下竞态旁路。
3. record identity 必须在 task 创建时生成并保持不可变。audit 不应在 record 缺失时把 `task.id` 当作临时 record identity，因为后续补 record 会让同一 task 产生两个事件命名空间。
4. occurrence 的目录 identity 必须等于 payload `record_id`。严格 fail-closed 投影能保留问题可见性，不应通过自动改写事件消除异常。
5. 历史目录归并只能由 immutable relocation/alias receipt 表达。receipt 至少绑定源 identity、目标 identity、原因、时间、操作者/工具和事件 digest；没有 receipt 时保持错误，而不是猜测迁移意图。

## T0262 落地形态

- 统一原子入口 `scripts/task_identity.py`：仓库级 flcok 锁（`/tmp/pdca-task-identity-{sha256(root)}.lock`）+ `_next_task_id` reservation + `O_EXCL` create-only 写入 + 异常时清理半成品；`create_task` 强制 `record = "{task_id}-{slug}"`，不一致抛 `RECORD_MISMATCH`。
- 入口收敛：triage、to-tickets、Act follow-up 统一 CLI `task_identity.py create`；promotion 复用 `_create_task_unlocked`（持 `_promotion_lock` 不重入加锁）。
- audit fail-closed：`flow_audit.py` 移除 `task.id` fallback，缺 record（`RECORD_MISSING`）或非法路径（`AUDIT_RECORD_PATH_INVALID`）写入 `records/__quarantine/flow-audit.json`（record_id 为 null），不向 `records/<task-id>/flow-events` 写第二身份事件。
- 只读诊断：`identity_diagnostics` 报告 duplicate task IDs、duplicate slugs、event path mismatch、`record_derived_mismatches`（record 存在但不等于派生的 `T{id}-{slug}`）；缺失 record 的历史任务不计冲突（历史不改写）。接入 `validate-workflow.py --all`（并入 valid）与 `pdca-doctor.py`（不并入全局 valid，避免历史冲突使环境检查永久 red）。
- seam 契约锚点：新测试文件以 `SEAM_TARGET` 常量承载被测模块路径，满足 `seam_contract.py` 的目标引用校验。

## 验证方式

- 正例：并发创建至少两个不同 slug，断言 task ID 全局唯一。
- 负对照：受仓库锁保护的 promotion 并发创建只产生一个授权任务。
- 身份生命周期：同一 task 在任何阶段生成的事件只进入一个 record identity。
- 历史兼容：源事件字节不变；只有 digest 匹配的 relocation receipt 可以参与派生读取。
- 真实观察：上线后至少 14 天或 20 个真实新任务，按创建入口统计 duplicate ID、missing record、path mismatch、创建失败和人工恢复。

## 证据边界

上述规则由当前机制和可执行复现支持。它们不证明既有每个重复 ID 都由并发造成，也不证明 T0252 历史事件由哪个命令搬移；缺少 receipt 的历史归因必须保持 `inconclusive`。
