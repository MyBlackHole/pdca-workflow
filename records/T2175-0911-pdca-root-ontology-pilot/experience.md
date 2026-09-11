# T2175 经验记录

## 来源

- 当前任务：`T2175-0911-pdca-root-ontology-pilot`
- 核心产物：`ontology:concept/pdca`
- 有效证据：`pdca-root-model-v4`、`root-validation-v5`、`convergence-map-v7`

## 可复用经验

- “本体是图”描述权威语义拓扑；“本体树驱动”描述从任务有界子图投影到执行树或 DAG 的产品设计原则，两者不能互相替代。
- 每个 PDCA 是独立完整循环。协调 Agent 派发一对一全新子 Agent 后停止运行，恢复时只读取当前任务持久化产物并执行 `ontology_conformance_verification`。
- `parent` 和 `dependencies` 只用于拆分与调度，不能成为生命周期控制、跨任务检查或验收代理。
- 本体建模完成不等于 runtime 已投射；配置、实现和测试的差距必须单独进入 `ontology_projection` 周期。

## 纠偏经验

- 初版遗漏“本体树驱动”，说明结构正确性检查不能替代产品核心目标检查。
- 初版把恢复动作写成检查其他任务，混淆了 Agent 执行上下文与任务依赖关系；符合性验证必须绑定当前独立任务。
- 定向扫描只覆盖本任务修改文件会漏掉仓库级旧控制语义。后续清理旧场景时应先声明完整权威入口集合，再以全集合扫描作为验收证据。
