---
schema: pdca.asset/v2
id: ontology:process/select-task-subgraph
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.9
summary: 当前节点的有界上下文选择
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/process
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-node-contract
  - ontology:concept/task-unit-test
  - ontology:concept/ontology-asset
  - ontology:concept/pdca-task
  - ontology:concept/work-dependency-graph
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# 当前节点的有界上下文选择

## CONTEXT-01：选择输入，不改变目标树与任务数

本节点保留原ID以兼容引用。它只控制某个任务读取哪些定义/证据，不再把本体图任意投影为任务DAG。目标树及每节点任务覆盖由TREE-01/SCENE-01确定，不能因为检索只命中部分节点就省略其余任务。

## 输入与动作

1. 确认work/tree/node/scene/attempt，读取当前节点定义或建模seed、适用祖先约束、当前阶段规范、suite索引与授权输入。
2. 知识库只采用适用的active定义；先读ONTOLOGY-01证据状态。reference必须逐主张核验并登记claim-review；blocked只作待审对象，不能继承其旧约束。未核验主张不得成为oracle，不能改写协议。当前建模任务可以读自己的candidate定义作为被测产物，而非已经发布的规范。
3. 按ONTOLOGY-01展开继承/实例约束和必需输入；relates_to/guides只供检索。组成树的全部节点仍必须有任务，但当前Agent不用读取每个后代正文。
4. 组合任务导入直接孩子固定交付包/接口/证据摘要，需查原始事实时按授权固定指针读取；不导入孩子活动对话。审查同理。
5. 记录ID/revision/真实摘要/固定可读位置/选取理由。套件可分批执行，只将相关失败和覆盖摘要装入上下文，不漏掉必需案例。
6. 当前节点无法在预算内实施/组合/审查时，建模阶段继续拆分；冻结后按TREE-01新版本处理，执行Agent不能随意拆成隐藏任务或把多个节点合并。

## 输出与失败

输出有界输入索引和当前节点的内部步骤计划；步骤可关联多条约束，但不是跨节点的任务替代物。必需输入缺失、版本冲突或预算不足时停止并说明，不以全量历史对话兜底。


## 弱关联停止与去重

relates_to/guides默认零隐式递归：只有当前节点的某项明确检索问题需要，才将关联加入候选队列；记录(node_id,revision)的visited、加载理由和直接来源。已读同版本不反复加载；发现同ID不同版本先核对基线，不用“最后读到”覆盖旧约束。

显式检索预算限定文件/字节或宿主可测token及停止条件，数值来自当前任务，不虚构模型容量。弱相关可以在预算到达时停止；必需约束/输入超预算必须blocked并调整读取计划或按TREE重建节点，不能静默删除必需内容。检索环合法、调度边仍只来自DEPENDENCY-01；rule_authorities是规则定位权威，不从relates_to重新推导门禁。

## 3.3：检索与执行读取的区别

建模Plan执行REUSE-01，先记录已查库、版本、候选和不采用理由；其他场景只加载已有definition_refs与闭包，不把检索到的新head替换基线。授权旧库可用baseline_snapshot，但同ID/revision异字节冲突必须阻断；跨namespace别名不自动等价。

可读不等于可采用。外部事实按ONTOLOGY-01，采用/错误公告按ADOPT-01。同一节点部分采用仍需覆盖所有适用必需约束；冻结依赖/术语/用例不能在按需读取时漂移。未读闭包允许延迟加载，但真正使用时必须校验固定摘要。

## 引用用途和读取预算

按照NODE-01先区分protocol_baseline、subject_snapshot、business definition；协议已在工作基线固定时按需读取，不重复伪装为各节点新业务实体。多个兄弟可读同一定义，唯一组成归属不禁止知识复用。源端无稳定约束ID时记录固定字节anchor/原文映射，不能制造不存在的源路径。

本地节点负担的缩减由DECOMP-01评估，包括未来实施与审查，不用缩窄用户范围来满足预算。知识库检索失败与无可用候选分别记录，缺历史records不作create理由。

<a id="context-action-cost"></a>
## 按整个任务观察成本

输入索引将每项写为“是什么、何时读取、固定位置/摘要”；当前必须正文不藏在可选参考链接后。额外领域方法在当前问题需要时按需读取，不因新增skill而自动新增节点或重跑总流程。

压缩或恢复使用 [RECOVERY 导航](../concept/pdca-recovery.md#recovery-capsule)。比较优化时分别记录首次加载、重复读取、恢复后重查和返工；记录实际文件/字节与宿主提供的token，后者不可取得时为unknown，不用字节换算补齐。重复读取减少但漏约束增加不算改进。真实对照方法只在维护时读 [行为评测入口](../../tests/agent-behavior-eval/suite.md)，不属于每次任务必读集。
