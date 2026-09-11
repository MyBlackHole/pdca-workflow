---
schema: pdca.asset/v2
id: ontology:concept/work-dependency-graph
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.2
summary: 工作实例依赖图、版本提交与检测时机
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-node-contract
  - ontology:concept/work-tree-scheduling
  - ontology:concept/blocking-edges
dependency_spec:
  schema: pdca.dependency-snapshot/v1
  edge_direction: producer_to_consumer
  vertex_identity:
  - work_id
  - tree_revision
  - node_id
  - scene
  exclude_relations:
  - relates_to
  - guides
  algorithms:
  - dfs_three_color
  - kahn_with_cycle_witness
  checkpoints:
  - candidate_edge_change
  - tree_freeze
  - plan_input_binding
  - dispatch
  - plan_to_do
  commit_requires: expected_parent_graph_and_authorized_view_match
---

# 工作实例的依赖快照与查环

## DEPENDENCY-01：组成树不改变，检查实际输入前置

知识库frontmatter的requires/depends_on空图无环不能证明工作调度正确。检查对象是本次工作生成的目标节点、实际输入声明和跨场景固定产物。边统一表示producer→consumer，顶点携带work/tree/node/scene，不混用执行方向。

| 场景 | 自动导出的前置边 | 含义 |
|---|---|---|
| ontology_modeling | 父建模→孩子建模 | 父seed固定交付后展开孩子 |
| ontology_projection | 孩子实现→父实现 | 必需孩子完整PDCA且full交付可用；额外实际输入同样要有生产者 |
| ontology_conformance_verification | 孩子审查→父审查 | 失败对象的有效审查报告也可作为输入，报告本身须完成契约 |

跨场景边必须有真实产物producer身份。整树冻结回执与固定release等工作级屏障可作为不带Agent的具名事件顶点，仅约束时间，不新增业务任务；禁止把未来父实现当成孩子建模已存在输入。冻结前验证所有声明边、屏障和已存在固定外部产物的合法来源。relates_to/guides不产生边。

## 声明、检查与提交的唯一职责

节点建模任务在work-node.dependencies声明具名输入，记录producer_node/scene/artifact、consumer、必需性和来源约束。宿主工作索引唯一写入者把声明与场景导出边合成不可变`graphs/<graph-revision>.md`；semantic判断仍由节点建模任务负责。

图快照记录work/tree、覆盖scope、顶点/有来源的直接边、输入清单摘要、graph_revision、parent_graph_ref/digest、检查器或人工方法、结果、环路径/拓扑顺序。语义图digest由外部check回执引用，不自包含摘要。图不是在task模板里由Agent随手改的可变数组。

检查时机：每次新增/修改候选依赖；整树冻结前；节点Plan固定实际输入时；宿主派发与Plan→Do消费快照时。检查与提交绑定同一scope的expected_parent_revision/digest；宿主无法可靠实现单写者/比较提交则不能并发发布图。

冻结树包含所有声明场景依赖的图快照及检查回执。派发读取工作已授权的pinned_graph_ref/digest，而不是仓库里任意“最新图”；与该工作视图的当前授权快照不匹配就拒绝。其他分支的未批准候选图不能使合法旧固定工作自动失效。新增真实前置不得借绑定优化改变冻结依赖；需要语义变化则回建模新树版本。

Plan只能把已声明生产者落实到可用固定artifact/attempt，不能增加未确认边。建模正在展开新孩子时更新候选图；当前根/父任务只消费其已固定前置，不能被未来后代要求循环阻塞。最终整树检查仍必须覆盖全量节点与场景，局部前沿通过不等于整树通过。

## 算法与拒绝信息

用完整直接邻接表的DFS三色标记或Kahn拓扑排序，时间O(V+E)，不要求存储传递闭包。先拒绝缺失端点、重复身份、自环、来源不明或错误scene引用。检测组成导出边与额外输入边的并集；各子图分别无环不足以通过。Kahn若有剩余顶点，再在剩余子图找出一条实际环，不把所有剩余节点误报成同一个环。

环记录包括闭合node/scene路径、每条边来源、被阻断候选及修正建议；阻止该候选提交/受影响派发，由有权的建模节点新attempt修接口、归属或依赖。冻结版本需要新tree_revision，不能删边伪造就绪，也不能改叶→根原则。

图检查通过后如果当前授权视图换成不同graph_ref/digest，重新检查/明确重新基线，不能复用旧receipt。图的字节完整性不代替生产者交付状态检查；依赖无环也不证明资源获取无死锁，资源按RESOURCE-01排序/成组取得。

## 任务预算与大图

全图检查可以用宿主通用图工具或分片清单扫描，Agent只读环证据和本节点前置摘要。不能只检查直接双向边，也不能为了减少上下文漏掉长环。算法测试可用参考模型，但实际生成图必须另有真实检查记录。

模板：[依赖快照](../../templates/dependency-snapshot.md)、[图检查回执](../../templates/dependency-check.md)。案例覆盖三节点长环、组成与额外边混合环、合法跨场景顺序、检查后改图及空知识依赖图的误用。

## 自动父边不能代替实际产物绑定

父modeling→子modeling可自动导出，不要求重复手写同一边；但孩子额外读取父suite/run/review时，必须逐项固定生产者task/attempt/artifact摘要和适用状态。自动seed边不认证这些额外文件，也不允许读取活动任务的私有上下文。明确导入的固定产物不是“树外资料”。

冻结前的全场景图表达生产关系与顺序，不要求未来projection/verification产物已经存在；这些版本在各自Plan绑定。局部建模前沿检查可用于当前派发，但不得冒充整树全覆盖检查。图check的scope、vertices、edges和graph_digest均对实际图核验。


<a id="dependency-complete-check"></a>
## DEPENDENCY-01 · 覆盖、算法、回执三者一致

图顶点应覆盖固定规格中每个适用 node/scene 及具名屏障；按边来源核验完整端点/身份、组成和跨场景关系。存在完整标签但无顶点不算覆盖。图检查 result=cyclic/invalid/unknown 不得放行，即使 graph_digest 正确；result=acyclic 也须与实际全图重算相符。局部图检查不得冒充 tree_freeze 全域。
