## 事实核验

- 已验证：T0268-T0272 的 task.json scenario_type 均为 research，但 scripts/ 与 tests/ 下存在对应可测试产出（脚本+测试+全量回归），与 research 路径 C（仅调研+报告）不符。
- 已验证：137 任务中无缺失 scenario_type，六场景路由契约与 flow-do 文档锚点一致。

## 查重

- T0139（六场景评测 harness）、T0244（流程实现审查）均未覆盖场景归属判定规则；knowledge 无重复；out-of-scope 无命中。

## 分类

- **category**: enhancement
- **scenario_type**: development
- **summary**: 为 research/development 场景归属补充边界判定规则，消除元审查类任务的模式错配。
- **current behavior**: triage-work 分类表按输入形态粗分六场景；"Research / analyse X" 一律归 research。元审查系列 T0268-T0272 均标 research，但实际产出为可测试工具代码（脚本 + 测试 + 全量回归），与 research 路径 C（仅调研+报告）不符，实际按 development 流程执行。
- **desired behavior**: 含可测试代码产出的任务归 development；纯结论性调研归 research。triage 阶段可机械判定归属。
- **key interfaces**: triage 分类、scenario_type、flow-do 路径路由、可测试产出判定。
- **acceptance criteria**:
  - 运行检查得到明确的场景归属判定结果，与历史错配任务（T0268-T0272）的期望归属一致。
  - 规则同时适用于 development/design/review 等其他边界情形。
- **out of scope**: 不改六种场景本身的步骤内容；不重分类历史归档任务。
- **information gaps**: 除 research↔development 外，是否还有其他边界错配实例需一并覆盖。

## 优先级与下一步

- **priority**: P1
- **推荐方向**: Grill 确认边界判定阈值与落地载体（triage-work 分类表 / 独立检查脚本 / 校验器），再定 PRD。
- **信息缺口**: 无。
