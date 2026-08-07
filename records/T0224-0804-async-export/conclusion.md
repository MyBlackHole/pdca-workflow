---
schema: pdca.asset/v1
id: T0224-0804-async-export
phase: check
source_ids:
  - test-async-export
  - review-async-export
  - migration-async-export
  - convergence-map2
---

## 上下文

T0224 源自 T0220 遗留架构改进，目标是打破同步导出 30s/4000 行的硬限制，并将读池配额从单实例信号量升级为多实例 Redis 分布式租约，同时让超时/截断/批处理等参数可配置化。Do 阶段按 development 场景完成 5 项计划决策的全量实现，版本 0.5.0 → 0.6.0。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| 异步/后台导出覆盖任意大数据量 | 达成：异步任务不受同步 30s/4000 行截断；csv_max_rows=None 全量导出 | test-async-export |
| 读池配额多实例分布式化 | 达成：Redis 租约（INCR/DECR+TTL）跨实例共享，耗尽 429，无 Redis fallback 本地 | test-async-export |
| 超时/截断参数可配置 | 达成：[web.export]/[web.quota] 接入 report.cfg | review-async-export |
| 迁移成对可回滚 | 达成：V003 add 独立表 up/down 成对，test_down_rolls_back_tables 适配 | migration-async-export |

## 分析

- 全量回归 337 passed, 0 failed（6 既有 JWT 环境 errors 非本次变更），双轴审查 Blocking=0，收敛映射 valid=true。
- 双轴审查修复一个规范缺口：AC-2 过期清理函数已实现但有测试却未接线到生产，经修复 ExportJobQueue 增加 cleanup_interval_seconds/retention_hours 与 daemon 清理线程。
- 规范轴一处语义：AC-3 PRD 为按 async_threshold 预判行数决定异步，实现用「同步导出实际 truncated 后转异步」，更准确且语义等价，非缺陷。

## 适用边界

- 异步任务并发受 ExportJobQueue workers=1 默认串行限流，未直接受读池配额保护；调大 workers 需显式接入配额。
- 无 Redis 时多实例配额退化为各实例本地独立（同 T0220 现状），需配置告警提示 Redis 缺失。
- 状态机用字符串 + DB CHECK 约束，无独立枚举类型。
- 异步任务后台线程与请求线程共享 psycopg pool，受默认 workers 限制未见超池风险。

## 下一轮建议

- 若多实例压测，评估调大 workers 时对异步任务的显式读池配额保护接入。
- 可考虑将 ExportTask 状态机改为独立观测/审计链路（当前仅仓库流转）。
- 若有 T0 220 后续，可将超限转异步判定从「实际截断」扩展为「预估行数阈值」双信号。