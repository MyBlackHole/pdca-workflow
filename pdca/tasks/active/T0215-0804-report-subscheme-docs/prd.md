# 补齐三份报表中心子方案契约文档 — 规格文档

## 问题陈述

主方案 `cdm-report-center-final-technical-solution.md`（需求 140）引用了三份"可独立阅读、与本方案契约保持一致"的子方案，但当前仓库中均不存在：

- `cdm_report_center_web_api_subscheme.md`（Web API 契约）
- `cdm_report_center_collection_service_subscheme.md`（Collection Service 契约）
- `cdm_report_center_cli_subscheme.md`（CLI 契约）

后续所有实现子任务（T0216~T0222）以这些契约为输入。

## 解决方案

按主方案章节提炼并补齐三份子方案，每份内容必须与主方案已冻结边界一致，不得引入新范围。

## Seam 分析

- 验收以"与主方案逐条可追溯 + 契约项无遗漏/无新增"为 pass/fail 信号；人工 + checklist 复核。
- 契约项覆盖：RPC Job 契约（4.2.1）、JSONL 契约（6.2）、CLI 参数白名单/Keyset（CLI 子方案）、Web API 请求/返回契约（3.1）。

## 用户故事

1. 作为实现者，我想要三份契约文档，以便 report-web / collection-service / cdm-data-cli 有唯一实现输入。

## 实现决策

- 落地仓库：**aio-cdm 本仓**，与主方案同目录（`/home/black/Downloads/aio-cdm/`）。
- 三份文档分别从主方案 1、2、3、4、5、6、7、8 章节与关联子方案引用提炼，保持与主方案术语一致（见 pdca/CONTEXT.md）。

## 测试决策

- 本任务为文档任务，无代码测试；以主方案章节双向映射 checklist 验收。

## 验收标准

- [ ] AC-1: 三份子方案文档创建于 aio-cdm 本仓主方案同目录，文件名与主方案引用一致（§1 引用清单）。
- [ ] AC-2: Web API 子方案定义验证码登录、Token 校验、备份域管理、RPC 连通性测试、固定报表查询、同步导出与"我的报告"的请求/返回契约（§3.1、§8）。
- [ ] AC-3: Collection Service 子方案定义 APScheduler 调度、固定 Topic Worker、CDM RPC/CLI 数据流、JSONL 临时文件、Metric Builder、Report DB 入库、失败重试与重启恢复（§2.1、§4、§5、§6.3/6.4、§7）。
- [ ] AC-4: CLI 子方案定义 `cdm-data-cli` 受控 Topic 命令、参数白名单、Keyset 游标、JSONL 输出与字段归一化契约（§6.2、§3.5.2）。
- [ ] AC-5: 三份文档与主方案关键数字一致（周期 60/5/10 分钟、超时、100 域、csv_max_rows=4000 等），无新增范围。

## 范围外

- 不编写实现代码。
- 不修改主方案文档。

## 备注

- 依赖：无（仅主方案）。
- 下游：T0216、T0217、T0218、T0219、T0220 以其为契约基线。
