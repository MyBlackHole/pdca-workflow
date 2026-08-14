---
schema: pdca.asset/v1
id: T0262-0814-followup-atomic-task-record-identity
phase: check
source_ids: [ac1-shared-entry-tests, ac2-concurrent-unique, ac3-immutable-record, ac4-no-fallback-quarantine, ac5-identity-diagnostics, ac6-history-failclosed, ac7-full-test-suite, ac8-frozen-baseline, convergence-map]
---

## 上下文

T0261 验证了 record 机制确实发现真实缺陷，并推荐组合方案：所有 task 创建入口统一进入仓库级原子创建事务；task 出生即分配不可变 record identity；audit 取消 `task.id` fallback；历史只诊断不改写。本任务（T0262）实施该方案，覆盖 triage、to-tickets、promotion、Act-followup 四个创建入口，并接入统一诊断。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：统一原子创建事务（仓库锁 + ID reservation + create-only 写入 + 失败回滚）能保证并发下 ID 与 record 唯一 | **supported**：`scripts/task_identity.py` 通过 `flock` 仓库锁 + `_next_task_id` reservation + `O_EXCL` create-only + 异常时清理半成品；50 并发测试保持唯一（`test_concurrent_create_keeps_task_ids_unique` 通过）。 |
| H2：task 出生即带不可变 `meta.record`，且身份被后续变更时拒绝 | **supported**：`create_task` 强制 `record = "{task_id}-{slug}"`，传入不一致 record 抛 `RECORD_MISMATCH`；T0262 自身 task.json 即带正确 record。 |
| H3：record 缺失时 audit 不再 fallback 到 `task.id`，而是 fail closed | **supported**：`flow_audit.py` 移除 fallback，缺 record 报 `RECORD_MISSING`、非法路径报 `AUDIT_RECORD_PATH_INVALID`，写入 `records/__quarantine/flow-audit.json`；不向 `records/<task-id>/flow-events` 写第二身份。 |
| H4：历史 occurrence 字节不被修改，只诊断 | **supported**：`identity_diagnostics` 只读扫描，无任何写入；AC-6 测试覆盖。 |
| H5：诊断层面（validate-workflow --all / pdca-doctor）能体现 identity 健康度 | **supported（有边界）**：`--all` 并入 identity 使 valid 红灯；doctor 的全局 valid 不并入 identity，避免历史冲突使环境检查永久 red。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 统一入口共享锁/reservation/create-only | ac1-shared-entry-tests（test_task_identity 5 项） | Passed |
| AC-2 50 并发不重复 | ac2-concurrent-unique | Passed |
| AC-3 出生即不可变 record，变更被拒绝 | ac3-immutable-record | Passed |
| AC-4 缺 record 时不写 fallback 事件 | ac4-no-fallback-quarantine（test_flow_audit 3 项） | Passed |
| AC-5 新事件目录 identity == payload record_id | ac5-identity-diagnostics（7 项诊断测试） | Passed |
| AC-6 历史字节不改写；兼容缺 receipt 时 fail closed | ac6-history-failclosed | Passed |
| AC-7 promotion 既有并发测试与完整相关测试集通过 | ac7-full-test-suite：27 passed（本任务相关），全量非 doctor 180 passed | Passed |
| AC-8 冻结 baseline + 记录上线时刻，观察由 follow-up 承接 | ac8-frozen-baseline：identity-baseline.json | Deployed（观察中） |

### 关键实现决策

- **统一入口**：`scripts/task_identity.py` 自包含 `TaskIdentityError`，`_create_task_unlocked` 被 `flow_issues.py` 的 `promote_candidate` 复用；promotion 持 `_promotion_lock` 再调 `_create_task_unlocked`，避免重入加锁死锁。
- **fail-closed 审计**：缺 record / 非法 record 路径写入 `records/__quarantine/flow-audit.json`，`record_id` 为 null；这是 AC-4 的直接落地，也是 AC-6"兼容路径缺 receipt 时 fail closed"。
- **身份诊断**：`identity_diagnostics` 新增 `record_derived_mismatches` 维度（record 存在但不等于派生的 `T{id}-{slug}`），与 duplicate IDs、duplicate slugs、event path mismatch 并列；缺失 record 的历史任务不计冲突（AC-6 不改写）。
- **seam 契约**：为 4 个新测试文件补充 `SEAM_TARGET` 锚点，本任务 PRD 声明的 seam 全部干净（`seam_contract.py` 对 T0262 PRD 返回 valid=true）。

### 已知边界（非本任务引入）

- `tests/test_operations.py` 的 `test_doctor_uses_explicit_fallbacks` 与 `test_doctor_reports_seam_contracts_segment` 在真实仓库失败，原因：9 个既有外部任务（round66/67 系列）PRD seam 声明指向外部 C++ 测试文件（本仓库不存在），doctor 在真实仓库返回非零。已在 `git stash` 基线验证：**stash 掉本任务全部改动后这两个测试同样失败**，确认是既有环境状态，非本任务回归。
- `identity_diagnostics` 当前报告 25 个 duplicate task IDs、4 个 duplicate slugs、5 条 event path mismatch、20 条 record_derived_mismatch。这些是 T0140 之前旧约定（`R-{id}-{name}`）与未迁移任务的历史状态；按 AC-6 只诊断不改写，作为冻结 baseline 上报。

## 失败原因（仅 rejected/partial）

无。本任务全部 AC 通过，无 rejected/partial 项。

## 适用边界

- 统一入口保证**新**任务唯一；历史 25 个冲突 ID 与 20 条 record 派生不一致仍待人工处置（T0261 建议的 relocation receipt 机制未实施，属后续候选）。
- 兼容路径（补写过的 record 切换）缺 relocation receipt 时 fail closed，但已有 quarantine 事件的处置策略尚未定义。
- AC-8 的 effectiveness verdict 需要 14 天或 20 个真实新任务的观察数据，本任务仅完成部署 + 冻结 baseline + 记录上线时刻（2026-08-14T23:46:16+08:00 transition 进入 check）。
- doctor 的全局 valid 可能因既有外部任务的 seam 而 red，与 identity 改造无关。

## 下一轮建议

1. 创建独立观察 follow-up 任务：14 天后或累计 20 个经统一入口创建的真实新任务后，对照 T0261 baseline（23 dup / 47 slug / 49 task / 5 mismatch）与本任务 baseline（25 dup / 4 slug / 5 mismatch / 20 record-mismatch）报告 duplicate、missing record、mismatch、创建失败和人工恢复次数。
2. 处置 20 条 record_derived_mismatch（旧 `R-` 约定任务）与 25 条 duplicate：评估批量迁移或 alias receipt。
3. 定义 `__quarantine/flow-audit.json` 事件的转正/废弃处置流程。
4. 评估外部 round66/67 任务 seam 缺失是否应由 `seam_contract` 忽略外部项目 seam，或将 doctor 的环境假设与真实仓库隔离。