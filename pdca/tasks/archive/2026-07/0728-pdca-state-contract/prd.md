# 实现严格任务 schema、语义门禁与历史清理

## 问题陈述

当前门禁主要检查字段或文件存在，不能阻止拒绝确认、无效证据、空处置和矛盾归档状态。历史任务包含多种松散格式，父任务已决定不增加兼容规则。

## 解决方案

- 定义 task、clarification、evidence、verdict、disposition 的 JSON Schema。
- 实现跨文件引用、digest、时间顺序及 phase/status/active/states 对应关系的语义验证。
- 为阶段转换生成可审计 receipt，并保证重复调用幂等。
- 先冻结并测试 schema，再 dry-run 生成逐项历史删除 manifest。
- 排除 `records/`、`knowledge/`、`pdca/journal/`；逐项校验 digest 和数量后删除，未被 Git 跟踪的目标必须有用户明确授权。

## 验收标准

- [ ] 每个合法阶段至少一个正例，每条不变量至少一个反例。
- [ ] 未确认 final_confirmation、无效 evidence、缺 verdict、空 disposition、矛盾 archive 均被拒绝。
- [ ] dry-run 不修改文件，manifest 含具体路径、原因和摘要。
- [ ] 受保护目录不可能进入删除 manifest。
- [ ] 清理后不存在不符合严格 schema 的历史 task。

## 范围外

- 兼容旧 task 格式。
- 删除 records、knowledge 或 journal。
- schema 未冻结前执行删除。
