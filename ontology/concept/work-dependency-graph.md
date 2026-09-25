---
schema: pdca.asset/v2
id: ontology:concept/work-dependency-graph
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: DEPENDENCY-01：从本体关系投影真实产物依赖，依赖不等于授权
---

# DEPENDENCY-01：本体关系到任务依赖

领域 ontology 可以表达组成、使用、产生、消费、约束、引用等多种关系；
工作 dependency graph 只投影其中**会影响任务输入可用性或组合正确性**的关系。

因此：

- ontology relation 存在，不自动等于 task dependency；
- task dependency 必须能说明来自哪个 ontology/work relation；
- composition tree 与 data/product dependency graph 分开保存；
- dependency edge 不创造用户授权。

## Dependency Edge

每条任务依赖至少说明：

- source node；
- target node；
- 来源 ontology/work relation；
- target 实际需要的固定 output/interface；
- output/version 可用性的证据；
- source 变化后哪些 evidence 会 stale。

不能只依据目录、task name 或 PASS 字段声明 dependency ready。

例如父节点“包含”孩子是 composition；只有父 implement/verify 真正需要孩子固定交付时，
才另外存在 child output -> parent input 的 dependency。

## Ready 与失效

有向数据依赖应无环；若领域存在反馈关系，应通过固定版本/iteration 说明，而不是制造运行时循环等待。

输入 ready 只表示该 task 的固定依赖已经可用，可以向用户提出启动建议；
没有用户操作不能自动创建 task、Agent 或推进阶段。

源 ontology revision、dependency relation 或实际 output 变化后，相关 context refs、mapping、
Check/Verify evidence 必须标 stale；不能继续沿用旧组合结论。

## 上下文用途

CONTEXT-01 读取 dependency graph 时，只取当前 task 真正需要的：

- dependency node 的固定接口/交付；
- 对应 relation 含义；
- version/digest；
- applicability / limitation。

**不读取 dependency task 的完整 Plan/Do/Check/Act 历史。**
依赖提供的是固定事实与交付，不是另一个 Agent 的活动上下文。
