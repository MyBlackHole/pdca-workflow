# T0159 实施顺序

## 垂直切片 1：不可变 occurrence

- 冻结 event schema、规范化与稳定 ID。
- 实现 report/query-one CLI。
- 接入 transition audit。
- 先覆盖人工中途上报、重复重试、冲突、路径逃逸和并发。

## 垂直切片 2：确定性 projection

- 实现版本化 fingerprint。
- 生成稳定 backlog、输入摘要和 digest。
- 实现紧凑 list/show 查询。
- 覆盖错误合并、规则升级、损坏事件和重复运行。

## 垂直切片 3：治理 decision 与 candidate

- 实现 decision schema 与确认引用校验。
- 实现 dry-run candidate 和不可变候选版本。
- 验证所有受控动作在缺确认时 fail-closed。

## 垂直切片 4：Improvement Task 晋级

- 由已确认 candidate 创建严格 Plan task。
- 分配单调 task ID，写入来源关系。
- 不写 final_confirmation，不调用 transition。

## 垂直切片 5：效果判定

- 冻结观察计划并校验部署回执。
- 生成 improved/neutral/regressed verdict。
- improved 生成 verified decision；regressed 生成未确认回滚 candidate。

## 垂直切片 6：端到端与 AI 友好度

- 完整反馈链 fixture。
- 相同缺陷输入的新旧配对。
- 导航、合约、故障恢复和上下文 bytes 分别报告。
- 双轴审查 Blocking 清零后登记 evidence 与 convergence map。

## 提交边界

- 一个功能提交完成 T0159 主体；必要时按合约/聚合/治理拆为小提交，但每个提交必须测试通过。
- 仅暂存 T0159 范围文件，保留工作区其他任务改动。
