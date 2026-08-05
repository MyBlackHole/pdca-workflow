# T0223 Triage Brief — worker 接线适配层

## 分类
- category: enhancement
- scenario_type: development
- 来源: T0218 conclusion 下一轮建议（真实 Worker 未接入调度链路等已知限制）

## 验证结果
继承 T0218 已归档结论（verdict=confirmed），以下缺口经代码实测确认：
1. `JobHandlerRegistry.register()` 全仓无调用点（job_spec.py:64 仅定义）——scheduler 触发时 `registry.get(topic)` 抛 `JOB_SPEC_INVALID`（job_spec.py:83）
2. `TaskRepository` 仅 Protocol（workers/base.py:32），无 SQLAlchemy 实现；`increment_retry`/`update_status` 持久化缺失
3. `Ingester` 仅 Protocol（workers/base.py:47），未接入 report-center 入库事务
4. RPyC `allow_pickle=True` + `allow_all_attrs=True`（app.py:69）安全收紧未做

## 查重
- pdca/tasks（active+archive）：无同类任务（T0219 为 report-web，T0220 为 templates，不重叠）
- knowledge/report-center/：db-adapter-pg-practices.md（T0216）、cli-from-scratch-lazy-import.md（T0217）可复用，非重复
- 无 out-of-scope 冲突

## 信息缺口
- 真实 TaskRepository 的建表（report-db 库的 task 表）是否已由 T0216 迁移提供？——需在 P1/P2 确认 report-center 的 report_center_db 层现有 schema
- Ingester 复用 T0216 report-db adapter 的入库能力，还是需要新适配？

## 推荐下一步
进入 P1 澄清：读取 report-center 仓库现有 report_center_db 层，确认 TaskRepository 持久化可复用的基础
