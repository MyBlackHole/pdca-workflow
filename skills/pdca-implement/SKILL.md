---
name: pdca-implement
description: 用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。只实现固定本体节点，不重新发明任务树。
metadata:
  version: 5.0.0-rc.2
---

# 本体投影：把固定节点实现为真实实体

## 先定位，不以加载当授权

定位 **PDCA_ROOT** 和原 task/Agent；已有绑定优先于 cwd/环境变量。
先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)并核对当前 user operation、node、ontology revision、
Plan/AC、写域和依赖。当前会话不是该任务执行者时只路由回原 Agent，不接管。

## 场景身份

Implement task 必须已经绑定：

- `work_id/node_id`；
- 固定 ontology revision；
- 当前 node responsibility / I/O / constraints；
- [CONTEXT-01](../../ontology/process/select-task-subgraph.md) 选择出的最小本体子图；
- 当前 scene 的目标写域与 mapping rules。

没有这些固定模型输入时，不能用“实现过程中顺便补模型”继续。

## 投影

Do 将当前节点模型投影为真实代码、文档、配置、schema 或其他实体，并保存：

```text
ontology object / relation / constraint
              -> target location
              -> projection rule
              -> evidence / verification signal
```

只实现当前 node 的职责。兄弟/孩子正式节点由各自 task/Agent 处理；
组合时只读取其固定 deliverable/interface，不吸收完整活动历史。

## Work Unit

Work Unit 只用于当前正式 task 的 Do 内部局部执行、隔离分析或工具调用。
它是当前 CONTEXT-01 子图的进一步切片：

- 不创建 node_id；
- 不创建正式 child task；
- 不拥有新的 ontology responsibility；
- 不扩大父 task 的 context/authority。

Work Unit 发现模型缺口时把证据交回原任务，由
[EVOLVE-01](../../ontology/concept/ontology-evolution.md) 判断受影响动作；
不因每个新关系端点自动转场，也不以局部执行名义修补固定模型或扩大职责。

## 阶段方法

| 阶段 | 动作与交付 |
|---|---|
| Plan | 固定 node/revision、最小 context refs、目标位置、mapping、AC、业务写域和必要依赖 |
| Do | 投影真实实体，保存 model→target mapping、实际操作和证据；局部切片可用 Work Unit |
| Check | 检查 source→target 遗漏、target→source 无模型依据增加、接口/约束和必要产品行为 |
| Act | 固定 implementation version、mapping、证据与未验证范围 |

模型缺失或错误时停止依赖错误模型的实施，仍可按 CONTEXT-01 在原授权读域核实并在获准记录区报告。
修订建议不是新模型的编写或采用；需要 modeling 时由用户决定，不能静默改 scene 或重定义 node。
