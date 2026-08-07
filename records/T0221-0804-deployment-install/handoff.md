# T0221 交接记录

## 当前状态
- T0221（两阶段安装部署与配置校验）已 Check 完成，verdict=confirmed，进入 Act 收尾。
- 代码已提交 `e9e9b24`（report-center repo，0.4.0→0.5.0，21 文件 +1250 行）。
- 知识已沉淀 `knowledge/report-center/deployment-assembly-patterns.md`。
- disposition=projected，正在归档。

## 未完成事项
- AC-7 双平台（x86_64/aarch64）实机安装/卸载/升级/回退验收——延后 **T0222**（目标环境）。
- 健康检查的 report_db/jobstore/login 探针为框架占位——待服务侧装配（T0218/T0219 已具备连接逻辑）补齐真实探针。
- T0224（异步导出，源自 T0220）plan 阶段待推进。

## 已知约束
- 沙箱禁 bind TCP 端口：健康检查"通过路径"仅由单测保证，成功路径端到端验证需真实主机。
- 全量测试 6 errors 为既有 `REPORT_TOKEN_PRIVATE_KEY` 未配置环境问题，与 T0221 无关。
- `--install-db` 需 `REPORT_ADMIN_PASSWORD` 环境变量与可达 DB，否则中止（有保护）。

## 推荐的下一步
1. 完成本任务归档（Ac6 日志 → Ac7 提交 → Ac8 mv archive/）。
2. 推进 T0222 双平台实机验收并回填 AC-7 验收记录。
3. 推进 T0224 异步导出（plan 阶段）。
4. 后续若安装链路在真实主机暴露问题：`git revert` + 重装 + migration down.sql。

## 关键上下文文件列表
- `pdca/tasks/active/T0221-0804-deployment-install/`：task.json（verdict/disposition）、prd.md、clarifications.jsonl、convergence.json
- `records/T0221-0804-deployment-install/`：conclusion.md、evidence/
- `knowledge/report-center/deployment-assembly-patterns.md`
- `report-center/deploy/bin/install.sh`、`collection_service/cli.py`、`collection_service/deploy_install.py`

## suggested skills
- `advance-phase`（归档转换）、`write-journal`（Ac6）、`verify-convergence`（若再验证）、`feature-commit-format`（后续提交）
