# ADR-0024：统一 task/record identity 原子创建事务

## 状态

Proposed

## 背景

T0260 发现 23 个 task ID 冲突与 5 条 event path mismatch；T0261 用真实历史、隔离仓库并发复现与真实 transition 路径证明：普通 scan→create 缺少仓库级临界区会生成重复 task ID，audit 在 `meta.record` 缺失时回退到 `task.id` 会为同一任务制造两个 record identity。当前仅 promotion 有锁，triage、to-tickets、Act follow-up 直接扫描写文件，违反已证实的不变量：task 创建必须处于仓库级临界区，record identity 必须在创建时生成且不可变。

## 候选方案

1. 仅全局原子 task ID 分配器：解决 ID 冲突，但 audit fallback 仍会制造第二 record identity，身份分裂问题未解决。
2. 仅以不可变 record identity 为主键：解决身份分裂，但 task ID 冲突仍可能让引用歧义。
3. 组合方案（推荐）：单一创建入口在锁内完成 ID reservation + slug 查重 + record 生成 + create-only 写入；audit 移除 `task.id` fallback 并 fail-closed；诊断工具机器可读暴露剩余异常。

## 决策

选择方案 3。新建 `scripts/task_identity.py` 作为唯一 task 创建入口，`triage`、`to-tickets`、promotion 与 Act follow-up 全部改调；task 出生即生成不可变 `meta.record` 并创建 `records/<record>/`；`flow_audit` 缺 record 时 fail-closed 且不写 fallback 事件；`pdca_core` 提供全局 ID/slug 唯一性与 event path==payload 诊断。历史事件不自动改写，mismatch 只能通过后续的 immutable relocation/alias receipt 显式解释。

## 后果

- 消除新 task ID 冲突与 record 双身份，flow backlog 可投影。
- 统一入口迁移不完整会形成双轨：skill 文档与脚本同步收敛，禁止直接写 task.json。
- 出生即建 `records/<record>/` 会增加空目录，换取身份路径不可分裂。
- 历史 5 条 mismatch 保持可见错误直到 receipt 机制就绪，不改写不可变事件。
- 观察窗跨周期，由独立 follow-up 任务以 baseline 配对判定 effectiveness。
