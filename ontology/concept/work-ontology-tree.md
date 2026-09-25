---
schema: pdca.asset/v2
id: ontology:concept/work-ontology-tree
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: TREE-01：从领域本体关系投影工作组成树
---

# TREE-01：从领域本体关系投影工作组成树

工作树不是 Agent 临时写出的调度目录，而是**已固定领域本体及工作实例的任务视图**。
先有可定位的 ontology object / relation / constraint，再判断哪些语义关系投影为工作组成关系。

## 从本体到工作树

根目标绑定一个固定 ontology revision 和 work instance。组成边必须能够回指到模型中的对象及关系，
并说明为什么该关系表示“父目标由这些直接职责组成”，而不是仅因为文件、模块、目录或执行步骤相邻。

每个 work node 至少绑定：

- 稳定 `node_id`；
- 对应 ontology object / work instance；
- ontology revision；
- 当前节点职责；
- 固定输入/输出；
- 适用约束/不变量；
- 可独立验收义务；
- 直接组成关系及其来源；
- 直接依赖关系引用；
- direct child seed 或 leaf 理由。

**Ontology relation 是产生候选节点的来源，但不是每条关系都必须变成任务。**
只有满足 NODE-01 / DECOMP-01 的独立职责和验收边界，才投影为正式 work node。

## 根到叶建模

建模从根向叶展开：

```text
user goal
  -> ontology objects / relations / constraints
  -> work instance
  -> work node candidates
  -> composed work tree
```

父节点只固定直接 child seed、关系、共享接口和组合责任，不替孩子完成自己的详细建模。
孩子由自己的 modeling task 继续判断是否存在更深的本体实体关系与正式节点；不固定深度，也不默认无限展开。

没有独立语义职责的文件修改、函数、命令、测试步骤留在当前节点内部，不进入工作树。

## 冻结与后续场景

最终树清单列：

- 固定 ontology revision；
- 完整 node 集合；
- 每个 node 对应的 ontology object/work instance；
- 组成边及来源关系；
- dependency refs；
- 各 node 的 scene 义务与 AC；
- unknown / 未决关系。

检查根唯一、组成无环、端点存在、需求覆盖以及关系语义能够解释。
用户对具体版本作冻结确认。冻结只允许后续任务引用该结构，不自动创建孩子、不自动启动 implement/verify。

树不是全部知识图。领域 ontology 可以存在大量非组成关系；只有与当前工作职责和验收有关的关系进入工作树。
需求仍是最终判断依据，本体模型必须可被 Check/Verify 推翻。
