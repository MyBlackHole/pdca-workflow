---
schema: pdca.asset/v1
id: ontology:concept/writing-for-agents
type: concept
layer: Knowledge
status: active
summary: 为 Agent 写作：文档和技能的通用写作原则
relations:
  specializes:
  - ontology:principle
---


# Writing For Agents

为 Agent 写作：文档和技能的通用写作原则。

## Grounding 依赖图

概念必须 grounding 后才能被后续块依赖——读者带来（prerequisite）或先前块引入（introduced）。每 beat 声明 `requires`（读者带来）或 `grounds`（先前块引入）两组概念，候选续写只能从当前 grounded 集合可达。未 grounding 的概念不得被后续块依赖。选择空间被依赖图机械约束。

## 信息层级

信息层级：步骤（in-file step）→ 文件中引用（in-file reference）→ 披露引用（disclosed reference）。
