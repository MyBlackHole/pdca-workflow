---
name: pdca-verify
description: 用户明确选择本体符合性验证，或已有验证任务需要场景方法时使用。验证同一节点的需求→模型→实现→行为。
metadata:
  version: 5.0.0-rc.2
---

# 本体符合性验证：验证实现是否忠实

## 先定位，不以加载当授权

定位 **PDCA_ROOT**、原 verify task/Agent 和真实 user operation。
先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)。
已有 task 不自动改 scene/revision；当前会话不是原执行者时只路由，不接管。

## 验证身份

Verify task 必须绑定与被审实现一致的：

- `work_id/node_id`；
- ontology revision；
- implementation/mapping version；
- requirement/AC/oracle；
- CONTEXT-01 选择出的最小本体子图；
- 必要 dependency deliverables 与行为证据。

Verify 不重新建模、不重新拆任务，也不读取实现 Agent 的完整活动历史。
实现报告只是 claim，不是事实。

## 验证链

逐层核验：

1. **requirement → model**：当前 node 的需求是否被对象/关系/约束覆盖；
2. **model → implementation**：模型语义是否在 mapping/target 中真实表达；
3. **implementation → behavior**：真实运行/可观察行为是否满足模型和需求；
4. **node → neighbors**：必要 composition/dependency interface 是否与固定邻接交付一致。

错误模型与错误实现不能互相证明；没有运行事实保持 unknown/not_run。

## 独立上下文

Fresh verify Agent 只接收当前 node 的最小子图、固定 implementation/mapping 和必要证据。
不继承 implement Agent 的调试历史、推理过程、未固定假设或父/兄弟 conversation，
以减少确认偏差与上下文污染。

## 阶段方法

| 阶段 | 动作与交付 |
|---|---|
| Plan | 固定 node/revision、实现版本、mapping、验证问题、反例方向、行为证据需求和标准 |
| Do | 执行 requirement→model→implementation→behavior 及必要接口核验，保存事实/反证 |
| Check | 使用 AI Scope/Consistency/Adversarial/Evidence 四遍审查，核验 Do 的证据与结论 |
| Act | 用户明确选择接受、失败归档、提出返工或获准发布 |

发现模型根本错误时报告 affected node/relation/constraint，由用户决定是否启动新的 pdca-model；
不能在 verify 内静默修改模型或 implementation。
