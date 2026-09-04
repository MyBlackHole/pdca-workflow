---
schema: pdca.asset/v1
id: ontology:domain/report-center-async-export-distributed-quota-patterns
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/report-center-async-export-distributed-quota-patterns/1.0.0
summary: 异步导出与分布式配额模式（report-center）
domain:
- ontology:domain/report-center
relations:
  specializes:
  - ontology:domain/report-center
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q '异步导出与分布式配额' ontology/domain/report-center/report-center-async-export-distributed-quota-patterns.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


---
knowledge: report-center/async-export-distributed-quota-patterns.md
source: records/T0224-0804-async-export/conclusion.md
---

# 异步导出与分布式配额模式（report-center）

## 背景

大数据量报表导出受同步链路硬限制（30s 超时、4000 行截断）阻碍，且多实例部署下读池配额各自为政。T0224 落地异步后台导出 + Redis 分布式配额租约，以消除这些限制。

## 可复用模式

### 1. 进程内后台任务队列 + 状态机持久化

- **模式**：`ExportJobQueue`（进程内线程 worker 消费 FIFO task_id 队列）+ `run_export_task` 状态机（queued→running→completed/failed），任务状态持久化到独立表（`rpt_export_task`），CAS 流转保证幂等。
- **落盘与清洗**：产物写 output_dir，`cleanup_expired_exports` 定期线程按 retention_hours 删除过期表+文件。
- **要点**：队列线程 worker 数默认 1，天然串行限流；后台线程与请求线程共享 DB 连接池。

### 2. 同步保留 + 超限自动转异步

- 超大数据导出不破坏既有同步链路：同步导出若实际 truncated，则转异步（返回 202 + task_id）。比"按预估行数阈值"更准确且语义等价。
- 异步导出用 `csv_max_rows=None` 破除截断，支持批量分页遍历。

### 3. Redis 分布式配额租约（多实例共享）

- `read_pool_quota` 采用双后端：Redis 租约（INCR/DECR + TTL）跨实例共享资源上限；无 Redis 时退化本地信号量（保证单实例正确性，分布式失效需配置告警）。
- 用 `key_store` 依赖注入隔离 infra，耗尽返回 429。多实例压测验证守护。

## 迁移模式：为新增独立表适配回滚测试

- 新增独立表（`rpt_export_task`）的迁移要**成对 up/down**。
- 既有 `test_down_rolls_back_tables` 原先只回滚 V001，会遗留 V002/V003 表、重放冲突；改为**倒序回滚全部 specs（V002→V001）**后再清审计重放，兼容新增独立表。清理测试库 schema（`DROP rpt_*` + 重置 `rpt_schema_migration`）后恢复。

## 适用边界 / 风险

- 异步任务不受读池配额保护，靠 workers=1 默认限流；扩 workers 需显式接入配额。
- 无 Redis 时配额退化为各实例本地独立（同旧现状），需配置告警。
- 状态机用字符串 + DB CHECK 兜底，无独立枚举。