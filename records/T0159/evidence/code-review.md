# Code Review — T0159

基点：`65b2d87f10248aba10e373f7fdc3f76b57b87366`（Plan 完成提交）。

范围：Flow Issue occurrence、projection/query、decision/candidate、promotion、effectiveness verdict、cutover 集成及其公共 CLI 夹具。

## 标准轴

- warning: `scripts/flow_issues.py:1` — 单一模块现为 1263 行，同时承担不可变存储、投影、治理、任务晋级和效果判定；当前测试覆盖充分，但后续迭代应按 storage/projection/governance/effect 分拆，降低改动耦合。
- info: `scripts/flow_issues.py:18`、`scripts/flow_issues.py:923` — 晋级去重使用 POSIX `fcntl.flock`，当前 Linux 执行环境可用；若支持 Windows，需要替换为跨平台文件锁适配层。
- info: 生产 CLI 没有 `shell=True`、`eval`、`exec` 或不可信反序列化；路径输入先限制为受控名称/相对位置，写入使用独占创建或原子替换。

标准轴 Blocking：0。

## 规范轴

- 缺失：无。四类严格 schema、独立不可变 occurrence、确定性 fingerprint/backlog、紧凑分页查询、绑定用户确认的 decision、dry-run candidate、受控 Plan task、三态 effectiveness verdict 和 cutover 都已实现。
- 范围蔓延：无。没有引入模型训练、自动 patch/merge/阶段推进/回滚、固定次数触发、Web UI 或历史 `flow-audit/v1` 迁移。
- 实现偏差：无。transition cutover 后仅记录新 occurrence，保留历史 v1 文件不变；improved 仅生成 verified decision，regressed 仅生成待确认 rollback candidate。

规范轴 Blocking：0。

## 验证

- `python3 -m unittest discover`：52 passed。
- `python3 scripts/run-flow-issue-fixtures.py --all`：8/8 passed；紧凑 list 上下文为 603 bytes，按 issue 展开为 1218 bytes。
- `python3 -m py_compile scripts/*.py`、全部 schema JSON 解析与 `git diff --check`：通过。
