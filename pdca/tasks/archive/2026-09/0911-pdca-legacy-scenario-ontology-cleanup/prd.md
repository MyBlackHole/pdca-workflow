# 清理 PDCA 核心权威入口的旧场景控制语义

## 问题陈述

T2175 已确认 PDCA 根本体只使用 `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification` 三个专业职责，并由执行契约决定具体工作。但仓库的部分活跃核心入口仍用 `scenario_type`、`development/bugfix/research/documentation/design/review` 或 A/B/C 承担任务分类、流程路由或门禁控制，造成根本体与关联权威节点不一致。

## 目标

清除活跃 PDCA 核心权威入口中的旧场景控制语义，使 `ontology_role` 与 `execution_contract` 成为工作内容和行为选择的唯一结构化来源。旧词仍可作为具体 skill 名称、证据种类或普通业务描述出现，但不得继续决定任务生命周期、执行路线、门禁或职责。

## 范围

- PDCA 的全局代理入口、Plan/Do/Check/Act 流程节点、阶段概念以及任务分诊和用户路由技能。
- 活跃本体中以旧六场景进行分类、边界裁决或 A/B/C 路由的概念和关系。
- 删除已失去权威意义的旧场景边界本体节点及其活跃引用，不保留兼容别名。
- 修改技能后重新生成技能索引。

## 范围外

- 历史 `records/`、`pdca/journal/` 和归档任务中的事实记录。
- 配置、Python runtime 和测试中的字段迁移；由后续 `ontology_projection` PDCA 承担。
- 删除名为 `research`、`code-review` 等可选工具 skill；工具名称本身不属于控制语义。
- `documentation` 作为证据种类、`bug` 作为普通问题描述等非控制用法。

## 验收标准

- [ ] AC-1: 产出核心权威入口清单，并逐项标明旧词是控制语义、工具名称、证据类型、普通描述还是历史事实。
- [ ] AC-2: 全局代理入口不再声明 Do 按 `meta.scenario_type` 执行，改为按 `meta.ontology_role` 与 `meta.execution_contract` 执行。
- [ ] AC-3: Plan、Do、Check、Act 和阶段权威节点不再使用六场景、A/B/C 或“6 路由”控制阶段行为。
- [ ] AC-4: 分诊、用户路由及上下文编排技能不再把旧六场景映射为 `ontology_role` 或执行路径，统一输出三个专业职责和四字段执行契约。
- [ ] AC-5: 旧场景边界本体节点从活跃本体删除，所有活跃关系和流程入口均无悬空引用，且不创建兼容别名或重定向节点。
- [ ] AC-6: `research`、`code-review` 等具体 skill 仅作为执行契约可选择的工具；工具名称不参与任务分类、阶段转换或门禁。
- [ ] AC-7: 对声明的核心权威入口全集运行残留扫描，`scenario_type`、六场景分组、A/B/C 路由和“6 路由”控制语义均为零命中；允许项必须逐条说明语义类别。
- [ ] AC-8: `python3 scripts/ontology-validate.py --ontology-dir ontology`、本体图孤岛检查、技能索引检查和任务收敛校验全部通过。

## 关联本体节点

- `ontology:concept/pdca`
- `ontology:concept/pdca-phase`
- `ontology:process/flow-plan`
- `ontology:process/flow-do`
- `ontology:process/flow-check`
- `ontology:process/flow-act`
- `ontology:domain/skill-triage-work`
- `ontology:concept/pdca-scenario-boundary-rule`（删除候选）

## 拆分映射

- 权威入口与阶段语义 -> `ontology:concept/pdca`、`ontology:concept/pdca-phase`、`ontology:process/flow-*`
- 分诊与工具选择语义 -> `ontology:domain/skill-triage-work` 及关联路由技能
- 旧边界规则退役 -> `ontology:concept/pdca-scenario-boundary-rule` 及其活跃引用
- 一致性验证 -> 当前任务的权威入口清单、残留扫描与本体校验
