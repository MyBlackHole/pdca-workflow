# T0224 跟进：异步导出与分布式配额 — 规格文档

## 问题陈述

- **现状**: report-web 报表导出（CSV/PDF）完全同步，在请求线程内一次性生成
  bytes 返回；`csv_max_rows`（默认 4000）超限即截断并由 `X-Report-Truncated`
  标注；导出期间持有读连接配额（Export2）跨多个短事务循环读取。逻辑读池配额
  （Query16/Export2/Metric2）为单进程 `threading.BoundedSemaphore`，多实例部署
  时配额重复计数。导出参数（行数/超时/批次/配额值）硬编码在 `create_app`
  默认值，未接入 `report.cfg`（生产 zero-param 调用全部落默认值，无法运维调节）。
  report-web 进程内无任何后台任务机制。
- **目标**: 任意大数据量的导出不受请求超时与 4000 行截断限制；读池配额跨
  report-web 多实例分布式共享；导出相关参数可配置。
- **差距**: 同步导出无法承载大数据量；配额单点不满足多实例；参数硬编码不可
  运维调节；无后台任务基建。

## 解决方案

保留既有同步 `/export` 端点（小数据量低延迟）；新增异步导出能力：请求行数超过
阈值自动转异步，后台队列生成 CSV/PDF 落盘，下载端点按任务 ID 拉取产物。读池
配额改为 Redis 分布式租约。导出参数全部接入 `report.cfg` 的 `[web.export]` 与
`[web.quota]`。

## Seam 分析

### 测试接缝
- 异步任务队列：进程内队列入队/执行/状态流转，单测构造任务不连真实 DB。
- 导出落盘/下载：导出目录临时文件 + 状态表，测试隔离用 `tmp_path`。
- 分布式配额：Redis 租约逻辑用 mock 键操作；真实 Redis 用 conftest 集成。
- 迁移：`rpt_export_task` 表 up/down 成对，沿用 PostgreSQLMigrationAdapter。

### 验收可测性
- 每个 AC 有明确 pass/fail 信号（状态=queued/running/completed/failed、文件存在、
  429/202 响应、参数读配置生效）。
- 边界：超限自动转异步（阈值）、配额耗尽 429、任务不存在 404、产物过期清理。
- 分层：单元测试（导出服务/配额/队列）+ 集成测试（迁移/API 装配）。

## 用户故事

1. 作为报表用户，我想要大数据量导出不因请求超时/4000 行截断失败，以便获取
   完整数据。
2. 作为运维，我想要导出参数（行数/超时/批次/配额）可从 report.cfg 调节，以便
   按主机能力调优。
3. 作为运维，我想要多实例 report-web 共享读池配额，以便多实例部署不超读连接。
4. 作为运维，我想要异步任务状态与产物下载可追踪，以便确认导出完成并取回文件。

## 实现决策

- 新增/修改模块：
  - `report_web/report/export_service.py` — 复用 `_iter_all` keyset 循环，新增
    异步写入落盘；新增 `async_threshold` 判定。
  - `report_web/report/export_async.py`（新增）— 进程内后台队列 worker、任务
    状态机（queued→running→completed/failed）、产物路径与过期清理。
  - `report_web/report/quota.py` — `ReadPoolQuota` 改 Redis 分布式租约
    （INCR/DECR + TTL），单点信号量逻辑保留为 fallback。
  - `report_web/app.py` — 新增 `POST /export/async`、`GET /export/async/{id}`；
    `/export` 超限自动转异步（202）。
  - `report_center_db/postgres/export_task.py`（新增）— `rpt_export_task` 表
    CRUD/状态流转。
  - `migrations/postgresql/V002__export_task.up.sql/down.sql`（新增）。
  - `deploy/conf/report.cfg.example` — 增加 `[web.export]`（csv_max_rows、
    pdf_max_tabular_rows、pdf_table_rows_per_page、async_threshold、export_
    timeout_ms、batch_size）与 `[web.quota]`（query/export/metric）。
  - `report_web/config.py`（或 app 装配）— 从 report.cfg 读导出/配额参数。
- 接口定义：
  - `POST /export/async`：body 同 `/export`（template_code+filter+format），
    返回 `{task_id, status}` 202。
  - `GET /export/async/{task_id}`：返回 `{status, progress?, download_url?,
    expires_at?}`；completed 时 `download_url` 指向产物文件。
  - Redis 租约键：`report:quota:{type}`，INCR 超上限拒绝，DECR/TTL 释放。
- 架构决策：见 `docs/adr/ADR-0015-async-export-distributed-quota.md`。
- 数据模型变更：`rpt_export_task`（id uuid PK、template_code、params jsonb、
  status、progress int、product_path、expires_at、created_by、created_at、
  updated_at）。

## 测试决策

- 只测外部行为：API 响应码、状态流转、文件产物存在、配额 429。
- 被测模块：`test_export_async.py`（队列/状态机/落盘）、`test_quota.py` 扩展
  （Redis 租约）、`test_report_templates_api.py` 扩展（异步端点/自动转异步）、
  `test_migrations.py` 扩展（V002 成对）。
- 先例：`tests/test_export_service.py`、`tests/test_quota.py`、
  `tests/test_report_templates_api.py`、`tests/test_migrations.py`。

## 验收标准

使用规范 Markdown checkbox；系统按出现顺序确定 `AC-1`、`AC-2`……。

- [ ] AC-1: 异步导出端点 `POST /export/async` 创建任务返回 202 与 task_id；任务
  状态经 queued→running→completed/failed 流转并持久化到 `rpt_export_task`。
- [ ] AC-2: 完成的任务产物落盘（CSV/PDF）并由 `GET /export/async/{task_id}`
  返回可下载链接；任务不存在返回 404；产物带过期时间并可清理。
- [ ] AC-3: 既有 `/export` 同步端点保持兼容；请求行数超过 `async_threshold`
  自动转异步返回 202（不截断），未超限保持同步流式返回。
- [ ] AC-4: 导出任务执行不受单请求 30s statement_timeout 限制；大数据量导出
  无 4000 行截断（无 `X-Report-Truncated` 截断行为）。
- [ ] AC-5: 读池配额改为 Redis 分布式租约；多实例共享 query/export/metric 配额，
  耗尽返回 HTTP 429；单点 BoundedSemaphore 逻辑保留为无 Redis fallback。
- [ ] AC-6: 导出参数（csv_max_rows/pdf 页/超时/批次/async_threshold）与配额值
  （query/export/metric）从 `report.cfg` 的 `[web.export]`/`[web.quota]` 读取；
  零参 create_app 回落默认值；report.cfg.example 同步增加示例。
- [ ] AC-7: `rpt_export_task` 迁移 up/down 成对，全量回归通过（含既有 JWT 环境
  问题外）。

## 范围外

- collection-service 的采集任务机制不改动（异步导出只在 report-web 进程内）。
- 对象存储集成（无当前部署依赖）。
- 页面查询 2s/导出 30s 采集超时基线不调整（网络层不变）。
- 物理连接池（min/max/connect_timeout）本次不接 report.cfg（走既有环境变量）。

## 备注

- 参照 collection-service 的 `JobHandlerRegistry`（handler_code 稳定字符串）范式
  设计导出 handler 注册，避免 RPC 跨进程传递 callable。
- Redis 租约需要处理实例崩溃释放（TTL 租约自动过期）。
- 配额口径：quota.py 注释"读池共 20 条连接"与 connection.py 默认 max_size=10
  不一致——本次以 report.cfg 配置为准统一。
