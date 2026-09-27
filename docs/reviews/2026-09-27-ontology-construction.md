# 本体构建审查：reference knowledge 与 project ontology 的边界

日期：2026-09-27
审查基线：`51203294814f690c21cc96a68574ba106c9368ae`（已合并 PR #28，protocol 4.0.0-rc.4 / Skill bundle 5.0.0-rc.3）。

这是维护审查记录，不是正式 PDCA Task、project ontology revision、独立 reviewer 结论或宿主验收。
本轮只审查“当前体系是否足以稳定构建 project ontology”，不修改 normative authority，不新增 schema/validator，也不伪造一个示例项目模型。

## Scope

审查范围包括当前 4.x ontology lifecycle、SCENE-01 的 pdca-model 构建链、`ontology/` 物理知识库结构、representative reference assets、已退役的 3.x meta-ontology / ontology validation / tree-node record shapes，以及 project ontology 的实际落地状态。

不审查 600+ reference 的领域事实是否真实，不把抽样结论扩展成“所有 reference 都错误”。

## Inventory

当前 `ontology/` 共 634 个文件：

| 目录 | 文件数 | 当前角色 |
|---|---:|---|
| concept | 155 | current authority + reference concepts + retired compatibility pointers |
| contracts | 36 | current contracts + retired 3.x record pointers |
| domain | 317 | reference domain knowledge |
| entity | 56 | reference entities / technical models |
| pattern | 40 | reusable reference patterns |
| pitfall | 6 | reference pitfalls |
| principle | 7 | reference principles |
| process | 9 | current phase/scene processes + reference process |
| fact | 1 | historical/reference fact |
| decision/documentation/provenance/role | 4 | supporting knowledge/navigation |
| root | 3 | INDEX / LOAD-MAP / README |

当前树中不存在 `ontology/projects/`。仓库已经有很大的 reference knowledge library，但当前 main 没有一个真实 project/work ontology revision 可作为 4.x Modeling 的落地样例。

## Finding 1 — 物理目录混合三种语义层

`ontology/` 同时存放 runtime normative protocol ontology、reference knowledge library 和规范上预留的 project ontology store。

`ontology/domain/*` 不等于 project domain model；`ontology/entity/*` 不等于当前 work instance；`ontology/pattern/*` 不等于当前 modeling rule。reference 的 relation/attribute 不能因为“已经在 ontology 目录”就自动成为当前模型的一部分。

当前 REUSE→ADOPT 已经提供重要隔离，这是正确方向。

## Finding 2 — 缺少 current project ontology construction contract

ONTOLOGY-01 已经规定 ontology source 应有 stable identity/revision、object/entity、semantic relation、constraint/invariant、applicable work/instance、requirement/source/provenance、unknown/limitation。

但它主要回答“什么东西有资格叫 ontology source”，没有把一个 project ontology revision 的内部语义构成说到足以让不同 Agent 稳定地产生等价结构。

3.x 原来承担类似职责的 `meta-ontology`、`ontology-creation-gate`、`ontology-validate`、`ontology-fidelity-criterion`、`tree-spec/tree-manifest/work-node` 现在都已 retired，并明确不适用于 4.x。

因此 4.x 不是“已有 schema 没启用”，而是确实没有 current rigid project ontology schema。这个选择本身合理，但需要更清晰的 semantic construction contract，否则 Modeling 仍可能退化成自由格式设计文档。

## Finding 3 — reference library 不能直接充当 project ontology

抽样的 active reference 普遍带有 `authority: reference`、`validation.claim_status: unverified`、migration provenance、3.1.0 revision，以及面向历史 task/环境的 testable signal 或 source path。

代表性样本：

- `ontology/domain/core-project-goal.md` 是项目目标知识说明，不是某个 work 的 ontology instance；
- `ontology/domain/core-bcachefs-study-map.md` 是学习导航；
- `ontology/pattern/knowledge-map-building.md` 是方法论；
- `ontology/fact/tls-exec-truncation-investigation-state.md` 是特定历史调查状态；
- `ontology/entity/bcachefs-btree.md` 很接近高质量技术 ontology candidate，但仍是 unverified reference，并包含历史本机路径和 retired structural-check 引用。

这些资产可以提供 definition/claim candidate，但不能整文件 wholesale adopt 成当前 project model。

## Finding 4 — relation semantics 过度依赖关系名和正文解释

reference 中常见 `specializes / instance_of / relates_to / composed_of / guides`，但 current project ontology 没有明确要求 relation type 自身固定 semantic meaning、source/target role、direction、domain/range 或 endpoint kind、需要时的 cardinality，以及 composition/dependency implication。

TREE-01 已正确要求解释“为什么某 relation 是 composition”，但如果 project model 本身没有固定 relation semantics，TREE 仍可能只能靠 Agent 临时解释。

generic `relates_to` 永远不应直接推出 composition 或 dependency。

## Finding 5 — semantic property、constraint 与 verification signal 有混合风险

部分 reference entity 把领域属性、completeness quality claim、constraint、shell/grep testable signal、evidence level 一起放在 `attributes`。

对 reference knowledge 可以容忍，但 project ontology 应严格区分：

1. semantic property：对象本身的属性、类型、单位、范围；
2. relation：对象间语义联系；
3. constraint/invariant：必须满足的规则；
4. observation/test signal：如何验证某 constraint/claim；
5. task acceptance criterion：当前 work 是否接受该产物。

否则“模型是什么”和“怎么检查模型”会再次混成一层。

## Finding 6 — provenance 可追溯，但部分 reference 不可移植

代表性技术 reference 中存在 `/home/black/.../source.c:line`、`records/Txxxx-...` 和某次本机 grep 命令。这些可作为历史环境线索，但不能自动作为另一 project/work 的 current evidence。

