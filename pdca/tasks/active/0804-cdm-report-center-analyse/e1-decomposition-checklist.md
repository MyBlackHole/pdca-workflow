# Evidence E1 — 拆解产物逐条验证（AC-1~AC-6）

> record: T0214-0804-cdm-report-center-analyse · 2026-08-04
> 验证方式：脚本化检查 8 个子任务目录/字段/PRD 结构与澄清记录

## 验证结果

| AC | 内容 | 结果 |
|----|------|------|
| AC-1 | 8 个子任务目录存在，含 task.json + prd.md，meta.phase=plan | PASS |
| AC-2 | 子任务 parent=T0214，父 children=[T0215..T0222] 双向一致 | PASS |
| AC-3 | 每个子 PRD 含 `## 验收标准` + `- [ ] AC-x:` checkbox + 主方案章节引用 | PASS |
| AC-4 | 子任务 ID 无重复，首个为契约文档（T0215 subscheme） | PASS |
| AC-5 | 每个子 PRD 明确仓库路径（aio-cdm / report-center）与依赖 | PASS |
| AC-6 | clarifications.jsonl 含 grilling + direction_confirm，ADR-0013 存在 | PASS |

## 子任务清单（ID / 标题 / 仓库 / 依赖）

| ID | 标题 | 仓库 | 依赖 | AC 数 |
|----|------|------|------|-------|
| T0215 | 补齐三份子方案契约文档 | aio-cdm | — | 5 |
| T0216 | Report DB 接口 + PG17 Adapter + Migrations | report-center | T0215 | 7 |
| T0217 | cdm-data-cli（Topic/JSONL/Keyset） | aio-cdm | T0215 | 7 |
| T0218 | collection-service（调度/worker/入库/恢复） | report-center | T0215,16,17 | 9 |
| T0219 | report-web（登录/域管理/连通性/保存报告） | report-center | T0215,16,18 | 8 |
| T0220 | 报表模板 + 16 查询 + CSV/PDF 导出 | report-center | T0215,16,19 | 8 |
| T0221 | 两包两阶段部署与配置校验 | report-center | 15,18,19,20 | 7 |
| T0222 | 容量模型与验收压测 | 两侧 | 全部 | 5 |

## 结论

主任务 6 项验收标准全部通过；拆解产物可交付，进入 Check 阶段。
