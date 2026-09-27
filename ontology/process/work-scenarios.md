---
schema: pdca.asset/v2
id: ontology:process/work-scenarios
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.4
dcterms_modified: '2026-09-25'
summary: SCENE-01：同一本体工作节点依次建模、实现投影、验证实现
scene_ids:
- pdca-model
- pdca-implement
- pdca-verify
scene_start_policy: explicit_user_operation
---

# SCENE-01：Model → Implement → Verify

三个场景固定为 `pdca-model`、`pdca-implement`、`pdca-verify`。
它们描述同一个 ontology-backed work node 的三种工作对象，不是 Plan/Do/Check 的别名。

```text
user requirement
      -> pdca-model
      -> fixed ontology node / relation / constraint
      -> pdca-implement
      -> real projected entity + mapping
      -> pdca-verify
      -> requirement -> model -> implementation -> behavior evidence
```

每个正式 node/scene 都是独立 task，使用自己的 fresh Agent 和 CONTEXT-01 选择出的 minimum sufficient subgraph；
同一 task 内仍由原 Agent 完成 Plan→Do→Check→Act。

## 跨场景身份

同一个 work node 在三个场景中保持：

- 相同 `work_id/node_id`；
- 可追溯的 ontology revision；
- 相同 responsibility 与核心 relation/constraint；
- scene-specific 输入/输出与 AC。

Implement/Verify 不得静默修改 node responsibility、composition 或 ontology meaning。
模型缺失或错误时按 [EVOLVE-01](../concept/ontology-evolution.md) 处置：停止依赖错误模型的实施，
在原授权范围内继续核实、报告；不在实现/验证场景修补模型或重新拆一棵任务树。

## pdca-model：定义“应该是什么”

Plan 固定用户目标、事实来源与建模范围；需要参考知识时先由 REUSE-01 找 candidate，
只有经 ADOPT-01 明确绑定的固定定义才成为本次输入。

Do 建立或按 EVOLVE-01 细化候选 ontology revision / work instance，并可基于该版本化 payload：

- 按 ONTOLOGY-01 形成 objects/attributes/relations/constraints/requirement coverage；
- 按 TREE-01 形成 candidate composition projection；
- 按 NODE-01 对 candidate work node 做 qualification；
- 形成 dependency relation candidates，交由 DEPENDENCY-01 固定真实 consumer dependency。

**Modeling Do/Check 不产生正式 task seed。**
Check 对照原需求、固定输入、EVOLVE delta、TREE integrity 和 NODE qualification 审查候选 M2/tree/node。

Act 只按批准范围固定新的 ontology revision、tree revision 与合格 node。
固定完成后，DECOMP-01 才能从这些已固定 node 产生后续 task seed candidate；
这些 seed 仍需用户选择创建，不自动采用到其他 task、不自动启动 child/implement/verify。

首次 root modeling 也遵守同一时序：root goal seed → candidate model/tree/node → Check → Act 固定第一个 root node/revision → 才允许后续 DECOMP。

## pdca-implement：把模型投影成真实实体

输入当前 `node_id`、固定 ontology revision、CONTEXT-01 子图、目标位置和 mapping rules。
Do 生成代码、文档、配置、数据结构或其他真实实体，并记录：

```text
ontology object / relation / constraint
            -> implementation target
            -> projection rule
            -> verification signal
```

Implement 只实现当前 node 的责任和允许写域。
已有模型中的正式 child 由自己的 task/Agent 实现；当前 task 不把兄弟/孩子完整上下文吸入父任务。

如果 Do 内需要局部拆执行，可以使用 Work Unit；Work Unit 不创造 node_id 或正式 child。
发现新的独立职责时按 EVOLVE-01 报告并停止受影响的扩张；不自动切换 modeling 或派发任务。

Check 双向检查 source→target 遗漏与 target→source 无模型依据增加，并运行必要产品验证。
Act 固定 implementation release/mapping；未运行 pdca-verify 时仍为 not_run。

## pdca-verify：验证实现是否忠实于模型和需求

用户显式启动新的独立 verify task。
它绑定与被审实现相同的 `work_id/node_id` 和固定 ontology revision，初始读取必要子图、
固定 implementation/mapping 以及行为证据；按 CONTEXT-01 在获准读域寻找模型未表达的关系和反证，
不扩大写域、不替换固定输入，也不把待核实资料自动采用为权威。

验证链：

1. requirement → model：需求是否被该节点模型覆盖；
2. model → implementation：object/relation/constraint 是否被忠实投影；
3. implementation → behavior：实际行为是否满足模型和需求；
4. composition/dependency：当前节点与必要邻接节点的固定接口是否一致。

错误模型和错误实现不能互相证明。verify Agent 按 REVIEW-01 保持独立且不修改被审业务对象或 oracle。

Plan 固定验证问题、CASE/oracle 与需要的 observation；Do 执行 requirement/model/mapping/behavior 核验，
TEST-01 只保存实际 observation，EVIDENCE-01 将 findings/observations 绑定到固定 claim。
conformance-review record 保存本 scene 的结构化验证矩阵；Check 再用 flow-check 审查 verify task 自身，
最终 task 结论只由 VERDICT-01 聚合。Act 只执行用户明确批准的处置。

## 覆盖与依赖

工作树定义 composition，DEPENDENCY-01 定义真实输入/产物依赖。
CONTEXT-01 根据二者只选择当前 task 必需的本体子图，不继承其他 Agent 活动历史。

一个 node 的 modeling 完成不表示 implement/verify 已完成；
一个 child 完成不表示 parent 组合自动成立；所有未获准或未运行场景明确 not_run。
输入 ready 只产生可启动建议，仍需要用户具体操作。