project ontology 中的 source ref 应区分：repository + fixed commit + path/symbol、stable external URL/document version、PDCA record ref、environment-local path + explicit environment identity，以及 unknown/missing source。

裸绝对路径不是可移植 provenance。

## Finding 7 — Definition / Work Instance / Work Node 需要更明确分层

正确链应保持：

```text
reusable definition
  -> adopted fixed definition
  -> current work instance
  -> composition/dependency projection
  -> qualified work node
  -> task seed
```

- Definition：可跨 work 复用的语义类型/关系/约束定义；
- Work Instance：这些定义在当前 requirement/project/work 上的具体适用与边界；
- Work Node：从 work instance 责任中投影出的可独立验收工作单位；
- Task：node + scene + attempt 的执行实例。

不能把 reference entity、work instance、node、task 当成同一 ID 的不同叫法。

## Finding 8 — 4.x Modeling pipeline 尚未被真实 project ontology 证明

当前设计链已经比较合理：

```text
root seed
  -> candidate ontology/work instance
  -> TREE candidate
  -> NODE qualification
  -> Check
  -> Act fixes ontology/tree/node
  -> DECOMP seed
```

但 main 中没有 `ontology/projects/.../<revision>` 实例，因此以下问题还没有真实证据：

- 一个 Agent 会把 project model 写成什么；
- 第二个 Agent 是否能只靠 fixed model root 恢复相同语义；
- relation endpoint 是否可无歧义解析；
- requirement coverage 是否完整；
- work instance 与 reusable definition 是否会混淆；
- Check 是否能在不写 validator 的情况下稳定发现缺失 relation/constraint/source；
- fixed project model 是否足以驱动 TREE/NODE/CONTEXT。

所以“规范链已经闭合”不能等价成“ontology construction 已被验证”。

## 应保留的设计方向

- 不创建第二套 semantic validator；
- 不靠 LOC/文件数/图数判断 ontology quality；
- reference 必须 REUSE→ADOPT，不能全库自动加载；
- candidate M2 与 adopted/fixed model 分离；
- TREE / NODE / DECOMP 分离；
- project model 可使用 Markdown 或其他已有格式，不要求统一 JSON/YAML；
- unknown/source limitation 是一等事实；
- Modeling Do/Check 不提前创建正式 child seed。

## 下一轮 normative 修改建议

下一轮应修改现有 authority，而不是增加新的 OntologyManifest 系统。

### A. 扩展 ONTOLOGY-01 为 semantic construction contract

不规定文件格式，但要求每个 project ontology revision 有一个唯一 model root ref，可定位完整 payload，并至少能解析出：revision identity + payload digest、adopted definition refs、requirement refs + explicit coverage、object definitions / object instances、semantic relation definitions + relation instances、constraints/invariants、current work instance、provenance、unknown/limitations。

如果模型拆为多文件，model root 负责定位这些固定组成部分；不需要额外 JSON manifest。

### B. 明确 relation contract

每个用于 project model 的 relation 必须能回答 relation 含义、source/target 角色、endpoint 是否可解析、方向/数量约束（需要时）、是否真的表示 composition/dependency，以及可观察 consequence/invariant（如适用）。

### C. 明确 constraint contract

每个重要 constraint/invariant 至少固定 subject、condition/predicate、applicability、expected invariant、observation/test signal、provenance/requirement source、unknown/limitation。

### D. Modeling Check 做 semantic closure

Check 至少主动检查 identity closure、type/instance consistency、relation endpoint closure、constraint observability、requirement coverage、provenance/source validity、unknown completeness、composition 与 dependency 分离、generic reference relation 没有被误投影，以及 adopted reference 的 stale/retired/local-only source limitation 已被显式处理。

这些是 AI review questions，不是新增 validator。

### E. REUSE/ADOPT 改为 claim/definition scoped adoption

采用一个 reference file 不等于采用其中所有 relations、validation recipes、local paths、historical task claims。ADOPT 应只固定本 work 真正采用的 definition/claim/constraint，其余内容保持 reference context。

### F. 用真实 root modeling 做第一份 project ontology

不要在本审查 PR 中伪造 `ontology/projects` 示例。

下一次真实 host-smoke 应把 bounded-counter 示例真正生成到 `ontology/projects/<test-project>/works/<work>/<revision>/...`，并验证 model root 可由另一 Agent 恢复、requirement→object/relation/constraint coverage、TREE 只来自显式 relation、NODE qualification 可回链、Act fixed 后 DECOMP 才产 child seed、CONTEXT 可只从 fixed ontology/work graph 选 child minimum subgraph。

这才是“本体构建能力”真正通过的证据。

## 非建议项

本轮明确不建议重新启用 3.x ontology-creation-gate、恢复 tree-spec/tree-manifest/work-node 旧 schema、新增 rigid OntologyManifest/ContextManifest、给 600+ reference 批量升级为 project ontology、用 Python/Shell 扫字段并据此判本体 PASS、把 reference 的 composed_of/relates_to 直接当 current tree/dependency，或因 project model 当前为空就预填伪造样例。

## 结论

当前 4.x 的生命周期架构方向是正确的，尤其 REUSE/ADOPT、EVOLVE、TREE/NODE/DECOMP 的拆分已经解决了“知识资产直接变任务”的主要风险。

当前最关键的剩余缺口是：

> project ontology 的 semantic construction contract 还不够具体，而且尚无真实 project ontology revision 证明它可以被不同 Agent 稳定构建、审查、恢复和投影。

因此下一步应先增强 ONTOLOGY-01 / SCENE-01 / REUSE-01 / ADOPT-01 的构建与 closure 语义，再用真实 root modeling 产出第一份 project ontology；而不是继续扩 reference library 或重新引入 schema/validator。