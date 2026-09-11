---
schema: pdca.asset/v2
id: ontology:concept/work-tree-scheduling
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.5
summary: 树形调度、并行与交付汇聚
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/pdca-task
  - ontology:concept/capability-protocol
  - ontology:concept/task-rework
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/work-dependency-graph
  - ontology:concept/pdca-phase-status
  - ontology:concept/ontology-adoption
scheduling_spec:
  projection_requires_frozen_tree: true
  projection_child_condition: completed_full_pdca_usable_fixed
  modeling_requires_frozen_tree: false
  review_accepts_subject_failure_report: true
  requires_clear_writer_slot: true
  ancestor_completion_blocks_child: false
  slot_key:
  - work_id
  - tree_revision
  - node_id
  - scene
  attempt_allocator: host_slot_single_writer_monotonic
  graph_authority: DEPENDENCY-01
  resources_authority: RESOURCE-01
  active_is_start_condition: false
---

# 树形就绪、执行槽与发布

## SCHED-01：宿主调度不控制节点内部PDCA

宿主根据已授权树/seed、DEPENDENCY-01固定图、公开固定交付和RESOURCE-01资源资格计算就绪；不读取Agent活动推理、不替其Plan、不代业务判定。依赖前置与资源互斥分开。

| scene | input_ready必要条件 |
|---|---|
| ontology_modeling | 根有用户目标/通用建模契约，或直接父seed正常交付；当前候选图版本与已固定前置一致，不要求先完成整树冻结 |
| ontology_projection | 整树冻结及授权图可核查；所有必需直接孩子完成自己的完整PDCA、full交付固定且delivery_usable；额外实际输入同样可用 |
| ontology_conformance_verification | 固定被审release可读或有明确缺失事实；所需孩子审查报告已经固定有效；报告判subject失败不等于报告不可用 |

孩子仅ready/running或归档失败不得使实现父节点就绪。父节点可在自己的孩子交付后启动，不等无关分支；也不等工作issue关闭或最终发布。每个内部节点、根仍独立完整PDCA，不用汇总孩子PASS替代组合工作。

## eligible_to_start与槽

宿主在实际串行/互斥边界校验：input_ready、绑定图仍是当前授权快照、当前协议与真实新Agent能力、独立消息路由、派发授权/wait-policy明确、槽可取得、私有记录区可取得。建模Plan确定业务写域后再在Plan→Do前取业务资源。slot键(work/tree/node/scene)对应一个有效attempt owner；资源冲突需跨slot/跨work检查。

attempt编号由槽唯一所有者从该槽保留历史中分配max+1，失败/取消不回收编号；task_id来自实际唯一机制并检查冲突。dispatch_request_id在spawn前固定，相同请求只查询同一结果；超时不能自行分配新attempt绕开未知创建。

新attempt只在旧attempt正常completed或合法interrupted、旧执行/记录写权已撤销、影响结清或新scope与保留隔离区不冲突、新任务获授权后取得槽。仅active值、心跳或锁租约到期不足以接管；无法证明安全则阻断。旧返回不能释放新owner资源、覆盖其产物或消费新请求。

## 资源与依赖

独立前沿在已证明容量和RESOURCE-01兼容范围内应并发推进，不得无依据按任务终态串行化；多分支不代表多数据库副本。每次取得/释放/保留资源有实际回执。无可靠排他时只能在允许的合作式串行或真实私有隔离下执行，不做未知旧写者自动接管。

DEPENDENCY-01控制候选修改、整树冻结、Plan绑定、派发和Plan→Do的图核验；实际图包括场景组成前置和额外输入，不能拿知识库空depends_on图代替。就绪检查消费已验证的图和实际交付状态，不能只看拓扑排序。

## 交付和停止

交付包含固定task/attempt、定义/suite/实现/孩子摘要、本地测试、node_local_pass、delivery_usable、原始证据和正常终态回执；本地可用与工作缺陷关闭/整树发布按VERDICT-01分别判定。仅支持full，不采用失败实现的未定义降级例外。

