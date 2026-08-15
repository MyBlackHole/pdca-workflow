---
schema: pdca.asset/v1
id: T0215-0804-report-subscheme-docs
phase: check
source_ids: [e1-subscheme-checklist, convergence-map]
---

## 上下文

补齐需求 140 主方案引用的三份子方案契约文档，作为 T0216~T0220 实现的对齐基线。契约锚点为主方案 §3.1/§3.5/§4.2/§6.2/§8。

## 假设与结果

- **假设**：主方案信息足以提炼出可执行的 Web API / Collection Service / CLI 三份契约，且不引入新范围。
- **结果**：三份文档已落 aio-cdm 本仓主方案同目录，文件名与 §1 引用一致；5 项 AC 脚本化验证 PASS；convergence 验证 `valid: true`。

## 分析

- Web API 子方案：完整定义认证（验证码/登录/改密/登出/Token TTL）、备份域管理（CRUD/启停/删除/连通性）、报表查询/同步导出、我的报告，及 24 个错误码的 HTTP 映射。
- Collection Service 子方案：定义进程边界、Job/RPyC 契约（JobSpec、10 个 RPC 方法）、三 Topic 执行语义、JSONL 文件状态机、11 类失败处理、重启恢复、原子性边界。
- CLI 子方案：定义固定子命令、参数白名单、Keyset 扫描、JSONL 契约、entity_key/去重/关系解析/容量规则，并补齐与 `collection-jobs.yaml` 重叠键一致。
- 关键数字（周期、超时、100 域、cursor_overlap、分区 260、csv_max_rows）与主方案逐项核对一致；未引入一期范围外能力。
- 局限：契约文档是文字规格，尚未经实现/契约测试反验证；CLI 子方案的 ORM 字段级映射（如 `rdb_application_node_map`）以主方案描述为准，实现时需对源码核对。

## 适用边界

- 本文档为契约基线；T0216~T0220 实现必须与本文一致，发现冲突以主方案为准并回评审。
- 三份文档为需求 140 一期范围；范围变更需重写契约。

## 下一轮建议

1. T0216（Report DB Adapter）与 T0217（cdm-data-cli）可并行启动，均依赖本任务契约。
2. 实现 T0217 时对 CLI 子方案引用的 ORM 字段逐一核对 `aio-cdm` 源码，更新 CLI 子方案的字段级映射。
3. 各下游子任务 Do 阶段补充契约测试，回链本文档锚点。
