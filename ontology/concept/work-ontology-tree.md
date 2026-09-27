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
summary: TREE-01：把固定 ontology/work relation 投影为 composition tree
---

# TREE-01：Composition projection

TREE-01 只回答：**固定 ontology/work instance 中哪些语义关系构成当前工作的父子 composition。**
它不定义 node 资格、不生成 task seed，也不承担 dependency graph。

## 输入

普通工作树投影必须基于：

- 已固定/adopted ontology revision；
- 当前 work instance；
- 用户目标/requirement coverage；
- 能解释 composition 的 ontology/work relations。

首次 root modeling 在尚无 ontology node 时只有 root goal seed；它不是树节点。
root modeling 固定第一个 ontology/work node 后，才开始普通 tree projection。

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

固定 tree revision 时检查：

- root 唯一；
- composition 无环；
- edge endpoints 可定位；
- requirement coverage 可追溯；
- parent/child 语义关系能解释；
- unknown / 未决 composition 明确保留。

树中的每个正式节点必须另外满足 NODE-01。
哪些合格 node 要形成正式 task seed，由 DECOMP-01 决定；TREE 不直接创建 child/task/Agent。

用户冻结 tree revision 只允许后续 task 引用该固定结构，不自动启动 model/implement/verify。
领域 ontology 可以包含大量不进入 composition tree 的非组成关系。
