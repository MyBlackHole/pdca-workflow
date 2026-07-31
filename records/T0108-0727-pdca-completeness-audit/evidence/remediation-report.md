# T0108 AGENTS.md 建设复核

## 变更

已在仓库根目录创建 `AGENTS.md`，职责限定为项目级入口路由：

- 声明 `PDCA_HOME`、任务、archive、records、knowledge 和 journal 路径。
- 声明 Plan→Do→Check→Act→archive 的硬门禁。
- 明确用户确认不可由子代理、直接 metadata 修改或未登记证据绕过。
- 索引 `flows/`、`skills/`、`SKILLS-INDEX.md` 和外部项目初始化脚本。
- 明确流程正文仍以 `flows/` 与 `skills/` 为权威，不复制完整规则。

## 验证

- `test -f AGENTS.md`：通过。
- `rg` 验证入口包含 `PDCA_HOME`、`final_confirmation`、`register-evidence`、阶段流程和 `init-external.sh`：通过。
- `git diff --check`：通过。

## 边界

该建设只解决项目入口缺失（B1/S3）；父子聚合、归档恢复、确认语义和内容来源链仍由 T0109–T0112 处理。
