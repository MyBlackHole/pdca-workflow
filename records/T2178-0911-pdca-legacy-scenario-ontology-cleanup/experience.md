# T2178 经验记录

## 来源

- 当前任务：`T2178-0911-pdca-legacy-scenario-ontology-cleanup`
- 本体锚点：`ontology:concept/pdca`
- 有效证据：`t2178-core-authority-inventory-v2`、`t2178-authority-change-snapshot-v2`、`t2178-validation-report-v3`、`t2178-convergence-map-v5`

## 可复用经验

- 权威入口清单不能只依赖 frontmatter 或本体索引发现；根说明、上下文和路由文档即使不是标准本体节点，也必须按实际控制职责纳入。
- 旧词清理必须区分流程控制语义与普通业务表达。工具名、证据种类和历史事实可以保留，但不得决定职责、阶段、门禁或执行路径。
- 删除旧概念时应同时验证节点文件、活跃引用、别名和重定向，避免形成隐式兼容层。
- 符合性审查应以完整权威入口集合为边界，并把零命中扫描、本体结构校验、技能索引和收敛映射组合为可复验证据。

## 纠偏

首次 Do 把 active `pdca.asset` 节点集合误当成全部核心入口，遗漏 `README.md`、`ontology/README.md` 和 `pdca/CONTEXT.md`。主协调器记录审查失败后，由同一一对一子 Agent 修正清单、文档和证据；旧证据被替换而未覆盖审查历史。
