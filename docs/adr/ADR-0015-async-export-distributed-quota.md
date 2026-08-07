# ADR-0015: Report-Web 异步导出与分布式读池配额

- 日期: 2026-08-07
- 状态: 已确认

## 背景

T0220 完成 report-web 报表模板查询与 CSV/PDF **同步**导出：请求线程内一次性
生成 bytes 返回，`csv_max_rows`(默认 4000)超限即截断并由 `X-Report-Truncated`
标注；逻辑读池配额为单进程 `threading.BoundedSemaphore`（Query16/Export2/Metric2），
参数硬编码在 `create_app` 默认值，未接入 `report.cfg`（生产 zero-param 调用全部
落默认值）。大数据量无法在请求内完成，且多实例部署时配额会重复计数。

T0224 作为 T0220 遗留架构改进，目标：任意大数据量的异步导出、读池配额跨实例
分布式化、超时/截断/配额参数可配置。

## 决策

### D1 异步导出产物：落盘文件 + 下载端点
异步任务把 CSV/PDF 结果写盘到导出目录 `report_web/data/exports/`，新增
持久任务状态表 `rpt_export_task`（id/状态/进度/产物路径/过期/创建者）。report-web
新增两条端点：`POST /export/async`（创建任务）与 `GET /export/async/{id}`（查询
状态+就绪下载链接）。放弃 DB BLOB 存储（大文件占库、扩展差）与对象存储集成
（当前部署无对象存储，工程量大）。

### D2 异步任务机制：自建进程内后台队列
不引入 APScheduler/celery/arq。report-web 进程内自建轻量后台队列：
`threading.Thread` worker + `queue.Queue`；任务状态写 `rpt_export_task`；
生成逻辑复用既有 `ExportService._iter_all`（keyset 分页）。模块级 handler 注册
范式沿用 collection-service 的 `JobHandlerRegistry`（`handler_code` 稳定字符串）。
report-web 单实例部署（systemd 单进程），进程内队列足以承载。

### D3 分布式配额：Redis 分布式租约
复用既有 `RedisKeyStore`（验证码/Token/限流在用）。把单进程
`ReadPoolQuota` 的 `BoundedSemaphore` 改为 Redis 原子计数租约：`INCR/DECR`
键 + TTL 租约，跨多 report-web 实例共享 query/export/metric 配额。耗尽返回
HTTP 429（语义同现状）。放弃"仅可配置化"与"保持单点"——以满足 meta.convergence
的"多实例分布式化"。

### D4 参数可配置化：全量接入 report.cfg
在 `report.cfg.example` 增加 `[web.export]` 与 `[web.quota]` section，把
`csv_max_rows`、pdf 页数/上限、导出超时、批次大小、query/export/metric 配额值
从 `create_app` 硬编码改为从配置读取。采集侧的 2s/30s 超时基线保持现状
（本次只引出网络层不变）。`create_app` 零参生产调用时回落到默认值。

### D5 同步/异步共存 + 超限自动转异步
保留既有 `/export` 同步端点（小数据量低延迟）；新增异步端点。请求行数超过
配置阈值 `async_threshold`（默认 = csv_max_rows 4000）时 `/export` 自动转异步，
返回 202 + 任务 ID；未超限保持同步流式。不破坏既有 API。

## 权衡

- 备选：DB BLOB 存结果 —— 放弃（大文件占 DB、扩展差，详见 D1）
- 备选：DB 对象存储 —— 放弃（当前链路无对象存储）
- 备选：APScheduler 移植 / celery+broker —— 放弃（引入 broker/进程依赖重，
  单实例配额队列足矣，详见 D2）
- 备选：配额仅可配置化不分布式 —— 放弃（不满足"多实例分布式化"收敛目标，
  见 D3）
- 备选：全部导出改异步 —— 放弃（破坏既有同步 API 低延迟语义，见 D5）

## 影响

- report-web 新增：异步导出端点、后台队列、`rpt_export_task` 表、Redis 配额
  租约、report.cfg 参数接线。
- 影响 `report_web/report/export_service.py`、`quota.py`、`app.py`、`connection.py`、
  `deploy/conf/report.cfg.example`、迁移目录。
- 既有同步导出 API 保持兼容（超限自动转异步为新增行为）。

## 回滚

- `git revert` 至 0.5.0（e9e9b24）。
- `rpt_export_task` 表由 down.sql 回退；异步端点移除后同步 `/export` 恢复
  原全同步逻辑。
- Redis 配额租约键可手动清理（TTL 租约自动释放）。