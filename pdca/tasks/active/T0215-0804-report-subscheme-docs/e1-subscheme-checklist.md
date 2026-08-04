# Evidence E1 — 三份子方案契约文档逐条验证（AC-1~AC-5）

> record: T0215-0804-report-subscheme-docs · 2026-08-04
> 验证方式：文件存在性 + 契约覆盖 + 关键数字一致性核对

## 验证结果

| AC | 内容 | 结果 |
|----|------|------|
| AC-1 | 三份文档创建于 aio-cdm 本仓主方案同目录，文件名与主方案 §1 引用一致 | PASS |
| AC-2 | Web API 子方案覆盖 §3.1/§8 契约（认证/Token/域管理/连通性/查询/导出/保存报告） | PASS |
| AC-3 | Collection Service 子方案覆盖 §2.1/§4/§5/§6.3/§6.4/§7 契约 | PASS |
| AC-4 | CLI 子方案覆盖 §6.2/§3.5.2 契约（参数白名单/Keyset/JSONL/entity_key/字段归一化） | PASS |
| AC-5 | 三份文档关键数字与主方案一致，无新增范围 | PASS |

## 产物清单

| 文件 | 字节 | 覆盖章节 |
|------|-----:|----------|
| `cdm_report_center_web_api_subscheme.md` | 12809 | §3.1、§3.1.2~3.1.7、§8.1~8.6 |
| `cdm_report_center_collection_service_subscheme.md` | 12477 | §2.1、§3.2、§4、§4.2/4.2.1、§5、§6.1~6.4、§7 |
| `cdm_report_center_cli_subscheme.md` | 8902 | §3.5.2~3.5.5、§6.2、§6.4、§3.4.1 |

## 关键数字一致性核对

- 周期 60/5/10 分钟、Job ID `resource/task/capacity:{domain_id}`、`max_instances=1`、100 域上限、`cursor_overlap=60s`、分区上限 260、`csv_max_rows=4000`、rpc 端口 6611、Scheduler RPC 默认 8889 —— 与主方案逐项一致。
- CLI 子方案补充 `collection-jobs.yaml` 重叠键（page_size 500/1000/500、cli_timeout 1500/180/180、rpc_wait 1800/240/240、max_file 256/64/64 MiB），两处取值一致。
- 未引入主方案一期范围外能力（无告警/异步导出/多库适配/首次全量）。

## 结论

5 项验收标准全部通过；三份契约文档可作 T0216~T0220 的实现对齐基线。
