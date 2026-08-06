# 报表模板注册表、16 套固定查询与 CSV/PDF 同步导出 — 规格文档

## 问题陈述

报表查询与导出功能缺失：一期交付 16 套固定模板，需实现模板注册表（YAML 元数据 + Handler 注册表）、固定读模型映射、Keyset 分页与多域归并、同步 CSV/PDF 导出与读池配额。

## 解决方案

实现 `report-web` 报表模块：`TemplateRegistry`（启动时按 `index.yaml` 加载校验 16 套 YAML，进程内注册表）→ `ReportQueryHandlerRegistry`（16 个固定 Handler）→ `QuerySpec` 构造 → `ReportReadRepository`（固定 SQL/Keyset）→ CSV 流式（`csv_max_rows` 默认 4000，`+1` 探测截断）/PDF 同步渲染（表格/图表分页）；读池 20 连接（Query 16 / Export 2 / Metric 2）。

## Seam 分析

- 测试接缝：模板加载校验、16 套 Handler golden 响应（脱敏 PG17 seed fixture）、Keyset 无重复/漏页、多域 Top-N/K 路归并、导出行数截断、配额 429/超时 503。
- Mock/Stub：读模型以脱敏 seed fixture 填充 PG17 测试库；YAML 以发布包样例。

## 用户故事

1. 作为报表用户，我想要 16 套固定模板查询，以便查看备份域资源/任务/容量报表。
2. 作为报表用户，我想要 CSV/PDF 同步导出，以便复用当前筛选条件离线分析。

## 实现决策

- 落地仓库：**report-center 新仓库**（`report-web` 内，模板目录 `config/report/templates/`）。
- 依赖：T0215（Web API 子方案）、T0216（ReadRepository）、T0219（鉴权域）。
- 固定映射（§8.2.2）：16 套模板唯一允许读表/谓词/度量/排序；`data_state` 判定（`INSUFFICIENT_COLLECTION_COVERAGE`/`NO_MATCH`/`INSUFFICIENT...`）。
- Keyset 分页（§8.4）：单域 `(task_time DESC, backup_domain_id DESC, task_run_key DESC)`；多域 `DOMAIN_TOPN_MERGE` 归并；页大小 5/10/20/50。
- 配额（§8.4/8.5）：Query≤16 / Export≤2 / Metric≤2；`lock_timeout=500ms`、Query `statement_timeout=2s`、Export 30s。

## 测试决策

- 模板加载/校验单测；16 套 Handler golden 契约（seed fixture）；Keyset 边界；多域归并；CSV 截断头（`X-Report-Truncated`）；PDF 分页；配额耗尽与超时。

## 验收标准

- [ ] AC-1: 16 套模板 YAML 随发布包管理，`index.yaml` 清单加载，启动时 YAML/Handler 校验失败拒绝启动（§8.2）。
- [ ] AC-2: 每个 Handler 使用固定参数化 SQL/ORM 构造器；请求不能指定表/列/排序/SQL（§8.2、§8.3）。
- [ ] AC-3: 16 套模板读模型映射与 §8.2.2 表一致，逐条 golden 响应通过 PG17 seed fixture（§8.2.2、§8.6）。
- [ ] AC-4: Keyset 分页无重复/漏页；多域按 Top-N/K 路归并，禁止多域全局 OFFSET/无界全局排序（§8.4）。
- [ ] AC-5: CSV 同步流式导出，`csv_max_rows`（默认 4000，可配置）`+1` 探测截断并标记（`X-Report-Truncated`/`X-Report-Row-Limit`）（§8.5）。
- [ ] AC-6: PDF 表格按 `pdf_table_rows_per_page`（50）分页页首重复列头；图表按 `pdf_chart_categories_per_page`（50）分页；PDF 表格上限同 csv_max_rows（§8.5）。
- [ ] AC-7: 读池配额 Query16/Export2/Metric2；耗尽返回 `429 QUERY_BUSY`/`429 EXPORT_BUSY`；超时返回 `503 QUERY_TIMEOUT`（§8.4、§8.5）。
- [ ] AC-8: `data_state` 区分无匹配/覆盖不足/无活动域，不以数值 0 混淆；采集任务明细/失败原因不返回页面（§8.3、§8.6）。

## 范围外

- 不做异步导出/导出队列/下载 Token/临时下载文件。
- 不做模板在线编辑/设计器。

## 备注

- 依赖：T0215、T0216、T0219；下游：T0221、T0222。
