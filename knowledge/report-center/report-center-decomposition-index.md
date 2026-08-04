# CDM 报表中心（需求 140）落地拆解索引

> 来源：records/T0214-0804-cdm-report-center-analyse/conclusion.md · 2026-08-04
> 目的：把主方案 `cdm-report-center-final-technical-solution.md`（1580 行）映射为可执行子任务树，作为后续实施子任务的跨会话导航。

## 拆解方法论（可复用模式）

把大型技术方案转为 PDCA 可执行任务树的步骤：

1. **契约先行**：方案引用的子方案/契约文档缺失时，首个子任务补齐契约，作为全部实现的唯一输入。
2. **按交付域划分**：契约文档 / DB Adapter / CLI / 采集服务 / Web 服务 / 报表 / 部署 / 压测，粒度 ≥ 一个 PDCA 周期。
3. **仓库归属决策**：跨仓/单仓归属写入 ADR；CLI 复用既有仓库只读资产，主应用归独立仓库解耦。
4. **验收可追溯**：每个子 PRD 的 `- [ ] AC-x:` 必须引用主方案章节号，Do 阶段可独立判定。

## 子任务索引（ID / 仓库 / 依赖）

| ID | 标题 | 仓库 | 依赖 |
|----|------|------|------|
| T0215 | 补齐三份子方案契约文档 | aio-cdm | — |
| T0216 | Report DB 接口 + PG17 Adapter + Migrations | report-center | T0215 |
| T0217 | cdm-data-cli（Topic/JSONL/Keyset） | aio-cdm | T0215 |
| T0218 | collection-service（调度/worker/入库/恢复） | report-center | T0215,16,17 |
| T0219 | report-web（登录/域管理/连通性/保存报告） | report-center | T0215,16,18 |
| T0220 | 报表模板 + 16 查询 + CSV/PDF 导出 | report-center | T0215,16,19 |
| T0221 | 两包两阶段部署与配置校验 | report-center | 15,18,19,20 |
| T0222 | 容量模型与验收压测 | 两侧 | 全部 |

## 关键契约锚点（主方案章节）

- 采集周期 60/5/10 分钟；100 域上限；csv_max_rows=4000；cursor_overlap=60s；分区上限 260。
- RPC Job 契约 §4.2.1；JSONL 契约 §6.2；失败处理 11 类 §6.4；重启恢复 §6.3.1。
- 一期边界：单机无 HA、PG17 单库、复用既有 rpc 工具、16 模板、不做告警/异步导出/首次全量。

## 下一轮建议

按依赖顺序调度子任务（T0215 先行）；每个子任务走完整 PDCA；各子任务 Do 以本索引的 AC 为最低门槛并补充代码级契约测试。
