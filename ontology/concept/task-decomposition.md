---
schema: pdca.asset/v2
id: ontology:concept/task-decomposition
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-25'
summary: DECOMP-01：正式子任务由本体实体关系驱动，并形成独立上下文边界
---

# DECOMP-01：本体驱动正式任务拆分

本页只定义**正式 PDCA 工作节点/子任务**如何产生。
正式拆分的第一依据是当前固定 ontology/work instance 中已经存在的对象、关系和约束，
不是代码量、工时、模块数量、token、并行度或 Agent 主观复杂度。

## 正式拆分链

```text
ontology object / relation
        -> work node candidate
        -> independent responsibility check
        -> task seed
        -> user selects/creates task
        -> fresh Agent
        -> minimum sufficient ontology subgraph
        -> independent PDCA
```

不得绕过前半段，直接从“实现步骤很多”生成正式子 Agent。

## 候选来源

候选 child 必须能回指：

- 当前固定 ontology revision；
- 一个具名 ontology object/work instance；
- 与父节点之间的语义关系；
- 必要 dependency relation；
- 适用于该节点的 constraints/invariants。

关系本身只是候选来源。只有 NODE-01 的正式任务资格成立时才形成 child seed：
独立职责、固定 I/O、可独立拒收成果、独立验证边界、明确组合责任。

如果无法从模型解释“为什么这是一个独立职责”，就不能为了控制 token、提高并行度或代码结构漂亮而创建正式 task。

## 拆分也是上下文隔离

创建正式 child 的重要目的之一是建立**语义上下文边界**。
child 不继承父/兄弟完整对话，而由 CONTEXT-01 从固定 ontology/work graph 中选择
minimum sufficient subgraph，包括当前 node、必要 relation endpoints、依赖交付、共享不变量、
固定需求和 scene 所需对象。

因此：

- 不用父 Agent 的长历史作为 child 的默认上下文；
- 不用“把整个 ontology 都发过去”替代子图选择；
- 不以摘要压缩代替语义选择；
- 不通过共享记忆把兄弟任务活动状态重新混入。

## Seed 与创建

分解只产生 candidate seed、来源关系、dependency、I/O、AC、组合责任和上下文边界。
父 Agent 可以说明为什么候选成立，但不能自行把候选变成已授权任务。

用户明确选择具名 child 后，宿主按 TASK-01 / agent-dispatch 创建 fresh Agent。
新 child、新 scene、新 attempt 均不继承未来阶段授权。

## Work Unit 的位置

Do-only Work Unit 不是正式任务拆分机制。

它只在**已经存在且已批准的正式 task 的 Do 内部**组织局部执行：

```text
formal ontology-backed task
        -> Do
        -> local Work Unit / command / isolated execution slice
```

Work Unit 不产生新的 node_id，不拥有新的 ontology responsibility，不创建新的 task/attempt，
也不能替代 fresh Agent 的正式上下文隔离。

如果 Work Unit 执行中发现新的独立 ontology responsibility 或原模型缺失，
停止当前扩张，返回 modeling/decomposition 候选；不能把它静默升级成子任务。

## 禁止的拆分依据

以下单独存在时均不能创建正式节点：

- 文件/目录/函数数量；
- LOC；
- 预计工时；
- token 或上下文长度；
- Agent 置信度；
- “可以并行”；
- “需要第二个 Agent”；
- 一个执行命令或测试步骤。

这些可以影响当前 task 内执行方式，但不能创造新的 ontology responsibility。
