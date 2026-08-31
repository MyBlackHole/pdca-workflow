# 集成 P1 差距：Phase Boundary 入 flow-do、Grounding 推广、触发条件建模

## 目标

将 T0431/T0432 已补充但未集成的 P1 概念集成到实际流程中，使本体从"静态定义"变为"动态触发"。

## 背景

T0434 识别 3 项 P1 差距，均已有概念节点但未集成到流程：
1. **G4**：Phase Boundary 决策树仅存在于 `ontology:concept/phase-boundary-decision-tree`，未在 flow-do 收尾阶段触发
2. **G5**：Grounding 依赖图仅存在于 `ontology:concept/grounding-dependency`，未在 writing-for-agents 写作规范中强制
3. **G6**：user-invoked/model-invoked 触发条件缺乏本体建模，概念节点存在但触发条件未形式化

## 实施计划

### G4：Phase Boundary 集成 flow-do
- 更新 `ontology/process/flow-do.md`，在收尾阶段添加 Phase Boundary 决策树输出
- 模型应在每个阶段切换时输出决策树（Continue/Clear/Handoff/Subagent/Compact）
- 第一个 yes 获胜，mid-phase 永不决策

### G5：Grounding 推广 writing-for-agents
- 更新 `ontology/concept/writing-for-agents.md`，添加 Grounding 依赖图要求
- 每个概念必须声明 `requires`（读者带来）或 `grounds`（先前块引入）
- 候选续写只能从当前 grounded 集合可达

### G6：触发条件建模
- 新建 `ontology:concept/trigger-condition` 概念节点
- 定义 user-invoked 和 model-invoked 的触发条件形式化表示
- 更新 `ontology/concept/user-invoked.md` 和 `ontology/concept/model-invoked.md` 添加触发条件属性

## 领域本体引用
- `ontology:concept/phase-boundary-decision-tree`
- `ontology:concept/grounding-dependency`
- `ontology:concept/user-invoked`
- `ontology:concept/model-invoked`
- `ontology:concept/writing-for-agents`
- `ontology:process/flow-do`