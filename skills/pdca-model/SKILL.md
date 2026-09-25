---
name: pdca-model
description: 用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。模型决定正式任务结构与上下文边界。
metadata:
  version: 5.0.0-rc.2
---

# 本体建模：定义对象、关系、约束与工作节点

## 先定位，不以加载当授权

核对本文件真实路径并定位集中 Git 工作副本 **PDCA_ROOT**。
既有任务绑定优先于 cwd/环境变量；冲突时停止，不在 TARGET_ROOT 创建另一套 records/规则。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读当前 task、原 Agent、最后完整事件和当前请求。
已有任务不自动改绑或升级规则；当前会话不是该任务执行者时只路由真实用户操作回原 Agent，
不可路由就阻断。

## 两种读取方式

- **已有 work/node**：已有 modeling task 就回原 Agent；没有 task 时，只基于该固定 node/revision
  提出 modeling 目标与创建请求。用户明确创建后按
  [agent-dispatch](../../ontology/contracts/agent-dispatch.md) 派发 fresh Agent。
- **首次根建模**：如果当前 work 尚无 ontology node，只允许建立一个 root goal seed：
  固定用户目标、范围、事实来源、预期模型与创建授权，然后创建唯一 root modeling bootstrap task。
  此时不得虚构 ontology revision/node，也不得派发 child/implement/verify task；Do 可以形成
  ontology-backed child seed，但只有 root modeling Act 固定第一个 root node/revision 后才进入正常派发流程。
- **已有阶段任务读取方法**：核对 task.scene=pdca-model 后只读下面的方法，不递归创建另一个 modeling task。

## 建模的核心输出

Model 不是“写一份设计说明”，而是建立可被后续任务引用的固定语义：

- ontology objects/entities；
- attributes；
- semantic relations；
- constraints/invariants；
- work instance；
- requirement coverage；
- `node_id` 及责任、I/O、AC；
- composition/dependency relation；
- direct child seed 或 leaf reason；
- unknown、来源和 revision。

[TREE-01](../../ontology/concept/work-ontology-tree.md) 将模型关系投影为工作树，
[NODE-01](../../ontology/concept/work-node-contract.md) 定义节点资格，
[DECOMP-01](../../ontology/concept/task-decomposition.md) 从合格节点产生正式 task seed。

因此**正式任务拆分来源于模型实体/关系**，不是 LOC、文件、工时、token 或并行需求。

## 上下文边界

每个正式 node 也是后续 context isolation 的锚点。
child task 创建时，由 [CONTEXT-01](../../ontology/process/select-task-subgraph.md)
从 ontology/work graph 选择 minimum sufficient subgraph，不能复制父/兄弟完整活动历史。

## 阶段方法

| 阶段 | 动作与交付 |
|---|---|
| Plan | 固定用户目标、事实来源、复用定义、要建模的对象/关系/约束、需求覆盖与验收方式 |
| Do | 建立/修订 ontology 与 work instance，形成 node、composition/dependency relation、child seed 或 leaf reason |
| Check | 核对需求→对象/关系/约束覆盖，检查节点资格、关系端点、来源、反例和 unknown |
| Act | 只按批准范围固定 ontology revision、work tree/node seed；不自动创建 child 或启动 implement |

同一 node 的 implement/verify 必须引用这里固定的身份和 revision。
