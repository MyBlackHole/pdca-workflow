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
revision: 4.0.0-rc.3
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
模型缺失或错误时停止并提出 modeling/新 revision，而不是在实现/验证场景重新拆一棵任务树。

## pdca-model：定义“应该是什么”

输入用户目标、固定事实来源和已采用定义。
Do 建立领域 ontology 及当前 work instance：

- objects/entities；
- attributes；
- semantic relations；
- constraints/invariants；
- requirement coverage；
- work node candidates；
- composition relation；
- dependency relation candidates；
- current node / direct child seed / leaf reason。

正式 child seed 必须按 TREE-01 / NODE-01 / DECOMP-01 从模型关系产生，
不能由代码结构、LOC、token 或并行需求反推一个“模型节点”。

Check 对照原需求、事实来源和反例验证模型覆盖、关系含义和约束可检验性。
Act 只按批准范围固定 ontology revision / work tree / node seed；不自动创建孩子或启动 implement。

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
发现新的独立 ontology responsibility 时停止扩张，回到 modeling/decomposition。

Check 双向检查 source→target 遗漏与 target→source 无模型依据增加，并运行必要产品验证。
Act 固定 implementation release/mapping；未运行 pdca-verify 时仍为 not_run。

## pdca-verify：验证实现是否忠实于模型和需求

用户显式启动新的独立 verify task。
它绑定与被审实现相同的 `work_id/node_id` 和固定 ontology revision，只读取该节点所需的最小子图、
固定 implementation/mapping 以及行为证据。

验证链：

1. requirement → model：需求是否被该节点模型覆盖；
2. model → implementation：object/relation/constraint 是否被忠实投影；
3. implementation → behavior：实际行为是否满足模型和需求；
4. composition/dependency：当前节点与必要邻接节点的固定接口是否一致。

错误模型和错误实现不能互相证明。审查 Agent 不修改被审业务对象或 oracle。
Plan 固定验证问题和标准；Do 实施核验；Check 使用 AI 四遍审查验证核验本身；
Act 由用户选择接受、失败归档、返工或获准发布。

## 覆盖与依赖

工作树定义 composition，DEPENDENCY-01 定义真实输入/产物依赖。
CONTEXT-01 根据二者只选择当前 task 必需的本体子图，不继承其他 Agent 活动历史。

一个 node 的 modeling 完成不表示 implement/verify 已完成；
一个 child 完成不表示 parent 组合自动成立；所有未获准或未运行场景明确 not_run。
输入 ready 只产生可启动建议，仍需要用户具体操作。
