## 当前状态

T0261 research 已完成 Check，用户确认 `partial`。根因证据、方案比较和正式结论已登记；Act 已沉淀确定性身份不变量，并创建 development 跟进 T0262。

## 未完成事项

- T0262 仍在 Plan，必须完成 Grill、方向确认、PRD/测试 seam 细化和 final confirmation。
- 实施后需观察至少 14 天或 20 个真实新任务，不能用 fixture 代替 effectiveness verdict。

## 已知约束

- 不改写历史 task、record 或 occurrence。
- T0252 的具体历史搬移命令没有 receipt，保持 inconclusive。
- 工作区包含大量用户既有未提交变更，禁止 `git add -A` 或提交不相关文件。
- `PDCA_HOME` 未设置时当前以仓库根目录 fallback；外部项目使用前应配置。

## 推荐的下一步

从 T0262 的 Plan 开始，先审核统一创建事务的锁粒度、跨文件失败恢复、record identity 格式、audit 缺 record 时的 fail-closed/quarantine 语义，以及历史 relocation receipt 是否属于 P0。

## 关键上下文文件列表

- `records/T0261-0814-followup-task-record-identity/conclusion.md`
- `records/T0261-0814-followup-task-record-identity/evidence/manifest.jsonl`
- `pdca/tasks/0814-followup-task-record-identity/solution-comparison.md`
- `knowledge/pdca-flow/task-record-identity-invariants.md`
- `pdca/tasks/0814-followup-atomic-task-record-identity/prd.md`

## Suggested skills

- `flows/flow-plan`
- `skills/grilling`
- `skills/to-tickets`（仅在拆解确有独立周期时）
- `flows/flow-do`
- `skills/register-evidence`
- `skills/verify-convergence`