正常结束先固定第四阶段回执和最终task视图，再交回记录写权；宿主封存后索引可见固定交付，不让孩子等待祖先完成。取消在原phase停止并按CONTROL-01结清，不登记为正常完整PDCA交付。用户等待只暂停该任务，无关分支继续。

后续产物改变使实际依赖与祖先组合/审查证据stale，按REWORK-01新attempt处理；发布引用明确图/树/产物集合，不能按mtime选择“最新”。

## 3.3：采用检查不改变任务拓扑

就绪节点启动还需ADOPT-01当前定义采用/公告范围合格；无法确认关键资料资格时blocked而非替换latest。正常新知识版本不阻塞仍采用有效旧版的树；实际迁移或已知错误才产生具名影响任务。全局库索引不是父任务控制者，不将共享发布/其他树完成加入孩子本地交付前置。

<a id="sched-fill-before-wait"></a>
## 就绪前沿：先派发可容纳任务，再进入等待

原目标/已采纳父 seed、当前授权依赖图与完整节点集合决定应检查的候选，不由当前结果目录列表自定。每次固定交付可用、资源/容量变化、确认响应、停止、创建结果查明或任务终态事件到达，宿主重算所有受影响的就绪项；只检查“刚结束任务的下一个兄弟”不充分。

一次调度机会内，在可信事件顺序上重复：核对当前图/输入仍有效 → 在真实余量内选择一个兼容任务 → 取得槽及私有记录区 → 提交真实异步创建 → 记录接受句柄或未知结果占用 → 继续处理其它可容纳任务。已提交创建的原生调用可以逐次发生；不得把“等待该调用被接受”和“等待该任务完整结束”混为一件事。没有可提交者或容量用尽后才等待后继事件。

目标是当前可提交集合达到资源兼容的极大集合，不要求求解全局最优排程，也不要求同一毫秒启动。每个未派发项记录具体前置/容量/冲突/授权/控制证据和下一唤醒条件；“优先 A”“逐个执行”“主界面在等待”不是依赖。按已授权优先级及稳定排序选择，独立旧候选应有可审计的公平性安排，不能被重复新到任务永久饿死。安全停止/用户取消优先，不为填满容量越过权限。

| 事件 | 处理 |
|---|---|
| A 等待自己的 Plan 或 Check 确认 | 只阻断 A 的对应边；B 满足自己的条件就继续。不得提前批准 B 的未来对象。 |
| 容量为2，A结束、B仍运行、C已就绪 | 在本轮事件处理后补入 C，不等待整批终态。 |
| A/B共享写资源、C不冲突 | 串行受冲突限制的部分，仍尝试 C；共享索引单写者不形成全工作锁。 |
| 创建超时、结果未知 | 同一 request_id 查询，不重建；保留其可能占用和写域，只在可证明剩余容量内派发其它任务。 |
| 真实容量仅1 | 可在原授权允许时串行，但报告并行受限；明确要求至少2路的验收不能标通过。 |
| 容量未知或原生工具只阻塞到终态 | 不假定多路；记录缺项并核验能力，不以多个任务名称冒充并发。 |

槽、在途创建、活跃会话、可运行执行位和待确认会话是不同计量。只有后端有证据支持挂起释放执行位时，才按该语义回收；不得把待确认 Agent 当作已经结束而重复派发。必须同时遵守实际会话上限、写权和预算；释放/交回按 RESOURCE，终态文字不自动释放资源。

<a id="sched-parent-local"></a>
## 父局部交付与并发前置

建模孩子在直接父 seed 的固定交付、完整父 PDCA、当前建模验收和可用终态可核验后才能启动；未冻结候选、Act草稿或后来补算摘要不满足。父自身只需完成自身及直接 seed，不等待后代、不等待整树冻结；此处局部候选图不要求提前获得最终全树图。父输入缺陷只阻断其依赖范围；某个孩子失败不阻断无依赖的兄弟。

[调度观测](../../templates/scheduling-observation.md)记录来源事件、完整前沿、容量、被提交请求及每项延期依据。没有事件顺序就不能计算实际并发或空闲原因；目录数量、mtime、spawn 名称不能代替轨迹。生产轨迹的来源核验与离线关系重放分开，有限检查通过不证明宿主真实执行。
