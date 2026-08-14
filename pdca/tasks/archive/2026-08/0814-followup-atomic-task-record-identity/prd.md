# 跟进：统一 task/record identity 创建事务

## 问题陈述

- **现状**: T0261 已通过真实并发复现与真实 transition 路径证明：普通 scan→create 可生成重复 task ID（隔离复现实际产生两个 `T9001`）；audit 在 record 缺失时回退到 `task.id`，会为同一任务制造两个 record identity（真实 `transition-phase.py` 路径可稳定复现）。当前仅 promotion 有仓库级锁；triage、to-tickets、Act follow-up 仍直接扫描写文件。
- **目标**: 所有 task 创建入口共享同一原子事务，task 出生即拥有不可变 record identity，事件系统不再回退到 `task.id`，identity 缺陷被诊断工具机器可读暴露。
- **差距**: 缺统一创建入口、缺出生即分配的不可变 record、audit 有 fallback、无全局 ID/slug 唯一性与 path invariant 诊断。

## 解决方案

引入单一 `scripts/task_identity.py`：仓库级 flock 锁内完成 ID reservation、slug 查重、`meta.record` 生成与 `records/<record>/` 目录创建，再以 create-only（`O_EXCL`）写入 task.json、clarifications.jsonl 与 prd.md；任何一步失败整体回滚。triage、to-tickets、promotion 与 Act follow-up 全部改调此入口，skill 文档同步收敛。`flow_audit.py` 移除 `task.id` fallback，缺 record 时 fail-closed 并记录 `RECORD_MISSING`。`pdca_core.py` 提供全局 identity 诊断，`validate-workflow.py --all` 与 `pdca-doctor.py` 输出机器可读结果。历史 5 条 mismatch 不改写，仅诊断；relocation/alias receipt 列为后续候选。

## Seam 分析

### 测试接缝

- 统一创建事务在 `scripts/task_identity.py` 的函数/CLI 边界测试：并发进程、失败回滚、record 不可变、slug 冲突、create-only 语义。
- promotion 迁移后在 `scripts/flow_issues.py` 回归测试既有并发保护不退化。
- audit fallback 移除后在 `scripts/flow_audit.py` 测试缺 record 时的 fail-closed 行为。
- 全局诊断在 `scripts/pdca_core.py` 测试 ID/slug 唯一性与 event path==payload。
- 外部依赖（文件系统、并发进程）通过临时隔离仓库 fixture 隔离；锁行为用真实子进程验证，不 mock。

### 声明的测试接缝

- seam: tests/test_task_identity.py -> scripts/task_identity.py
- seam: tests/test_flow_audit.py -> scripts/flow_audit.py
- seam: tests/test_flow_issues.py -> scripts/flow_issues.py
- seam: tests/test_identity_diagnostics.py -> scripts/pdca_core.py

### 验收可测性

- 每个 AC 均有 pass/fail 信号：并发用子进程计数、身份不可变用重复写拒绝、fallback 移除用缺 record 场景断言不写事件、诊断用机器可读 JSON 断言。

## 用户故事

1. 作为多会话并发的 PDCA 用户，我希望并发创建任务不会拿到重复 task ID，以便任何会话创建的任务都全局唯一可引用。
2. 作为执行者，我希望任务出生时即有不可变 record identity 和对应目录，以便 audit/evidence/结论始终落在同一命名空间。
3. 作为审计者，我希望缺 record 时阶段推进明确失败并记录原因，而不是静默制造第二身份。
4. 作为管理员，我希望 doctor/validate 用机器可读方式报告重复 ID、重复 slug 与 path mismatch，以便持续监控。

## 实现决策

