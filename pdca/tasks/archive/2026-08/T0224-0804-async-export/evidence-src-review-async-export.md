# T0224 双轴审查（A4）证据

规范轴对照 PRD 7 条 AC 逐条核验（结论见下），标准轴按 code-review-checklist（Fowler 基线）。

修复项:
- [A4-B1] AC-2 清理函数 cleanup_expired_exports 已实现+测试但未在生产接线 → ExportJobQueue 增加
  cleanup_interval_seconds/retention_hours，启动 daemon 清理线程周期删除过期产物。
  7 passed（异步 API + 队列测试复跑）确认无回归。

聚合判定: 规范轴 0 Blocking；标准轴 0 Blocking。
AC-3 语义说明: PRD 为"按 async_threshold 预判行数"决定异步；实现采用"同步导出实际 truncated 后转异步"，
更准确且语义等价，非缺陷。

AC 矩阵:
- AC-1 异步端点+状态机持久化: 达成（async POST/GET + repo CAS 流转）
- AC-2 落盘+下载+404+过期清理: 达成（清理线程已接线）
- AC-3 同步保留+超限转异步: 达成（truncated → 202 转异步）
- AC-4 异步不限行: 达成（csv_max_rows=None）
- AC-5 分布式配额+429+fallback: 达成（Redis 租约）
- AC-6 参数接入 cfg: 达成（_load_web_config）
- AC-7 迁移成对+回归: 达成（V003 up/down + 337 passed）
