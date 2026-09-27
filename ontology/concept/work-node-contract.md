---
schema: pdca.asset/v2
id: ontology:concept/work-node-contract
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: NODE-01：定义一个 ontology-backed work node 是否具备独立任务语义
---

# NODE-01：Work node qualification

NODE-01 只回答：**一个 ontology/work candidate 是否具备稳定、独立、可验收的工作节点语义。**
它不选择 context、不定义 scene 方法、不创建 task seed。

## Node contract

一个正式 work node 至少固定：

- stable `node_id`；
- ontology object / work instance ref 与 ontology revision；
- responsibility；
- inputs / outputs；
- necessary relation endpoints；
- constraints / shared invariants；
- acceptance criteria / oracle；
- composition refs 与组合责任；
- dependency refs；
- unknown / source refs。

scene-specific 输入/输出和模型/投影/验证方法由 SCENE-01 定义，不在 NODE 复制。
task initial context 由 CONTEXT-01 从本 node + relations/dependencies 中选择。

## Qualification

candidate 只有同时满足以下条件才是正式 node：

1. 当前目标中有独立 semantic responsibility；
2. inputs/outputs 可以固定；
3. relation/constraint 来源可定位；
4. 产物可被独立拒收；
5. 存在独立验证边界；
6. 与 parent/sibling 的 composition responsibility 能说明。

“改几个函数”“新增测试文件”“跑一条命令”等只有机械执行意义的部分不是 node；
留在现有 task 内作为步骤或 Do-only Work Unit。

同一 `node_id` 跨 model/implement/verify 保持同一 ontology meaning。
后续 scene 不能静默改 responsibility；模型错误或缺失时回到 modeling/evolution，而不是在 implement/verify 重定义 node。
