---
schema: pdca.asset/v1
id: ontology:concept/pdca-task
type: concept
layer: Knowledge
summary: PDCA 任务元概念
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-task

PDCA 任务元概念：一个完整 PDCA 周期的载体。

- **含义**：由 `task.json` 跟踪 `meta.phase` / `status` / 各类标记；阶段只能经 `transition-phase.py` 按 `pdca-transition` 合法边推进。
- **关键不变量**：`final_confirmation` / `check_confirmation` 不可由 AI 代签；阶段推进须经门禁校验。

## 决策背景（原 ADR-0002：严格任务合约与能力适配边界）
- 背景：流程曾同时依赖自然语言门禁、松散 task.json 字段与具体 Agent 平台工具名；历史任务 phase/status/active/states 互相矛盾仍通过校验。
- 决策：冻结严格新 schema（task.schema.json），fail-closed，不为旧格式增加兼容分支；清理不合规历史任务；技能只声明所需抽象能力（能力协议），具体平台工具由适配层解析。"

## 决策背景（原 ADR-0017：to-tickets 显式依赖边与 ready-set）
- 背景：to-tickets 只顺序拆解，无显式依赖边，无法校验 DAG 无环、无法计算可并行任务集。
- 决策：子任务显式声明 `dependencies`（直接前置边）；ready-set = 所有 blocker 已完成的可执行集合；`schemas/task.schema.json` 的 `additionalProperties:false` 要求新增字段同步改 schema，否则 doctor 校验失败。
