# 完成 PDCA 流程本体建模

## 问题陈述

当前 PDCA 本体已经描述阶段、转换、门禁、证据、判定、执行契约、恢复和反馈，但“结构合法”尚不等于“流程语义完整”。部分约束仍停留在正文，尚无统一机读完整性规范；因此现在直接重构 Python 脚本，仍可能把缺失语义重新写成硬编码。

本任务先完成 PDCA 流程本体建模，使后续新目录实现能够只消费本体及其派生合约，不再依赖旧场景分类或散落的流程判断。

## 目标

以 `ontology:process/pdca-flow-model` 为聚合根，完整表达：

1. 单任务生命周期和持续改进循环。
2. 任务、阶段、转换、门禁、验收标准、证据、判定、处置之间的关系。
3. 本体建模、本体投射、本体符合性验证三种职责。
4. 本体产出如何通过执行契约决定工作产品、动作、约束和验证信号。
5. rejected/partial 的恢复关系和 confirmed 的效果反馈关系。
6. 可机器检查的流程本体完整性规范。

## 本体产出契约

- `work_product`: 完整 PDCA 流程本体与机读完整性规范。
- `required_actions`: 盘点现有图谱；补齐节点和关系；定义角色与生命周期不变量；定义完整性问题集；执行结构与语义验证。
- `constraints`: 只使用三个专业本体职责；工具与 skill 不进入职责集合；不使用 A/B/C 或六场景作为控制字段；本任务不构建 Python runtime。
- `testable_signal`: 本体校验无错误，完整性问题集能逐项证明必需构件、关系和约束存在。

## 范围

- `ontology:concept/pdca`
- `ontology:process/pdca-flow-model`
- `pdca-task`、`pdca-phase`、`pdca-transition`、`pdca-gate`
- `pdca-acceptance-criterion`、`pdca-evidence`、`pdca-verdict`
- `pdca-execution-contract`、`pdca-recovery`、`pdca-feedback`
- `pdca-continuous-improvement`、`executor-adapter`
- 上述节点之间的组成、约束和可验证关系

## 不在范围

- 新建或重构 Python runtime。
- 迁移历史归档记录。
- 按工具、文档类型或旧场景名称建立流程分支。
- 修改外部项目业务代码。

## 执行策略

先执行 T2175 对 `ontology:concept/pdca` 的受控试点。试点进入 Check 后，根据实际证据重新审查并拆分其余 WBS；T2171-T2174 在此之前不进入 Do。

## 验收标准

- [ ] AC-1: `pdca-flow-model` 的 `composed_of` 覆盖阶段、转换、门禁、验收标准、证据、判定、执行契约、恢复和反馈，所有引用可解析。
- [ ] AC-2: 生命周期明确为 `plan→do→check→act→archive`，持续改进通过新一轮 Plan 表达，单任务转换图保持无环。
- [ ] AC-3: 三种且仅三种职责具有明确输入、输出、方向和退出判据；不存在 A/B/C 或六场景控制字段。
- [ ] AC-4: `pdca-execution-contract` 机读声明 `work_product`、`required_actions`、`constraints`、`testable_signal`，并明确 skill/tool 只是适配器。
- [ ] AC-5: Plan、Do、Check、Act 的入口、核心动作、产物和退出门禁均可由本体节点与关系追溯。
- [ ] AC-6: rejected/partial 必须关联恢复动作或后续任务；confirmed 必须关联效果反馈或显式 `unknown`。
- [ ] AC-7: 建立 PDCA 流程本体完整性问题集，覆盖构件完整、关系完整、职责完整、契约完整、闭环完整五类问题。
- [ ] AC-8: `python3 scripts/ontology-validate.py --ontology-dir ontology` 通过，且新增节点无悬空关系、无环、无孤岛、每个属性有可执行 `testable_signal`。
- [ ] AC-9: 形成供后续新 Python 实现消费的冻结输入边界，但本任务不创建 runtime 代码。

## 关联本体节点

```text
ontology:concept/pdca
ontology:process/pdca-flow-model
ontology:concept/pdca-task
ontology:concept/pdca-phase
ontology:concept/pdca-transition
ontology:concept/pdca-gate
ontology:concept/pdca-acceptance-criterion
ontology:concept/pdca-evidence
ontology:concept/pdca-verdict
ontology:concept/pdca-execution-contract
ontology:concept/pdca-recovery
ontology:concept/pdca-feedback
ontology:concept/pdca-continuous-improvement
ontology:concept/executor-adapter
```

## 拆分映射

- 生命周期与流程构件 -> ontology:process/pdca-flow-model
- 执行内容契约 -> ontology:concept/pdca-execution-contract
- 失败恢复闭环 -> ontology:concept/pdca-recovery
- 效果反馈闭环 -> ontology:concept/pdca-feedback
- 完整性问题集 -> ontology:concept/pdca