- 新增模块 `scripts/task_identity.py`，核心接口（供 CLI 与子进程共同使用）：
  - `create_task(root, *, slug, title, parent=None, dependencies=(), scenario_type, created_at, extra_meta=None) -> dict`：锁内做 `_reserve_task_id`（扫描 active+archive 取最大+1）、slug 查重、生成 `meta.record = f"{task_id}-{MMDD}-{slug}"` 并 `mkdir` 到 `records/<record>/`，create-only 写三个初始文件；失败清理已建目录与文件。
  - CLI：`python3 scripts/task_identity.py create --slug ... --title ... [--parent ...] [--dependencies ...] [--scenario-type ...] [--created-at ...] [--extra-meta json]`，输出 JSON（task_id、path、record、status）。
- `scripts/flow_issues.py::promote_candidate` 改为调用 `create_task`，传入 `improvement_source` 作为 `extra_meta`，删除自维护的锁/ID/写入分支，保留既有幂等 `unchanged` 语义。
- `scripts/flow_audit.py::audit_transition` 移除 `or task["id"]` fallback；缺 record 时 fail-closed：issues 增加 `RECORD_MISSING`，不写 fallback 事件。
- `scripts/pdca_core.py` 新增 `identity_diagnostics(root) -> dict`：全仓扫描 task.json 检查 task ID 与 slug 全局唯一；扫描 `records/*/flow-events` 检查事件目录与 payload `record_id` 一致。`validate-workflow.py --all` 与 `pdca-doctor.py` 输出并入。
- `skills/triage-work/SKILL.md`、`skills/to-tickets/SKILL.md`、`flows/flow-act/SKILL.md` 的创建指导改为调用 `task_identity.py`，删除"直接扫描写 task.json"步骤。
- `schemas/task.schema.json` 的 `meta.record` 保持非必填以兼容历史，但新创建必须带；`pdca_core.py` 校验 record 一旦设置不可改写。
- 架构决策记入 `docs/adr/ADR-0024-atomic-task-record-identity.md`。

## 测试决策

- 被测模块：`scripts/task_identity.py`、`scripts/flow_audit.py`、`scripts/flow_issues.py`、`scripts/pdca_core.py`。
- 好测试：只测外部行为（并发唯一、回滚清理、fail-closed、机器可读诊断），不测内部锁实现细节。
- 现有先例：`tests/test_flow_issues.py::test_concurrent_promotion_creates_one_task_even_with_different_requested_slugs` 的子进程并发模式、`tests/test_flow_audit.py` 的临时仓库 fixture。

## 验收标准

- [ ] AC-1: 所有 task 创建入口共享同一仓库锁、ID reservation 和 create-only 失败恢复语义。
- [ ] AC-2: 50 个并发创建请求不产生重复 task ID 或重复 record identity。
- [ ] AC-3: 新任务创建完成时即具有不可变 `meta.record`，后续变更身份被拒绝。
- [ ] AC-4: record 缺失时 audit 不向 `records/<task-id>/flow-events` 写入 fallback 事件。
- [ ] AC-5: 新事件全部满足目录 identity 等于 payload `record_id`。
- [ ] AC-6: 历史 occurrence 字节不被修改；兼容路径缺少有效 receipt 时 fail closed。
- [ ] AC-7: promotion 既有并发测试与完整相关测试集通过。
- [ ] AC-8: 上线后观察至少 14 天或 20 个真实新任务，并与 T0261 baseline 配对报告 duplicate、missing record、mismatch、创建失败和人工恢复。

## 范围外

- 不重写或删除既有 task、record、occurrence。
- 不实现 relocation/alias receipt 的 schema 与写入工具（列为后续改进候选）。
- 不为 5 条历史 mismatch 补写 receipt 或操作者归因。
- 不把 `meta.record` 变为 schema 强制必填（历史兼容）。
- 不引入 quarantine/system 第二事件命名空间。

## 备注

- AC-8 的观察窗必然跨周期：本任务收敛到"部署完成 + 冻结 baseline + 记录上线时刻"，观察判定由独立 follow-up 任务承接。
- 术语与不变量以 `knowledge/pdca-flow/task-record-identity-invariants.md` 为准。
- 开发顺序：先写失败测试（并发、身份不可变、fallback fail-closed、诊断），再实现，再迁移 promotion 与 skill 文档。
