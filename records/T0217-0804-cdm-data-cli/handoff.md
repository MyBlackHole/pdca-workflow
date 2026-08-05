# T0217 Handoff — cdm-data-cli 受控采集 CLI

## 当前状态
- do→check→act 已完成；verdict=confirmed；disposition=projected（已写 knowledge + manifest）
- 代码已提交 aio-cdm `feature/F-140-report-center` @ `1c47fa3fe`（32 文件 2303 行）
- pdca-workflow 侧：evidence 4 项 + convergence-map、conclusion.md、clarifications（final/check/grilling/knowledge_decision）、disposition、journal 已落盘
- 剩余 Ac7（提交 pdca-workflow）与 Ac8（归档 → archive + mv）未执行

## 未完成事项
- Ac7/Ac8：pdca-workflow `git commit`（evidence+conclusion+knowledge+manifest）→ `transition-phase --to archive` → `mv pdca/tasks/active/T0217-...` 至 `pdca/tasks/archive/2026-08/`
- T0216（Report DB Adapter）仍 plan 态，prd.md 已存在，可接续启动

## 已知约束
- 当前环境无 flask/aio，测试须 `python3 -m pytest tests/report_collect/ -q --noconftest`
- CI 强制 black + isort（--profile black）
- 生产装配（_load_models 语义名映射、REQUIRED_COLUMNS、凭据 validator、target_version 匹配）待 CDM 主机核对（实现清单已知限制 #2-#4）
- 真实 ORM 无 rel_*/backup_objects 独立表 → 源端归一化视图（已知限制 #1）

## 推荐的下一步
1. 完成 Ac7/Ac8 归档 T0217
2. 启动 T0216：Report DB Adapter（dwd_task_run 落库，含 §5.5「不落 source_table/source_id」约束）
3. T0218（channel 调用）/ T0222（CLI 压测）验收 Keyset 与超时分层

## 关键上下文文件列表
- aio-cdm `aio/report_collect/`（源码）+ `tests/report_collect/`（69 测试）+ `cdm_report_center_cli_subscheme.md`（契约唯一事实源）+ `cdm-report-center-final-technical-solution.md`（主方案）
- pdca-workflow `records/T0217-0804-cdm-data-cli/`（evidence/conclusion）+ `knowledge/report-center/cli-from-scratch-lazy-import.md`（沉淀）
- 真实 aio 模型源码 `/home/black/Public/aio/aio-cdm/`（字段核对）

## Suggested skills（后续会话加载）
- `feature-commit-format`：T0217 代码提交已用；后续功能提交复用
- `code-review-checklist` + `secure-coding`：双轴审查范式可复用
- `verify-convergence` / `advance-phase` / `append-confirmation`：阶段门禁已跑通
