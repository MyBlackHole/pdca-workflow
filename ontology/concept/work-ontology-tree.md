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
dcterms_modified: '2026-09-27'
summary: TREE-01：把版本化 ontology/work relation 投影为 composition tree
---

# TREE-01：Composition projection

TREE-01 只回答：**一个明确版本化的 ontology/work payload 中，哪些语义关系构成当前工作的父子 composition。**
它不定义 node 资格、不生成 task seed，也不承担 dependency graph。

## 输入

工作树 candidate 可以基于一个**明确版本化且有 payload digest 的 proposed ontology revision**；但只有 source ontology revision 已被 Modeling Act 固定，且 payload/digest 与投影时一致，tree 才能成为 fixed tree revision。

投影输入至少包括：

- fixed ontology revision，或明确版本化的 proposed revision/payload digest；
- 当前 work instance；
- 用户目标/requirement coverage；
- 能解释 composition 的 ontology/work relations。

首次 root modeling 开始时只有 root goal seed；seed 本身不是树节点。Modeling Do 形成具名、版本化的 proposed ontology/root work candidate 后，TREE 可以对该 proposed payload 形成 candidate composition；只有 Modeling Act 固定 source revision/tree/node 后，这些结构才可供 DECOMP 使用。

## Composition edge

每条 parent→child composition candidate 必须能说明：

- parent / child ontology object 或 work instance；
- 来源 relation；
- 为什么该关系表示“父职责由子职责组成”；
- shared interface/invariant；
- parent 的组合责任。

文件/目录/函数相邻、执行顺序、可以并行或“实现步骤很多”都不能产生 composition edge。

TREE 只保存 composition 视图。数据/产物依赖由 DEPENDENCY-01 单独维护；
一个 composition child 不代表 parent 一定消费其 output。

## Tree integrity

candidate tree 在 Check 中先检查：

- root 唯一；
- composition 无环；
- edge endpoints 可定位；
- requirement coverage 可追溯；
- parent/child 语义关系能解释；
- unknown / 未决 composition 明确保留。

树中的 candidate node 还必须分别经过 NODE-01 qualification。Modeling Act 只有在 source ontology revision 与 candidate tree/node 都通过当前 Check 后，才按批准范围固定 ontology/tree/node revisions。
哪些已固定合格 node 要形成正式 task seed，由 DECOMP-01 在之后处理；TREE 不直接创建 child/task/Agent。

用户冻结 tree revision 只允许后续 task/DECOMP 引用该固定结构，不自动启动 model/implement/verify。
领域 ontology 可以包含大量不进入 composition tree 的非组成关系。
