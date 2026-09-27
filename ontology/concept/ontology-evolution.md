---
schema: pdca.asset/v2
id: ontology:concept/ontology-evolution
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: EVOLVE-01：从固定模型产生不覆盖原输入的候选 revision
---

# EVOLVE-01：Ontology revision proposal

EVOLVE-01 只回答：**固定模型 M1 需要怎样变成候选 M2，以及这个变化是否仍在当前 modeling 授权边界内。**
它不采用 M2、不发布共享知识、不创建 work node/task，也不覆盖 M1。

## Revision delta

候选变化必须固定：

- base revision M1；首次 root modeling 可为空；
- proposed revision M2 / payload ref / digest；
- changed objects/relations/constraints；
- requirement/source/observation 动机；
- compatibility / affected refs；
- unknown 与 limitation。

记录格式复用 [ontology-revision](../contracts/record-shapes/ontology-revision.md)，不新增平行 schema。

## 内部细化 vs 边界变化

判断边界看已批准的目标、对外 responsibility/I/O、共享 invariant、AC/oracle、资源与读写域，
而不是“有没有新 entity”。

- **internal refinement**：在已批准 modeling Do/草稿写域内补充内部 object/attribute/relation/constraint，
  且不改变上述外部边界；可以继续形成 M2 candidate。
- **boundary-affecting change**：改变目标、对外接口、shared invariant、AC/oracle、责任分配，
  或需要扩大资源/写域；停止受影响动作，固定 delta/impact 后等待用户决定。

建模中发现新的独立责任，只把它作为 M2 中的 ontology/work relation 事实；
是否形成 work node/task seed 分别由 TREE/NODE/DECOMP 处理，EVOLVE 不创建 child。

## 其他 scene 发现模型缺口

Implement/Verify 可以在获准读域核实遗漏、反证和影响，并形成 revision proposal/evidence；
不能借此修改固定模型、自动采用 M2、修补被审对象或放宽 oracle。
安全且已获准的只读核验可以继续，依赖错误模型的受影响写动作停止。

## Candidate 与 adoption 分离

M2 是 modeling 产出候选，不反写 M1、原 assignment/baseline 或旧 evidence。
Modeling Act 可以按已批准处置固定 M2 为新的项目 ontology revision；
**其他 task 是否改用 M2 仍必须经过 ADOPT-01**。

M2 的出现不会自动使所有 M1 task stale。只有实际 source/relation/output 变化影响具体 consumer 时，
DEPENDENCY-01 才标记相关 refs/evidence stale。共享知识发布也是独立 Act 写入，不由 EVOLVE 自动执行。
